#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#           update_eph_l1.py: update eph l1 related data                            #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 21, 2019                                               #
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
import random
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions     as mcf        #---- contains other functions commonly used in MTA scripts
import glimmon_sql_read         as gsr
import envelope_common_function as ecf
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- update_eph_l1: update eph L1 related data                                            ---
#-------------------------------------------------------------------------------------------

def update_eph_l1():
    """
    update eph L1 related data
    input: none
    output: <out_dir>/<msid>_full_data_<year>.fits
    """
    t_file  = 'sce1300_full_data_*.fits*'
    out_dir = deposit_dir + 'Comp_save/Compephkey/'

    ifile = house_keeping + 'msid_list_ephkey'
    data  = mcf.read_data_file(ifile)
    msid_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        msid_list.append(atemp[0])

    [tstart, tstop, year] = ecf.find_data_collecting_period(out_dir, t_file)
#
#--- update the data
#
    get_data(tstart, tstop, year, msid_list, out_dir)
#
#--- zip the fits file from the last year at the beginning of the year
#
    ecf.check_zip_possible(out_dir)

#-------------------------------------------------------------------------------------------
#-- get_data: update eph l1 related data for the given data peirod                        --
#-------------------------------------------------------------------------------------------

def get_data(start, stop, year, msid_list, out_dir):
    """
    update eph l1 related data for the given data peirod
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
            year    --- data extracted year
            msid_list   --- list of msids
            out_dir --- output_directory
    output: <out_dir>/<msid>_full_data_<year>.fits
    """
    print(str(start) + '<-->' + str(stop))

    line = 'operation=retrieve\n'
    line = line + 'dataset = flight\n'
    line = line + 'detector = ephin\n'
    line = line + 'level = 0\n'
    line = line + 'filetype =ephhk \n'
    line = line + 'tstart = ' + str(start) + '\n'
    line = line + 'tstop = '  + str(stop)  + '\n'
    line = line + 'go\n'

    data_list = mcf.run_arc5gl_process(line)
#
#--- uppend the data to the local fits data files
#
    for fits in data_list:

        [cols, tbdata] = ecf.read_fits_file(fits)

        time  = tbdata['time']

        for col in msid_list:
#
#--- ignore columns with "ST_" (standard dev) and time
#
            mdata = tbdata[col]
            cdata = [time, mdata]
            ocols = ['time', col.lower()]

            if not os.path.isdir(out_dir):
                cmd = 'mkdir ' + out_dir
                os.system(cmd)

            ofits = out_dir + col.lower()+ '_full_data_' + str(year) +'.fits'
            if os.path.isfile(ofits):
                ecf.update_fits_file(ofits, ocols, cdata)
            else:
                ecf.create_fits_file(ofits, ocols, cdata)

        mcf.rm_files(fits)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_eph_l1()
