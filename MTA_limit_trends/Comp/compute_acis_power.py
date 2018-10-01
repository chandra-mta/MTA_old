#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#           compute_acis_power.py: compute acis power and fill data                 #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 08, 2018                                               #
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
import update_database_from_ska as udfs       #---- database update related scripts
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- compute_acis_power: compute acis power from existing msid values and update database  --
#-------------------------------------------------------------------------------------------

def compute_acis_power():
    """
    compute acis power from existing msid values and update database
    input:  none, but read data from achieve
    output: <msid>_data.fits/<msid>_short_data.fits/<msid>_week_data.fits
    """
#
#--- set a couple of values/list
#
    group     = 'Compacispwr'
    msid_list = ['1dppwra', '1dppwrb']
    msid_sub  = [['1dppwra', '1dp28avo', '1dpicacu', '*'], ['1dppwrb', '1dp28bvo', '1dpicbcu', '*']]
#
#--- create msid <---> unit dictionary
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read mta database
#
    mta_db = ecf.read_mta_database()

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
        udfs.update_database(msid, group,  glim, msid_sub = msid_sub)

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
    if msid == '1dppwra':
        msid_v = '1dp28avo'
        msid_a = '1dpicacu'
    else:
        msid_v = '1dp28bvo'
        msid_a = '1dpicbcu'

    glim_v = mta_db[msid_v]
    glim_a = mta_db[msid_a]

    if len(glim_v) > len(glim_a):
        flist1 = glim_v
        flist2 = glim_a
    else:
        flist1 = glim_a
        flist2 = glim_v

    
    glim   = []
    for k in range(0, len(flist1)):
        start1 = flist1[k][0]
        for m in range(0, len(flist2)):
            start2 = flist2[m][0]
            if start1 <= start2:
                pos = m
                break

        yl = flist1[k][2] * flist2[pos][2]
        yu = flist1[k][3] * flist2[pos][3]
        rl = flist1[k][4] * flist2[pos][4]
        ru = flist1[k][5] * flist2[pos][5]

        nlist = [flist1[k][0], flist1[k][1], yl, yu, rl, ru]
        glim.append(nlist)
        
    return glim


#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

        compute_acis_power()

