#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#######################################################################################
#                                                                                     #
#       gratgen_categorize_data.py: separate gratgen data into different categories   #
#                                                                                     #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                 #
#                                                                                     #
#           last update: May 20, 2019                                                 #
#                                                                                     #
#######################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import numpy
import getopt
import os.path
import time
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time
import random
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import update_database_suppl    as uds
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- other settings
#
na     = 'na'
cname_list = ['retr_hetg', 'retr_letg', 'insr_hetg', 'insr_letg', 'grat_active', 'grat_inactive']
msid_list  = ['4hposaro', '4hposbro', '4lposaro', '4lposbro',\
              '4mp28av', '4mp28bv', '4mp5av', '4mp5bv']

#----------------------------------------------------------------------------------------
#-- gratgen_categorize_data: separate gratgen data into different categories           --
#----------------------------------------------------------------------------------------

def gratgen_categorize_data():
    """
    separate gratgen data into different categories
    input: none but use <data_dir>/Gratgen/*.fits
    output: <data_dir>/Gratgen_<catogry>/*.fits
    """
#
#--- get the basic information
#
    [udict, ddict, mta_db, mta_cross] = ecf.get_basic_info_dict()

    for msid in msid_list:
        cols = ['time', msid, 'med', 'std', 'min', 'max', 'ylower',\
                'yupper', 'rlower', 'rupper', 'dcount', 'ylimlower',\
                'ylimupper', 'rlimlower', 'rlimupper']

        glim = ecf.get_limit(msid, 0, mta_db, mta_cross)

        for category in cname_list:
            print("Running: " + str(msid) + '<-->'  + category )

            cfile1 = data_dir + 'Gratgen/' + category.capitalize() + '/' + msid + '_data.fits'
            cfile2 = data_dir + 'Gratgen/' + category.capitalize() + '/' + msid + '_short_data.fits'
            cfile3 = data_dir + 'Gratgen/' + category.capitalize() + '/' + msid + '_week_data.fits'

            stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
            tcut1  = 0.0
            tcut2  = Chandra.Time.DateTime(stday).secs - 31622400.0  #--- a year agao
            tcut3  = Chandra.Time.DateTime(stday).secs - 864000.0    #--- 10 days ago

            if os.path.isfile(cfile1):
                tchk = ecf.find_the_last_entry_time(cfile1)
            else:
                tchk = 0

            ifile = house_keeping + category
            data  = mcf.read_data_file(ifile)
            start = []
            stop  = []
            for ent in data:
                atemp = re.split('\s+', ent)
                val1 = float(atemp[0])
                val2 = float(atemp[1])
                if val1 >  tchk:
                    start.append(val1)
                    stop.append(val2)

            if len(start) == 0:
                continue

            for k in range(0, len(start)):
                diff =  stop[k] - start[k]
                if diff < 300:
                    start[k] -= 100
                    stop[k] = start[k] + 300.   

                data = fetch.MSID(msid, start[k], stop[k])

                if k == 0:
                    ttime = list(data.times)
                    tdata = list(data.vals)
                else:
                    ttime = ttime + list(data.times)
                    tdata = tdata + list(data.vals)

            if len(ttime) == 0:
                continue

            stat_out1 = get_stat(ttime, tdata, glim, 86400.0)
            stat_out2 = get_stat(ttime, tdata, glim, 3600.0)
            stat_out3 = get_stat(ttime, tdata, glim, 300.0)

            if tchk > 0:
                ecf.update_fits_file(cfile1, cols, stat_out1, tcut = tcut1)
                ecf.update_fits_file(cfile2, cols, stat_out2, tcut = tcut2)
                ecf.update_fits_file(cfile3, cols, stat_out3, tcut = tcut3)
            else:
                ecf.create_fits_file(cfile1, cols, stat_out1, tcut = tcut1)
                ecf.create_fits_file(cfile2, cols, stat_out2, tcut = tcut2)
                ecf.create_fits_file(cfile3, cols, stat_out3, tcut = tcut3)

