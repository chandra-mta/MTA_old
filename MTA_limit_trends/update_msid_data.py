#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#       update_msid_data.py: update all msid database listed in msid_list           #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 17, 2019                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import time
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions     as mcf        #---- contains other functions commonly used in MTA scripts
import update_database_suppl    as uds

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
    data  = mcf.read_data_file(ifile)

    for ent in data:
        atemp     = re.split('\s+', ent)
        msid      = atemp[0]
        group     = atemp[1]
        
        print("Updating: " + group + ': ' + msid)

        uds.run_update_with_ska(msid, group)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
            msid_list = sys.argv[1]
            msid_list.strip()
            update_msid_data(msid_list=msid_list)
    else:

        update_msid_data()
