#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#           update_acis_ctemp.py: update acis temp data in C                        #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 07, 2018                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time
import datetime

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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat        as tcnv       #---- contains MTA time conversion routines
import mta_common_functions     as mcf        #---- contains other functions commonly used in MTA scripts
import glimmon_sql_read         as gsr
import envelope_common_function as ecf
import fits_operation           as mfo
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- update_acis_ctemp:  update acis temp data in C                                       ---
#-------------------------------------------------------------------------------------------

def update_acis_ctemp():
    """
    update acis temp data in C
    input: none
    output: <out_dir>/<msid>_full_data_<year>fits
    """

    t_file  = '1cbat_full_data_*.fits*'
    out_dir = deposit_dir + '/Comp_save/Compaciscent/'

    ifile = house_keeping + 'msid_list_compaciscent'
    data  = ecf.read_file_data(ifile)
    acis_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        acis_list.append(atemp[0])



    [tstart, tstop, year] = ecf.find_data_collecting_period(out_dir, t_file)

    get_data(tstart, tstop, year, acis_list, out_dir)
#
#--- zip the fits file from the last year at the beginning of the year
#
    ecf.check_zip_possible(out_dir)

#-------------------------------------------------------------------------------------------
#-- get_data: update msid data in msid_list for the given data period                     --
#-------------------------------------------------------------------------------------------

def get_data(start, stop, year, msid_list, out_dir):
    """
    update msid data in msid_list for the given data period
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
            year    --- the year in which data is extracted
            msid_list   --- a list of msids
            out_dir --- output_directory
    """

    print str(start) + '<-->' + str(stop)

    for msid in msid_list:

        out   = fetch.MSID(msid, start, stop)
        tdat  = out.vals - 273.15
        ttime = out.times

        ocols = ['time', msid]
        cdata = [ttime, tdat]
           
        ofits = out_dir + msid + '_full_data_' + str(year) +'.fits'
        if os.path.isfile(ofits):
            ecf.update_fits_file(ofits, ocols, cdata)
        else:
            ecf.create_fits_file(ofits, ocols, cdata)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_acis_ctemp()
