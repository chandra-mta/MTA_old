#!/usr/bin/env  /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#       interruptFunctions.py: collections of python scripts for science run interruption computation       #
#                                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                                   #
#                                                                                                           #
#               last update: Sep 12, 2017                                                                   #
#                                                                                                           #
#############################################################################################################

import math
import re
import sys
import os
import string
import astropy.io.fits  as pyfits
import time

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')

#
#--- reading directory list
#
path = '/data/mta/Script/Interrupt/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv
import mta_common_functions as mcf
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#
#--- need a special treatment for the following msids
#
special_list = ['3FAMTRAT', '3FAPSAT', '3FASEAAT', '3SMOTOC', '3SMOTSTL', '3TRMTRAT']


#---------------------------------------------------------------------------------------------------------
#--- findCollectingPeriod: find start and ending time of data collecting/plotting period               ---
#---------------------------------------------------------------------------------------------------------

def findCollectingPeriod(startYear, startYday, stopYear, stopYday):
    """
    for given, starting year/ydate, stopping year/ydate of the interruption, 
    set data collecting/plotting period. output are: data collecting starting 
    year, yday, stopping year, yday, plotting starting year, yday, plotting 
    stopping year, yday, and numbers of pannel needed to complete the plot.
    input:  startYear   --- starting year
            startYday   --- starting ydate
            stopYear    --- stopping year
            stopYday    --- stopping ydate
    output: pYearStart
            periodStart
            pYearStop
            periodStop
            plotYearStart
            plotStart
            plotYearStop
            plotStop
            pannelNum
    """
#   
#--- set up extract time period; starting 2 days before the interruption starts
#--- and end 5 days after the interruption ends.
#

#
#--- check beginning
#
    pYearStart  = startYear
    periodStart = startYday - 2
#   
#--- for the case the period starts from the year before
#
    if periodStart < 1:
        pYearStart -= 1

        chk = 4.0 * int(0.25 * pYearStart)
        if chk == pYearStart:
            base = 366
        else:
            base = 365

        periodStart += base

#
#--- check ending. If the interruption does not finish in a 5 day period, extend
#--- the period at 5 day step wise until it covers the entier interruption period.
#

    chk = 4.0 * int(0.25 * pYearStart)
    if chk == pYearStart:
        base = 366
    else:
        base = 365

    if stopYear == pYearStart:
        pYearStop  = pYearStart
        period     = int((stopYday - periodStart) / 5) + 1
        periodStop = periodStart + 5 * period

        if periodStop > base:
            periodStop -= base
            pYearStop  += 1
    else:
#   
#--- for the case stopYear > pYearStop
#
        pYearStop  = stopYear
        period     = int((stoyYday + base - periodStart) /5 ) + 1
        periodStop = periodStart + 5 * period - base

#
#--- setting plotting time span
#
    plotYearStart = pYearStart
    plotStart     = periodStart
    plotYearStop  = pYearStop
    plotStop      = periodStop

    if plotYearStop > plotYearStart:
        chk = 4.0 * int(0.25 * plotYearStart)

        if chk == plotYearStart:
            base = 366
        else:
            base = 365

        plotYearStop = plotYearStart
        periodStop  += base

    pannelNum    = period      	                                #---- the number of panels needed


    return (pYearStart, periodStart, pYearStop, periodStop, plotYearStart, plotStart, plotYearStop, plotStop, pannelNum)

#----------------------------------------------------------------------------------------------------------
#--- useArc5gl: extrat data using arc5gl                                                                ---
#----------------------------------------------------------------------------------------------------------

def useArc5gl(operation, dataset, detector, level, filetype, startYear = 0, startYdate = 0, stopYear = 0 , stopYdate = 0, deposit = './Working_dir/'):
    """
    extract data using arc5gl. 
    input:  start ---   stop (year and ydate) 
            operation   --- (e.g., retrive) 
            dataset     ---(e.g. flight) 
            detector    --- (e.g. hrc) 
            level       --- (eg 0, 1, 2) 
            filetype    ---(e.g, evt1)
            startYear
            startYdate
            stopYear
            stopYdate
    output: data        --- a list of fits file extracted
    """
