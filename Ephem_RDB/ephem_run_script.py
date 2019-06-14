#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#############################################################################
#                                                                           #
#       ephem_run_script.py: update dephem.rdb file                         #
#                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           last update: Jun 13, 2019                                       #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import time
import Chandra.Time
import unittest
#
#--- read data paths
#
path = '/data/mta/Script/Ephem/house_keeping/dir_list_py'

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
sys.path.append(mta_dir)
#
#--- import several functions
#
import convert_ephem_data   as ced  #---- convert binary data into ascii data file
import cocochan             as cch  #---- convert Chandra ECI linear coords to GSE, GSE coords
import mta_common_functions as mcf  #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a few paths
#
kp_file  = '/data/mta4/proj/rac/ops/KP/k_index_data'

#-----------------------------------------------------------------------------------
#-- update_dephem_data: the main script to update dephem.rdb file                ---
#-----------------------------------------------------------------------------------

def update_dephem_data():
    """
    the main script to update dephem.rdb file
    input:  none
    output: <ds_rep>/dephem.rdb)
    """
#
#--- find currently available data from GOT site
#
    cdata = find_available_deph_data()
#
#--- check already processed data
#
    last = find_the_last_entry()
#
#--- compare them and process the new eph data
#
    for ent in cdata:
        atemp = re.split('\/', ent)
        btemp = re.split('.EPH', atemp[len(atemp)-1])
        ctemp = re.split('DE', btemp[0])
        try:
            time  = int(ctemp[1])
        except:
            continue

        if time <= last:
            continue
        else:
#
#---- using lephem.pro, create an ascii file
#
            chk = run_lephem(ent, time)
            if chk == 0:
                continue                #---- the process failed; skip the rest
#
#--- using kplookup, put soloar wind information
#
            chk = run_kplookup(time)
            if chk == 0:
                continue                #--- it seems no data file created, skip
#
#---- update <ds_rep>/dephem.rdb with the new info
#
            update_rdb(time)

#-----------------------------------------------------------------------------------
#-- find_available_deph_data: create a list of potential new data file name       --
#-----------------------------------------------------------------------------------

def find_available_deph_data():
    """
    create a list of potential new data file name
    input:  none, but read from /dsops/GOT/aux/DEPH.dir/
    output: cdata   --- a list of the data file names
    """
#
#--- find current time
#
    today = time.strftime('%Y:%j', time.gmtime())
    atemp = re.split(':', today)
    year  = int(atemp[0])
    ydate = int(atemp[1])

    syear = str(year)
    tyear = syear[2] + syear[3]
#
#--- first 20 days of the year, we also check the last year input data
#
    if ydate < 20:
        lyear  = year -1
        slyear = str(lyear)
        ltyear = slyear[2] + slyear[3]

        cmd = 'ls /dsops/GOT/aux/DEPH.dir/DE' + ltyear + '*.EPH >  ' + zspace
        os.system(cmd)
        cmd = 'ls /dsops/GOT/aux/DEPH.dir/DE' + tyear  + '*.EPH >> ' + zspace
        try:
            os.system(cmd)
        except:
            pass
    else:
        cmd = 'ls /dsops/GOT/aux/DEPH.dir/DE' + tyear  + '*.EPH >  ' + zspace
        try:
            os.system(cmd)
        except:
            pass
    try:
        cdata = mcf.read_data_file(zspace, remove=1)
    except:
        cdata = []
        mcf.rm_files(zspace)

    return cdata

#-------------------------------------------------------------------------------------------
#-- find_the_last_entry: find the time stamp of the last processed data                   --
#-------------------------------------------------------------------------------------------

def find_the_last_entry():
    """
    find the time stamp of the last processed data
    input:  none, but read from /data/mta/Script/Ephem/EPH_Data/*dat0
    output: last    --- the time stamp of the last data file proccessed: <yy><ydate>
    """
    cmd = 'ls ' + eph_dir + 'DE*.EPH.dat00 > ' + zspace
    os.system(cmd)

    pdata = mcf.read_data_file(zspace, remove=1)

    last  = pdata[len(pdata) -1]
    atemp = re.split('DE', last)
    btemp = re.split('.EPH', atemp[1])
    last  = int(btemp[0])

    return last

#-------------------------------------------------------------------------------------------
#-- run_lephem: run idl script lephem.pro which convert the data into ascii data         ---
#-------------------------------------------------------------------------------------------

