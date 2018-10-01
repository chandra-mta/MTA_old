#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#           compute_sim_flex.py: computing sim flex difference                      #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 14, 2018                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import time
#import numpy
#import astropy.io.fits  as pyfits
#import Ska.engarchive.fetch as fetch
#import Chandra.Time

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
import envelope_common_function as ecf
import update_database_suppl    as uds
#import glimmon_sql_read         as gsr
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- compute_sim_flex: compute sim flex diff                                               --
#-------------------------------------------------------------------------------------------

def compute_sim_flex():
    """
    compute the difference between sim flex temp and set point 
    input:  none, but read data from achieve
    output: <msid>_data.fits/<msid>_short_data.fits/<msid>_week_data.fits
    """
#
#--- set a couple of values/lists
#
    group     = 'Compsimoffset'
    msid_list = ['flexadif', 'flexbdif', 'flexcdif']
    msid_sub  = [['flexadif', '3faflaat', '3sflxast', '-'],\
                 ['flexbdif', '3faflbat', '3sflxbst', '-'],\
                 ['flexcdif', '3faflcat', '3sflxcst', '-']]
    mta_db    = ecf.read_mta_database()

    for msid in msid_list:
#
#--- get limit data table for the msid
#
        try:
            tchk  = ecf.convert_unit_indicator(udict[msid])
        except:
            tchk  = 0

        glim  = get_limit_for_acis_power(msid, mta_db)
#
#--- update database
#
        uds.run_update_with_ska(msid, group, msid_sub_list=msid_sub, glim=glim)

#-------------------------------------------------------------------------------------------
#-- get_limit_for_acis_power: compute acis power limits from voltage and current          --
#-------------------------------------------------------------------------------------------

def get_limit_for_acis_power(msid,  mta_db):
    """
    compute acis power limits from voltage and current
    input:  msid        --- msid
            mta_db      --- a dictionary of mta msid <---> limist
    output: glim        --- a list of lists of lmits. innter lists are:
                            [start, stop, yl, yu, rl, ru]
    """
    if   msid == 'flexadif':
        #msid_t = '3faflaat' 
        #msid_s = '3sflxast' 
        msid_t = 'flexatemp'
        msid_s = 'flexatset'

    elif msid == 'flexbdif':
        #msid_t = '3faflbat' 
        #msid_s = '3sflxbst' 
        msid_t = 'flexbtemp'
        msid_s = 'flexatset'
    else:
        #msid_t = '3faflcat' 
        #msid_s = '3sflxcst' 
        msid_t = 'flexctemp'
        msid_s = 'flexatset'

    glim_t = mta_db[msid_t]
    glim_s = mta_db[msid_s]

    if len(glim_t) > len(glim_s):
        flist1 = glim_t
        flist2 = glim_s
    else:
        flist1 = glim_s
        flist2 = glim_t

    
    glim   = []
    for k in range(0, len(flist1)):
        start1 = flist1[k][0]
        for m in range(0, len(flist2)):
            start2 = flist2[m][0]
            if start1 <= start2:
                pos = m
                break

        yl = flist1[k][2] - flist2[pos][2]
        yu = flist1[k][3] - flist2[pos][3]
        rl = flist1[k][4] - flist2[pos][4]
        ru = flist1[k][5] - flist2[pos][5]

        nlist = [flist1[k][0], flist1[k][1], yl, yu, rl, ru]
        glim.append(nlist)
        
    return glim


#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

        compute_sim_flex()

