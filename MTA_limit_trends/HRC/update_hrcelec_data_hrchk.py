#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################
#                                                                                   #
#           update_hrcelec_data_hrchk.py: update hrcelec data from archive data     #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 29, 2019                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time
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
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import update_database_suppl    as uds
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

dpath  = data_dir + '/Hrcelec/'

msid_list =['hvpsstat', 'mlswenbl', 'mlswstat', 'mtrcmndr', 'mtritmp', 'mtrselct',\
            'mtrstatr', 'n15cast', 'p15cast', 'p24cast','scidpren']

#-----------------------------------------------------------------------------------
#-- update_hrcelec_data_hrchk: update hrcelec data from archive data              --
#-----------------------------------------------------------------------------------

def update_hrcelec_data_hrchk():
    """
    update hrcelec data from archive data
    input:  none but read from data fits files from <data_dir>/Hrcelec/
    output: updated fits data files
    """
#
#--- set data cutting time
#
    stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
    stday = Chandra.Time.DateTime(stday).secs - 86400.0     #--- set the ending to the day before
    mago1 = stday - 31536000.0                              #--- a year ago
    mago2 = stday - 604800.0                                #--- a week ago

    mlen = len(msid_list)                                   #--- numbers of msids 
    chk  = 0
#
#--- set te data extraction date to the next date from the the last data extracted date
#
    t_list = find_starting_date()
    for start in t_list:
        out = Chandra.Time.DateTime(start).date
        print("Processing: " + str(out))

        stop  = start + 86400.0
        extract_hrcelec_data(start, stop, mago1, mago2, mlen)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def extract_hrcelec_data(start, stop, mago1, mago2, mlen):
#
#--- extract hrchk fits files
#
    flist = extract_hrchk(start, stop)
#
#--- combine extracted fits files for the day
#
    outfits   = 'comb_data.fits'
    comb_fits = ecf.combine_fits(flist, outfits)
#
#--- work on each msid
#
    for k in range(0, mlen):
        msid  = msid_list[k]
        cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower',\
                 'yupper', 'rlower', 'rupper', 'dcount', 'ylimlower',\
                 'ylimupper', 'rlimlower', 'rlimupper']
#
#--- long term data  (one day interval)
#
        ofits = dpath + msid + '_data.fits'
        cdata = get_stat(comb_fits, msid)

        if os.path.isfile(ofits):
            ecf.update_fits_file(ofits, cols, cdata)
        else:
            ecf.create_fits_file(ofits, cols, cdata)
#
#--- short term data (one hour interval)
#
        ofits = dpath + msid + '_short_data.fits'
        cdata = get_stat_interval(comb_fits, msid, 3600.0)

        if os.path.isfile(ofits):
            ecf.update_fits_file(ofits, cols, cdata)
        else:
            ecf.create_fits_file(ofits, cols, cdata)
#
#--- remove older data
#
        try:
            uds.remove_old_data(ofits, cols, mago1)
        except:
            pass
#
#--- week long data (five minute interval)
#
        ofits = dpath + msid + '_week_data.fits'
        cdata = get_stat_interval(comb_fits, msid, 300.0)

        if os.path.isfile(ofits):
            ecf.update_fits_file(ofits, cols, cdata)
        else:
            ecf.create_fits_file(ofits, cols, cdata)
#
#--- remove older data
#
        try:
            uds.remove_old_data(ofits, cols, mago2)
        except:
            pass

    mcf.rm_files('comb_data.fits')

#-----------------------------------------------------------------------------------
#-- find_starting_date: set starting and stopping time from the last entry of a fits file 
#-----------------------------------------------------------------------------------

