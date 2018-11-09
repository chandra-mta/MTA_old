#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           create_weekly_report.py: create weekly report                                                   #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Nov 09, 2018                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import copy
import math
import Cookie
import unittest
import time
import random

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release;  source /home/mta/bin/reset_param ', shell='tcsh')
#ascdsenv['IDL_PATH'] = '+/usr/local/rsi/user_contrib/astron_Oct17/pro:+/home/mta/IDL:/home/nadams/pros:+/data/swolk/idl_libs:/home/mta/IDL/tara:widget_tools:utilities:event_browser'
ascdsenv['IDL_PATH'] = '+/data/mta/Script/Weekly/IDL_lib/pro:+/home/mta/IDL:/home/nadams/pros:+/data/swolk/idl_libs:/home/mta/IDL/tara:widget_tools:utilities:event_browser'
ascdsenv2 = getenv('source /proj/sot/ska/bin/ska_envs.csh', shell='tcsh')
#ascdsenv2['IDL_PATH'] = '+/usr/local/rsi/user_contrib/astron_Oct17/pro:+/home/mta/IDL:/home/nadams/pros:+/data/swolk/idl_libs:/home/mta/IDL/tara:widget_tools:utilities:event_browser'
ascdsenv2['IDL_PATH'] = '+/data/mta/Script/Weekly/IDL_lib/pro:+/home/mta/IDL:/home/nadams/pros:+/data/swolk/idl_libs:/home/mta/IDL/tara:widget_tools:utilities:event_browser'
 
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folders
#
#sys.path.append(base_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#
#--- set directory paths
#
d_dir  = '/data/mta4/www/DAILY/mta_deriv/'
wdir   = '/data/mta/Script/Weekly/'
tdir   = wdir + 'Templates/'
odir   = '/data/mta4/www/REPORTS/'
#
#--- admin email address
#
admin  = 'tisobe@cfa.harvard.edu,msobolewska@cfa.harvard.edu'
ephtv_list = ['5EIOT', '5EPHINT', 'HKEBOXTEMP', 'HKGHV', 'HKN6I', 'HKN6V', 'HKP27I', 'HKP27V', 'HKP5I', 'HKP5V', 'HKP6I', 'HKP6V', 'TEIO', 'TEPHIN']

#------------------------------------------------------------------------------------------
#-- create_weekly_report: main script to create the weekly report for the week          ---
#------------------------------------------------------------------------------------------

def create_weekly_report(date, year, debug = 0):
    """
    main script to set up the weekly report template for the week
    input:  date    --- date in the format of mmdd (e.g. 0910)
            year    --- year in the format of yyyy (e.g. 2015)
            debug   --- if it is other than 0, print out some output
    output: a direcotry containing templete (e.g. Sep10)
    """
#
#--- if the test is requested, create Test directory
#
    if debug != 0:
        os.system('mkdir /data/mta/Script/Weekly/Test/')
        odir = '/data/mta/Script/Weekly/Test/'
    else:
        odir = '/data/mta4/www/REPORTS/'

    oned  = 86400

    syear = str(year)                       #--- 4 digit year
    yrd2  = year[2] + year[3]               #--- 2 digit year
    year  = int(float(year))                #--- integer year
    
    date  = str(date)

    smon  = date[0] + date[1]               #--- two digit month
    mon   = int(float(smon))                #--- integer month
    lmon  = tcnv.changeMonthFormat(mon)     #--- month in letter (e.g.Mar)

    sday  = date[2] + date[3]               #--- two digit mday
    day   = int(float(sday))                #--- integer mday

    stop = tcnv.convertDateToCTime(year, mon, day, 0, 0, 0)

    day_n = stop - 7 * oned
#    tout  = tcnv.axTimeMTA(day_n)
#    ttemp = re.split(':', tout)
#    iru_start  = str(ttemp[0]) + '_' + str(ttemp[1])

    #day01 = stop - 6 * oned
    #day0  = stop - 7 * oned
    day01 = stop - 5 * oned
    day0  = stop - 6 * oned
    lday0 = stime_to_ddate(day0)
    sday0 = sdate_to_ldate(lday0)
    start = day0
    lday1 = stime_to_ddate(day01)

    tout  = tcnv.axTimeMTA(day0)
    ttemp = re.split(':', tout)
    iru_start  = str(ttemp[0]) + '_' + str(ttemp[1])
#
#---  year of the beginning of the period; could be different from that of the end
#
    byear      = ttemp[0]    

    lday0 = stime_to_ddate(day0)

    day1  = stop - 5 * oned
    lday1 = stime_to_ddate(day1)

    day2  = stop - 4 * oned
    lday2 = stime_to_ddate(day2)
    sday2 = sdate_to_ldate(lday2)

    day3  = stop - 3 * oned
    lday3 = stime_to_ddate(day3)

    day4  = stop - 2 * oned
    lday4 = stime_to_ddate(day4)
    sday4 = sdate_to_ldate(lday4)

    day5  = stop - 1 * oned
    lday5 = stime_to_ddate(day5)

    day6  = stop 
    lday6 = stime_to_ddate(day6)
    sday6 = sdate_to_ldate(lday6)

    #tout  = tcnv.axTimeMTA(day5)
    tout  = tcnv.axTimeMTA(day6)
    ttemp = re.split(':', tout)
    iru_stop    = '_' + str(ttemp[1])

    day7  = stop + 1 * oned
    lday7 = stime_to_ddate(day7)
