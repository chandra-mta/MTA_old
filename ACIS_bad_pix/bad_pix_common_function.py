#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#############################################################################################
#                                                                                           #
#       bad_pix_commections of functions used in ACIS Bad Pixel Scripts                     #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update Mar 28, 2019                                                        #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import astropy.io.fits as pyfits
import time

path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#--- extractCCDInfo: extract CCD information from a fits file                                    ---
#---------------------------------------------------------------------------------------------------

def extractCCDInfo(ifile):
    """
    extreact CCD infromation from a fits file
    input:  file        --- fits file name
    output: ccd_id      --- ccd #
            readmode    --- read mode
            date_obs    --- observation date
            overclock_a --- overclock a 
            overclock_b --- overclock b 
            overclock_c --- overclock c 
            overclock_d --- overclock d 
    """
#
#--- read fits file header
#
    try:
        hdr = pyfits.getheader(ifile)
        ccd_id   = hdr['CCD_ID']
        readmode = hdr['READMODE']
        date_obs = hdr['DATE-OBS']
        try:
            overclock_a = hdr['OVERCLOCK_A']
            overclock_b = hdr['OVERCLOCK_B']
            overclock_c = hdr['OVERCLOCK_C']
            overclock_d = hdr['OVERCLOCK_D']
        except:
            overclock_a = 'NA'
            overclock_b = 'NA'
            overclock_c = 'NA'
            overclock_d = 'NA'
    
        return [ccd_id, readmode, date_obs, overclock_a, overclock_b, overclock_c, overclock_d]
    except:
        return ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']

#---------------------------------------------------------------------------------------------------
#--- extractBiasInfo: extract Bias information from a fits file                                  ---
#---------------------------------------------------------------------------------------------------

def extractBiasInfo(ifile):

    """
    extreact CCD infromation from a fits file
    input:  file        --- fits file name
    output: feb_id      --- FEB ID
            datamode    --- DATAMODE
            start_row   --- STARTROW
            row_cnt     --- ROWCNT
            orc_mode    --- ORC_MODE
            deagain     --- DEAGAIN
            biasalg     --- BIASALG
            biasarg#    --- BIASARG# #: 0 - 3
            overclock_# --- INITOCL# #: A, B, C, D
    """
#
#--- read fits file header
#
#    try:
    hdr  = pyfits.getheader(ifile)

    fep_id      = hdr['FEP_ID']
    datamode    = hdr['DATAMODE']
    start_row   = hdr['STARTROW']
    row_cnt     = hdr['ROWCNT']
    orc_mode    = hdr['ORC_MODE']
    deagain     = hdr['DEAGAIN']
    biasalg     = hdr['BIASALG']
    biasarg0    = hdr['BIASARG0']
    biasarg1    = hdr['BIASARG1']
    biasarg2    = hdr['BIASARG2']
    biasarg3    = hdr['BIASARG3']
    overclock_a = hdr['INITOCLA']
    overclock_b = hdr['INITOCLB']
    overclock_c = hdr['INITOCLC']
    overclock_d = hdr['INITOCLD']

    return [fep_id, datamode, start_row, row_cnt, orc_mode, deagain, biasalg, biasarg0, biasarg1, biasarg2, biasarg3,  overclock_a, overclock_b, overclock_c, overclock_d]
#    except:
#        return ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']

#---------------------------------------------------------------------------------------------------
#--- findHeadVal: find header information for a given header keyword name                        ---
#---------------------------------------------------------------------------------------------------

def findHeadVal(name, data):

    """
    find header information for a given header keyword name   
    input:  name --- header keyword name
            data --- a list of fits file name
    output  val  --- header keyword value
    """
    val = 'INDEF'
    for ent in data:
        m = re.search(name, ent)
        if m is not None:
            atemp = re.split('\s+|\t+', ent)
            val   = atemp[2]
            try:
                val = float(val)
                val = int(val)
            except:
                pass

            break
    return(val)

#---------------------------------------------------------------------------------------------------
#--- extractTimePart: extract the time part from fits file name                                  ---
#---------------------------------------------------------------------------------------------------

def extractTimePart(ifile):
    """
    extract the time part from fits file name
    input:  file  --- file name
    output: stime --- file creation time in seconds from 1.1.1998
    """
#
#--- first check whether this is acis file
#
    cpart = ''
    try:
        m1 = re.search('acisf', ifile)
        m2 = re.search('acis',  ifile)
        if m1 is not None:
            cpart = 'acisf'

        elif m2 is not None:
            cpart = 'acis'
    
        if cpart == '':
            return  -999
#
#--- now extract time stamp
#
        else:
            atemp = re.split(cpart, ifile)
            btemp = re.split('N',   atemp[1])

            stime = int(float(btemp[0]))
            return stime
    except:
        return -999

#---------------------------------------------------------------------------------------------------
#--- convertTime: extract time part from a data path (year, month, day) and covnert to DOM       ---
#---------------------------------------------------------------------------------------------------

def convertTime_xxx(line):

    """
    extract time part from a data path (year, month, day) and covnert to DOM 
    Input:  line  --- fits file name (with a full data path)
                      example: /dsops/ap/sdp/cache/2013_05_26/acis/acisf485989498N001_5_bias0.fits
    Output: ctime --- file creation date in DOM
    """

    atemp = re.split('\/', line)
    btemp = re.split('_', atemp[5])
    year  = int(btemp[0])
    month = int(btemp[1])
    day   = int(btemp[2])

    ctime = tcnv.findDOM(year, month, day, 0, 0, 0)             #---- day of mission

    return ctime

#---------------------------------------------------------------------------------------------------
#--- sortAndclean: sort and clean a list (removing duplicated entries)                           ---
#---------------------------------------------------------------------------------------------------

def sortAndclean_xxx(inlist, icol = 0):
    """
    sort and clean a list (removing duplicated entries) 
    input:  inlist --- a list
    output: inlist --- a list cleaned
    """
    inlist.sort()
    inlist = list(set(inlist))

    return inlist

#---------------------------------------------------------------------------------------------------
#---- findTimeFromHead: isolate time part from a file and convert to DOM                         ---
#---------------------------------------------------------------------------------------------------

def findTimeFromHead_xxx(ifile):
    """
    isolate time part from a file and convert to DOM
    input:  file --- fits file name
            dom  --- file creation time in DOM
    """

    stime = extractTimePart(ifile)
    ctime = tcnv.convertCtimeToYdate(stime)
    (year, month, date, hours, minutes, seconds, ydate, dom, sectime) = tcnv.dateFormatConAll(ctime)

    return int(dom)
