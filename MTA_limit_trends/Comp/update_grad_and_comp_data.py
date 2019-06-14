#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#       update_grad_and_comp_data.py: collect grad and comp data for trending       #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 21, 2019                                               #
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions     as mcf        #---- contains other functions commonly used in MTA scripts
import glimmon_sql_read         as gsr
import envelope_common_function as ecf
import fits_operation           as mfo
import update_database_suppl    as uds        #---- database update supplemental scripts
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

testfits = data_dir + 'Gradablk/haftbgrd1_data.fits'

#-------------------------------------------------------------------------------------------
#-- update_grad_and_comp_data: collect grad and  comp data for trending                  ---
#-------------------------------------------------------------------------------------------

def update_grad_and_comp_data(date = ''):
    """
    collect grad and  comp data for trending
    input:  date    ---- the data colletion  end date in yyyymmdd format. if not given, yesterday's date is used
    output: fits file data related to grad and comp
    """
#
#--- read group names which need special treatment
#
    sfile = house_keeping + 'mp_process_list'
    glist = mcf.read_data_file(sfile)
#
#--- create msid <---> unit dictionary
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read mta database
#
    mta_db = ecf.read_mta_database()
#
#--- read mta msid <---> sql msid conversion list
#
    mta_cross = ecf.read_cross_check_table()
#
#--- find date to read the data
#
    if date == '':
        date_list = ecf.create_date_list_to_yestaday(testfits)

    else:
        date_list = [date]

    for day in date_list:
#
#--- find the names of the fits files of the day of the group
#
        print("Date: " + str(day))
    
        for group in glist:
            print("Group: " + str(group))
            cmd = 'ls /data/mta_www/mp_reports/' + day + '/' + group + '/data/mta*fits* > ' + zspace
            os.system(cmd)
    
            flist = mcf.read_data_file(zspace, remove=1)
#
#--- combined them
#
            flen = len(flist)
    
            if flen == 0:
                continue
    
            elif flen == 1:
                cmd = 'cp ' + flist[0] + ' ./ztemp.fits'
                os.system(cmd)
    
            else:
                mfo.appendFitsTable(flist[0], flist[1], 'ztemp.fits')
                if flen > 2:
                    for k in range(2, flen):
                        mfo.appendFitsTable('ztemp.fits', flist[k], 'out.fits')
                        cmd = 'mv out.fits ztemp.fits'
                        os.system(cmd)
#
#--- read out the data for the full day
#
            [cols, tbdata] = ecf.read_fits_file('ztemp.fits')
    
            cmd = 'rm -f ztemp.fits out.fits'
            os.system(cmd)
#
#--- get time data in the list form
#
            dtime = list(tbdata.field('time'))
    
            for k in range(1, len(cols)):
#
#--- select col name without ST_ (which is standard dev)
#
                col = cols[k]
                mc  = re.search('ST_', col)
                if mc is not None:
                    continue
#
#---- extract data in a list form
#
                data = list(tbdata.field(col))
#
#--- change col name to msid
#
                msid = col.lower()
#
#--- get limit data table for the msid
#
                try:
                    tchk  = ecf.convert_unit_indicator(udict[msid])
                except:
                    tchk  = 0
    
                glim  = ecf.get_limit(msid, tchk, mta_db, mta_cross)
#
#--- update database
#
                uds.update_database(msid, group, dtime, data, glim)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
            date = sys.argv[1]
            date.strip()
            update_grad_and_comp_data(date)
    else:
        update_grad_and_comp_data()