#-------------------------------------------------------------------------------------------
#-- get_stat: compute stat for the given data                                             --
#-------------------------------------------------------------------------------------------

def get_stat(ttime, tdata, glim, step):
    """
    compute stat for the given data 
    input:  ttime   --- a list of time data
            tdata   --- a list of data
            glim    --- a lower and upper limit values
    output: wtime   --- a list of time in sec from 1998.1.1
            wdata   --- a list of the  mean of each interval
            wmed    --- a list of the median of each interval
            wstd    --- a list of the std of each interval
            wmin    --- a list of the min of each interval
            wmax    --- a list of the max of each interval
            wyl     --- a list of the rate of yellow lower violation
            wyu     --- a list of the rate of yellow upper violation
            wrl     --- a list of the rate of red lower violation
            wru     --- a list of the rate of red upper violation
            wcnt    --- a list of the total data counts
            wyl     --- a list of the lower yellow limits
            wyu     --- a list of the upper yellow limits
            wrl     --- a list of the lower red limits
            wru     --- a list of the upper red limits
    """

    wtime = []
    wdata = []
    wmed  = []
    wstd  = []
    wmin  = []
    wmax  = []
    wyl   = []
    wyu   = []
    wrl   = []
    wru   = []
    wcnt  = []
    wsave = []

    dtime = numpy.array(ttime)
    ddata = numpy.array(tdata)

    spos  = 0
    chk   = 1
    send  = dtime[spos]

    for k in range(0, len(dtime)):
        if dtime[k] < send:
            chk = 0
        else:
            sdata = ddata[spos:k]
            if len(sdata) < 1:
                continue

            avg   = sdata.mean()
            med   = numpy.median(sdata)
            sig   = sdata.std()
            try:
                amin  = sdata.min()
                amax  = sdata.max()
            except:
                amin  = 0
                amax  = 0
            ftime = dtime[spos + int(0.5 * (k-spos))]
            vlimits = uds.find_violation_range(glim, ftime)
            [yl, yu, rl, ru, tot] = uds.find_violation_rate(sdata, vlimits)
            wtime.append(ftime)
            wdata.append(avg)
            wmed.append(med)
            wstd.append(sig)
            wmin.append(amin)
            wmax.append(amax)
            wyl.append(yl)
            wyu.append(yu)
            wrl.append(rl)
            wru.append(ru)
            wcnt.append(tot)
            wsave.append(vlimits)
            
            spos = k
            send = dtime[k] + step
            chk  = 1
#
#--- check whether there are any left over; if so add it to the data lists
#
    if chk == 0:

        sdata = ddata[spos:k]
        avg   = sdata.mean()
        med   = numpy.median(sdata)
        sig   = sdata.std()
        amin  = sdata.min()
        amax  = sdata.max()
        ftime = dtime[spos + int(0.5 * (k-spos))]
        vlimits = uds.find_violation_range(glim, ftime)
        [yl, yu, rl, ru, tot] = uds.find_violation_rate(sdata, vlimits)
        wtime.append(ftime)
        wdata.append(avg)
        wmed.append(med)
        wstd.append(sig)
        wmin.append(amin)
        wmax.append(amax)
        wyl.append(yl)
        wyu.append(yu)
        wrl.append(rl)
        wru.append(ru)
        wcnt.append(tot)
        wsave.append(vlimits)

    vtemp = [[], [], [], []]
    for k in range(0, len(wsave)):
        for m in range(0, 4):
            vtemp[m].append(wsave[k][m])

    wdata = [wtime, wdata, wmed, wstd, wmin, wmax, wyl, wyu, wrl, wru, wcnt] +  vtemp

    return wdata

#--------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        ltype = sys.argv[1]
    else: 
        ltype = ''

    gratgen_categorize_data()
