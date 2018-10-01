#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       acis_dose_create_image.py: convert acis fits files to png image files                   #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: May 03, 2017                                                               #
#                                                                                               #
#################################################################################################

import sys
import os
import string
import re
import getpass
import socket
import fnmatch 

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
#--- append path to a privte folder
#

sys.path.append(mta_dir)
sys.path.append(bin_dir)

#
#--- this convert fits files to image files
#

import mta_convert_fits_to_image_ciao as mtaimg

#
#--- check whose account, and set a path to temp location
#

user = getpass.getuser()
user = user.strip()

#
#---- find host machine name
#

machine = socket.gethostname()
machine = machine.strip()

#
#--- set temp directory/file
#
tempdir = '/tmp/' + user + '/'
tempout = tempdir + 'ztemp'

#
#--- directory containin plotting related scripts
#
pbin_dir =  '/home/ascds/DS.release/otsbin/'

#----------------------------------------------------------------------------------------------------------------
#---  create_acis_maps: create HRC image maps for given year and month                                       ----
#----------------------------------------------------------------------------------------------------------------

def create_acis_maps(year='NA', month='NA', comp_test = 'NA'):

    """
     create ACIS image maps for given year and month 
    """

    if year == 'NA' or month == 'NA':
        year  = raw_input('Year: ')
        year  = int(year)
        month = raw_input('Month: ')
        month = int(month)
#
#--- images for the center part
#

    if comp_test == 'test':
        acis_dose_conv_to_png(test_mon_dir, test_img_dir, year, month)
        acis_dose_conv_to_png(test_cum_dir, test_img_dir, year, month)
    else:
        acis_dose_conv_to_png(mon_dir, img_dir, year, month)
        acis_dose_conv_to_png(cum_dir, img_dir, year, month)


#----------------------------------------------------------------------------------------------------------------
#--- acis_dose_conv_to_png: prepare to convet fits files into png images                                      ---
#----------------------------------------------------------------------------------------------------------------

def acis_dose_conv_to_png(indir, outdir, year, month):

    """
    prepare to convet fits files into png images, input: indir, outdir, year, month
    """

    syear = str(year)
    smon  = str(month)
    if month < 10:
        smon = '0' + smon

    hname =  'ACIS*' + smon + '_' + syear + '*.fits*'

    for file in os.listdir(indir):

        if fnmatch.fnmatch(file, hname):

            btemp   = re.split('\.fits', file)
            out     = btemp[0]
            outfile = outdir + out

            file_p  = indir + file

            mtaimg.mta_convert_fits_to_image(file_p, outfile, 'log', '125x125', 'heat', 'png')
            cmd = 'convert -trim ' + outfile + ' ztemp.png'
            os.system(cmd)
            cmd = 'mv ztemp.png ' + outfile
            os.system(cmd)
        else:
            pass


#--------------------------------------------------------------------------------------------

if __name__ == '__main__':

    create_acis_maps()


