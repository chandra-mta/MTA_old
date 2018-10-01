#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#   find_focal_temp_peaks.py: find acis focal temperature peack postion, temp, and width    #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Jul 23, 2018                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import time
import operator
import math
import numpy
import astropy.io.fits  as pyfits
from datetime import datetime
import Chandra.Time
import unittest

#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

BTFMT    = '%m/%d/%y,%H:%M:%S'
basetime = datetime.strptime('01/01/98,00:00:00', BTFMT)

#-----------------------------------------------------------------------------------------------
#-- find_focal_temp_peaks: estimate focal temperature peak position, temperature, and the peak width
#-----------------------------------------------------------------------------------------------

def find_focal_temp_peaks(year='', month='', mday='', tdiff=''):
    """
    estimate focal temperature peak position, temperature, and the peak width.
    the data are collected Thu - Thu span close to the date given.
    input:  year    --- year of the period. default: '' (means the current year)
            month   --- month of the period, default: '' (mean the current month)
            mday    --- date of the month   defalut: '' (menas today's date)
    output: focal_temp_list:    a file contain, peak positioin, temperature, and the peak width
    """
#
#--- find time spans that the data will be collected (Thu - Thu period)
#
    [tstart, tstop]      = find_time_span(year, month, mday)
#
#--- extract data for the period. the temperature values are smoothed
#
    out   = Chandra.Time.DateTime(tstop).date
    atemp = re.split(':', out)
    tyear = int(atemp[0])
    yday  = int(atemp[1])
    [time_set, temp_set] = read_focal_temp(tyear, yday, tstart, tstop)

#
#--- find peak position, temperature and width of the peak
#
    peak_list = select_peak(time_set, temp_set, tdiff)
    peak_list = clean_up_peak_list(peak_list)
    peak_list = convert_to_readable(peak_list)
#
#--- print out the data
#
    fo     = open('/data/mta/Script/Weekly/Focal/focal_temp_list', 'w')
#
#--- if the top of the peak from the last period is in the plotting range, keep it; otherwise drop
#
    yb_cut = yday - 8
    for ent in peak_list:
        vtime = float(ent[0])
        if vtime < yb_cut:
            continue

        ltime  = adjust_digit_format(vtime)
        ltemp  = adjust_digit_format(float(ent[1]))
        lwidth = adjust_digit_format(float(ent[2]), top =1)

        line = '<tr align=center><td>' + str(ltime) + '</td>'
        line = line + '<td>'           + str(ltemp) + '</td>'
        line = line + '<td>'           + str(lwidth) + '</td></tr>\n'
        fo.write(line)
    fo.close()
    
#-----------------------------------------------------------------------------------------------
#-- adjust_digit_format: adjust print out digit format                                        --
#-----------------------------------------------------------------------------------------------

def adjust_digit_format(val, top=3):
    """
    adjust print out digit format
    input:  val --- value
            top --- how many digit we need; defalut:3
    output: sval    --- format adjusted sting value
    """
    
    if val > 0:
        sign = ''
    else:
        sign = '-'

    val   = abs(val)
    sval  = str(val)
    atemp = re.split('\.', sval)
    p1    = atemp[0]
    p2    = atemp[1]

    p1_len = len(p1)
    if p1_len < top:
        if sign == '':
            for k in range(p1_len, top):
                p1 = '0' + p1
        else:
            sp = ''
            for k in range(p1_len, top):
                sp = ' ' + sp
                p1 = sp + '-' + p1
    if len(p2) < 2:
        p2 = p2 + '0'

    sval = p1 + '.' + p2
    if sign == '-':
        sval = '-' + sval

    return sval

#-----------------------------------------------------------------------------------------------
#-- find_time_span: find time span for Thu to Thu nearest to a given date                     --
#-----------------------------------------------------------------------------------------------

def find_time_span(year = '', month = '', mday = ''):
    """
    find time span for begining of Fri to the end of hu nearest to a given date
    input:  year    --- year.           default: current year
            month   --- month.          default: current month
            mday    --- month date.     default: today's date
    """
#
#--- if date is given, fine week day and year date
#
    if year != '':    
        input_time = str(year) +':' + str(month) + ':' + str(mday)
        tlist = time.strptime(input_time, "%Y:%m:%d") 
        wday  = tlist.tm_wday
        yday  = tlist.tm_yday
