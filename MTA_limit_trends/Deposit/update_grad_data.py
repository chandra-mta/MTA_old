#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#       update_grad_data.py: update comp related data using mp data                 #
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
#-- update_grad_data: update grad related data in full resolution                         --
#-------------------------------------------------------------------------------------------

def update_grad_data():
    """
    update grad related data in full resolution
    input:  none
    output: <out_dir>/<msid>_full_data_<year>.fits
    """
    t_file  = 'hcapgrd1_full_data_*.fits*'
    out_dir = deposit_dir + '/Grad_save/'
    tdir    = out_dir + 'Gradcap/'
#
#--- read grad group name
#
    gfile     = house_keeping + 'grad_list'
    grad_list = ecf.read_file_data(gfile)

    [tstart, tstop, year] = ecf.find_data_collecting_period(tdir, t_file)

    get_data(tstart, tstop, year, grad_list, out_dir)

#-------------------------------------------------------------------------------------------
#-- get_data: update msid data in msid_list for the given data period                     --
#-------------------------------------------------------------------------------------------

def get_data(tstart, tstop, year, grad_list, out_dir):
    """
    update msid data in msid_list for the given data period
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
            year    --- the year in which data is extracted
            grad_list   --- a list of  group name in grads
            out_dir --- output_directory
    """

    print "Period: " + str(tstart) + '<-->' + str(tstop) + ' in Year: ' + str(year)
#
#--- extract ecach group data
#
    for group in grad_list:
        print group

        line = 'operation=retrieve\n'
        line = line + 'dataset = mta\n'
        line = line + 'detector = grad\n'
        line = line + 'level = 0.5\n'
        line = line + 'filetype = ' + group + '\n'
        line = line + 'tstart = '   + str(tstart) + '\n'
        line = line + 'tstop = '    + str(tstop)  + '\n'
        line = line + 'go\n'

        fo = open(zspace, 'w')
        fo.write(line)
        fo.close()

        try:
            cmd = ' /proj/sot/ska/bin/arc5gl  -user isobe -script ' + zspace + '> ztemp_out'
            os.system(cmd)
        except:
            cmd = ' /proj/axaf/simul/bin/arc5gl -user isobe -script ' + zspace + '> ztemp_out'
            os.system(cmd)

        mcf.rm_file(zspace)

        data_list = ecf.read_file_data('ztemp_out', remove=1)
#
#--- fits data name starts from the second entry
#
        data_list = data_list[1:]
#
#---  read the first fits file and prep for the data list
#
        [cols, tbdata] = ecf.read_fits_file(data_list[0])
        col_list = []
        for ent in cols:
            if ent.lower() == 'time':
                continue
            mc = re.search('st_', ent.lower())
            if mc is not None:
                continue

            col_list.append(ent)

        mcf.rm_file(data_list[0])
        tdata = tbdata['time']
        mdata = []
        for col in col_list:
            mdata.append(tbdata[col])
#
#--- read the rest of the data
#
        clen  = len(col_list)
        for k in range(1, len(data_list)):
            fits = data_list[k]
            [cols, tbdata] = ecf.read_fits_file(fits)
            tdata = numpy.append(tdata, tbdata['time'])
            for m in range(0, clen):
                cdata = tbdata[col_list[m]]
                mdata[m] = numpy.append(mdata[m], cdata)

            mcf.rm_file(fits)

        dout  = out_dir + group.capitalize() + '/'

        if not os.path.isdir(dout):
            cmd = 'mkdir ' + dout
            os.system(cmd)
#
#--- write out the data to fits file
#
        for k in range(0, clen):
            col = col_list[k]
            ocols = ['time', col.lower()]
            cdata = [tdata, mdata[k]]

            ofits = dout + col.lower()+ '_full_data_' + str(year) +'.fits'

            if os.path.isfile(ofits):
                ecf.update_fits_file(ofits, ocols, cdata)
            else:
                ecf.create_fits_file(ofits, ocols, cdata)

#
#--- zip the fits file from the last year at the beginning of the year
#
        ecf.check_zip_possible(dout)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_grad_data()
