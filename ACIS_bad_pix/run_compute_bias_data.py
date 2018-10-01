#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################################
#                                                                                                               #
#               run_compute_bias_data.py: run a script to extract bias related data                             #
#                                                                                                               #
#                       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                               #
#                       Last Update: Sep 15, 2014                                                               #
#                                                                                                               #
#################################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits as pyfits

#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/bias_dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat       as tcnv
import mta_common_functions    as mcf
import bad_pix_common_function as bcf
import compute_bias_data       as cbd

#---------------------------------------------------------------------------------------------------
#--- compute_bias_data: the calling function to extract bias data                               ----
#---------------------------------------------------------------------------------------------------

def compute_bias_data():

    """
    the calling function to extract bias data
    Input:  None but read from local files (see find_today_data)
    Output: bias data (see extract_bias_data)
    """

    chk = mcf.chkFile('./','Working_dir')
    if chk == 0:
        cmd = 'mkdir ./Working_dir'
        os.system(cmd)
    else:
        cmd = 'rm -rf ./Working_dir/*'
        os.system(cmd)
#
#--- find which data to use
#
    today_data = cbd.find_today_data()
#
#--- extract bias reated data
#
    cbd.extract_bias_data(today_data)

#---------------------------------------------------------------------------------------------------
#-- update_bias_html: update bias_home.html page                                                 ---
#---------------------------------------------------------------------------------------------------

def update_bias_html():

    """
    pdate bias_home.html page
    Input: None but read from:
            <house_keeping>/bias_home.html
    Output: <web_dir>/bias_home.html
    """
#
#--- find today's date
#
    [year, mon, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime()

    lmon = str(mon)
    if mon < 10:
        lmon = '0' + lmon
    lday = str(day)
    if day < 10:
        lday = '0' + lday
#
#--- line to replace
#
    newdate = "Last Upate: " + lmon + '/' + lday + '/' + str(year)
#
#--- read the template
#
    line = house_keeping + 'bias_home.html'
    data = mcf.readFile(line)
#
#--- print out
#
    outfile = web_dir + 'bias_home.html'
    fo   = open(outfile, 'w')
    for ent in data:
        m = re.search('Last Update', ent)
        if m is not None:
            fo.write(newdate)
        else:
            fo.write(ent)
        fo.write('\n')
    fo.close()

#--------------------------------------------------------------------

if __name__ == '__main__':

    compute_bias_data()

    update_bias_html()

