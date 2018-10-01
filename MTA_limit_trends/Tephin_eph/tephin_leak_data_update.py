#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#       tephin_leak_data_update.py: update tephin - ephin rate/leak current data    #
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
import update_database_suppl    as uds
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- tephin_leak_data_update: update tephin - ephin rate/leak current data                ---
#-------------------------------------------------------------------------------------------

def tephin_leak_data_update(year=''):
    """
    update tephin - ephin rate/leak current data
    input:  year    --- year of the data to be updated. if it is '', the current year is used
    output: <data_dir>/<msid>/<msid>_data_<year>.fits
    """
#
#--- set data extraction period
#
    tout = set_time_period(year)
    if len(tout) == 6:
        [lstart, lstop, lyear, tstart, tstop, year] = tout
        chk = 1
    else:
        [tstart, tstop, year] = tout
        chk = 0
#
#--- get the basic information
#
    [udict, ddict, mta_db, mta_cross] = ecf.get_basic_info_dict()
#
#--- extract tephin data
#
    tchk  = ecf.convert_unit_indicator(udict['tephin'])
    glim  = ecf.get_limit('tephin', tchk, mta_db, mta_cross)
#
#--- for the case the time span goes over the year boundary
#
    if chk == 1:
        ltephin = update_database('tephin', 'Eleak', glim, ltstart, ltstop, lyear)

    tephin  = update_database('tephin', 'Eleak', glim, tstart, tstop, year)

#
#--- read msid list
#
    mfile = house_keeping + 'msid_list_eph_tephin'
    data  = ecf.read_file_data(mfile)

    for ent in data:
#
#--- find msid and group name
#
        mc = re.search('#', ent)
        if mc is not None:
            continue
        try:
            [msid, group] = re.split('\s+', ent)
        except:
            atemp = re.split('\s+', ent)
            msid  = atemp[0]
            group = atemp[1]

        msid.strip()
        group.strip()
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
        try:
            out = fetch.MSID(msid, '2017:001:00:00:00', '2017:002')
            print "MSID: " + msid
        except:
            missed = house_keeping + '/missing_data'
            fo     = open(missed, 'a')
            fo.write(msid)
            fo.write('\n')
            fo.close()

            continue
#
#--- for the case, the time span goes over the year boundary
#
        if chk == 1:
            update_database(msid, group,  glim, ltstart, ltstop, lyear, sdata=ltephin)

        update_database(msid, group,  glim, tstart, tstop, year, sdata=tephin)

#-------------------------------------------------------------------------------------------
#-- set_time_period: setting data extract data period                                     --
#-------------------------------------------------------------------------------------------

def set_time_period(year):
    """
    setting data extract data period
    input:  year    --- year of the data to be extracted. if it is '', the current year will be used
    output: start   --- starting time in sec from 1998.1.1
            stop    --- stopping time in sec from 1998.1.1
            tyear   --- year

            when the period is going over the year boundary, output provide 6 output including:

            lstart  --- starting time in the last year 
            lstop   --- stopping time in the last year
            lyear   --- last year
    """
    if year == '':
#
#--- find this year
#
        tyear  = int(time.strftime("%Y", time.localtime()))
#
#--- find the latest tephin_data fits file 
#
        tephin = data_dir + 'Eleak/Tephin/tephin_data' + str(tyear) + '.fits'
        if os.path.isfile(tephin):
            start = ecf.find_the_last_entry_time(tephin)
#
#--- today's date
#
            stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
            stop  = Chandra.Time.DateTime(stday).secs

            return [start, stop, tyear]

        else:
#
#--- if the time span goes over the year boundary, return two sets of periods
#
            start = str(year)   + ':001:00:00:00'
            start = Chandra.Time.DateTime(start).secs
            stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
            stop  = Chandra.Time.DateTime(stday).secs
#
#-- the last year update
#
            lyear = tyear - 1
            ltephin = data_dir + 'Eleak/Tephin/tephin_data' + str(lyear) + '.fits'
            lstart = ecf.find_the_last_entry_time(ltephin)
            lstop  = str(tyear) + ':001:00:00:00'
            lstop  = Chandra.Time.DateTime(stop).secs

            return [lstart, lstop, lyear, start, stop, tyear]
         
    else:
#
#--- the case creating the entire year 
#
        start = str(year)   + ':001:00:00:00'
        start = Chandra.Time.DateTime(start).secs
        stop  = str(year+1) + ':001:00:00:00'
        stop  = Chandra.Time.DateTime(stop).secs

        return [start, stop, year]


#-------------------------------------------------------------------------------------------
#-- update_database: update/create fits data files of msid                                --
#-------------------------------------------------------------------------------------------

def update_database(msid, group, glim, pstart, pstop, year, sdata=''):
    """
    update/create fits data files of msid
    input:  msid    --- msid
            pstart  --- starting time in seconds from 1998.1.1; defulat = 0 (find from the data)
            pstop   --- stopping time in seconds from 1998.1.1; defulat = 0 (find from the data)
            sdata   --- data set to be added as an independent data
    output: <msid>_data.fits, <msid>_short_data.fits
    """

    cols  = ['time', 'tephin', 'med', 'std', 'min', 'max', 'ylower', 'yupper', 'rlower', 'rupper', 'dcount',\
             'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

    cols2 = ['time', 'tephin',  msid, 'med', 'std', 'min', 'max', 'ylower', 'yupper', 'rlower', 'rupper',\
             'dcount', 'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

#
#--- make sure that the sub directory exists
#
    out_dir = data_dir + 'Eleak/' + msid.capitalize() + '/'

    if not os.path.isdir(out_dir):
        cmd = 'mkdir ' + out_dir
        os.system(cmd)
    
    fits = out_dir + msid + '_data' + str(year) + '.fits'
#
#--- tephin data
#
    out     = fetch.MSID(msid, pstart, pstop)
    tdata   = out.vals
    ttime   = out.times

    [week_p, xxx, xxx2] = uds.process_day_data(msid, ttime, tdata, glim)
#
#---- tephin case
#
    if sdata == '':

        if os.path.isfile(fits):
            ecf.update_fits_file(fits, cols, week_p)
        else:
            ecf.create_fits_file(fits, cols, week_p)

        return week_p[1]
#
#--- all other msids
#
    else:
        slen = len(sdata)
        clen = len(week_p[1])
        if slen == clen:
            new = week_p[:1] + [sdata] + week_p[1:]
        elif slen < clen:
            diff = clen - slen
            for k in range(0, diff):
                sdata.append(sdata[-1])

            new = week_p[:1] + [sdata] + week_p[1:]
        else:
            
            tdata = sdata[:clen]
            new = week_p[:1] + [tdata] + week_p[1:]
        
        if os.path.isfile(fits):
            ecf.update_fits_file(fits, cols2, new)
        else:
            ecf.create_fits_file(fits, cols2, new)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        year = int(sys.argv[1])
    else:
        year = ''

    tephin_leak_data_update(year)