#
#--- find today's date information (in local time)
#
    else:
        tlist = time.localtime()

        year  = tlist[0]
        mon   = tlist[1]
        day   = tlist[2]
        wday  = tlist[6]
        yday  = tlist[7]
#
#--- find the differnce to Wednesday (Thursday). wday starts on Monday (0)
#--- and set data collect date span
#
        diff  = 4 - wday

        if diff != 0:
            yday += diff
            if yday < 1:
                year -= 1
                base = find_base_data(year)
                yday = base - yday

    syear = year
    syday = yday - 7

    if syday < 0:
        syear -= 1
        base = find_base_data(year)
        syday += base
#
#--- convert time into seconds from 1998.1.1
#--- put extra 24 hrs before and 6 hrs after to cover the border line peak 
#
    start = convertto1998sec(syear, syday) - 3600.0 * 24.0
    stop  = convertto1998sec(year,  yday)  + 3600.0 * 6.0

    return [start, stop] 

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def find_base_data(year):

    if tcnv.isLeapYear(syear) == 1:

        base = 366
    else:
        base = 365

    return base

#-----------------------------------------------------------------------------------------------
#-- convertto1998sec: convert time format from mm/dd/yy,hh:mm:ss to seconds from 1998.1.1    ---
#-----------------------------------------------------------------------------------------------

def convertto1998sec(year, yday):
    """
    convert time format from mm/dd/yy,hh:mm:ss to seconds from 1998.1.1
    input:  ftime      --- time in mm/dd/yy,hh:mm:ss or yyyy-mm-dd,hh:mm:ss
    output  stime      --- time in seconds from 1998.1.1
    """
    lyday = str(yday)
    if yday < 10:
        lyday = '00' + lyday
    elif yday < 100:
        lyday = '0'  + lyday

    ftime   = str(year) + ':' + str(lyday) + ':00:00:00'
    sec1998 = Chandra.Time.DateTime(ftime).secs

    return sec1998


#-----------------------------------------------------------------------------------------------
#-- read_focal_temp: read focal plane temperature data                                        --
#-----------------------------------------------------------------------------------------------

def read_focal_temp(tyear, yday, tstart, tstop):
    """
    read focal plane temperature data
    input:  tyear   --- this year
            yday    --- today's y date
            tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output: ftime   --- a list of time 
            focal   --- a list of focal temp
    """
#
#--- if y daay is less than 8, read the data from the last year
#
    if yday < 8:
        ifile  = '/data/mta/Script/ACIS/Focal/Data/focal_plane_data_5min_avg_' + str(tyear-1)
        data   = read_data_file(ifile, sep='\s+', c_len=2)
        ftime  = data[0]
        focal  = data[1]
    else:
        ftime  = []
        focal  = []
#
#--- otherwise, just read this year
#
    ifile  = '/data/mta/Script/ACIS/Focal/Data/focal_plane_data_5min_avg_' + str(tyear)
    data   = read_data_file(ifile, sep='\s+', c_len=2)
    ftime  = ftime + data[0]
    focal  = focal + data[1]
#
#--- select out the data for the last 7 days
#
    [ftime, focal] = select_data_by_date(ftime, focal, tstart, tstop)
    
    return [ftime, focal]

#-----------------------------------------------------------------------------------------------
#-- select_data_by_date: selet out the potion of the data by time                             --
#-----------------------------------------------------------------------------------------------

def select_data_by_date(x, y, tstart, tstop):
    """
    selet out the potion of the data by time
    input:  x       --- a list of time data
            y       --- a list of data
            tstart  --- a starting time in seconds from 1998.1.1
            tstop   --- a stopping time in seconds from 1998.1.1
    output: x       --- a list of time data selected
            y       --- a list of data selected
    """
    
    x   = numpy.array(x)
    y   = numpy.array(y)
    ind = [(x > tstart) & (x < tstop)]
    x   = list(x[ind])
    y   = list(y[ind])
    
    return [x, y]

#-----------------------------------------------------------------------------------------------
#-- smooth_data: take averages of temperatures and return lists of time and temperature lists --
#-----------------------------------------------------------------------------------------------

