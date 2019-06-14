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
#
#--- read grad group name
#
gfile     = house_keeping + 'grad_list'
grad_list = mcf.read_data_file(gfile)

mon_list1 = [1, 32, 60, 91, 121, 152, 192, 213, 244, 274, 305, 335]
mon_list2 = [1, 32, 61, 92, 122, 153, 193, 214, 245, 275, 306, 336]

dout      = './Outdir/Compacispwr/'

#-------------------------------------------------------------------------------------------
#-- update_acis_power: 
#-------------------------------------------------------------------------------------------

def update_acis_power():
    """
    """
    for year in range(1999, 2019):
        nyear = year 
        if mcf.is_leapyear(year):
            mon_list = mon_list2
        else:
            mon_list = mon_list1

        for mon in range(0, 12):
            if year ==  1999:
                if mon < 7:
                    continue
            if year == 2018:
                if mon > 1:
                    break

            if mon == 11:
                bday   = mon_list[mon]
                eday   = 1
                nyear += 1
            else:
                bday = mon_list[mon]
                eday = mon_list[mon+1]

            cbday = str(bday)
            if bday < 10:
                cbday = '00' + cbday
            elif bday < 100:
                cbday = '0'  + cbday


            ceday = str(eday)
            if eday < 10:
                ceday = '00' + ceday
            elif eday < 100:
                ceday = '0'  + ceday

            start =  str(year)  + ':' + cbday + ':00:00:00'
            stop  =  str(nyear) + ':' + ceday + ':00:00:00'

            get_data(start, stop, year)

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def get_data(start, stop, year):

    print(str(start) + '<-->' + str(stop))

    for msid in ['1dppwra', '1dppwrb']:

        if msid == '1dppwra':
            msid_v = '1dp28avo'
            msid_a = '1dpicacu'
        else:
            msid_v = '1dp28bvo'
            msid_a = '1dpicbcu'

        out   = fetch.MSID(msid_v, start, stop)
        tdat1 = out.vals
        ttime = out.times
        out   = fetch.MSID(msid_a, start, stop)
        tdat2 = out.vals

        tlen1 = len(tdat1)
        tlen2 = len(tdat2)
        if tlen1 == 0 or tlen2 == 0:
            continue

        if tlen1 > tlen2:
            diff = tlen1 - tlen2
            for k in range(0, diff):
                tdat2 = numpy.append(tdat2, tadt2[-1])
        elif tlen1 < tlen2:
            diff = tlen2 - tlen1
            for k in range(0, diff):
                tdat1 = numpy.append(tdat1, tadt1[-1])

        ocols = ['time', msid]
        cdata = [ttime, tdat1 * tdat2]
           
        ofits = dout + msid + '_full_data_' + str(year) +'.fits'
        if os.path.isfile(ofits):
            update_fits_file(ofits, ocols, cdata)
        else:
            create_fits_file(ofits, ocols, cdata)
        
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

    update_acis_power()