#
#---- setting file name
#
    atemp = re.split('\/', lday6)
    file_date  = atemp[0] + atemp[1]
    file_date2 = atemp[0] + '/' + atemp[1]
    file_name  = file_date + '.html'
#
#--- title
#
    titledate     = lday0 + ' - ' + lday6

    ldate         = sdate_to_ldate(lday6)
    ldate_sp      = sdate_to_ldate_with_space(lday6)

#
#--- focal temp file name
#
    fptemp        = file_date + '_fptemp.png'
    fpext_range   = str(start)+' '+  str(stop)
    fpstart       = str(start)
    fplsub        = '"'+ sday0 + '", "' + sday2  + '", "' +  sday4  + '", "' + sday6 + '"'
    fpdsub        = str(day0) + ', ' + str(day2) + ', ' + str(day4) + ', ' + str(day6)
#
#--- IRU span
#
    irudate       = iru_start + iru_stop
    irudate       = str(syear) + '/' +  iru_start + iru_stop        #--- Jul 27, 2018
#
#--- telemetry idl command
#
    telmstart     = stime_to_ddate2(start)
    telmstop      = stime_to_ddate2(stop)
    telem_command = 'weekly_telem,' + telmstart + ',' + telmstop
#
#--- telemetry header line
#
    daylist = '|' + lday0 +'|' + lday1 + '|' + lday2 +'|' + lday3 +'|' + lday4 +'|' + lday5 +'|' + lday6  

