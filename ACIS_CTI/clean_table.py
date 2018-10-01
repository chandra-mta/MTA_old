#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       clean_table.py: sort and cleaned data tables in <data_dir>/Results                          #
#                                                                                                   #
#           author: t. isobe(tisobe@cfa.harvard.edu)                                                #
#                                                                                                   #
#           Last Update:    Mar 17, 2014                                                            #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- check whether this is a test case
#
comp_test = 'live'
if len(sys.argv) == 2:
    if sys.argv[1] == 'test':   #---- test case
        comp_test = 'test'
    elif sys.argv[1] == 'live': #---- automated read in
        comp_test = 'live'
    else:
        comp_test = sys.argv[1].strip() #---- input data name
#
#--- reading directory list
#
if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py_test'
else:
    path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
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

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def clean_table():
    
    """
    sort and clean the table data in <data_dir>/Results
    Input:  none but read from <data_dir>/Results/<elm>_ccd<ccd#>
    Output: cleaned up <data_dir>/Results/<elm>_ccd<ccd#>
    """
#
#--- make a backup
#
    atime = tcnv.currentTime(format='UTC')
    tyear = str(atime[0])
    syear = tyear[2] + tyear[3]

    tmon  = atime[1]
    smon  = str(tmon)
    if int(tmon) < 10:
        smon = '0' + smon

    tday  = atime[2]
    sday  = str(tday)
    if int(tday) < 10:
        sday = '0' + sday

    cout = data_dir + '/Results/Save_' + smon + sday + syear
    mcf.mk_empty_dir(cout)
    cmd  = 'cp -f  ' + data_dir + '/Results/*_ccd* ' + cout + '/.'
    os.system(cmd)
#
#--- now clean up the data
#
    cmd = 'ls ' + data_dir + '/Results/*_ccd* > ' + zspace
    os.system(cmd)

    f     = open(zspace, 'r')
    flist = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)

    for file in flist:
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        data.sort()
        
        prev    = data[0]
        cleaned = [prev]

        for ent in data:
            if ent == prev:
                prev = ent
            else:
                cleaned.append(ent)
                prev = ent

        fo  = open(file, 'w')
        for ent in cleaned:
            line = ent + '\n'
            fo.write(line)

        fo.close()


#--------------------------------------------------------------------


if __name__ == '__main__':

    clean_table()