def smooth_data(time_set, temp_set):
    """
    take averages of temperatures and return lists of time and temperature lists
    input:  time_set    --- a list of time in seconds from 1998.1.1
            temp_set    --- a list of temperature 
    output: stime_set   --- a list of time in seconds from 1998.1.1
            stemp_list  --- a list of smoothed temperature 
    """
    
    tspan = 600                 #---- average is currently taken for 10 min span
    prev = time_set[0]
    sum  = temp_set[0]
    cnt  = 1
    stime_set = []
    stemp_set = []
    for i in range(1, len(time_set)):
        if time_set[i] < prev + tspan:
#
#--- drop extreme temperature cases; probably they are glitchs
#
            if temp_set[i] < -130:
                continue
            if temp_set[i] > -70:
                continue
            sum += temp_set[i]
            cnt += 1
        else:
            avg = sum / cnt
            stime_set.append(prev+ 300)
            stemp_set.append(avg)
            prev = time_set[i]
            sum  = temp_set[i]
            cnt  = 1

    avg = sum / cnt
    avg = '%.2f' % round(avg, 2)
    avg = float(avg)
    diff = 0.5 * (time_set[-1] + prev)
    stime_set.append(diff)
    stemp_set.append(avg)

    return[stime_set, stemp_set]

#-----------------------------------------------------------------------------------------------
#-- mving_avg_data: take a moving average                                                      -
#-----------------------------------------------------------------------------------------------

def mving_avg_data(time_set, temp_set):
    """
    take a moving average
    input:  time_set    ---- a list of time
            temp_set    ---- a set of temperature 
    output: stime_set   ---- a list of time
            stemp_set   ---- a list of smoothed temp list
    """
    
    tstep = 10                  #--- moving average is currently taken for 10 data points

    hstep = int(0.5 * tstep)
    stime_set = []
    stemp_set = []
    tlen      = len(time_set)

    for i in range(hstep+1 , tlen-hstep-1):
        sum = 0
        cnt = 0
        for m in range(0, tstep):
            step = i + m - hstep
            sum += temp_set[step]
            cnt += 1
        avg = sum / cnt
        avg = '%.2f' % round(avg, 2)
        avg = float(avg)
        stime_set.append(int(float(time_set[i])))
        stemp_set.append(avg)


    return [stime_set, stemp_set]

#-----------------------------------------------------------------------------------------------
#-- find_turning_point: find peaks and valleys of the focal temperature data                 ---
#-----------------------------------------------------------------------------------------------

def find_turning_point(time_set, temp_set):
    """
    find peaks and valleys of the focal temperature data
    input:  time_set    --- a list of time in seconds from 1998.1.1
            temp_set    --- a list of forcal temperature
    """

    up_list   = []
    down_list = []
#
#--- find whether the temperature is going up or down at the begining
#
    diff = temp_set[1] - temp_set[0]
    if diff >= 0:
        slope = 1
    else:
        slope = 0

    for i in range(1, len(time_set)):
        diff = temp_set[i] - temp_set[i-1]
        if diff >= 0:
            cslope = 1
        else:
            cslope = 0
#
#--- if the slope direction changes, we assume that we reached a peak (or a valley)
#
        if slope != cslope:
#
#---  the valley must be lower then -115
#
            if cslope == 1:
                if temp_set[i] < -115:
                    up_list.append(i)
#
#--- the peak must be higher than -118.5
#
            else:
                if temp_set[i] > -118.5:
                    down_list.append(i)
            slope = cslope

    return [up_list, down_list]

#-----------------------------------------------------------------------------------------------
#-- select_peak: find a peak and valleys srrounding the peak                                 ---
#-----------------------------------------------------------------------------------------------

