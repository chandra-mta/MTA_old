#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       extract_goes.py: extract GOES-11/15 data and plot the results           #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Spe 12, 2017                                       #
#                                                                               #
#       P1    .8 -   4.0 MeV protons (Counts/cm2 sec sr MeV) Uncorrected        #
#       P2   4.0 -   9.0 MeV protons (Counts/cm2 sec sr MeV) Uncorrected        #
#       P5  40.0 -  80.0 MeV protons (Counts/cm2 sec sr MeV) Uncorrected        #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import string

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
#--- append path to a privte folder
#

sys.path.append(bin_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv

#
#--- Science Run Interrupt related funcions shared
#

import interruptFunctions as itrf

#-----------------------------------------------------------------------------------------------
#--- extractGOESData: extract GOES data from NOAA site, and create a local data base         ---
#-----------------------------------------------------------------------------------------------

def extractGOESData(event, start, stop, comp_test='NA'):

    """
    Extract GOES data from NOAA site, and create a locat data base. 
    input:  event       --- event name
            start       --- starting time
            stop        --- stopping time
                (e.g., 20120313        2012:03:13:22:41        2012:03:14:13:57'
           comp_test    --- option; if given, testing 
                            (if comp_test == test, the test data will be read)
    output: <data_dir>/<event>_goes.txt
            <stat_dir>/<event>_geos_stat
    """

#
#--- modify date formats
#
    begin = start + ':00'
    (year1, month1, date1, hours1, minutes1, seconds1, ydate1, dom1, sectime1) = tcnv.dateFormatConAll(begin)
    end   = stop  + ':00'
    (year2, month2, date2, hours2, minutes2, seconds2, ydate2, dom2, sectime2) = tcnv.dateFormatConAll(end)

#
#--- find plotting range
#

    (pYearStart, periodStart, pYearStop, periodStop, plotYearStart, plotStart, plotYearStop, plotStop, pannelNum) \
                 = itrf.findCollectingPeriod(year1, ydate1, year2, ydate2)
#
#--- reformat plotting start / stop time 
#
    (year3, month3, date3, hours3, minutes3, seconds3, ydate3, dom3, sectime3) = tcnv.dateFormatConAll(pYearStart, periodStart)
    (year4, month4, date4, hours4, minutes4, seconds4, ydate4, dom4, sectime4) = tcnv.dateFormatConAll(pYearStop, periodStop)

#
#--- set input data type: old if pre 2011, otherwise new
#--- the first two is from http://goes.ngdc.noaa.gov/data/avg/ and the 'new' one is from http://www.swpc.noaa.gov/ftpdir/lists/pchan/
#--- although they all use p1, p2, and p5, the value are not compatible.
#
    if year3 <= 2009:
        dtype = 'G105'
    elif year3 < 2011:
        dtype = 'G115'
    else:
        dtype = 'new'

#
#--- create a list of html address from which we extract GOES data
#
    htmlList = []
#
#--- for the starting year and the ending year is same
#
    if year3 == year4:
#
#--- for the case the starting month and ending month is same
#
        if month3 == month4:
            tmon = str(month3)
            if month3 < 10:
                tmon = '0' + tmon

            for tday in range(date3, date4+1):
                if tday < 10:
                    tday = '0' + str(tday)
                else:
                    tday = str(tday)

                timeStamp = str(year3) + tmon + tday
#
#--- after 2012, the data are obtained from different site. data are largely missing
#--- 2011, and previous to that we have all record at ngdc site
#
                if dtype == 'new':
#                    html  = 'http://www.swpc.noaa.gov/ftpdir/lists/pchan/' + timeStamp + '_Gp_pchan_5m.txt'
                    html  = '/data/mta4/www/DAILY/mta_rad/GOES/' + timeStamp + '_Gp_pchan_5m.txt'
                else:
                    syear = str(year3)
                    html  = 'http://goes.ngdc.noaa.gov/data/avg/' + str(year3) + '/' + dtype + syear[2] + syear[3] + tmon + '.TXT'

                htmlList.append(html)

        else:
#
#---- for the case, the period goes over two months
#
            if month3 == 2:
                chk = 4.0 * int(0.25 * year3)
                if chk == year3:
                    endDate = 29
                else:
                    endDate = 28
            elif month3 == 1 or month3 == 3 or month3 == 5 or month3 == 7 or month3 == 8 or month3 == 10:
                endDate = 31
            else:
                endDate = 30

            tmon = str(month3)
            if month3 < 10:
                tmon = '0' + tmon

            for tday in range(date3, endDate+1):
                timeStamp = str(year3) + tmon + str(tday)
                if dtype == 'new':
                    html  = '/data/mta4/www/DAILY/mta_rad/GOES/' + timeStamp + '_Gp_pchan_5m.txt'
                else:
                    syear = str(year3)
                    html  = 'http://goes.ngdc.noaa.gov/data/avg/' + str(year3) 
                    html  = html + '/' + dtype + syear[2] + syear[3] + tmon + '.TXT'

                htmlList.append(html)

            tmon = str(month4)
            if month4 < 10:
                tmon = '0' + tmon

            for tday in range(1, date4+1):
                if tday < 10:
                    tday = '0' + str(tday)
                else:
                    tday = str(tday)

                timeStamp = str(year3) + tmon + tday
                if dtype == 'new':
                    html = '/data/mta4/www/DAILY/mta_rad/GOES/' + timeStamp + '_Gp_pchan_5m.txt'
                else:
                    syear = str(year3)
                    html = 'http://goes.ngdc.noaa.gov/data/avg/' + str(year3) + '/' 
                    html = html + dtype + syear[2] + syear[3] + tmon + '.TXT'

                htmlList.append(html)
    else:
#
#--- for the case the period goes over two years
#
        for tday in range(date3, 32):
            timeStamp = str(year3) + tmon + str(tday)
            if dtype == 'new':
                html      = '/data/mta4/www/DAILY/mta_rad/GOES/' + timeStamp + '_Gp_pchan_5m.txt'
            else:
                syear = str(year3)
                html = 'http://goes.ngdc.noaa.gov/data/avg/' + str(year3) + '/' 
                html = html + dtype + syear[2] + syear[3] + tmon + '.TXT'

            htmlList.append(html)

        for tday in range(1, date4+1):
            if tday < 10:
                tday = '0' + str(tday)
            else:
                tday = str(tday)

            timeStamp = str(year4) + tmon + tday
            if dtype == 'new':
                html      = '/data/mta4/www/DAILY/mta_rad/GOES/' + timeStamp + '_Gp_pchan_5m.txt'
            else:
                syear = str(year3)
                html = 'http://goes.ngdc.noaa.gov/data/avg/' + str(year4) + '/' 
                html = html + dtype + syear[2] + syear[3] + tmon + '.TXT'

            htmlList.append(html)
#
#--- prepare to print out data
#
    if comp_test == 'test':
        ofile = test_data_dir + event + '_goes.txt'
    else:
        ofile = data_dir + event + '_goes.txt'

    out   = open(ofile, 'w')
    line  = 'Science Run Interruption: ' + str(start) +'\n\n'
    out.write(line)
    out.write('dofy\t\tp1\t\t\tp2\t\t\tp5\n')
    out.write("-------------------------------------------------------------------\n")
#
#--- now extract data from NOAA web site
#
    for html in htmlList:
        f = open(html, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
#
#--- extract needed data and print them out in a data file
#

#
#--- if data are collected after 2011, start here
#

        if dtype == 'new':
            for ent in data:
                atemp = re.split('\s+|\t+', ent)
    
                if ent and atemp[0].isdigit():
                    timestamp = atemp[0]  + ':' + atemp[1] + ':' + atemp[2] + ':'  + atemp[3][0] 
                    timestamp = timestamp + atemp[3][1] + ':' + atemp[3][2] + atemp[3][3] + ':00'
    
                    (dyear, dmonth, dday, dhours, dminutes, dseconds, dydate) = tcnv.dateFormatCon(timestamp)
    
                    if dyear == pYearStart:
                        if dydate >= plotStart and dydate <= plotStop:
    
                            line = '%4.3f\t\t%3.2e\t%3.2e\t%3.2e\n' %\
                                   (dydate, float(atemp[6]), float(atemp[7]), float(atemp[10]))
                            out.write(line)
                    else:
#
#--- for the case, the period goes over two years
#
                        chk = 4.0 * int(0.25 * pYearStart)
                        if chk == pYearStart:
                            base = 366
                        else:
                            base = 365
    
                        dydate += base
                        if dydate >= plotStart and dydate <= plotStop:
    
                            line = '%4.3f\t\t%3.2e\t%3.2e\t%3.2e\n' %\
                                    (dydate, float(atemp[6]), float(atemp[7]), float(atemp[10]))
                            out.write(line)
#
#--- if the data is collected before 2011, start here
#
        else:
            for ent in data:
                atemp = re.split('\s+|\t+', ent)
    
                if ent and atemp[0].isdigit():
                    dyear = atemp[0][0] + atemp[0][1]
                    dyear = int(dyear)
                    if dyear > 90:
                        dyear += 1900
                    else:
                        dyear += 2000

                    dydate   = float(atemp[2])
                    dhours   = float(atemp[1][0] + atemp[1][1])
                    dminutes = float(atemp[1][2] + atemp[1][3])
                    dydate  += (dhours/24.0 + dminutes / 1440.0)
    
                    if dyear == pYearStart:
                        if dydate >= plotStart and dydate <= plotStop:
    
                            line = '%4.3f\t\t%3.2e\t%3.2e\t%3.2e\n' %\
                                    (dydate, float(atemp[10]), float(atemp[11]), float(atemp[14]))
                            out.write(line)
                    else:
#
#--- for the case, the period goes over two years
#
                        chk = 4.0 * int(0.25 * pYearStart)
                        if chk == pYearStart:
                            base = 366
                        else:
                            base = 365
    
                        dydate += base
                        dydate += base
                        if dydate >= plotStart and dydate <= plotStop:
    
                            line = '%4.3f\t\t%3.2e\t%3.2e\t%3.2e\n' %\
                                    (dydate, float(atemp[10]), float(atemp[11]), float(atemp[14]))
                            out.write(line)

    if len(htmlList) > 0:
        out.close()

#--------------------------------------------------------------------
#--- computeGOESStat: computing GOES statitics                    ---
#--------------------------------------------------------------------

def computeGOESStat(event, startTime, comp_test ='NA'):

    """
    read data from goes data, and compute statistics
    input:  event       --- event name
            startTime   --- starting time
            comp_test   --- option, if yes, use the test data
    output: <stat_dir>/<event>_goes_stat
    """

    begin = startTime + ':00'           #---- modify the format to work with dateFormatCon

    (year, month, day, hours, minutes, seconds, interruptTime) = tcnv.dateFormatCon(begin)

    if comp_test == 'test':
        file = test_data_dir + event + '_goes.txt'
    else:
        file = data_dir + event + '_goes.txt'

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    p1Avg      = 0
    p1Avg2     = 0
    p1Max      = -1e5
    p1Min      =  1e8
    p1MaxTime  = 0
    p1MinTime  = 0
    p1IntValue = 0

    p2Avg      = 0
    p2Avg2     = 0
    p2Max      = -1e5
    p2Min      =  1e8
    p2MaxTime  = 0
    p2MinTime  = 0
    p2IntValue = 0

    p5Avg      = 0
    p5Avg2     = 0
    p5Max      = -1e5
    p5Min      =  1e8
    p5MaxTime  = 0
    p5MinTime  = 0
    p5IntValue = 0

    p1cnt      = 0
    p2cnt      = 0
    p5cnt      = 0
    ind        = 0                        #---- indicator whther the loop passed the interruption time

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        btemp = re.split('\.', atemp[0])

        if ent and btemp[0].isdigit():

            atemp = re.split('\s+|\t+', ent)
            if len(atemp) < 4:
                continue

            val0  = float(atemp[0])     #--- time
            val1  = float(atemp[1])     #--- p1
            val2  = float(atemp[2])     #--- p2
            val3  = float(atemp[3])     #--- p5
            

            if val1 > 0:                #--- 0 could mean that there is no data; so we ignore it
                p1Avg    += val1
                p1Avg2   += val1 * val1
    
                if val1 > p1Max:
                    p1Max     = val1
                    p1MaxTime = val0
                elif val1 < p1Min:
                    p1Min     = val1
                    p1MinTime = val0
                p1cnt += 1

            if val2 > 0:
                p2Avg   += val2
                p2Avg2  += val2 * val2

                if val2 > p2Max:
                    p2Max     = val2
                    p2MaxTime = val0
                elif val2 < p2Min:
                    p2Min     = val2
                    p2MinTime = val0
                p2cnt += 1

            if val3 > 0:
                p5Avg  += val3
                p5Avg2 += val3 * val3
    
                if val3 > p5Max:
                    p5Max     = val3
                    p5MaxTime = val0
                elif val3 < p5Min:
                    p5Min     = val3
                    p5MinTime = val0
                p5cnt += 1
#
#--- finding the value at the interruption
#
            if interruptTime <=  val0 and ind == 0:
                p1IntValue = val1
                p2IntValue = val2
                p5IntValue = val3
                ind = 1
#
#--- compute averages
#
    if p1cnt > 0 and p2cnt > 0 and p5cnt > 0:
        p1Avg /= p1cnt
        p2Avg /= p2cnt
        p5Avg /= p5cnt
#
#--- compute stndard deviation
#    
    try:
        p1Sig = math.sqrt(p1Avg2 / p1cnt - p1Avg * p1Avg)
    except:
        p1Sig = -999
    try:
        p2Sig = math.sqrt(p2Avg2 / p2cnt - p2Avg * p2Avg)
    except:
        p2Sig = -999
    try:
        p5Sig = math.sqrt(p5Avg2 / p5cnt - p5Avg * p5Avg)
    except:
        p5Sig = -999

    if comp_test == 'test':
        file = test_stat_dir + event + '_goes_stat'
    else:
        file = stat_dir + event + '_goes_stat'

    line = '\t\tAvg\t\t\tMax\t\tTime\t\tMin\t\tTime\t\tValue at Interruption Started\n'

    line = line + '-'*95 + '\n'

    line = line + 'p1\t%2.3e +/- %2.3e\t\t%2.3e\t%4.3f\t\t%2.3e\t%4.3f\t\t%2.3e\n'\
                    % (p1Avg, p1Sig, p1Max, p1MaxTime, p1Min, p1MinTime, p1IntValue)

    line = line + 'p2\t%2.3e +/- %2.3e\t\t%2.3e\t%4.3f\t\t%2.3e\t%4.3f\t\t%2.3e\n'\
                    % (p2Avg, p2Sig, p2Max, p2MaxTime, p2Min, p2MinTime, p2IntValue)

    line = line + 'p5\t%2.3e +/- %2.3e\t\t%2.3e\t%4.3f\t\t%2.3e\t%4.3f\t\t%2.3e\n'\
                    % (p5Avg, p5Sig, p5Max, p5MaxTime, p5Min, p5MinTime, p5IntValue)

    f    = open(file, 'w')
    f.write(line)
    f.close()
    