def run_lephem(fname, time):
    """
    run idl script lephem.pro which convert the data into ascii data
    input:  fname   --- the name of the input file: DE<time>.EPH
            time    --- time stamp of the file copied
    output: ascii data file -- DE<time>.EPH.dat0
    """
    cmd = 'cp ' + fname + ' ' +  eph_dir + '.'
    os.system(cmd)

    cname = 'DE' + str(time) + '.EPH'
    
    try:
        ced.convert_ephem_data(cname)
        return 1
    except:
        return 0

#-------------------------------------------------------------------------------------------
#-- run_kplookup: append kp value to DE<time>.EPH.dat0 and create DE<time>.EPH.dat0.0    ---
#-------------------------------------------------------------------------------------------

def run_kplookup(time):
    """
    append kp value to DE<time>.EPH.dat0 and create DE<time>.EPH.dat0.0
    input:  time    --- time in the format of <yy><ydate>
    output: DE<time>.EPH.dat00 updated for the soloar wind influence
    """
    ifile = eph_dir + 'DE' + str(time)  +  '.EPH.dat0'
#
#--- there is a data file; update with kp value
#
    if os.path.isfile(ifile):
        kplookup(ifile)
        return 1
#
#--- there is no data file; skip 
#
    else:
        return 0

#-----------------------------------------------------------------------------------
#-- kplookup: look up kp value and append to the data                            ---
#-----------------------------------------------------------------------------------

def kplookup(ifile):
    """
    look up kp value and append to the data
    input:  ifile   --- input data file name
    output: ofile   --- output data file name; <ifile>0
    """
#
#--- read data and separate into column data; stime is Chandra time
#
    data  = mcf.read_data_file(ifile)
    cdata = mcf.separate_data_to_arrays(data)
#
#--- make sure that the data is accending order in time
#
    stime = numpy.array(cdata[0])
    ndata = numpy.array(data)
    ind   = numpy.argsort(stime)
    stime = list(stime[ind])
    ndata = list(ndata[ind])
#
#--- read the current kp data
#
    kpdata      = mcf.read_data_file(kp_file)
    [csec, ckp] = mcf.separate_data_to_arrays(kpdata)
#
#--- compare them and match kp to the data
#
    dlen  = len(ndata)
    klen  = len(ckp)
    line  = ''
    mv    = 1
    for k in range(0, dlen):
        for m in range(mv, klen):
            if (stime[k] >= csec[m-1]) and (stime[k] < csec[m]):
                line = line + ndata[k] + '\t' + "%1.2f" % float(ckp[m-1]) + '\n'
                mv += 1
                break

            elif stime[k] < csec[m-1]:
                break   

            elif stime[k] > csec[m]:
                mv += 1
                continue
#
#--- write out the ifile with matched kp value (a file name has an extra "0" at the end)
#
    ofile = ifile + '0'
    with open(ofile, 'w') as fo:
        fo.write(line)

#-------------------------------------------------------------------------------------------
#-- update_rdb: update dephem.rdb file                                                   ---
#-------------------------------------------------------------------------------------------

def update_rdb(time):
    """
    update dephem.rdb file
    input:  time    --- time in format of <yy><ydate>
            read from <rdb_dir>/dephem.rdb
    output: updated <rdb_dir>/dephem.rdb
    """
#
#---input file name
#
    ifile = eph_dir + 'DE' + str(time) + '.EPH.dat00'
#
#--- create data with the format of: 
#---        time    ALT ECIX    ECIY    ECIZ    GSMX    GSMY    GSMZ    CRMREG
#
    oline = cch.cocochan(ifile)
    try:
        atemp = re.split('\s+', oline)
        start = float(atemp[0])
    except:
        return 'NA'
#
#--- read the rdb file (dephem.rdb)
#
    rdb_file  = ds_rep + 'dephem.rdb'
    rdb       = mcf.read_data_file(rdb_file)
#
#---- extract the data from dephem.rdb up to the starting time of the new data
#
    rline = ''
    for ent in rdb:
        atemp = re.split('\s+', ent)

        try:
            rtime = float(atemp[0])
        except:
            continue 

        if rtime < stime:
            rline = ent + '\n'
        else:
            break
#
#--- update dephem.rdb
#
    line = rline + oline

    with  open(rdb_file, 'w') as fo:
        fo.write(line)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_dephem_data()
