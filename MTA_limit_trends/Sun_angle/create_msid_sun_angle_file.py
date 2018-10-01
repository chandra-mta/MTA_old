#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#           create_msid_sun_angle_file.py: create sun angle -- msid value data fits file            #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Feb 13, 2018                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import math
import sqlite3
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

sun_angle_file = data_dir +  'sun_angle.fits' 

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def create_msid_sun_angle_file(msid_list, inyear = ''):
    """
    create sun angle - msid data fits file
    input:  msid_list   --- the name of msid list which list msids and group id
            inyear      --- the year in which you want to extract the data; if "", 1999-current year
    output: <data_dir>/<group>/<msid>_sun_angle_<year>.fits
    """
    if inyear == '':
        this_year = int(float(time.strftime("%Y", time.gmtime())))
        year_list = range(1999, this_year+1)
    else:
        year_list = [inyear]

    [s_time, s_angle] = read_fits(sun_angle_file, ['time', 'sun_angle'])

    ifile  = house_keeping + msid_list
    f      = open(ifile, 'r')
    data   = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        group = atemp[1]
        mc = re.search('#', msid)
        if mc is not None:
            continue

        print "msid: " + msid

        odir = data_dir + group.capitalize() + '/' + msid.capitalize()
        if not os.path.isdir(odir):
            cmd = 'mkdir ' + odir
            os.system(cmd)

        mfile = data_dir + group.capitalize() + '/' + msid + '_data.fits'

        if not os.path.isfile(mfile):
            print "No data file found: " + str(mfile)
            continue

        try:
            [m_time, m_val, m_min, m_max] = read_fits(mfile, ['time', msid, 'min', 'max'])
        except:
            print "Could not read: " + str(mfile)
            continue

        for year in year_list:

            print "Year: " + str(year)

            ofits = odir + '/' + msid + '_sun_angle_' + str(year) + '.fits'
            cols  = ['sun_angle', msid, 'min', 'max']
            cdata = match_the_data(s_time, s_angle, m_time, m_val, m_min, m_max, year)

            create_fits_file(ofits, cols, cdata)


#-----------------------------------------------------------------------------------
#-- match_the_data: extract sun angle - msid value data for a given year          --
#-----------------------------------------------------------------------------------

def match_the_data(s_time, s_angle, m_time, m_val, m_min, m_max, year):
    """
    extract sun angle - msid value data for a given year
    input:  s_time  --- an array of sun angle data time
            s_angle --- an array of sun angle data
            m_time  --- an array of msid data time
            m_val   --- an array of msid data
            m_min   --- an array of msid min values
            m_max   --- an array of msid max_values
    output: angle   --- an array of sun angles
            mval    --- an array of msid values correspond to the sun angle
            mmin    --- an array of msid min values correspond to the sun angle
            mmax    --- an array of msid max values correspond to the sun angle

    """
#
#--- select out the data of the year
#
    start = str(year)   + ':001:00:00:00'
    stop  = str(year+1) + ':001:00:00:00'
    start = Chandra.Time.DateTime(start).secs
    stop  = Chandra.Time.DateTime(stop).secs

    s_time2  = s_time[(s_time  >= start) & (s_time < stop)]
    s_angle2 = s_angle[(s_time >= start) & (s_time < stop)]
    m_time2  = m_time[(m_time  >= start) & (m_time < stop)]
    m_val2   = m_val[(m_time   >= start) & (m_time < stop)]
    m_min2   = m_min[(m_time   >= start) & (m_time < stop)]
    m_max2   = m_max[(m_time   >= start) & (m_time < stop)]

    kstart = 0
    kend   = len(s_time2)-1
    angle  = []
    mval   = []
    mmin   = []
    mmax   = []
    chk    = 0

    for m in range(0, len(m_time2)):
        for k in range(kstart, kend):
            if (m_time2[m] >= s_time2[k]) and (m_time2[m] <= s_time2[k+1]):
                mval.append(m_val2[m])
                mmin.append(m_min2[m])
                mmax.append(m_max2[m])

                diff1 = abs(m_time2[m] - s_time2[k])
                diff2 = abs(m_time2[m] - s_time2[k+1])
                tot   = diff1 + diff2
                aval  = s_angle2[k] * diff2 / tot + s_angle2[k+1] * diff1 /tot
                angle.append(aval)

                kstart = k-1
                break
            else:
                if k == kend:
                    chk = 1
                    break
        if chk > 0:
            break


    angle = numpy.array(angle)
    mval  = numpy.array(mval)

    return [angle, mval, mmin, mmax]


#-----------------------------------------------------------------------------------
#-- read_fits: read fits file                                                     --
#-----------------------------------------------------------------------------------

def read_fits(fits, col_list):
    """
    read fits file
    input:  fits        --- file name
            col_list    --- a list of column names to be extracted 
    output: out         --- a list of data arrays corresponding to the column list
    """

    f = pyfits.open(fits)
    data = f[1].data
    f.close()

    out = []
    for col in col_list:
        out.append(data[col])

    return out

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

    if len(sys.argv) == 2:
        msid_list = sys.argv[1]
        create_msid_sun_angle_file(msid_list)

    elif len(sys.argv) == 3:
        msid_list = sys.argv[1]
        year      = int(float(sys.argv[2]))
        create_msid_sun_angle_file(msid_list, year)

    else:
        print "please provide <msid_list>. you can also specify the year"
