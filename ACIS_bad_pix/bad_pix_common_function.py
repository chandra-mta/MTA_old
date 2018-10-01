#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################################
#                                                                                                                       #
#       bad_pix_common_function.py: collections of functions used in ACIS Bad Pixel Scripts                             #
#                                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                                   #
#                                                                                                                       #
#           last update May 13, 2014                                                                                    #
#                                                                                                                       #
#########################################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import pyfits

path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat      as tcnv       #---- contains MTA time conversion routines
import mta_common_functions   as mcf        #---- contains other functions commonly used in MTA scripts

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#--- extractCCDInfo: extract CCD information from a fits file                                    ---
#---------------------------------------------------------------------------------------------------

def extractCCDInfo(file):

    """
    extreact CCD infromation from a fits file
    Input:  file        --- fits file name
    Output: ccd_id      --- ccd #
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
        hdr = pyfits.getheader(file)
        ccd_id      = hdr['CCD_ID']
        readmode    = hdr['READMODE']
        date_obs    = hdr['DATE-OBS']
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

def extractBiasInfo(file):

    """
    extreact CCD infromation from a fits file
    Input:  file        --- fits file name
    Output: feb_id      --- FEB ID
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
    hdr  = pyfits.getheader(file)

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
    Input:  name --- header keyword name
            data --- a list of fits file name
    Output  val  --- header keyword value
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
#--- convertTime: extract time part from a data path (year, month, day) and covnert to DOM       ---
#---------------------------------------------------------------------------------------------------

def convertTime(line):

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

def sortAndclean(inlist, icol = 0):
    
    """
    sort and clean a list (removing duplicated entries) 
    Input:  inlist --- a list
    Output: inlist --- a list cleaned
    """
    inlist.sort()
    inlist = list(set(inlist))

    return inlist

#---------------------------------------------------------------------------------------------------
#---- findTimeFromHead: isolate time part from a file and convert to DOM                         ---
#---------------------------------------------------------------------------------------------------

def findTimeFromHead(file):

    """
    isolate time part from a file and convert to DOM
    Input:  file --- fits file name
            dom  --- file creation time in DOM
    """

    stime = extractTimePart(file)
    ctime = tcnv.convertCtimeToYdate(stime)
    (year, month, date, hours, minutes, seconds, ydate, dom, sectime) = tcnv.dateFormatConAll(ctime)

    return int(dom)

#---------------------------------------------------------------------------------------------------
#--- extractTimePart: extract the time part from fits file name                                  ---
#---------------------------------------------------------------------------------------------------

def extractTimePart(file):

    """
    extract the time part from fits file name
    Input:  file  --- file name
            stime --- file creation time in seconds from 1.1.1998
    """

    cpart = ''
    try:
        m  = re.search('acisf', file)
        m2 = re.search('acis',  file)
        if m is not None:
            cpart = 'acisf'
        elif m2 is not None:
            cpart = 'acis'
    
        if cpart == '':
            return  -999
        else:
            atemp = re.split(cpart, file)
            btemp = re.split('N',     atemp[1])
            stime = float(btemp[0])
    
            return stime
    except:
        return -999
