#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#       dea_full_data_update.py: update deahk search database                       #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 21, 2018                                               #
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
import fits_operation           as mfo
import update_database_suppl    as uds
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

mon_list1 = [1, 32, 60, 91, 121, 152, 192, 213, 244, 274, 305, 335]
mon_list2 = [1, 32, 61, 92, 122, 153, 193, 214, 245, 275, 306, 336]

out_dir = './Outdir/'


#-------------------------------------------------------------------------------------------
#-- dea_full_data_update: update deahk search database                                    --
#-------------------------------------------------------------------------------------------

def dea_full_data_update(chk):
    """
    update deahk search database
    input:  chk --- whether to request full data update: chk == 1:yes
    output: <deposit_dir>/Deahk/<group>/<msid>_full_data_<year>fits
    """

    tyear = int(float(time.strftime("%Y", time.gmtime())))

    cmd   = 'ls ' + data_dir + 'Deahk_*/*_week_data.fits > ' + zspace
    os.system(cmd)
    data  = ecf.read_file_data(zspace, remove=1)
    
    for ent in data:
        atemp = re.split('\/', ent)
        group = atemp[-2]
        btemp = re.split('_', atemp[-1])
        msid  = btemp[0]
        print "MSID: " + str(msid) + ' in ' + group
        
        [cols, tbdata] = ecf.read_fits_file(ent)

        dtime = tbdata['time']
        tdata = tbdata[msid]
        cols  = ['time', msid]
#
#--- regular data update
#
        if chk == 0:
#
#--- normal daily data update
#
            ofits = deposit_dir + 'Deahk_save/' + group + '/' + msid + '_full_data_' + str(tyear) + '.fits'
            if os.path.isfile(ofits):
                ltime = ecf.find_the_last_entry_time(ofits)
                ctime = str(tyear+1) + ':001:00:00:00'
                nchk  = 0
#
#--- if the data is over the year boundray, fill up the last year and create a new one for the new year
#
            else:
                ofits = deposit_dir + 'Deahk_save/' + group + '/' + msid + '_full_data_' + str(tyear-1) + '.fits'
                nfits = deposit_dir + 'Deahk_save/' + group + '/' + msid + '_full_data_' + str(tyear) + '.fits'
                try:
                    ltime = ecf.find_the_last_entry_time(ofits)
                except:
                    continue

                ctime = str(tyear) + ':001:00:00:00'
                nchk  = 1

            select = [(dtime > ltime) & (dtime < ctime)]
            stime  = dtime[select]
            sdata  = tdata[select] 
            cdata  = [stime, sdata]
            ecf.update_fits_file(ofits, cols, cdata)

            if nchk > 0:
                select = [dtime >= ctime]
                stime  = dtime[select]
                sdata  = tdata[select] 
                cdata  = [stime, sdata]
                ecf.create_fits_file(nfits, cols, cdata)
#
#--- start from beginning (year 1999)
#
        else:
            for year in range(1999, tyear+1):
                tstart = str(year)     + ':001:00:00:00'
                tstart = Chandra.Time.DateTime(tstart).secs
                tstop  = str(year + 1) + ':001:00:00:00'
                tstop  = Chandra.Time.DateTime(tstop).secs
    
                select = [(dtime >= tstart) & (dtime < tstop)]
                stime  = dtime[select]
                sdata  = tdata[select]
                cdata  = [stime, sdata]
    
                out    = deposit_dir + 'Deahk_save/' + group + '/'
                if not os.path.isdir(out):
                    cmd = 'mkdir ' + out
    
                out    = out + msid + '_full_data_' + str(year) + '.fits'
    
                ecf.create_fits_file(out, cols, cdata)

#--------------------------------------------------------------------

if __name__ == '__main__':

    
    if len(sys.argv) > 1:
        chk = sys.argv[1]
    else:
        chk = 0

    dea_full_data_update(chk)



