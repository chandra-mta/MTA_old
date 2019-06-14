#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################
#                                                                                   #
#   check_file_update_date.py: find the files which are not updated for a while     #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               last update: May 20, 2019                                           #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import random
import time
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
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
    ignore = mcf.read_data_file(ifile)

    cmd  = 'ls ' + data_dir + '*/*fits > ' +  zspace
    os.system(cmd)

    data = mcf.read_data_file(zspace, remove=1)

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

        with open(zspace, 'w') as fo:
            fo.write(line)
        
        cmd  = 'cat ' + zspace + ' | mailx -s "Subject: MTA Trending data update problem!" '
        cmd  = cmd + 'tisobe@cfa.harvard.edu'
        os.system(cmd)

        mcf.rm_files(zspace)

    else:
        line = 'Secondary data update finished: ' 
        line = line +  time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + '\n'

        with open(zspace, 'w') as fo:
            fo.write(line)
        
        cmd  = 'cat ' + zspace + ' | mailx -s "Subject: Secondary Data Update" tisobe@cfa.harvard.edu'
        os.system(cmd)

        mcf.rm_files(zspace)

#-----------------------------------------------------------------------------------
#-- find_modified_time: check whether the file was updated in a given time period --
#-----------------------------------------------------------------------------------

def find_modified_time(ifile, stime):
    """
    check whether the file was updated in a given time period
    input:  file    --- file name
            stime   --- time periond in seconds (backward from today)
    ouput:  mtime   --- the difference between the file created time and the stime
    """
    try:
        mtime = os.path.getmtime(ifile) - Ebase_t - stime
        return  mtime

    except OSError:
        return  -999

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    check_file_update_date()