def select_peak(time_set,temp_set,tdiff=0.3):
    """
    find a peak and valleys srrounding the peak
    input:  time_set    --- a list of time in seconds from 1998.1.1
            temp_set    --- a list of temperatures
            tdiff       --- a criteria difference between peak and valley
    output: peak_list   --- a list  of lists of:
                [<peak position> <peak temp> <valley position1> <valley temp> <valley position2> <valley temp>]
    """

    [up_list, down_list] = find_turning_point(time_set, temp_set)

    fo = open('focal_peak_ref', 'w')
    for i in range(0, len(up_list)):
        k = up_list[i]
        try:
            k1 = up_list[i+1]
        except:
            k1 = up_list[len(up_list)-1]
        line = '\t\t' + str(Chandra.Time.DateTime(time_set[k]).date) + "<--->" 
        line = line +  str(sec1998tofracday(time_set[k])) +"<--->" + str(temp_set[k]) + '\n'
        fo.write(line)
        for m in down_list:
            if time_set[m] >= time_set[k] and time_set[m] <= time_set[k1]:
                line = '\nPEAK:' + str(Chandra.Time.DateTime(time_set[m]).date) + "<--->" 
                line = line + str(sec1998tofracday(time_set[m])) +"<--->" + str(temp_set[m]) + '\n\n'
                fo.write(line)

    fo.close()

    peak_list = []
#
#--- find a peak and it temperature
#
    lstart = up_list[0]
    for k in down_list:
        htemp = temp_set[k]
        for m in range(0, len(up_list)):
            p1 = time_set[up_list[m]]
            try:
                p2 = time_set[up_list[m+1]]
                lchk = 0 
            except:
                p2 = time_set[-1]
                lchk = 1
            spoint = 0
#
#--- find two valleys around the peak
#
            if time_set[k] >= p1 and time_set[k] <= p2:
#
#--- if the temperature difference between the peak and the valley is less than 1 degree
#--- find the next closest valley point
#
                for l in range(m, 0, -1):
                    diff = htemp - temp_set[up_list[l]]
                    if diff > tdiff:
                        spoint = up_list[l]
                        break
                epoint = len(up_list) - 1
                for l in range(m+1, len(up_list)):
                    diff = htemp - temp_set[up_list[l]]
                    if diff > tdiff:
                        epoint = up_list[l]
                        break

                p1 = time_set[spoint]
                p2 = time_set[epoint]

                peak_list.append([time_set[k], temp_set[k], p1, temp_set[spoint], p2, temp_set[epoint]])
                break

    return peak_list

#-----------------------------------------------------------------------------------------------
#-- clean_up_peak_list: find overlapped data and combine them                                 --
#-----------------------------------------------------------------------------------------------

def clean_up_peak_list(peak_list):
    """
    find overlapped data and combine them
    input:  peak_list   --- a list of lists of:
            [<peak position> <peak temp> <valley position1> <valley temp> <valley position2> <valley temp>]
    output: mpeak_list  --- a cleaned up list of lists
    """
                
    [m_time, m_temp, s_time, s_temp, e_time, e_temp] = peak_list[0]
    p_len        = len(peak_list)
    cleaned_list = []
    for i in range(1, p_len):
        [m_time2, m_temp2, s_time2, s_temp2, e_time2, e_temp2] = peak_list[i]

        if s_time > s_time2:
            continue
#
#--- if two set of peaks have the same start and stop valley positions, combine them
#
        elif s_time == s_time2 and e_time == e_time2:
            if m_temp < m_temp2:
                m_time = m_time2
                m_temp = m_temp2
#
#--- if the start and stop time are in order (in two set), save the data
#
        elif s_time < s_time2:
            if e_time > s_time2:

                if m_temp2 > m_temp:
                    m_time = m_time2
                    m_temp = m_temp2
                    s_time = s_time2
                    s_temp = s_temp2
                    e_time = e_time2
                    e_temp = e_temp2

            alist = [m_time, m_temp, s_time, s_temp, e_time, e_temp]
            cleaned_list.append(alist)
            m_time = m_time2
            m_temp = m_temp2
            s_time = s_time2
            s_temp = s_temp2
            e_time = e_time2
            e_temp = e_temp2

            if i == p_len -1:
                alist = [m_time, m_temp, s_time, s_temp, e_time, e_temp]
                cleaned_list.append(alist)
                break

#
#--- remove duplicate
#
    prev  = cleaned_list[0]
    mpeak_list = [prev]
    for i in range(1, len(cleaned_list)):
        if prev == cleaned_list[i]:
            continue
        else:
            prev = cleaned_list[i]
            mpeak_list.append(prev)

    return mpeak_list


#-----------------------------------------------------------------------------------------------
#-- convert_to_readable: convert the data to reable form                                     ---
#-----------------------------------------------------------------------------------------------

