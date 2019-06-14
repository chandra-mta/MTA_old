#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#########################################################################################
#                                                                                       #
#   remove_html_from_interactive_dir.py: remove html files older than one day old       #
#                                                                                       #
#           author: t. isobe    (tisobe@cfa.harvard.edu)                                #
#                                                                                       #
#           last update: May 22, 2019                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import time

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
#
#--- set a temporary file name
#
import random
rtail  = int(time.time()*random.random())
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------------------
#-- delate_old_file: remove html files older than one day old from Interactive directory 
#----------------------------------------------------------------------------------------

def delate_old_file():
    """
    remove html files older than one day old from Interactive directory
    input:  none, but read from the directory
    oupupt: none
    """
#
#--- find html files in Interactive directory
#
    cmd   = 'ls ' +   web_dir + 'Interactive/* > ' + zspace
    os.system(cmd)

    dlist = mcf.read_data_file(zspace, remove=1)
#
#--- set one day ago 
#
    cdate = time.time() - 60.0 * 60.0 * 24.0
#
#--- remove any files created older than one day ago
#
    if len(dlist) == 0:
        exit(1)

    for cfile in dlist:
        mc = re.search('html', cfile)
        if mc is not None:
            ftime = os.path.getmtime(cfile)
            if ftime < cdate:
                cmd = 'rm -rf  ' + cfile
                os.system(cmd)

#----------------------------------------------------------------------------------------

if __name__ == '__main__':

    delate_old_file()