#
#--- use arc5gl to extract ephin data
#
    (year1, month1, day1, hours1, minute1, second1, ydate1) = tcnv.dateFormatCon(startYear, startYdate)
    
    (year2, month2, day2, hours2, minute2, second2, ydate2) = tcnv.dateFormatCon(stopYear, stopYdate)

    stringYear1 = str(year1)
    stringYear2 = str(year2)

    arc_start = str(month1) + '/' + str(day1) + '/' + stringYear1[2] + stringYear1[3] 
    arc_start = arc_start   + ',' + str(hours1) + ':'+ str(minute1) + ':00'

    arc_stop  = str(month2) + '/' + str(day2) + '/' + stringYear2[2] + stringYear2[3] 
    arc_stop  = arc_stop    + ',' + str(hours2) + ':'+ str(minute2) + ':00'


    intime = str(startYear) + ':' + adjust_ydate_format(startYdate) + ':00:00:00'
    arc_start = tcnv.axTimeMTA(intime)
    intime = str(stopYear) + ':' + adjust_ydate_format(stopYdate)   + ':00:00:00'
    arc_stop = tcnv.axTimeMTA(intime)
    #print "I AM HERE: " + str(arc_start)  + "<--->" + str(arc_stop)

    line = 'operation='         + operation  + '\n'
    line = line + 'dataset='    + dataset    + '\n'
    line = line + 'detector='   + detector   + '\n'
    line = line + 'level='      + str(level) + '\n'
    line = line + 'filetype='   + filetype   + '\n'

    line = line + 'tstart='   + str(arc_start) + '\n'
    line = line + 'tstop='    + str(arc_stop)  + '\n'

    line = line + 'go\n'

    f = open(zspace, 'w')
    f.write(line)
    f.close()

    cmd  = 'cd ' + deposit + '; arc5gl -user isobe -script ' + zspace + ' >./zlist'
    os.system(cmd)
    cmd  = 'rm ' + zspace
    os.system(cmd)

    infile = deposit + '/zlist'
    f    = open(infile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    cmd  = 'rm ' + infile
    os.system(cmd)

    return data


#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

def adjust_ydate_format(ydate):

    ydate = int(float(ydate))
    sdate = str(ydate)

    if ydate < 10:
        sdate = '00' + sdate
    elif ydate < 100:
        sdate = '0' + sdate

    return sdate

#-------------------------------------------------------------------------------------------------------
#--- useDataSeeker: extract data using dataseeker.pl                                                 ---
#-------------------------------------------------------------------------------------------------------

def useDataSeeker(startYear, startYdate, stopYear, stopYdate, msid):
    """
    extract data using dataseeker. 
    input:  start, stop (e.g., 2012:03:13:22:41)
            msid    ---- msid
    output: data    --- two column data (time and msid data)
    """

#
#--- set dataseeker input file
#

    (year1, month1, day1, hours1, minute1, second1, ydate1, dom1, sectime1)\
                                = tcnv.dateFormatConAll(startYear, startYdate)

    (year2, month2, day2, hours2, minute2, second2, ydate2, dom2, sectime2)\
                                = tcnv.dateFormatConAll(stopYear, stopYdate)
#
#--- check a dummy 'test' file exists. it also needs param directory
#
    if not os.path.isfile('test'):
        fo = open('./test', 'w')
        fo.close()

    try:
        clean_dir('param')
    except:
        cmd = 'mkdir ./param 2> /dev/null'
        os.system(cmd)

    mcf.rm_file('./temp_out.fits')
#
#--- name must starts with "_"
#
    mc  = re.search('deahk',  msid.lower())
    mc2 = re.search('oobthr', msid.lower())
#
#--- deahk cases
#
    if mc is not None:
        atemp = re.split('deahk', msid)
        val   = float(atemp[1])
        if val < 17:
            name = 'rdb..deahk_temp.' + msid.upper() + '_avg'
        else:
            name = 'rdb..deahk_elec.' + msid.upper() + '_avg'
#
#--- oobthr cases
#
    elif mc2 is not None:
        name = 'mtatel..obaheaters_avg._' + msid.lower() + '_avg'
#
#--- special cases (see the list at the top)
#
    elif msid.upper() in special_list:
        name = msid.upper() + '_AVG'

    else:
        name = '_' + msid.lower() + '_avg'
#
#--- create dataseeker command
#
    cmd1 = '/usr/bin/env PERL5LIB="" '
    
    cmd2 = ' source /home/mta/bin/reset_param; '
    cmd2 = ' '
    cmd2 = cmd2 + ' /home/ascds/DS.release/bin/dataseeker.pl '
    cmd2 = cmd2 + ' infile=test  outfile=temp_out.fits  '
    cmd2 = cmd2 + ' search_crit="columns=' + name
    cmd2 = cmd2 + ' timestart='  + str(sectime1)
    cmd2 = cmd2 + ' timestop='   + str(sectime2)
    cmd2 = cmd2 + ' " loginFile='+ house_keeping + 'loginfile '
    
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
    
    cmd  = 'rm /data/mta/dataseek* 2>/dev/null'
    os.system(cmd)


    [cols, tbdata] = read_fits_file('./temp_out.fits')
    mcf.rm_file('./temp_out.fits')

    time = list(tbdata.field('time'));
    vals = list(tbdata.field(cols[1]));

    data = [time, vals]

    return data

#------------------------------------------------------------------------------------------------------
#-- read_fits_file: read table fits data and return col names and data                               --
#------------------------------------------------------------------------------------------------------

def read_fits_file(fits):
    """
    read table fits data and return col names and data
    input:  fits--- fits file name
    output: cols--- column name
    tbdata  --- table data
    to get a data for a <col>, use:
    data = list(tbdata.field(<col>))
    """
    hdulist = pyfits.open(fits)
#
#--- get column names
#
    cols_in = hdulist[1].columns
    cols= cols_in.names
#
#--- get data
#
    tbdata  = hdulist[1].data
    
    hdulist.close()
    
    return [cols, tbdata]


#--------------------------------------------------------------------------------------------------
#--- sci_run_add_to_rad_zone_list: adding radiation zone list to rad_zone_list                  ---
#--------------------------------------------------------------------------------------------------

def sci_run_add_to_rad_zone_list(file='NA'):

    """
    adding radiation zone list to rad_zone_list. 
    input: file     --- the name of inputfile containing:
                e.g. 20120313        2012:03:13:22:41        2012:03:14:13:57         53.3   auto
    output  <house_keeping>/rad_zone_list
    """
#
#--- check whether the list alread exists; if it does, read which ones are already in the list
#
    cmd = 'ls ' + house_keeping + '* > ./ztemp'
    os.system(cmd)
    test = open('./ztemp').read()
    os.system('rm -f ./ztemp')
 
    m1   = re.search('rad_zone_list',  test)
    m2   = re.search('rad_zone_list~', test)

    eventList = []
    echk      = 0
    if m1 is not None:
        line = house_keeping + 'rad_zone_list'
        f    = open(line, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        for ent in data:
            atemp = re.split('\s+|\t+', ent)
            eventList.append(atemp[0])
            echk = 1


#
#--- if file is not given (if it is NA), ask the file input
#

    if file == 'NA':
        file = raw_input('Please put the intrrupt timing list: ')

    f    = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

#
#--- put the list in the reverse order
#
    data.reverse()

    for ent in data:
        if not ent:
            break

#
#--- a starting date of the interruption in yyyy:mm:dd:hh:mm (e.g., 2006:03:20:10:30)
#--- there could be multiple lines of date; in that is the case, the scripts add the rad zone list
#--- to each date
#

        etemp = re.split('\s+', ent)
        echk = 0
        for comp in eventList:
           if comp == etemp[0]:
               echk = 1
               break

        if echk == 0:
    
            atemp = re.split(':', etemp[1])
            year  = atemp[0]
            month = atemp[1]
            date  = atemp[2]
            hour  = atemp[3]
            mins  = atemp[4]

#
#--- convert to dom/sec1998
#
            ydate = tcnv.findYearDate(int(year), int(month), int(date))
            dom   = tcnv.findDOM(int(year), int(ydate))
            line  = year + ':' + str(int(ydate)) + ':' + hour + ':' + mins + ':00'
            csec  = tcnv.axTimeMTA(line)

#
#--- end date
#

            atemp  = re.split(':', etemp[2])
            eyear  = atemp[0]
            emonth = atemp[1]
            edate  = atemp[2]
            ehour  = atemp[3]
            emins  = atemp[4]
     
            ydate  = tcnv.findYearDate(int(eyear), int(emonth), int(edate))
            line   = eyear + ':' + str(int(ydate)) + ':' + ehour + ':' + emins + ':00'
            csec2  = tcnv.axTimeMTA(line)

#
#--- date stamp for the list
#
            list_date = str(year) + str(month) + str(date)
#
#--- check radiation zones for 3 days before to 5 days after from the interruptiondate
#--- if the interruption lasted longer than 5 days, extend the range 7 more days
#

            begin = dom - 3
            end   = dom + 5

            diff  = csec2 - csec
            if diff > 432000:
                end += 7
#
#--- read radiation zone infornation
#
            infile = house_keeping + '/rad_zone_info'
            f      = open(infile, 'r')
            rdata  = [line.strip() for line in f.readlines()]
            f.close()
        
            status = []
            rdate  = []
            chk    = 0
            last_st= ''
            cnt    = 0
        
            for line in rdata:
                atemp = re.split('\s+', line)
        
                dtime = float(atemp[1])                 #--- dom of the entry or exit
        
                if chk  == 0 and atemp[0] == 'ENTRY' and dtime >= begin:
                    status.append(atemp[0])
                    rdate.append(dtime)
                    chk += 1
                    last_st = atemp[0]
                    cnt += 1
                elif chk > 0 and dtime >= begin and dtime <= end:
                    status.append(atemp[0])
                    rdate.append(dtime)
                    last_st = atemp[0]
                    cnt += 1
                elif atemp[1] > end and last_st == 'EXIT':
                    break
                elif atemp[1] > end and last_st == 'ENTRY':
                    status.append(atemp[0])
                    rdate.append(dtime)
                    cnt += 1
                    break
            
            f = open('./temp_zone', 'w')

#
#--- a format of the output is, e.g.: '20120313    (4614.2141112963,4614.67081268519):...'
#

            line = list_date + '\t'
            f.write(line)
        
            upper = cnt -1
            i = 0;
            while i < cnt:
                line = '(' + str(rdate[i]) + ','
                f.write(line)
                i += 1
                if i < upper:
                    line = str(rdate[i]) + '):'
                    f.write(line)
                else:
                    line = str(rdate[i]) + ')\n'
                    f.write(line)
                i += 1
        
            f.close()

#
#--- append the past rad zone list 
#

            oldFile = house_keeping + '/rad_zone_list~'
            crtFile = house_keeping + '/rad_zone_list'
    
            if m1 is not None:
                cmd = 'cat '+ './temp_zone ' + crtFile +  ' > ./temp_comb'
                os.system(cmd)
    
            else:
                os.system('mv .temp_zone ./temp_comb')

            os.system('rm ./temp_zone')

#
#--- save the old file and move the update file to rad_zone_list
#

            if m2 is not None:
                cmd     = 'chmod 775 ' + crtFile + ' ' +  oldFile
                os.system(cmd)
        
            if m1 is not None:
                cmd     = 'mv ' + crtFile + ' ' + oldFile
                os.system(cmd)
        
                cmd     = 'chmod 644 ' +  oldFile
                os.system(cmd)
        
            cmd     = 'mv  ' + './temp_comb ' + crtFile
            os.system(cmd)


#------------------------------------------------------------------------------------------------------------
#--- sci_run_compute_gap: for given data, recompute the science run lost time excluding rad zones         ---
#------------------------------------------------------------------------------------------------------------

def sci_run_compute_gap(file = 'NA'):
    """
    for a given file name which contains a list like: "20120313        2012:03:13:22:41        2012:03:14:13:57         53.3   auto", recompute the lost science time (excluding radiation zone) 
    input:  file   --- input file name
    output: file   --- update file
    """
#
#--- if file is not given (if it is NA), ask the file input
#

    if file == 'NA':
        file = raw_input('Please put the intrrupt timing list: ')

    f = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

#
#--- a starting date of the interruption in yyyy:mm:dd:hh:mm (e.g., 2006:03:20:10:30)
#--- there could be multiple lines of date; in that is the case, the scripts add the rad zone list
#--- to each date
#

    update = []

    for ent in data:

        if not ent:                         #--- if it is a blank line end the operation
            break

        etemp = re.split('\s+', ent)
        atemp = re.split(':', etemp[1])
        year  = atemp[0]
        month = atemp[1]
        date  = atemp[2]
        hour  = atemp[3]
        mins  = atemp[4]

#
#--- convert to dom/sec1998
#
        ydate = tcnv.findYearDate(int(year), int(month), int(date))              #--- a function from convertTimeFormat
        dom   = tcnv.findDOM(int(year), int(ydate), int(hour), int(mins), 0)     #--- a function from convertTimeFormat
        line  = year + ':' + str(ydate) + ':' + hour + ':' + mins + ':00'
        csec  = tcnv.axTimeMTA(line)                                             #--- a function from convertTimeFormat

#
#--- end date
#

        atemp  = re.split(':', etemp[2])
        eyear  = atemp[0]
        emonth = atemp[1]
        edate  = atemp[2]
        ehour  = atemp[3]
        emins  = atemp[4]

        ydate = tcnv.findYearDate(int(eyear), int(emonth), int(edate))
        dom2  = tcnv.findDOM(int(eyear), int(ydate), int(ehour), int(emins), 0)
        line  = eyear + ':' + str(ydate) + ':' + ehour + ':' + emins + ':00'
        csec2 = tcnv.axTimeMTA(line)
    
#
#--- date stamp for the list
#
        list_date = str(year) + str(month) + str(date)

#
#--- read radiation zone information from "rad_zone_list" and add up the time overlap with 
#--- radiatio zones with the interruption time period
#

        line  = house_keeping + '/rad_zone_list'
        f     = open(line, 'r')
        rlist = [line.strip() for line in f.readlines()]
        f.close()

        sum = 0
        for record in rlist:
            atemp = re.split('\s+', record)
            if list_date == atemp[0]:
                btemp = re.split(':', atemp[1])

                for period in btemp:

                    t1 = re.split('\(', period)
                    t2 = re.split('\)', t1[1])
                    t3 = re.split('\,', t2[0])
                    pstart = float(t3[0])
                    pend   = float(t3[1])

                    if pstart >= dom and  pstart < dom2:
                        if pend <= dom2:
                            diff = pend - pstart
                            sum += diff
                        else:
                            diff = dom2 - pstart
                            sum += diff
                    elif pstart < dom2 and pend > dom:
                        if pend <= dom2:
                            diff = pend - dom
                            sum += diff
                        else:
                            diff = dom2 - dom
                            sum += diff

                break
                
        sum *= 86400                            #--- change unit from day to sec

        sciLost = (csec2 - csec - sum) / 1000   #--- total science time lost excluding radiation zone passes

        line = etemp[0] + '\t' + etemp[1] + '\t' + etemp[2] + '\t' + "%.1f" %  sciLost  + '\t' + etemp[4]

        update.append(line)
#
#--- update the file 
#
    oldfile = file + '~'
    cmd = 'mv ' + file + ' ' + oldfile
    os.system(cmd)
    f = open(file, 'w')
    for ent in update:
        f.write(ent)
        f.write('\n')

    f.close()

#-----------------------------------------------------------------------------------------
#---removeNoneData: remove data which is missing and replaced as a very small value     --
#-----------------------------------------------------------------------------------------

def removeNoneData(x, y, xnew, ynew, lower, upper=1e99):

    'remove data which is missing and replaced as a very small value.'


    for i in range(0, len(y)):
       if y[i] > lower and y[i] < upper:
          xnew.append(x[i])
          ynew.append(y[i])


