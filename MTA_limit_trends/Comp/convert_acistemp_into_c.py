#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################
#                                                                                   #
#       convert_acistemp_into_c.py: convert acistemp fits into that in C            #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               last update: Oct 30, 2017                                           #
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
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

bcols   = ['med', 'min', 'max', 'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

#-----------------------------------------------------------------------------------
#-- convert_acistemp_into_c: convert all acistemp fits files in K into that of C  --
#-----------------------------------------------------------------------------------

def convert_acistemp_into_c():
    """
    convert all acistemp fits files in K into that of C
    input:  none, but read from <data_dir>/Acistemp/*fits
    output: converted fits files in Compaciscent/*fits
    """

    outdir = data_dir + '/Compaciscent/'
    cmd = 'ls ' + data_dir + '/Acistemp/*fits* > ' + zspace
    os.system(cmd)
    fits_list = mcf.readFile(zspace)
    mcf.rm_file(zspace)


    for fits in fits_list:
        atemp = re.split('\/', fits)
        fname = atemp[-1]
        btemp = re.split('_', fname)
        msid  = btemp[0]
        cols  = [msid] + bcols

        flist = pyfits.open(fits)
        fdata = flist[1].data

        for col in cols:
            odata      = fdata[col] - 273.15    #--- this is a numpy object
            fdata[col] = odata

        flist[1].data = fdata

        outfile = outdir + fname
        mcf.rm_file(outfile)
        flist.writeto(outfile)


#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    convert_acistemp_into_c()
