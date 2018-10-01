#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################
#                                                                                   #
#   check_file_update_date.py: find the files which are not updated for a while     #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               last update: Mar 13, 2018                                           #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import random
import math
import sqlite3
import unittest
import time
import datetime
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
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
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import convertTimeFormat        as tcnv #---- converTimeFormat contains MTA time conversion routines
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

Ebase_t  = time.mktime((1998, 1,  1, 0, 0, 0, 5, 1, 0))

#-----------------------------------------------------------------------------------
#-- check_file_update_date: find the files which are not updated for a while      --
#-----------------------------------------------------------------------------------

def check_file_update_date():
    """
    find the files which are not updated for a while
    input:  none, but read from <data_dir>
    output: if there are problems, mail wil be sent out
    """
#
#--- the files listed in <house_keeping>/ignore_list are not updated 
#
    ifile  = house_keeping + 'ignore_list'
    ignore = ecf.read_file_data(ifile)

    cmd  = 'ls ' + data_dir + '*/*fits > ' +  zspace
    os.system(cmd)

    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
    stday = Chandra.Time.DateTime(stday).secs - 86400.0  * 8.0 

    save = []
    for ent in data:
        out = find_modified_time(ent, stday)
        if out < 0:
            if ent in ignore:
                continue

            save.append(ent)

    if len(save) > 0:
        line = 'Following files are not updated more than a week\n\n'
        for ent in save:
            line = line + ent + '\n'

        fo = open(zspace, 'w')
        fo.write(line)
        fo.close()
        cmd  = 'cat ' + zspace + ' | mailx -s "Subject: MTA Trending data update problem!" tisobe@cfa.harvard.edu'
        os.system(cmd)

        mcf.rm_file(zspace)

    else:
        line = 'Secondary data update finished: ' +   time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + '\n'

        fo = open(zspace, 'w')
        fo.write(line)
        fo.close()
        cmd  = 'cat ' + zspace + ' | mailx -s "Subject: Secondary Data Update" tisobe@cfa.harvard.edu'
        os.system(cmd)

        mcf.rm_file(zspace)


#-----------------------------------------------------------------------------------
#-- find_modified_time: check whether the file was updated in a given time period --
#-----------------------------------------------------------------------------------

def find_modified_time(file, stime):
    """
    check whether the file was updated in a given time period
    input:  file    --- file name
            stime   --- time periond in seconds (backward from today)
    ouput:  mtime   --- the difference between the file created time and the stime
    """
    try:
        mtime = os.path.getmtime(file) - Ebase_t - stime
        return  mtime

    except OSError:
        return  -999


#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    check_file_update_date()

