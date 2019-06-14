#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################
#                                                                                   #
#           create_otg_time_list.py: create otg time start stop time list files     #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 28, 2019                                               #
#                                                                                   #
#####################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import numpy
import getopt
import os.path
import time
import astropy.io.fits  as pyfits
import Chandra.Time
import random
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- other settings
#
na     = 'na'

otg = '/data/mta_www/mta_otg/OTG_filtered.rdb'

cname_list = ['retr_hetg', 'retr_letg', 'insr_hetg', 'insr_letg', 'grat_active', 'grat_inactive']

#------------------------------------------------------------------------------------
#-- create_otg_time_list: create otg time start stop time list files              ---
#------------------------------------------------------------------------------------

def create_otg_time_list():
    """
    create otg time start stop time list files
    input:  none
    output: in <house_keeping>, 'retr_hetg', 'retr_letg', 'insr_hetg', 'insr_letg', 'inactive'
    """
    otg_data = otg_separate()

    for k in range(0, 6):
        line = ''
        [start, stop] =  otg_data[k]
        for m in range(0, len(start)):
            line = line + str(start[m]) + '\t' + str(stop[m]) + '\n'

        ofile = house_keeping + cname_list[k]
        with open(ofile, 'w') as fo:
            fo.write(line)

#------------------------------------------------------------------------------------
#-- otg_separate: create lists of lists of starting and stopping times of each category   
#------------------------------------------------------------------------------------

def otg_separate():
    """
    create lists of lists of starting and stopping times of each category
    input:  none, but read from /data/mta_www/mta_otg/OTG_filtered.rdb
    output: a list of lists of [[starting time]. [stopping time]] of each category
            see cname_list for the order of the category
    """
    data = mcf.read_data_file(otg)

    retr_hetg_b = []
    retr_hetg_e = []

    retr_letg_b = []
    retr_letg_e = []

    insr_hetg_b = []
    insr_hetg_e = []

    insr_letg_b = []
    insr_letg_e = []

    active_b    = []
    active_e    = []

    inactive_b  = []
    inactive_e  = []

    for ent in data:
        atemp = re.split('\s+', ent)

        direction = atemp[0].lower()        #--- reter or insr
        grating   = atemp[1].lower()        #--- hetg or letg
#
#--- starting and stopping time of the condition 
#
        try:
            start     = float(atemp[2])
        except:
            continue

        start     = time_conversion(start)
        stop      = float(atemp[4])
        stop      = time_conversion(stop) 

        if direction == 'insr':
            if grating == 'hetg':
                insr_hetg_b.append(start)
                insr_hetg_e.append(stop) 

            elif grating == 'letg':
                insr_letg_b.append(start)
                insr_letg_e.append(stop) 

            active_b.append(start)
            active_e.append(stop)

            if (len(inactive_b) > 0) and (start > inactive_b[-1]):
                inactive_e.append(start)

        elif direction == 'retr':
            if grating == 'hetg':
                retr_hetg_b.append(start)
                retr_hetg_e.append(stop) 

            elif grating == 'letg':
                retr_letg_b.append(start)
                retr_letg_e.append(stop) 

            active_b.append(start)
            active_e.append(stop)

            if len(inactive_b) == len(inactive_e):
                inactive_b.append(stop)

            elif len(inactive_b) > len(inactive_e):
                inactive_b = inactive_b[:-1]

            elif len(inactive_b) < len(inactive_e):
                inactive_e = inactive_e[:-1]
                inactive_b.append(stop)
#
#--- the end of the inactive category is usually open; so close it with today's date
#
    stday = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
    stop  = Chandra.Time.DateTime(stday).secs
    inactive_e.append(stop)

    return [[retr_hetg_b, retr_hetg_e], [retr_letg_b, retr_letg_e], [insr_hetg_b, insr_hetg_e],\
            [insr_letg_b, insr_letg_e], [active_b, active_e], [inactive_b, inactive_e]]

#------------------------------------------------------------------------------------
#-- time_conversion: convert time format from <yyyyddd.ddd> to second from 1998.1.1--
#------------------------------------------------------------------------------------

def time_conversion(atime):
    """
    convert time format from <yyyyddd.ddd> to second from 1998.1.1
    input:  time    --- time in <yyyyddd.ddd> format
    output: time    --- time in second from 1998.1.1
    """
    atime = str(atime)

    year = str(atime[0:4])
    yday = str(atime[4:7])

    fday = float('0' + atime[7:])

    val  = 24 * fday
    hh   = int(val)
    val  = 60 * (val - hh)
    mm   = int(val)
    ss   = 60 * (val - mm)
    ss   = int(ss)

    lhh  = mcf.add_leading_zero(hh)
    lmm  = mcf.add_leading_zero(mm)
    lss  = mcf.add_leading_zero(ss)

    time = year + ':' + yday + ':' + lhh + ':' + lmm + ':' + lss

    time = Chandra.Time.DateTime(time).secs

    return time

#-------------------------------------------------------------------------------------------
#-- find_the_last_entry_time: find the last logged time                                   --
#-------------------------------------------------------------------------------------------

def find_the_last_entry_time(fits):
    """
    find the last logged time
    input:  fits    --- fits file name
    output: ctime   --- the last logged time
    """
    f = pyfits.open(fits)
    data = f[1].data
    f.close()

    ctime = numpy.max(data['time'])

    return ctime

#------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        ltype = sys.argv[1]
    else: 
        ltype = ''

    create_otg_time_list()