def convert_to_readable(peak_list):
    """
    convert the data to reable form
    input:  peak_list   ---  a list of lists of:
           [<peak position> <peak temp> <valley position1> <valley temp> <valley position2> <valley temp>]
    output: lday        --- ydate
            focal       --- focal temperature (in C)
            width       --- width of the peak in day)
    """

    slist = []
    for ent in peak_list:
        lday  = sec1998tofracday(ent[0])
        focal = float(ent[1])
        focal = "%.2f" % round(focal, 2)
        start = ent[2]
        stop  = ent[4]
        width = (stop -start)/86400.
        width = "%.2f" % round(width, 2)

        alist = [lday, focal, width]
        slist.append(alist)

    return slist

#-----------------------------------------------------------------------------------------------
#-- sec1998tofracday: convert time from seconds from 1998.1.1 to fractional yday              --
#-----------------------------------------------------------------------------------------------

def sec1998tofracday(stime):
    """
    convert time from seconds from 1998.1.1 to fractional yday 
    input:  stime   --- time in seconds from 1998.1.1
    output: lday    --- fractional year date. igore year
    """

    ptime = Chandra.Time.DateTime(stime).date
    atemp = re.split(':', ptime)
    day   = float(atemp[1])
    hh    = float(atemp[2])
    mm    = float(atemp[3])
    ss    = float(atemp[4])
    dtime = day + hh/24.0 + mm/ 1440.0 + ss / 86400.0
    lday  = "%.2f" % round(dtime, 2)

    return lday

#-----------------------------------------------------------------------------------------------
#-- read_data_file: read ascii data file                                                      --
#-----------------------------------------------------------------------------------------------

def read_data_file(ifile, sep='', remove=0, c_len=0):
    """
    read ascii data file
    input:  ifile   --- file name
    sep --- split indicator: default: '' --- not splitting
    remove  --- indicator whether to remove the file after reading: default: 0 --- no
    c_len   --- numbers of columns to be read. col=0 to col= c_len. default: 0 --- read all
    output: data--- a list of lines or a list of lists
    """
    
    f= open(ifile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    
    if remove > 0:
        mcf.rm_file(ifile)
    
    if sep != '':
        atemp = re.split(sep, data[0])
        if c_len == 0:
            c_len = len(atemp)
        save = []
        for k in range(0, c_len):
            save.append([])
    
        for ent in data:
            atemp = re.split(sep, ent)
            for k in range(0, c_len):
                try:
                    save[k].append(float(atemp[k]))
                except:
                    save[k].append(atemp[k])
    
        return save
    
    else:
        return data


#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#-----------------------------------------------------------------------------------------

    def test_find_time_span(self):

        [start, stop] = find_time_span()

        print 'TIME START/STOP: ' + str(start) + '<--->' + str(stop)

#-----------------------------------------------------------------------------------------

    def test_find_focal_temp_list(self):

        comp = [['22.52', -115.19, '0.85'], ['23.77', -114.81, '1.21'], ['25.15', -112.8, '1.19'], \
                ['26.81', -114.69, '1.10'], ['27.82', -111.39, '0.73']]
        year = 2016
        month = 1
        mday  = 29
        [start, stop]        = find_time_span(year, month, mday)
        [time_set, temp_set] = find_focal_temp_list(start, stop)

        peak_list = select_peak(time_set, temp_set)
        peak_list = clean_up_peak_list(peak_list)
        peak_list = convert_to_readable(peak_list)

        self.assertEquals(peak_list, comp)

        for ent in peak_list:
            print str(ent)

#-----------------------------------------------------------------------------------------------
 
if __name__ == "__main__":
#
#--- if you like to specify the date, give year, month, and date
#
    test  = 0
    tdiff = 0.3
    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':
            test = 1
            del sys.argv[1:]
        else:
            year  = ''
            month = ''
            mday  = ''
            tdiff = float(sys.argv[1])

    elif len(sys.argv) == 4:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
        mday  = int(float(sys.argv[3]))
    elif len(sys.argv) == 5:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
        mday  = int(float(sys.argv[3]))
        tdiff = float(sys.argv[4])
    else:
        year  = ''
        month = ''
        mday  = ''

    if test == 0:
        find_focal_temp_peaks(year, month, mday, tdiff)
    else:
        unittest.main()
