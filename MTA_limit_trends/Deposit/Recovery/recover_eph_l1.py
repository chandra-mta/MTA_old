#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 20, 2019                                               #
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
path = '/data/mta/Script/MTA_limit_trends/Scripts3.6/house_keeping/dir_list'
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
import fits_operation           as mfo
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

out_dir = './Outdir/Compephkey/'

#-------------------------------------------------------------------------------------------
#-- update_eph_l1: 
#-------------------------------------------------------------------------------------------

def update_eph_l1():
    """
    """

    ifile = house_keeping + 'msid_list_ephkey'
    data  = mcf.read_data_file(ifile)
    msid_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        msid_list.append(atemp[0])

    for year in range(1999, 2019):
        nyear = year 

        for month in range(1, 13):
            if year ==  1999:
                if month < 8:
                    continue
            if year == 2018:
                if month > 2:
                    break

            cmon = str(month)
            if month < 10:
                cmon = '0' + cmon
            nmon = month + 1
            if nmon > 12:
                nmon =1
                nyear += 1
            cnmon = str(nmon)
            if nmon < 10:
                cnmon = '0' + cnmon

            start =  str(year)  + '-' + cmon  + '-01T00:00:00'
            stop  =  str(nyear) + '-' + cnmon + '-01T00:00:00'

            get_data(start, stop, year, msid_list)

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def get_data(start, stop, year, msid_list):

    print(str(start) + '<-->' + str(stop))

    line = 'operation=retrieve\n'
    line = line + 'dataset = flight\n'
    line = line + 'detector = ephin\n'
    line = line + 'level = 0\n'
    line = line + 'filetype =ephhk \n'
    line = line + 'tstart = ' + start + '\n'
    line = line + 'tstop = '  + stop  + '\n'
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
                update_fits_file(ofits, ocols, cdata)
            else:
                create_fits_file(ofits, ocols, cdata)

        mcf.rm_files(fits)

#-------------------------------------------------------------------------------------------
#-- update_fits_file: update fits file                                                    --
#-------------------------------------------------------------------------------------------

def update_fits_file(fits, cols, cdata):
    """
    update fits file
    input:  fits    --- fits file name
            cols    --- a list of column names
            cdata   --- a list of lists of data values
    output: updated fits file
    """
    f     = pyfits.open(fits)
    data  = f[1].data
    f.close()

    udata = []
    chk   = 0
    for k in range(0, len(cols)):
        try:
            nlist   = list(data[cols[k]]) + list(cdata[k])
            udata.append(numpy.array(nlist))
        except:
            chk = 1
            pass

    if chk == 0:
        try:
            create_fits_file(fits, cols, udata)
        except:
            pass

#-------------------------------------------------------------------------------------------
#-- create_fits_file: create a new fits file for a given data set                         --
#-------------------------------------------------------------------------------------------

def create_fits_file(fits, cols, cdata):
    """
    create a new fits file for a given data set
    input:  fits    --- fits file name
            cols    --- a list of column names
            cdata   --- a list of lists of data values
    output: newly created fits file "fits"
    """
    dlist = []
    for k in range(0, len(cols)):
        aent = numpy.array(cdata[k])
        dcol = pyfits.Column(name=cols[k], format='F', array=aent)
        dlist.append(dcol)

    dcols = pyfits.ColDefs(dlist)
    tbhdu = pyfits.BinTableHDU.from_columns(dcols)

    mcf.rm_files(fits)
    tbhdu.writeto(fits)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_eph_l1()
