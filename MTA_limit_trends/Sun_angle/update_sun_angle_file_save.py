#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#           update_sun_angle_file.py: update sun_angle.fits file                                    #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Jul 07, 2017                                                               #
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
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

cols = ['time', 'sun_angle']

fits_file = data_dir +  'sun_angle.fits' 

#-----------------------------------------------------------------------------------
#-- run_sun_angle_update: update sun_angle.fits file                              --
#-----------------------------------------------------------------------------------

def run_sun_angle_update():
    """
    update sun_angle.fits file
    input:  none but read <data_dir>/sun_angle.fits
    output: updated <data_dir>/sun_angle.fits
    """
#
#--- check whether the data file exists
#
    if os.path.isfile(fits_file):
#
#--- find the last entry date
#
        f = pyfits.open(fits_file)
        data  = f[1].data
        f.close()
        begin = data['time'][-1]

    else:
        begin = Chandra.Time.DateTime('1999:202:00:00:00').secs

    update_sun_angle_file(begin)

#-----------------------------------------------------------------------------------
#-- update_sun_angle_file: update sun_angle.fits from begining to yesterday's date -
#-----------------------------------------------------------------------------------

def update_sun_angle_file(begin):
        """
        update sun_angle.fits from begining to yesterday's date
        input:  begin   --- starting time in seconds from 1998.1.1
        output: updated <data_dir>/sun_angle.fits
        """
#
#--- find the yesterday's date in seconds from 1998.1.1
#
        stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
        stday = Chandra.Time.DateTime(stday).secs - 86400.0     #--- set the ending to the day before
#
#--- fill up the data till yesterday
#
        if stday > begin:
            end = begin + 86400.0
            while stday > begin:

                u = Chandra.Time.DateTime(begin)
                print u.date

                cdata = find_pitch_angle(begin, end)
                update_fits_file(fits_file, cols, cdata)
                begin = end
                end   = begin + 86400.0
                if begin >= stday:
                    break

#-----------------------------------------------------------------------------------
#-- find_pitch_angle: create a table of time and sun pitch angle                  --
#-----------------------------------------------------------------------------------

def find_pitch_angle(start, stop):
    """
    create a table of time and sun pitch angle
    input:  start   --- starting time in seconds from 1998.1.1
            stop    --- stopping time in seconds from 1998.1.1
    output: time    --- a list of time in seconds from 1998.1.1
            pitch   --- a list of ptich in degree
    """
#
#--- extract pcad aspsol fits files for the given time period
#
    f_list = extract_aspsol(start, stop)

    f_list.sort()

    time_list  = []
    pitch_list = []
    prev       = 0.0
    for fits in f_list:

        mc = re.search('.fits', fits)
        if mc is None:
            continue

        f     = pyfits.open(fits)
        data  = f[1].data
        f.close()

        time  = data['time']
        ra    = data['ra']
        dec   = data['dec']
        prev  = 0
        m     = 0
        for k in range(0, len(time)):
#
#--- select one data every 5 mins
#
            itime = int(time[k])
            if itime == prev:
                continue

            if m % 300 == 0:
#
#--- get the sun angle
#
                pitch = find_chandra_pitch(time[k], ra[k], dec[k])
                time_list.append(itime)
                pitch_list.append(pitch)
            prev  = itime
            m += 1

        cmd = 'rm ' + fits
        os.system(cmd)

    time    = numpy.array(time_list)
    pitch   = numpy.array(pitch_list)
    return [time, pitch]

#-----------------------------------------------------------------------------------
#-- extract_aspsol: extract pacd aspsol fits file using arc5gl                    --
#-----------------------------------------------------------------------------------

def extract_aspsol(start, stop):
    """
    extract pacd aspsol fits file using arc5gl
    input:  start   --- starting time in seconds from 1998.1.1
            stop    --- stopping time in seconds from 1998.1.1
    output: data    --- a list of fits files extracted
            pcadf*_asol1.fits.gz
    """

    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=pcad\n'
    line = line + 'subdetector=aca\n'
    line = line + 'level=1\n'
    line = line + 'filetype=aspsol\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop=' + str(stop) + '\n'
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

    cmd  = 'rm  ./zlist'
    os.system(cmd)

    return data

#-----------------------------------------------------------------------------------
#-- find_chandra_pitch: compute the sun angle                                     --
#-----------------------------------------------------------------------------------

def find_chandra_pitch(time, ra, dec):
    """
    compute the sun angle
    input:  time    --- time in seconds from 1998.1.1
            ra      --- ra of Chandra pointing direction
            dec     --- dec of Chandra pointing direction
    output: pitch   --- sun angle in degree
    """
    [sun_ra, sun_dec] =  Ska.Sun.position(time)
    pitch = Ska.astro.sph_dist(ra, dec, sun_ra, sun_dec)

    return pitch

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

    if len(sys.argv) == 3:
        tstart = float(sys.argv[1])
        tstop  = float(sys.argv[2])
        cdata  = find_pitch_angle(tstart, tstop)    
        update_fits_file('./temp_sun_angle.fits', cols, cdata)

    else:
        run_sun_angle_update()

