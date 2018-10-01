#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#       update_msid_data.py: update all msid database listed in msid_list           #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 14, 2018                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import time
#import numpy
#import astropy.io.fits  as pyfits
#import Ska.engarchive.fetch as fetch
#import Chandra.Time

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
import envelope_common_function as ecf
import update_database_suppl    as uds
#import glimmon_sql_read         as gsr
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- update_msid_data: update all msid listed in msid_list                                 --
#-------------------------------------------------------------------------------------------

def update_msid_data(msid_list='msid_list_fetch'):
    """
    update all msid listed in msid_list
    input:  msid_list   --- a list of msids to processed. default: msid_list_fetch
    output: <msid>_data.fits/<msid>_short_data.fits/<msid>_week_data.fits
    """

    ifile = house_keeping + msid_list
    data  = ecf.read_file_data(ifile)

    for ent in data:
        atemp     = re.split('\s+', ent)
        msid      = atemp[0]
        group     = atemp[1]
        
        print "Updating: " + group + ': ' + msid

        uds.run_update_with_ska(msid, group)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
            msid_list = sys.argv[1]
            msid_list.strip()
            update_msid_data(msid_list=msid_list)
    else:

        update_msid_data()
