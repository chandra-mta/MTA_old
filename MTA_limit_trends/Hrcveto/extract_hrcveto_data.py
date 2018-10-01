#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#       extract_hrcveto_data.py: extract hrc veto data using arc5gl                 #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 21, 2017                                               #
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

testfits   = data_dir + '/Hrcveto/vlevart_data.fits'

#-------------------------------------------------------------------------------------------
#-- extract_hrcveto_data: extract hrc veto data                                           --
#-------------------------------------------------------------------------------------------

def extract_hrcveto_data():
    """
    extract hrc veto data
    input:  none
    output: fits file data related to grad and comp
    """
#
#--- set basic information
#
    group = 'Hrcveto'
    cols  = ['TLEVART', 'VLEVART', 'SHEVART']
    [udict, ddict, mta_db, mta_cross] = ecf.get_basic_info_dict()
#
#--- find the date to be filled
#
    ctime = ecf.find_the_last_entry_time(testfits)
    start = Chandra.Time.DateTime(ctime).date 

    today = time.strftime("%Y:%j:00:00:00", time.gmtime())
    ctime = Chandra.Time.DateTime(today).secs - 43200.0
    stop  = Chandra.Time.DateTime(ctime).date 

    print "Group: " + group + ': ' + str(start) + '<-->' + str(stop)

    [xxx, tbdata] = uds.extract_data_arc5gl('hrc', '0', 'hrcss', start, stop) 
#
#--- get time data in the list form
#
    dtime = list(tbdata.field('time'))

    for col in cols:
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
        uds.update_database(msid, group, dtime, data, glim)



#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
            date = sys.argv[1]
            date.strip()
            extract_hrcveto_data(date)
    else:
        extract_hrcveto_data()

