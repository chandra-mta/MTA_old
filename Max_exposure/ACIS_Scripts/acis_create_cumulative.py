#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       acis_create_cumulative.py: separate given acis image to sections and crate      #
#                                  cumulative image files                               #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Dec 03, 2014                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')

#
#--- reading directory list
#

path = '/data/mta/Script/Exposure/house_keeping/acis_dir_list'
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
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv

#
#--- Exposure related funcions shared
#

import exposureFunctions as expf


#-----------------------------------------------------------------------------------------------------------
#-- acis_create_cumulative: create four small section images and create cumulatvie images                ---
#-----------------------------------------------------------------------------------------------------------
            
def acis_create_cumulative(file='NA', comp_test = 'NA'):

    """
    create four small section images and create cumulatvie images
    input: file (e.g. ACIS_05_2012.fits)
    """

    if file == 'NA':
        file = raw_input('Input file name (ACIS_<month>_<year>.fits*): ')
        file = file.strip()


    atemp = re.split('.fits', file)
    btemp = re.split('ACIS', atemp[0])
    erange= btemp[1]
    ctemp = re.split('_', atemp[0])
    mon   = int(ctemp[1])
    year  = int(ctemp[2])
    lmon  = mon - 1
    smon  = str(lmon)
    syear = str(year)
    if lmon < 1:
        lmon = 12
        smon = str(lmon)
        syear = str(year  - 1)
    if lmon < 10:
        smon = '0' + smon
    
#
#--- full image
#
    last =  cum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '.fits.gz'
    out  = 'ACIS_07_1999' + erange + '.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimgcalc ' + last + ' ' + file + ' ' + out + ' add'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- CCD I2
#
    sec  = 'ACIS' + erange + '_i2.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmcopy ' + file + '[264:1285,1416:2435] ' + sec
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    last =  cum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_i2.fits.gz'
    out  = 'ACIS_07_1999' + erange + '_i2.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimgcalc ' + last + ' ' + sec + ' ' + out + ' add'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- CCD I3
#
    sec  = 'ACIS' + erange + '_i3.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmcopy ' + file + '[1310:2331,1416:2435] ' + sec
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    last =  cum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_i3.fits.gz'
    out  = 'ACIS_07_1999' + erange + '_i3.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimgcalc ' + last + ' ' + sec + ' ' + out + ' add'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- CCD S2
#
    sec  = 'ACIS' + erange + '_s2.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmcopy ' + file + '[80:1098,56:1076] ' + sec
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    last =  cum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_s2.fits.gz'
    out  = 'ACIS_07_1999' + erange + '_s2.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimgcalc ' + last + ' ' + sec + ' ' + out + ' add'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- CCD S3
#
    sec  = 'ACIS' + erange + '_s3.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmcopy ' + file + '[1122:2141,56:1076] ' + sec
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    last =  cum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_s3.fits.gz'
    out  = 'ACIS_07_1999' + erange + '_s3.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimgcalc ' + last + ' ' + sec + ' ' + out + ' add'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
    
#
#--- gip the files and move to depositories
#
    mfits = 'ACIS' + erange + '*.fits'
    cfits = 'ACIS_07_1999' + erange + '*.fits'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' gzip ' + mfits + ' ' + cfits
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#-- if this is a test, output directory is different
#
    if comp_test == 'test':
        cmd = 'mv ' + cfits + '.gz ' + test_cum_dir
        os.system(cmd)

        cmd = 'mv ' + mfits + '.gz ' + test_mon_dir
        os.system(cmd)
    else:
        cmd = 'mv ' + cfits + '.gz ' + cum_dir
        os.system(cmd)

        cmd = 'mv ' + mfits + '.gz ' + mon_dir
        os.system(cmd)



#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    acis_create_cumulative()
