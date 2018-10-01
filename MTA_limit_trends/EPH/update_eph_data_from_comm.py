#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#       update_eph_data_from_comm.py: collect eph data for trending                 #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Jun 08, 2018                                               #
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

testfits = data_dir + 'Ephhk/eiostatus_a_data.fits'

#-------------------------------------------------------------------------------------------
#-- update_eph_data_from_comm: collect eph data for trending                             ---
#-------------------------------------------------------------------------------------------

def update_eph_data_from_comm(date = ''):
    """
    collect eph data for trending
    input:  date    ---- the data collection end date in yyyymmdd format. if not given, yesterday's date is used
    output: fits file data related to grad and comp
    """
#
#--- read group names which need special treatment
#
    #sfile = house_keeping + 'eph_list'
    #glist = ecf.read_file_data(sfile)
    glist = ['ephhk',]
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
        yesterday = datetime.date.today() - datetime.timedelta(1)
        yesterday = str(yesterday).replace('-', '')
        date_list = create_date_list(yesterday)

    else:
        date_list = [date]

    error_message = ''
    for day in date_list:
#
#--- find the names of the fits files of the day of the group
#
        dline = "Date: " + str(day)
        print dline
    
        for group in glist:
            print "Group: " + str(group)
            #cmd = 'ls /data/mta_www/mp_reports/' + day + '/' + group + '/data/eph*static*fits* > ' + zspace
            cmd = 'ls /data/mta_www/mp_reports/' + day + '/' + group + '/data/* > ' + zspace
            os.system(cmd)
    
            tlist = ecf.read_file_data(zspace, remove=1)
            flist = []
            for ent in tlist:
                mc = re.search('_STephhk_static_eio0.fits',  ent)
                if mc is not None:
                    flist.append(ent)
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
                mcf.rm_file('ztemp.fits')
                mfo. appendFitsTable(flist[0], flist[1], 'ztemp.fits')
                if flen > 2:
                    for k in range(2, flen):
                        mfo. appendFitsTable('ztemp.fits', flist[k], 'out.fits')
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
                mc  = re.search('quality', col, re.IGNORECASE)
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
                wline = uds.update_database(msid, group.capitalize(), dtime, data, glim)

                if wline != "":
                    error_message = error_message + dline + '\n' + wline
#
#--- if there are errors, sending error message
#
    if error_message != "":
        error_message = 'MTA limit trend EPH got problems: \n' + error_message

        fo = open(zspace, 'w')
        fo.write(error_message)
        fo.close()
        cmd  = 'cat ' + zspace + ' | mailx -s "Subject: EPH data update problem " tisobe@cfa.harvard.edu'
        os.system(cmd)
        mcf.rm_file(zspace)

#-------------------------------------------------------------------------------------------
#-- create_date_list: find the last entry date and then make a list of dates up to yesterday
#-------------------------------------------------------------------------------------------

def create_date_list(yesterday):
    """
    find the last entry date and then make a list of dates up to yesterday
    input:  yesterday   --- date of yesterday in the format of yyyymmdd
    output: otime       --- a list of date in the format of yyyymmdd
    """
#
#--- find the last entry date from the "testfits" file
#
    try:
        f = pyfits.open(testfits)
        data = f[1].data
        f.close()
#
#--- find the last time logged and changed to a python standard time insecods
#
        ltime = numpy.max(data['time'])  + 883630800.0
    except:
        ltime = 48902399                #--- 1999:202:00:00:00
#
#--- find the time of the start of the day
#
    ct    = time.strftime('%Y%m%d', time.gmtime(ltime))
    year  = int(ct[0:4])
    mon   = int(ct[4:6])
    day   = int(ct[6:8])
    dt    = datetime.datetime(year, mon, day)
    ltime = time.mktime(dt.timetuple())
#
#--- set starting day to the next day
#
    ltime = ltime + 86400.0
#
#--- convert yesterday to seconds
#
    yesterday = str(yesterday)
    year  = int(yesterday[0:4])
    mon   = int(yesterday[4:6])
    day   = int(yesterday[6:8])
    dt    = datetime.datetime(year, mon, day)
    stime = time.mktime(dt.timetuple())

    ctime = [ltime]
    while ltime < stime:
        ltime += 86400.0
        ctime.append(ltime)
#
#--- convert the list to yyyymmdd format
#
    otime = []
    for ent in ctime:
        oday =  time.strftime('%Y%m%d', time.gmtime(ent))
        otime.append(oday)

    return otime


#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
            date = sys.argv[1]
            date.strip()
            update_eph_data_from_comm(date)
    else:
        update_eph_data_from_comm()

