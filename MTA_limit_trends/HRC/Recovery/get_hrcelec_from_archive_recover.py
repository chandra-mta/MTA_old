#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#           get_hrcelec_from_archive_recover.py: get hrc elec related msid from archive             #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Jan 11, 2018                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import math
import unittest
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.Sun
import Ska.astro
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
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import fits_operation           as mfits
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

msid_list =['hvpsstat', 'mlswenbl', 'mlswstat', 'mtrcmndr', 'mtritmp', 'mtrselct', 'mtrstatr', 'n15cast', 'p15cast', 'p24cast']


mday1 = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
mday2 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def extract_data():

    mlen = len(msid_list)
    clen = 15
    chk  = 0

    #for year in range(1999, 2018):
    for year in range(2017, 2018):
        for month in range(1, 13):
            if year == 1999 and month < 9:
                continue
            if year == 2017 and month < 12:
                continue

            if year == 2017 and month >= 1:             #---- short term start
                chk = 1

            print "Period: " + str(year) + ': ' + str(month)
#
#--- initialize 2D array
#
            darray = []
            for k in range(0, mlen):
                darray.append([])

                for m in range(0, clen):
                    darray[k].append([])
#
#--- check a leap year
#
            if tcnv.isLeapYear(year) == 1:
                lday = mday2[month-1]
            else:
                lday = mday1[month-1]
    
            lmon = str(month)
            if month < 10:
                lmon = '0' + lmon
    
            for day in range(1, lday+1):

                if day < 5:
                    continue

                lday = str(day)
                if day < 10:
                    lday = '0' + lday
#
#--- extract fits files for one day
#
                start = str(year) + '-' + lmon  + '-' + lday + 'T00:00:00'
                stop  = str(year) + '-' + lmon  + '-' + lday + 'T23:59:59'
    
                flist = extract_hrchk(start, stop)
#
#--- combine extracted fits files
#
                comb_fits = combine_fits(flist)
#
#--- work on each msid
#
                for k in range(0, mlen):
                    msid  = msid_list[k]
                    cdata = get_stat(comb_fits, msid)

                    for m in range(0, clen):
                        darray[k][m].append(cdata[m])
#
#--- short term data (past one year)
#
                    if chk > 0:
                        ddata = get_stat_short(comb_fits, msid)
                        cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower', 'yupper', 'rlower', 'rupper',\
                            'dcount', 'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

                        ofits = 'Results/' + msid + '_short_data.fits'

                        if os.path.isfile(ofits):
                            update_fits_file(ofits, cols, ddata)
                        else:
                            create_fits_file(ofits, cols, ddata)

#
#--- for a long term data, create once a month
#
            for k in range(0, mlen):
                msid = msid_list[k]
                cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower', 'yupper', 'rlower', 'rupper',\
                         'dcount', 'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']
    
                cdata = darray[k]
                ofits = 'Results/' + msid + '_data.fits'

                if os.path.isfile(ofits):
                    update_fits_file(ofits, cols, cdata)
                else:
                    create_fits_file(ofits, cols, cdata)

        cmd = 'rm -f comb_data.fits'
        os.system(cmd)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def combine_fits(flist):

    outname = 'comb_data.fits'

    cmd     = 'mv -f ' + flist[0] + ' ' +  outname
    os.system(cmd)

    for k in range(1, len(flist)):
        try:
            mfits.appendFitsTable(outname, flist[k], 'temp.fits')
        except:
            continue

        cmd = 'mv temp.fits ' + outname
        os.system(cmd)
        cmd = 'rm -f ' + flist[k]
        os.system(cmd)

    cmd = 'rm -rf *fits.gz'
    os.system(cmd)

    return outname

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def get_stat(fits, msid):

    hdulist = pyfits.open(fits)
    tbdata  = hdulist[1].data
    dtime   = tbdata.field('time')
    data    = tbdata.field(msid)
    hdulist.close()

    ftime   = dtime.mean()
    fdata   = data.mean()
    fmed    = numpy.median(data)
    fstd    = data.std()
    fmin    = data.min()
    fmax    = data.max()
    dlen    = len(list(data))

    return [ftime, fdata, fmed, fstd, fmin, fmax, 0.0, 0.0, 0.0, 0.0,  dlen, -999, 999, -999, 999]

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def get_stat_short(fits, msid):

    hdulist = pyfits.open(fits)
    tbdata  = hdulist[1].data
    dtime   = tbdata.field('time')
    data    = tbdata.field(msid)
    hdulist.close()
    
    diff    = 0
    dtsave  = []
    ddsave  = []
    start   = dtime[0]
    asave   = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

    for k in range(0, len(dtime)):

        diff = dtime[k] - start

        if diff >= 3600:
            dtsave = numpy.array(dtsave)
            ddsave = numpy.array(ddsave)
            try:
                val = dtsave.mean()
            except:
                continue 
            asave[0].append(val)

            try:
                val = ddsave.mean()
            except:
                val = 0
            asave[1].append(val)

            try:
                val = numpy.median(ddsave)
            except:
                val = 0
            asave[2].append(val)

            try:
                val = ddsave.std()
            except:
                val = 0
            asave[3].append(val)

            try:
                val = ddsave.min()
            except:
                val = 0
            asave[4].append(val)

            try:
                val = ddsave.max()
            except:
                val = 0
            asave[5].append(val)

            asave[6].append(0.0)
            asave[7].append(0.0)
            asave[8].append(0.0)
            asave[9].append(0.0)

            try:
                val = len(list(ddsave))
            except:
                val = 0
            asave[10].append(val)

            asave[11].append(-999)
            asave[12].append(999)
            asave[13].append(-999)
            asave[14].append(999)

            start  = dtime[k]
            dtsave = []
            ddsave = []
        else:
            dtsave.append(dtime[k])
            ddsave.append(data[k])
