#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#   update_ephkey_l1_data.py: update ephkey L1 data                                 #
#       this is to recover just 2017 data for long term and short term              #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 09, 2018                                               #
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

test_fits = data_dir + 'Ephkey_l1/scct0_short_data.fits'

#-------------------------------------------------------------------------------------------
#-- update_ephkey_l1_data: update ephkey L1 data                                          --
#-------------------------------------------------------------------------------------------

def update_ephkey_l1_data(date = ''):
    """
    update ephkey L1 data 
    input:  date    ---- the date in yyyymmdd format. if not given, yesterday's date is used
    output: fits file data related to grad and comp
    """
#
#--- read group names which need special treatment
#
    file   = house_keeping + 'msid_list_ephkey'
    f      = open(file, 'r')
    data   = [line.strip() for line in f.readlines()]
    f.close()

    msid_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        msid_list.append(atemp[0])
        group = atemp[1]
#
#--- create msid <---> unit dictionary
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read mta database
#
    mta_db = ecf.read_mta_database()
#
#--- read mta msid <---> sql msid conversion list
#
    mta_cross = ecf.read_cross_check_table()
#
#--- create date list from the next day from the next entry to today
#
    if date == '':
#
#--- the date of the last entry
#
        stemp = ecf.find_the_last_entry_time(test_fits)
        stemp = Chandra.Time.DateTime(stemp).date
        atemp = re.split(':', stemp)
        syear = int(float(atemp[0]))
        sday  = int(float(atemp[1]))
#
#--- if the data is missing more than 6 hours, fill that day again
#
        shh   = int(float(atemp[2]))
        if shh < 18:
            sday -= 1
            if sday < 0:
                syear -= 1
                if tcnv.isLeapYear(syear) == 1:
                    sday = 366 
                else:
                    sday = 365
    
#
#--- find today's date
#
        stemp = time.strftime("%Y:%j", time.gmtime())
        atemp = re.split(':', stemp)
        lyear = int(float(atemp[0]))
        lday  = int(float(atemp[1]))
    
        date_list = []
        if syear == lyear:
            for day in range(sday+1, lday):
                lday = ecf.add_lead_zeros(day, 2)
    
                date = str(syear) + ':' + lday
                date_list.append(date)
        else:
            if tcnv.isLeapYear(syear) == 1:
                base = 367 
            else:
                base = 366
    
            for day in range(sday+1, base):
                lday = ecf.add_lead_zeros(day, 2)
    
                date = str(syear) + ':' + lday
                date_list.append(date)
    
            for day in range(1, lday):
                lday = ecf.add_lead_zeros(day, 2)
    
                date = str(lyear) + ':' + lday
                date_list.append(date)
    else:
        date_list.append(date)


    for date in (date_list):
        tstart = date + ':00:00:00'
        tstop  = date + ':23:59:59'

        uds.run_update_with_archive(msid_list, group, date_list, 'ephin', '0', 'ephhk', tstart, tstop)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
            date = sys.argv[1]
            date.strip()
            update_ephkey_l1_data(date)
    else:
        update_ephkey_l1_data()