def find_starting_date():
    """
    set starting and stopping time from the last entry of a fits file
    input: none but read from hvpsstat_data.fits
    output: start   --- starting time <yyyy>-<mm>-<dd>T00:00:00
            stop    --- stoping time  <yyyy>-<mm>-<dd>T23:59:59
    """
    test    = dpath + 'hvpsstat_data.fits'
    ltime   = ecf.find_the_last_entry_time(test) + 86400.0
    ltime   = mcf.convert_date_format(ltime, ifmt='chandra', ofmt='%Y:%j:00:00:00')
    ltime   = Chandra.Time.DateTime(ltime).secs

    today   = time.strftime('%Y:%j:00:00:00', time.gmtime())
    stime   = Chandra.Time.DateTime(today).secs - 86400.0
    t_list  = [ltime]
    while ltime < stime:
        ltime += 86400.0
        if ltime > stime:
            break
        else:
            t_list.append(ltime)

    return t_list

#-----------------------------------------------------------------------------------
#-- get_stat: find statistics of the fits data                                    --
#-----------------------------------------------------------------------------------

def get_stat(fits, msid):
    """
    find statistics of the fits data
    input:  fits    --- fits file name
            msid    --- msid which we want to extract the stat
    output: ftime   --- avg of time
            fdata   --- avg of msid data
            fmed    --- med of msid data
            fstd    --- std of msid data
            fmin    --- min of msid data
            fmax    --- max of msid data
            ylower  --- parcentage of lower yellow violation; set to 0
            yupper  --- parcentage of upper yellow violation; set to 0
            rlower  --- parcentage of lower red violation; set to 0
            rupper  --- parcentage of upper red violation; set to 0
            dlen    --- total numbers of data
            yllim   --- lower yellow limit value
            yulim   --- upper yellow limit value
            rllim   --- lower red limit value
            rulim   --- upper red limit value
    """
    hdulist = pyfits.open(fits)
    tbdata  = hdulist[1].data
    dtime   = tbdata.field('time')
    data    = tbdata.field(msid)
    hdulist.close()

    ftime   = numpy.mean(dtime)
    fdata   = numpy.mean(data)
    fmed    = numpy.median(data)
    fstd    = data.std()
    fmin    = data.min()
    fmax    = data.max()
    dlen    = len(list(data))
#
#--- return each value as a list
#
    return [[ftime], [fdata], [fmed], [fstd], [fmin], [fmax],\
            [0.0], [0.0], [0.0], [0.0],  [dlen], [-999], [999], [-999], [999]]

#-----------------------------------------------------------------------------------
#-- get_stat_interval: find statistics of the fits data and interval              --
#-----------------------------------------------------------------------------------

def get_stat_interval(fits, msid, interval):
    """
    find statistics of the fits data and interval
    input:  fits    --- fits file name
            msid    --- msid which we want to extract the stat
            interval--- the interval of data which we want to compute stats
    output: ftime   --- avg of time
            fdata   --- avg of msid data
            fmed    --- med of msid data
            fstd    --- std of msid data
            fmin    --- min of msid data
            fmax    --- max of msid data
            ylower  --- parcentage of lower yellow violation; set to 0
            yupper  --- parcentage of upper yellow violation; set to 0
            rlower  --- parcentage of lower red violation; set to 0
            rupper  --- parcentage of upper red violation; set to 0
            dlen    --- total numbers of data
            yllim   --- lower yellow limit value
            yulim   --- upper yellow limit value
            rllim   --- lower red limit value
            rulim   --- upper red limit value

    """
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

        if diff >= interval:
            dtsave = numpy.array(dtsave)
            ddsave = numpy.array(ddsave)

            try:
                val = numpy.mean(dtsave)
                asave[0].append(val)
            except:
                continue

            try:
                val = numpy.mean(ddsave)
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
    if diff < interval and len(dtsave) > 10:
        try:
            val = numpy.mean(dtsave)
            asave[0].append(val)
            chk = 1
        except:
            chk = 0

        if chk > 0:
            try:
                val = numpy.mean(ddsave)
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

    return asave

#-----------------------------------------------------------------------------------
#-- extract_hrchk: rchk fits data files from archive                              --
#-----------------------------------------------------------------------------------

def extract_hrchk(start, stop):
    """
    extract hrchk fits data files from archive
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

    cdata = mcf.run_arc5gl_process(line)

    if len(cdata) > 0:
        cmd = 'chmod 777 *fits.gz'
        os.system(cmd)

    return cdata

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    update_hrcelec_data_hrchk()