#
#--- find trending dates/title
#
    tfile = tdir + 'trending_order'
    f    = open(tfile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    data.reverse()
    chk = 0
    for ent in data:
        if ent == '\s+' or ent == '':
            continue 

        atemp = re.split(' : ', ent)
        adate = atemp[0].strip()
        aname = atemp[1].strip()
        file_date2.strip()
        if chk == 0:
            if str(adate) == str(file_date2):
                title = aname
                chk   = 1
        else:
            if aname == title:
                last_trend_date = adate
                break
#
#--- index.html input
#
    s1 = sday0[0:3] + ' ' + sday0[3:5]
    s2 = sday6[0:3] + ' ' + sday6[3:5]
    index = '<td> <a href="./' + str(year) + '/' + file_date + '.html">' + s1 + ' - ' + s2 + '</a>'
#
#--- debugging output
#
    if debug != 0:
        print "file_name; "       + file_name 
        print "title date: "      + titledate
        print "ldate: "           + ldate
        print "fptemp: "          + fptemp
        print "fpext_range: "     + fpext_range
        print "fpstart: "         + fpstart
        print " fplsub: "         + fplsub
        print " fpdsub: "         + fpdsub
        print "irudate: "         + irudate
        print "telmstart: "       + telmstart
        print "telmstop: "        + telmstop
        print "telmcommand: "     + telem_command
        print "daylist: "         + daylist
        print "title: "           + title
        print "last_trend_date: " + last_trend_date
        print "index: "           + index
#
#--- create a work directory
#
    cmd = 'mkdir ' + wdir  + ldate
    os.system(cmd)
    outdir = wdir + ldate + '/'

    cmd = 'cp ' + tdir + 'get_ftemp_data.perl' + ' ' + outdir
    os.system(cmd)
    cmd = 'cp ' + tdir + 'subst3.perl'         + ' ' + outdir
    os.system(cmd)
    cmd = 'cp ' + tdir + 'test'                + ' ' + outdir
    os.system(cmd)

    cmd = 'mkdir ' + outdir + '/param'
    os.system(cmd)

#
#--- create instruction page
#
    tfile = tdir + 'instruction'
    f     = open(tfile, 'r')
    input = f.read()
    f.close()
    input = input.replace('#LDATE_S#', ldate_sp)
    input = input.replace('#LDATE#',   ldate)
    input = input.replace('#DDATE#',   file_date)
    input = input.replace('#YEAR#',    syear)
    input = input.replace('#DAYLIST#', daylist)
    input = input.replace('#TELM_CMD#',telem_command)
    input = input.replace('#INDEX#',    index)

    ofile = outdir  + ldate.lower()
    fo    = open(ofile, 'w')
    fo.write(input)
    fo.close()
#
#--- focal temp related files
#
#    tfile = tdir + 'get_ftemp_wrap_script'
#    f     = open(tfile, 'r')
#    input = f.read()
#    f.close()
#
#    input = input.replace('#MANDD#',  ldate)
#    ofile = outdir + 'get_ftemp_wrap_script'
#    fo    = open(ofile, 'w')
#    fo.write(input)
#    fo.close()
#    cmd = 'chmod 755 ' + outdir + 'get_ftemp_wrap_script'
#    os.system(cmd)
#
#    tfile = tdir + 'get_ftemp_main_script'
#    f     = open(tfile, 'r')
#    input = f.read()
#    f.close()
#
#    #input = input.replace('#START#',  str(start))
#    #input = input.replace('#STOP#',   str(stop))
#    input = input.replace('#START#',  str(start + 86400))
#    input = input.replace('#STOP#',   str(stop + 86400))
#    ofile = outdir + 'get_ftemp_main_script'
#    fo    = open(ofile, 'w')
#    fo.write(input)
#    fo.close()
#
#    cmd = 'chmod 755 ' + outdir + 'get_ftemp_main_script'
#    os.system(cmd)
#
#    tfile = tdir + 'plot_erad_time.pro'
#    f     = open(tfile, 'r')
#    input = f.read()
#    f.close()
#
#    input = input.replace('#START#',       str(start))
#    input = input.replace('#SDATELIST#',   fpdsub)
#    input = input.replace('#LDATELIST#',   fplsub)
#    ofile = outdir + 'plot_erad_time.pro'
#    fo    = open(ofile, 'w')
#    fo.write(input)
#    fo.close()
#
#    cmd = 'cp -f ' + outdir + 'plot_erad_time.pro ./Focal/'
#    os.system(cmd)
#
#--- this_week file
#
    tfile = tdir + 'this_week'
    f     = open(tfile, 'r')
    input = f.read()
    f.close()
    input = input.replace('#DDATE#',   file_date)
    input = input.replace('#IRUSPAN1#', irudate)
    input = input.replace('#IRUSPAN2#', irudate)
    input = input.replace('#TITLE#',    title)
    input = input.replace('#TITLEDATE#',titledate)

    atemp = last_trend_date
    atemp = atemp.replace('/', '')
    input = input.replace('#PREVREPORT#', atemp)

    atemp = re.split('/', last_trend_date)
    pmon  = int(float(atemp[0]))
    lmon  = tcnv.changeMonthFormat(pmon)
    line  = lmon + ' ' + atemp[1]
#
#--- the previous report could be from the last year
#
    ryear = syear
    if mon < pmon:
        ryear = year -1
        ryear = str(ryear)

    input = input.replace('#RYEAR#',      ryear)

    input = input.replace('#PREVDATE#',   line)

    atitle = str(title)
    atitle = atitle.replace(' ', '_')

    #file  = tdir + 'Headers/' + atitle
    #fs    = open(file, 'r')
    #trend = fs.read()
    #fs.close()
    #input = input.replace("#TREND#", trend)

    [temp1, temp2, temp3, temp4] = read_cti_values()
    input = input.replace('#ATEMP#',  temp1)
    input = input.replace('#ATEMP2#', temp2)
    input = input.replace('#DTEMP#',  temp3)
    input = input.replace('#DTEMP2#', temp4)

    [val, step] = read_sim()
    input = input.replace('#WMOVE#', val)
    input = input.replace('#WSTEP#', step)
#
#--- make photon and bad pixel output
#
    run_bad_pix_and_photon(outdir)
#
#--- run to get focal temp fits files
#
    tstop = stop + 86400
    #[fcnt, fdata] = run_focal_temp_data(outdir, start, stop, fptemp)
    [fcnt, fdata] = run_focal_temp_data_new(fptemp, outdir)

    input = input.replace('#TEMPPEAK#', str(fcnt))
    input = input.replace('#TEMPLIST#', fdata)
#
#--- bad pixel
#
    file  = outdir + 'bad_pix_list'
    fs    = open(file, 'r')
    bdata = fs.read()
    fs.close()
    input = input.replace('BAD_PIXEL_TABLE', bdata)
#
#--- photon
#
    file  = outdir + 'photons'
    fs    = open(file, 'r')
    pdata = fs.read()
    fs.close()
    input = input.replace('PHOTON_TABLE', pdata)
#
#--- telem data
#
    update_weekly_telem(year, byear, mon)

    tdata = run_telem_data(telem_command, daylist, outdir)
    input = input.replace('TELEM_TABLE', tdata)
#
#--- trend data
#
    trend = set_trend_data_input(str(date))
    input = input.replace('#TREND#', trend)
#
#--- write out the weekly report
#
    ofile = outdir + file_name
    fo    = open(ofile, 'w')
    fo.write(input)
    fo.close()
#
#--- clean up
#
    cmd = 'rm ./out ./out2'
    os.system(cmd)
#
#--- move files
#
    move_files(date, year, outdir, file_name, fptemp, odir)
#
#--- send out email to admin; notify the job complete
#
    send_email_to_admin(date, year)


#----------------------------------------------------------------------------------
#-- stime_to_ddate: change data in second from 1998.1.1 to mm/dd/yy format       --
#----------------------------------------------------------------------------------

def stime_to_ddate(stime):
    """
    change data in second from 1998.1.1 to mm/dd/yy format
    input:  stime   --- time in seconds from 1998.1.1
    output: dtime   --- date in the form of mm/dd/yy (e.g. 08/19/15)
    """
    tlist       = tcnv.axTimeMTA(stime)
    atemp       = re.split(':', tlist)
    year        = int(float(atemp[0]))
    ydate       = int(float(atemp[1]))
    [mon, date] = tcnv.changeYdateToMonDate(year, ydate)

    lyear       = str(atemp[0])
    syr         = lyear[2] + lyear[3]
    
    smon  = str(mon)
    if mon < 10:
        smon = '0' + smon
    
    sday  = str(date)
    if date < 10:
        sday = '0' + sday
    
    dtime = smon + '/' + sday + '/' + syr
    
    return dtime

#----------------------------------------------------------------------------------
#-- stime_to_ddate2: change data in second from 1998.1.1 to yyyymmdd format      --
#----------------------------------------------------------------------------------

def stime_to_ddate2(stime):
    """
    change data in second from 1998.1.1 to yyyymmdd format
    input:  stime   --- time in seconds from 1998.1.1
    output: dtime   --- date in the form of yyyymmdd (e.g. 20150819)
    """
    tlist       = tcnv.axTimeMTA(stime)
    atemp       = re.split(':', tlist)
    year        = int(float(atemp[0]))
    lyear       = str(atemp[0])
    ydate       = int(float(atemp[1]))
    [mon, date] = tcnv.changeYdateToMonDate(year, ydate)
    

    smon  = str(mon)
    if mon < 10:
        smon = '0' + smon
    
    sday  = str(date)
    if date < 10:
        sday = '0' + sday
    
    dtime = lyear + smon + sday 
    
    return dtime

#----------------------------------------------------------------------------------
#-- sdate_to_ldate: change date in second from 1998.1.1 to MMMdd                 --
#----------------------------------------------------------------------------------

def sdate_to_ldate(sdate):
    """
    change date in second from 1998.1.1 to MMMdd
    input:  stime   --- time in seconds from 1998.1.1
    output: ldate   --- date in form of MMMdd (e.g. Aug19)
    """

    atemp = re.split('\/', sdate)
    mon   = int(float(atemp[0]))
    lmon  = tcnv.changeMonthFormat(mon)

    ldate = lmon + atemp[1]

    return ldate

#----------------------------------------------------------------------------------
#-- sdate_to_ldate_with_space: change date in second from 1998.1.1 to MMM dd     --
#----------------------------------------------------------------------------------

def sdate_to_ldate_with_space(sdate):
    """
    change date in second from 1998.1.1 to MMM dd
    input:  stime   --- time in seconds from 1998.1.1
    output: ldate   --- date in form of MMM dd (e.g. Aug 19)
    """

    atemp = re.split('\/', sdate)
    mon   = int(float(atemp[0]))
    lmon  = tcnv.changeMonthFormat(mon)

    ldate = lmon + ' ' +  atemp[1]

    return ldate


#----------------------------------------------------------------------------------
#-- read_cti_values: read cti values from the fitting result files               --
#----------------------------------------------------------------------------------

def read_cti_values():
    """
    read cti values from the fitting result file
    input:  none but read from /data/mta_www/mta_cti/Plot_adjust/fitting_result etc
    output: ftemp1  --- Adjucted cti in CTI/year
            ftemp2  --- Adjucted cti in CTI/day
            ftemp3  --- Detrended cti in CTI/year
            ftemp4  --- Detrended cti in CTI/day
    """

    file = '/data/mta_www/mta_cti/Plot_adjust/fitting_result'

    [ftemp1, ftemp2] = read_cti(file)

    file = '/data/mta_www/mta_cti/Det_Plot_adjust/fitting_result'

    [ftemp3, ftemp4] = read_cti(file)

    return [ftemp1, ftemp2, ftemp3, ftemp4]


#----------------------------------------------------------------------------------
#-- read_cti:  find a cti value from the file                                    --
#----------------------------------------------------------------------------------

def read_cti(file):
    """
    find a cti value from the file
    input:  file    ---- the file name
    output: ftemp1  ---- cti in CTI/year
            ftemp2  ---- cti in CTI/day
    """

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    chk = 0
    for ent in data:
        if chk == 0:
            mc = re.search('mn K alpha', ent)
            if mc is not None:
                chk = 1
                continue
        else:
            mc = re.search('ACIS-I Average:', ent)
            if mc is not None:
                atemp = re.split('\s+', ent)
                val   = float(atemp[2])
                yval  = val / 365.0
                ftemp1 = '%2.3e' % val
                ftemp2 = '%2.3e' % yval
                break


    return [ftemp1, ftemp2]


#----------------------------------------------------------------------------------
#-- read_sim: read sim movement values from weekly averaged page                 --
#----------------------------------------------------------------------------------

def read_sim():
    """
    read sim movement values from weekly averaged page
    input:  none, but read from /data/mta_www/mta_sim/wksum.html
    output: val     --- weekly average time/step
            step    --- counts of TSC moves
    """

    f    = open('/data/mta_www/mta_sim/wksum.html', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    data.reverse()

    i = 0
    for line in data:
        if line == '':
            continue

        if i == 4:
            atemp = re.split('<td>', line)
            btemp = re.split('</td>', atemp[1])
            val   = btemp[0].strip()
            val   = float(val)
            val   =  "%1.5f" % (val)
            val   = str(val)
        elif i == 13:
            atemp = re.split('<td>', line)
            btemp = re.split('</td>', atemp[1])
            step  = btemp[0].strip()
            break

        i += 1


    return [val, step]

#----------------------------------------------------------------------------------
#-- run_bad_pix_and_photon: run bad pixel table script and photon table scrit    --
#----------------------------------------------------------------------------------

def run_bad_pix_and_photon(outdir):
    """
    run bad pixel table script and photon table scrit
    input:  outdir  --- output directory name 
    output: files in outdir: bad_pix_list, photons
    """

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 =  'perl /data/mta4/MTA/bin/weekly_obs2html.pl 8 photons'
    cmd  = cmd1 + cmd2

#
#--- run the phonton script
#
    bash(cmd,  env=ascdsenv)
    mcf.rm_file(zspace)


    cmd2 = 'perl ' + tdir + 'read_bad_pix_new.perl'
    cmd  = cmd1 + cmd2

#
#--- run the bad pixel script
#
    bash(cmd,  env=ascdsenv)
    mcf.rm_file(zspace)

    cmd = 'mv photons bad_pix_list ' + outdir
    os.system(cmd)


#----------------------------------------------------------------------------------
#-- run_focal_temp_data_new: run focal temp script and create a plot, read a table   --
#----------------------------------------------------------------------------------

def run_focal_temp_data_new(fptemp, outdir):
    """
    read output of find_focal_temp_peaks.py and get focal temp information
    input:  fptemp  --- plot output name
            outdir  --- output directory
            read '/data/mta/Script/Weekly/Focal/focal_temp_list'
    output: fcnt    --- number of peaks observed
            fdata   --- table input
    """
#
#--- read the html table entries
#
    f    = open('/data/mta/Script/Weekly/Focal/focal_temp_list', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    fcnt  = len(data)
    fdata = ''
    for ent in data:
        fdata = fdata + ent + '\n'
#
#--- move the plot to an appropriate place
#
    cmd = 'mv /data/mta/Script/Weekly/acis_focal_temp.png ' + outdir + fptemp
    os.system(cmd)

    return [fcnt, fdata]

#----------------------------------------------------------------------------------
#-- run_focal_temp_data: run focal temp script and create a plot, read a table   --
#----------------------------------------------------------------------------------

#def run_focal_temp_data(outdir, start, stop, fptemp):
#    """
#    run focal temp script and create a plot, read a table
#    input:  outdir  --- output direcotry name
#            start   --- start time in seconds from 1998.1.1
#            stop    --- stop time in seconds from 1998.1.1
#            fptemp  --- plot name
#    output: fcnt    --- number of peaks observed
#            fdata   --- table input
#    """
#
#    cmd  = 'cp -f Templates/test .'
#    os.system(cmd)
#
#    cmd1 = '/usr/bin/env PERL5LIB="" '
#    #cmd2 = ' source /home/mta/bin/reset_param ; '
#    cmd2 =  ' /usr/local/bin/perl ' + outdir + 'get_ftemp_data.perl ' + str(start) + ' ' +  str(stop)
#    cmd  = cmd1 + cmd2
##
##--- run the focal temp script to extract data
##
#    bash(cmd,  env=ascdsenv)
#
#    cmd = 'cp -f *fits ./Focal/.'
#    os.system(cmd)
#
#    cmd = 'rm ./test'
#    os.system(cmd)
#
#    cmd = 'mv -f *fits ./Focal'
#    os.system(cmd)
#
#    cmd1 = "/usr/bin/env PERL5LIB="
#    cmd2 = ' idl ./Focal/run_temp > out'
#    cmd  = cmd1 + cmd2
##
##--- run the focal temp script to create a plot
##
#    bash(cmd,  env=ascdsenv2)
#
#    cmd = 'mv -f ./Focal/*fits ' + outdir 
#    os.system(cmd)
#
#    cmd = 'mv ./Focal/*.png ' + outdir + fptemp
#    os.system(cmd)
##
##--- read focal temp data
##
#    [fcnt, fdata] = read_focal_temp_output()
#
#    cmd = 'rm ./out'
#    ###os.system(cmd)
#
#    return [fcnt, fdata]

#----------------------------------------------------------------------------------
#-- read_focal_temp_output: read the focal temperature output and adjust it for better look 
#----------------------------------------------------------------------------------

def read_focal_temp_output():
    """
    read the focal temperature output and adjust it for better look
    input:  none, but read from forcal temp script output
    output: fcnt    --- number of peaks
            out     --- adjucted table
    """

    f    = open('./out', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    rows = []
    chk  = 0
    for ent in data:
        if chk == 0:
            mc = re.search('ALT', ent)
            if mc is not None:
                chk = 1
                continue
        else:
            mc1 = re.search('<tr',  ent)
            mc2 = re.search('</tr', ent)
            if mc1 is not None:
                save = ent
            elif mc2 is not None:
                save = save + ent
                rows.append(save)

    out = ''
    for ent in rows:
        atemp = re.split('<td>', ent)
        line  = '<tr align=center>'
        for i in range(1, 4):
            btemp = re.split('</td>', atemp[i])
            val   = float(btemp[0])
            val   = "%3.2f" % (val)
            val   = str(val)
            line  = line + '<td>' + val + '</td>'
        out = out +  line + '<td align=left>&#160</td></tr>\n'
        
    fcnt = len(rows)

    return [fcnt, out]

#----------------------------------------------------------------------------------
#-- update_weekly_telem: adjusting weekly_telem.pro                              --
#----------------------------------------------------------------------------------

def update_weekly_telem(year, byear,  mon):
    """
    adjusting weekly_telem.pro
        --- line 55 is the check of monthly boundary. it needs to be updated.
    input:  year    --- year in 4 digit
            bear    --- year of beginning date
            mon     --- month in 
    output: <wdir>/Telem/weekly_telem.pro updated
    """
#
#--- convert year, byear, and mon to integer
#
    year  = int(float(year))
    byear = int(float(byear))
    mon   = int(float(mon))
#
#--- if the year changes from the beginning of the period to the end of the period
#--- use the year of the beginning of the period and change the monthe Dec (12)
#
    if byear < year:
        year = byear
        mon  = 12
    else:
        mon -= 1                #--- a quick fix for the month change mon was "this month"
                                #--- and the transition occurs from the last month to this month

    mon_plus = (0, 32, 29, 32, 31, 32, 31, 32, 32, 31, 32, 31, 32)
    nyear = year
    nmon  = mon + 1
    if nmon > 12:
        nyear += 1
        nmon   = 1

    lday = mon_plus[mon]
#
#--- if it is a leap year, the end of Feb is 29
#
    if mon == 2:
        if tcnv.isLeapYear(year):
            lday += 1

    smon = str(mon)
    if mon < 10:
        smon = '0' + smon

    snmon = str(nmon)
    if nmon < 10:
        snmon = '0' + snmon

    this = str(year)  + smon  + str(lday)
    that = str(nyear) + snmon + '01'

    file = tdir + 'weekly_telem_template'
    f    = open(file, 'r')
    data = f.read()
    f.close()
    data = data.replace('#THIS#', this)
    data = data.replace('#THAT#', that)

    out  = wdir + 'Telem/weekly_telem.pro'
    fo   = open(out, 'w')
    fo.write(data)
    fo.close()

    cmd = 'chmod 755 ' + out
    os.system(cmd)

#----------------------------------------------------------------------------------
#-- run_telem_data: run telemetry data idl script and clean up the result        --
#----------------------------------------------------------------------------------

def run_telem_data(telem_command, daylist, outdir):
    """
    run telemetry data idl script and clean up the result
    input:  telem_command   --- idl command to extract data (e.g. weekly_telem,20150904,20150910)
            daylist         --- date header for telem.txt
            outdir          --- output directory name
    output: tdata           --- a table data created by the process
    """

    fo = open('./run_telem', 'w')
    fo.write("cd,'./Telem/'\n")
    fo.write(telem_command)
    fo.write('\n')
    #fo.write("cd,'../'\n")
    fo.write('exit\n')
    fo.close()

    fo = open('./Telem/header', 'w')
    fo.write(daylist)
    fo.write('\n')
    fo.close()

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' idl ./run_telem > out2'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv2)

    ##cmd  = 'idl ./run_telem > out2'
    ##os.system(cmd)
    ##cmd  = 'rm ./run_telem'
    ##os.system(cmd)

    cmd = 'cat ./Telem/header ./Telem/telem.txt > temp'
    os.system(cmd)
    cmd = 'mv temp ./Telem/telem.txt'
    os.system(cmd)
    
    cmd = 'cd ./Telem; perl ./telem.pl ./telem.txt ./telem.html > zzz'
    os.system(cmd)
    cmd = 'cd ./Telem; perl ./zx_find_error2.perl zzz > zx_error_list'
    os.system(cmd)
    cmd = 'cd ./Telem; perl ./zx_remove.perl > ./clean_list'
    os.system(cmd)
    cmd = 'cd ./Telem; perl ./reduce_entry.perl'
    os.system(cmd)
    cmd = 'cd ./Telem; perl ./telem.pl ./reduced_clean_list  telem.html'
    os.system(cmd)
    os.system(cmd)
    
    f     = open('./Telem/telem.html', 'r')
    edata = [line.strip() for line in f.readlines()]
    f.close()
#
#--- removing ephtv entries
#
    chk    = 0
    tdata  = ''
    for ent in edata:
        atemp = re.split('<tr><td>', ent)
        try:
            if atemp[1] in ephtv_list:
                chk = 1
        except:
            pass

        if ent == '</tr>':
            chk = 0
        if chk == 0:
            tdata = tdata + ent + '\n'

    cmd = 'mv ./Telem/telem.html ' + outdir
    os.system(cmd)

    cmd = ' cd ./Telem; rm -rf  zzz zx_error_list ./clean_list  ./reduced_clean_list ./header ./telem.txt ./run_telem'
    os.system(cmd)
    return tdata


#---------------------------------------------------------------------------------
#-- set_trend_data_input: create trend data table input                         --
#---------------------------------------------------------------------------------

def set_trend_data_input(tdate):
    """
    create trend data table input
    input:  tdate   --- date of the report
    output: out     --- string  of the html table of the trend
    """
#
#--- find which data to read from the report date
#
    title = find_input_title(tdate)
#
#--- read msid lists
#
    title  = title.replace(' ', '_')
    ltitle = title.lower()

    file = tdir + 'Headers/Dsave/' +  str(ltitle)
    f= open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- read header file
#
    file = tdir + '/Headers/' +  str(title)
    f= open(file, 'r')
    hdata = [line.strip() for line in f.readlines()]
    f.close()
#
#--- read group display name
#
    file = tdir + '/Headers/group_name'
    f= open(file, 'r')
    out = [line.strip() for line in f.readlines()]
    f.close()
    g_dict = {}
    for ent in out:
        atemp = re.split(':', ent)
        g_dict[atemp[0]] = atemp[1]

#
#--- create a dictionary which contains table name (e.g.acistemp.html) as key
#--- and head lines as data
#
    chk = 0
    hdict = {}
    for ent in hdata:
        if chk == 0:
            atemp = re.split('.html', ent)
            fname = atemp[0]
            line = ''
            chk = 1
        else:
            if ent == "<-->":
                hdict[fname] = line + '\n\n'
                chk = 0
                continue
            else:
                line = line + ent + '\n'
#
#--- go around all the data for the week
#
    out = '' 
    for ent in data:
        atemp     = re.split('<>', ent)
        btemp     = re.split('.html', atemp[0])
        group     = btemp[0]
        msid_list = re.split(':', atemp[1])
#
#--- read the current data from the web page
#
        disp = g_dict[group]
        save =  create_html_table(group, disp,  msid_list)
        out  = out + save
        out  = out + '</table>\n</ul >\n<br />\n\n\n'

    return out

#---------------------------------------------------------------------------------
#-- find_input_title: find data set name from the given report date             --
#---------------------------------------------------------------------------------

def find_input_title(tdate):
    """
    find data set name from the given report date
    input:  tdate   --- the date of the report in the form of mmdd, e,g 0910
    output: title   --- the name of the data (file)
    """

    tfile = tdir + 'trending_order'
    f= open(tfile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    
    data.reverse()
#
#--- the loop to locate the corresponding date
#
    title = 'na'

    for ent in data:
        if ent == '\s+' or ent == '':
            continue
    
        atemp = re.split(' : ', ent)
        adate = atemp[0].strip()
        adate = adate.replace('/', '')
        aname = atemp[1].strip()

        if adate == tdate:
            title = aname
            break
#
#--- if it can't find a corresponding date, send an error email and exit
#
    if title == 'na':
        fo = open(zspace, 'w')
        fo.write("Given date does may not be correct; can't find corresponding trend input. Exiting\n")
        fo.close()
        cmd = 'cat ' + zspace + ' | mailx -s "Subject: Weekly Report Error" ' + admin
        os.system(cmd)
        mcf.rm_file(zspace)

        print "Given date does may not be correct; can't find corresponding trend input. Exiting\n"
        exit(1)

    return title

#----------------------------------------------------------------------------------
#-- move_files: move the created files to the report directory                   --
#----------------------------------------------------------------------------------

def move_files(date, year, out_dir, file_name, fptemp, odir):
    """
    move the created files to the report directory
    input:  date        --- input date
            year        --- year of the data
            out_dir     --- output directory
            file_name   --- name of the output file
            fptemp      --- name of forcal temp gif file
            odir        --- output directory
    output: /data/mta4/www/REPORTS/yyyy/mmdd.html and focal temp plot
    """

    html_dir = odir + str(year)
#
#--- when year changes, you need to create a new output directory
#
    if os.path.isdir(html_dir) == False:
        cmd = 'mkdir ' + html_dir
        os.system(cmd)

    ofile    = out_dir + file_name
    pngfile  = out_dir + fptemp
    cmd      = 'cp ' + ofile + ' ' + pngfile + ' ' +  html_dir
    os.system(cmd)

    cmd      = 'chmod 775 '      + html_dir + '/*'
    os.system(cmd)

    cmd      = 'chgrp mtagroup ' + html_dir + '/*'
    os.system(cmd)

#----------------------------------------------------------------------------------
#-- send_email_to_admin: send out a notification email to admin                  --
#----------------------------------------------------------------------------------

def send_email_to_admin(date, year):
    """
    send out a notification email to admin
    input:  date        --- input date
            year        --- year of the data
    output: email to admin
    """


    line = 'Weekly Report for ' + str(date) + ' (' + str(year) + ') is created. Please check, '
    line = line + 'especially radiation condition of the week. \n\n'
    line = line + 'https://cxc.cfa.harvard.edu/mta/REPORTS/' + str(year) + '/' + str(date) + '.html\n\n'
    line = line + "Don't forget to edit index file: /data/mta4/www/REPORTS/index.html.\n"

    fo = open(zspace, 'w')
    fo.write(line)
    fo.close()

    cmd = 'cat ' + zspace + ' | mailx -s "Subject: Weekly Report for ' + str(date) + ' Created" ' + admin
    os.system(cmd)
    mcf.rm_file(zspace)

#----------------------------------------------------------------------------------
#-- find_date_and_year_for_report: find nearest Thursday date                    --
#----------------------------------------------------------------------------------

def find_date_and_year_for_report():
    """
    find nearest Thursday date 
    input:  none
    output: date    --- date of the nearest Thu in the format of mmdd (e.g. 0910)
            year    --- year of the nearest Thu
    """
#
#--- find today's date information (in local time)
#
    tlist = time.localtime()

    year  = tlist[0]
    mon   = tlist[1]
    day   = tlist[2]
    wday  = tlist[6]
    yday  = tlist[7]
#
#--- find the differnce to Thursday. wday starts on Monday (0)
#
    diff  = 3 - wday

    if diff != 0:
        yday += diff
        if yday < 1:
            year -= 1
            if tcnv.isLeapYear(year):
                base = 366
            else:
                base = 365

            yday = base - yday
#
#--- converting the year and ydate into the standard date output
#
        tline = str(year) + ' ' +str(yday)
        tlist = time.strptime(tline, "%Y %j")

        year  = tlist[0]
        mon   = tlist[1]
        day   = tlist[2]
#
#--- change the date foramt to mmdd (e.g. 0910)
#
    smon = str(mon)
    if mon < 10:
        smon = '0' + smon
    sday = str(day)
    if day < 10:
        sday = '0' + sday

    date = smon + sday

    year = str(year)

    return [date, year]

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def create_html_table(group, disp, msid_list):
    """
    create table msid entries of the group
    input:  group       --- group name
            disp        --- dispaly name
            msid_list   --- a list of msid in the group
    output: hline       --- html table elements
    """
#
#--- check whether this is the sun angle group
#
    mc     = re.search('_att', group)
    if mc is not None:
        att = 1
        group = group.replace('_att', '')
    else:
        att = 0

    group  = group.lower()
    cgroup = group.capitalize()
#
#--- set a path and html link to the main page
#
    if att == 0:
        ifile = '/data/mta4/www/MSID_Trends/' + cgroup + '/' + group + '_mid_static_long_main.html'
        hgrp  = 'https://cxc.cfa.harvard.edu/mta/MSID_Trends/' + cgroup + '/' + group + '_mid_static_long_main.html'
    else:
        ifile = '/data/mta4/www/MSID_Trends/' + cgroup + '/' + group + '_mid_long_sun_angle.html'
        hgrp  = 'https://cxc.cfa.harvard.edu/mta/MSID_Trends/' + cgroup + '/' + group + '_mid_long_sun_angle.html'

    hline = '<ul><li><h3><a href="' + hgrp + '">' + disp + '</a></h3></li></ul>\n'
    hline = hline + '<table border=1 cellpadding=3 cellspacing=2 style="margin-left:auto;margin-right:auto;text-align:center;">\n'
    if att == 0:
        hline = hline + '<th>MSID</th><th>Mean</th><th>RMS</th><th>Delta/Yr</th>'
        hline = hline + '<th>Delta/Yr/Yr</th><th>Unit</th><th>Description</th>\n'
    else:
        hline = hline + '<tr><th colspan=10>Select msid to open the Sun Angle Page</th></tr>\n'

    f     = open(ifile, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    ccnt = 0
    for msid in msid_list:
        msid = msid.lower()
#
#--- normal msid case
#
        if att == 0:
            for ent in data:
                mc = re.search(msid, ent)
                if mc is None:
                    continue
    
                atemp = re.split('</th>', ent)
                btemp = re.split('"',  atemp[0])
                html  = 'https://cxc.cfa.harvard.edu/mta/MSID_Trends/' + cgroup + '/' 
                html  = html + msid.capitalize()  + '/' + msid + '_mid_static_long_plot.html' 
    
                hline = hline + '<tr><th><a href="javascript:WindowOpener3(\''+  html + '\')">' + msid + '</th>'
                btemp = re.split('<th', atemp[1])
                hline = hline + btemp[0] + '</tr>\n'
                break 
#
#--- sun angle has a special way to display the table
#
        else:
            for ent in data:
                mc = re.search(msid, ent)
                if mc is None:
                    continue
                html  = 'https://cxc.cfa.harvard.edu/mta/MSID_Trends/' + cgroup + '/' 
                html  = html + msid.capitalize()  + '/' + msid + '_mid_long_sun_angle.html' 

                hline = hline + '<th><a href="javascript:WindowOpener3(\''+  html + '\')">' + msid + '</th>\n'
            ccnt += 1
            if ccnt >= 10:
                hline = hline + '</tr>\n<tr>\n'
                ccnt = 0
    if att == 1:
        hline = hline + '</tr>\n'

    return hline


#------------------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- set whether this is debuggin mode (anything larger than 0) or not (normal mode: 0)
#
    debug = 0
#
#--- if the date (in format of mmdd, e.g. 0910) and year are given
#
    if len(sys.argv) >= 2:
        date = sys.argv[1]
        year = sys.argv[2]
        create_weekly_report(date, year, debug = debug)
#
#--- if the date is not given, find the nearest Thu date
#
    else:
        [date, year] = find_date_and_year_for_report()
        print "Weekly Report Date: " + str(year) + ' / ' + str(date)
        create_weekly_report(date, year, debug = debug)