#
#--- left over
#
    if diff < 3600 and len(dtsave) > 10:
        dtsave = numpy.array(dtsave)
        ddsave = numpy.array(ddsave)

        try:
            val = dtsave.mean()
            asave[0].append(val)
            chk = 1
        except:
            chk = 0

        if chk > 0:
            val = ddsave.mean()
            asave[1].append(val)
    
            try:
                val = numpy.median(ddsave)
            except:
                val = 0
            asave[2].append(val)
    
            try:
                val = ddsave.std()
            except:
                val = 0
            asave[3].append(val)
    
            try:
                val = ddsave.min()
            except:
                val = 0
            asave[4].append(val)
    
            try:
                val = ddsave.max()
            except:
                val = 0
            asave[5].append(val)
    
            asave[6].append(0.0)
            asave[7].append(0.0)
            asave[8].append(0.0)
            asave[9].append(0.0)
    
            try:
                val = len(list(ddsave))
            except:
                val = 0
            asave[10].append(val)
    
            asave[11].append(-999)
            asave[12].append(999)
            asave[13].append(-999)
            asave[14].append(999)


    return asave

#-------------------------------------------------------------------------------------------
#-- update_fits_file: update fits file                                                    --
#-------------------------------------------------------------------------------------------

def update_fits_file(fits, cols, cdata):
    """
    update fits file
    input:  fits--- fits file name
    cols--- a list of column names
    cdata   --- a list of lists of data values
    output: updated fits file
    """
    
    f = pyfits.open(fits)
    data  = f[1].data
    f.close()
    
    udata= []
    for k in range(0, len(cols)):
        nlist   = list(data[cols[k]]) + cdata[k]
        udata.append(nlist)
    
    mcf.rm_file(fits)
    create_fits_file(fits, cols, udata)

#-------------------------------------------------------------------------------------------
#-- create_fits_file: create a new fits file for a given data set                         --
#-------------------------------------------------------------------------------------------

def create_fits_file(fits, cols, cdata):
    """
    create a new fits file for a given data set
    input:  fits--- fits file name
    cols--- a list of column names
    cdata   --- a list of lists of data values
    output: newly created fits file "fits"
    """
    
    #cdata = remove_duplicate(cdata)
    
    dlist = []
    for k in range(0, len(cols)):
        aent = numpy.array(cdata[k])
        dcol = pyfits.Column(name=cols[k], format='E', array=aent)
        dlist.append(dcol)
    
    dcols = pyfits.ColDefs(dlist)
    tbhdu = pyfits.BinTableHDU.from_columns(dcols)
    
    mcf.rm_file(fits)
    tbhdu.writeto(fits)


#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def extract_hrchk(start, stop):
    """
    extract hrchk data
    input:  start   --- starting time in yyyy-mm-ddThh:mm:ss
            stop    --- stopping time in yyyy-mm-ddThh:mm:ss
    output: data    --- a list of fits files extracted
    """

    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=hrc\n'
    line = line + 'level=0\n'
    line = line + 'filetype=hrchk\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop='  + str(stop)  + '\n'
    line = line + 'go\n'

    f    = open(zspace, 'w')
    f.write(line)
    f.close()

    cmd  = 'arc5gl -user isobe -script ' + zspace + ' >./zlist'
    os.system(cmd)
    cmd  = 'rm ' + zspace
    os.system(cmd)

    f    = open('./zlist', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    cmd  = 'rm -f  ./zlist'
    os.system(cmd)

    cdata = []
    for ent in data:
        mc = re.search('fits.gz', ent)
        if mc is not None:
            cdata.append(ent)

    cmd = 'chmod 777 *fits.gz'
    os.system(cmd)

    return cdata

#-----------------------------------------------------------------------------------
#-- update_fits_file: update fits file                                            --
#-----------------------------------------------------------------------------------

def update_fits_file(fits, cols, cdata):
    """
    update fits file
    input:  fits--- fits file name
    cols--- a list of column names
    cdata   --- a list of lists of data values
    output: updated fits file
    """
#
#--- if the fits file exists, append the new data
#
    if os.path.isfile(fits):

        f = pyfits.open(fits)
        data  = f[1].data
        f.close()
     
        udata= []
        for k in range(0, len(cols)):
            nlist   = list(data[cols[k]]) + list(cdata[k])
            udata.append(nlist)
    
        mcf.rm_file(fits)
#
#--- if the fits file does not exist, create one
#
    else:
        udata = cdata

    create_fits_file(fits, cols, udata)


#-----------------------------------------------------------------------------------
#-- create_fits_file: create a new fits file for a given data set                 --
#-----------------------------------------------------------------------------------

def create_fits_file(fits, cols, cdata):
    """
    create a new fits file for a given data set
    input:  fits--- fits file name
    cols--- a list of column names
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
    
    mcf.rm_file(fits)
    tbhdu.writeto(fits)



#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    extract_data()
