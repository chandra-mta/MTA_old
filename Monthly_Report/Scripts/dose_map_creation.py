#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       dose_map_creation.py: create ACIS and HRC dose maps                             #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: Nov 10, 2016                                                   #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import math
import numpy
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')

path = '/data/mta/Script/Python_script2.7/house_keeping/dir_list'
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
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf

#-----------------------------------------------------------------------------------
#-- dose_map_creation: create acis and hrc dose maps                              --
#-----------------------------------------------------------------------------------

def dose_map_creation(year='', mon=''):
    """
    create acis and hrc dose maps
    input:  year    --- year; if it is "", the year of the last month will be used
            mon     --- month;if it is "", the month value of the last month is used
    output: /data/mta/www/mta_max_exp/Images/*.png,     e.g., ACSI_11_2016_i2.png
    """
#
#--- if year and month are not given, use the last month's month and year value
#
    if year == '':
#
#--- find today's date
#
        ltime = tcnv.currentTime()
        year  = ltime[0]
        lyear = str(year)                           #--- '2016'
#
#--- set the last month's month and year
#
        mon   = ltime[1] -1    

        if mon < 1:
            mon   = 12
            year -= 1

    cmon   = str(mon)
    if mon < 10:
        cmon = '0' + cmon                           #--- e.g. 03 or 11

    lmon   = tcnv.changeMonthFormat(mon)            #--- e.g. Mar or Nov

    lmonyr = lmon.lower() + lyear[2] + lyear[3]     #--- e.g. jan16
    lm_y   = cmon + '_' + lyear                     #--- e.g. 03_2016
#
#--- create clean acis and hrc exposure maps using ds9
#
    run_exposure_maps(lyear, cmon)

#-----------------------------------------------------------------------------------
#-- run_exposure_maps: run through ACIS and HRC does fits files to create mpas   ---
#-----------------------------------------------------------------------------------

def run_exposure_maps(lyear, cmon):
    """
    run through ACIS and HRC does fits files to create mpas
    input:  lyear   --- "<year>"
            cmon    --- "<month>"
    output: png files in /data/mta_www/mta_max_exp/Images/
                        e.g., ACIS_<mon>_<year>.png
                              HRCI_08_1999_<mon>_<year>.png
    """

    file = '/data/mta_www/mta_max_exp/Cumulative/ACIS_07_1999_' + cmon + '_' + lyear

    for tail in ['', '_i2', '_i3', '_s2', '_s3']:
        fits  = file + tail + '.fits*'
        create_exposure_map(fits)


    file = '/data/mta_www/mta_max_exp/Month/ACIS_' + cmon + '_' + lyear

    for tail in ['', '_i2', '_i3', '_s2', '_s3']:
        fits  = file + tail + '.fits*'
        create_exposure_map(fits)

    fits = '/data/mta_www/mta_max_exp/Cumulative_hrc/HRCI_08_1999_' + cmon + '_' + lyear + '.fits*'
    create_exposure_map(fits)
    fits = '/data/mta_www/mta_max_exp/Cumulative_hrc/HRCS_08_1999_' + cmon + '_' + lyear + '.fits*'
    create_exposure_map(fits)


    fits = '/data/mta_www/mta_max_exp/Month_hrc/HRCI_' + cmon + '_' + lyear + '.fits*'
    create_exposure_map(fits)

    fits = '/data/mta_www/mta_max_exp/Month_hrc/HRCS_' + cmon + '_' + lyear + '.fits*'
    create_exposure_map(fits)

    os.system('mv -f /data/mta_www/mta_max_exp/Cumulative/*png     /data/mta_www/mta_max_exp/Images/.')
    os.system('mv -f /data/mta_www/mta_max_exp/Month/*png          /data/mta_www/mta_max_exp/Images/.')
    os.system('mv -f /data/mta_www/mta_max_exp/Cumulative_hrc/*png /data/mta_www/mta_max_exp/Images/.')
    os.system('mv -f /data/mta_www/mta_max_exp/Month_hrc/*png      /data/mta_www/mta_max_exp/Images/.')

#-----------------------------------------------------------------------------------
#-- create_exposure_map: create an exposure map from a fits file using ds9        --
#-----------------------------------------------------------------------------------

def create_exposure_map(fits):
    """
    create an exposure map from a fits file using ds9
    input:  fits    --- fits file name
    output: out     --- png file
    """

    atemp = re.split('fits', fits)
    out   = atemp[0] + 'png'
    cmd   = 'ds9 ' + fits + '  -zoom to fit -scale histequ -cmap Heat -export png ' + out + ' -quit'

    try:
        bash(cmd,  env=ascdsenv)
    except:
        pass

#-----------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 3:
        year = sys.argv[1]
        year = int(float(year))
        mon  = sys.argv[2]
        mon  = int(float(mon))
    else:
        year = ''
        mon  = ''

    dose_map_creation(year, mon)

