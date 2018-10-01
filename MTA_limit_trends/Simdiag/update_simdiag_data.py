#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#           update_simdiag_data.py: update sim diag related msids data              #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 21, 2018                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time
import datetime

#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat        as tcnv       #---- contains MTA time conversion routines
import mta_common_functions     as mcf        #---- contains other functions commonly used in MTA scripts
import glimmon_sql_read         as gsr
import envelope_common_function as ecf
import fits_operation           as mfo
import update_database_suppl    as uds
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

mday_list  = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
mday_list2 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

testfits = data_dir + '/Simactu/mrmdest_week_data.fits'

#-------------------------------------------------------------------------------------------
#-- update_simdiag_data: collect sim diag msids                                           --
#-------------------------------------------------------------------------------------------

def update_simdiag_data(date = ''):
    """
    collect sim diag msids
    input:  date    ---- the date in yyyymmdd format. if not given, yesterday's date is used
    output: fits file data related to simdiag
    """
#
#--- read group names which need special treatment
#
    sfile = house_keeping + 'msid_list_simdiag'
    data  = ecf.read_file_data(sfile)
    cols  = []
    g_dir = {}
    for ent in data:
        atemp = re.split('\s+', ent)
        cols.append(atemp[0])
        g_dir[atemp[0]] = atemp[1]
#
#--- get the basic information
#
    [udict, ddict, mta_db, mta_cross] = ecf.get_basic_info_dict()
#
#--- find date to read the data
#
    if date == '':
        yesterday = datetime.date.today() - datetime.timedelta(1)
        yesterday = str(yesterday).replace('-', '')
        date_list = find_the_last_entry_time(yesterday)
    else:
        date_list = [date]

    for sday in date_list:
        print "Date: " + sday

        start = sday + 'T00:00:00'
        stop  = sday + 'T23:59:59'

        [xxxx, tbdata] = uds.extract_data_arc5gl('sim', '0', 'simdiag', start, stop)
#
#--- get time data in the list form
#
        dtime = list(tbdata.field('time'))

        for k in range(0, len(cols)):
            col = cols[k]
#
#---- extract data in a list form
#
            data = list(tbdata.field(col))
#
#--- change col name to msid
#
            msid = col.lower()
#
#--- get limit data table for the msid
#
            try:
                tchk  = ecf.convert_unit_indicator(udict[msid])
            except:
                tchk  = 0

            glim  = ecf.get_limit(msid, tchk, mta_db, mta_cross)
#
#--- update database
#
            uds.update_database(msid, g_dir[msid], dtime, data, glim)


#-------------------------------------------------------------------------------------------
#-- find_the_last_entry_time: find the last logged time                                   --
#-------------------------------------------------------------------------------------------

def find_the_last_entry_time(yesterday):
    """
    find the last entry date and then make a list of dates up to yesterday
    input:  yesterday   --- date of yesterday in the format of yyyymmdd
    output: otime       --- a list of date in the format of yyyymmdd
    """
#
#--- find the last entry date from the "testfits" file
#
    f = pyfits.open(testfits)
    data = f[1].data
    f.close()
#
#--- find the last time logged and changed to a python standard time insecods
#
    ltime = numpy.max(data['time'])  + 883630800.0
#
#--- find the time of the start of the day
#
    ct    = time.strftime('%Y%m%d', time.gmtime(ltime))
    year  = int(ct[0:4])
    mon   = int(ct[4:6])
    day   = int(ct[6:8])
    dt    = datetime.datetime(year, mon, day)
    ltime = time.mktime(dt.timetuple())
#
#--- set starting day to the next day
#
    ltime = ltime + 86400.0
#
#--- convert yesterday to seconds
#
    yesterday = str(yesterday)
    year  = int(yesterday[0:4])
    mon   = int(yesterday[4:6])
    day   = int(yesterday[6:8])
    dt    = datetime.datetime(year, mon, day)
    stime = time.mktime(dt.timetuple())

    ctime = [ltime]
    while ltime < stime:
        ltime += 86400.0
        ctime.append(ltime)
#
#--- convert the list to yyyymmdd format
#
    otime = []
    for ent in ctime:
        oday =  time.strftime('%Y-%m-%d', time.gmtime(ent))
        otime.append(oday)

    return otime


#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
            date = sys.argv[1]
            date.strip()
            update_simdiag_data(date)
    else:
        update_simdiag_data()

