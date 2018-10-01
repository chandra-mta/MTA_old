#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################################
#                                                                                                                       #
#       run_extract_bad_pix.py: running extract_bad_pix.py script to extrat bad pixel data                              #
#                                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                                   #
#                                                                                                                       #
#           last update Sep 15, 2014                                                                                    #
#                                                                                                                       #
#########################################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits as pyfits
import unittest

#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')

#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'

f    = open(path, 'r')
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
import convertTimeFormat       as tcnv       #---- contains MTA time conversion routines
import mta_common_functions    as mcf        #---- contains other functions commonly used in MTA scripts
import bad_pix_common_function as bcf
import extract_bad_pix         as ebp

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def find_data_collection_interval():

    tlist = tcnv.currentTime(format='UTC')
    tyear = tlist[0]
    tyday = tlist[7]
    tdom  = tcnv.YdateToDOM(tyear, tyday)

    file  = data_dir + 'Disp_dir/hist_ccd3'
    f     = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    chk   = 0
    k     = 1
    while(chk == 0):
        atemp = re.split('<>', data[len(data)-k])
        ldom  = atemp[0]
        if mcf.chkNumeric(ldom) == True:
            ldom = int(ldom)
            chk = 1
            break
        else:
            k += 1

    ldom += 1
    return(ldom, tdom)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def mv_old_file(dom):

    dom -= 30
    if dom > 0:
        [year, ydate] = tcnv.DOMtoYdate(dom)
        sydate = str(ydate)
        if ydate < 10:
            sydate = '00' + sydate
        elif ydate < 100:
            sydate = '0' + sydate

        atime = str(year) + ':' + sydate + ':00:00:00'
        stime = tcnv.axTimeMTA(atime)

        cmd = 'ls ' + house_keeping + '/Defect/CCD*/* > ' + zspace
        os.system(cmd)
        fs = open(zspace, 'r')
        ldata = [line.strip() for line in fs.readlines()]
        fs.close()
        mcf.rm_file(zspace)
        for ent in ldata:
            atemp = re.split('\/acis', ent)
            btemp = re.split('_', atemp[1])
            if int(btemp[0]) < stime:
                out = ent
                out = out.replace('Defect', 'Defect/Save')
                cmd = 'mv ' + ent + ' ' + out 
                os.system(cmd)

#--------------------------------------------------------------------

if __name__ == '__main__':
#    
#--- run the control function; first find out data colleciton interval
#
    if len(sys.argv) == 3:
        start = sys.argv[1]
        start.strip()
        start = int(start)
        stop  = sys.argv[2]
        stop.strip()
        stop  = int(stop)
    else:
        (start, stop) = find_data_collection_interval()

    for dom in range(start, stop):

        ebp.find_bad_pix_main(dom)
        mv_old_file(dom)



