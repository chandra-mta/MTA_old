#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       compute_stat.py: compute statistics for the data given                  #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Apr 11, 2012                                       #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import string

#
#--- reading directory list
#

path = '/data/mta/Script/Interrupt/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append path to a privte folder
#

sys.path.append(bin_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#

import convertTimeFormat as tcnv

#
#--- Science Run Interrupt related funcions shared
#

import interruptFunctions as itrf

#
#---- EPHIN data extraction
#

import extract_ephin as ephin

#
#---- GOES data extraction
#

import extract_goes as goes

#
#---- ACE (NOAA) data extraction
#

import extract_noaa as noaa

#
#---- ACE (NOAA) statistics

import compute_ace_stat as astat

#---------------------------------------------------------------------------------------------------------------------
#--- compute_stat: compute statistics for all the data                                                            ----
#---------------------------------------------------------------------------------------------------------------------

def compute_stat():
    
    'compute stat for ephin, goes, and ace for a given event. input: a file name containing, e.g. 20110804        2011:08:04:07:03        2011:08:07:10:25        186.5   auto'

    
    file = raw_input('Please put the intrrupt timing list: ')

    f    = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        if not ent:
            break

        atemp = re.split('\s+|\t+', ent)
        event = atemp[0]
        start = atemp[1]
        stop  = atemp[2]
        gap   = atemp[3]
        type  = atemp[4]

#
#--- compute ephin statistics
#
        ephin.computeEphinStat(event, start)

#
#---- compute GOES statistics
#
        goes.computeGOESStat(event, start)

#
#---- compute ACE statistics
#
	astat.computeACEStat(event, start, stop)



#---------------------------------------------------------------------------------------------------------------------
#--- start script                                                                                                  ---
#---------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':

    compute_stat()
