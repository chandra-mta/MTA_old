#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################
#                                                                                   #
#       classify_hrc_data.py: separate hrc elec data into hrc i/s active periods    #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               last update: May 22, 2019                                           #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time
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
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- output file tail 
#
hclass   = ['i', 's', 'off']

#-----------------------------------------------------------------------------------
#-- classify_hrc_data: separate hrcelec fits data into hrc i/s active and off period fits files
#-----------------------------------------------------------------------------------

def classify_hrc_data(tail=''):
    """
    separate hrcelec fits data into hrc i/s active and off period fits files
    input:  tail    --- tail of fits file name, either "_week", "_short", or ""
            read from <house_keeping>/sptpast_list etc
                                <data_dir>/Hrcelec/*fits
    output: <data_dir>/Hrecelec_i/*fits
            <data_dir>/Hrecelec_s/*fits
            <data_dir>/Hrecelec_off/*fits

    Note: we assume that hrc i is on when imbpast is some where around 80 - 100 and hrc s is
          around 0. hrc s is on when sptpast is somewhere around 80 - 100 and hrc i is around 0.
          all other periods are assumed to be hrc in non-active mode.
    """
#
#--- update hrc i/s active periond table data
#
    get_hrc_condition()
#
#--- read the active period table (and off period table)
#
    hperiods = read_hrc_period(tail)
#
#--- get the full period data
#
    cmd  = 'ls ' + data_dir + 'Hrcveto/*' + tail + '_data.fits* > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)
#
#--- create the separate fits files accroding to the active periods
#
    for fits in data:

        if tail == '':
            mc1 = re.search('short', fits)
            mc2 = re.search('week',  fits)
            if (mc1 is not None) or (mc2 is not None):
                continue

        print("FITS:" + str(fits))

        for k in range(0, 3):
            htype = hclass[k]
            start = hperiods[k][0]
            stop  = hperiods[k][1]
            
            select_data_period(fits, start, stop, htype)

#-----------------------------------------------------------------------------------
#-- select_data_period: select the data under the periods and create a new fits file 
#-----------------------------------------------------------------------------------

def select_data_period(fits, start, stop, htype):
    """
    select the data under the periods and create a new fits file
    input:  fits    --- original fits file name
            start   --- a list of starting time of the period to be selected
            stop    --- a list of stopping time of the period to be selected
            htype   --- the tail of the output file (i, s, or off)
    output: <data_dir>/Hrcelec_<htype>/<fits file name>
    """
    flist = pyfits.open(fits)
    fdata = flist[1].data

    mlen  = len(start)
#
#--- select data in each period
#
    save = ''
    for k in range(0, mlen):
        mask = fdata['time'] >= start[k]
        out  = fdata[mask]
        mask = out['time']   < stop[k]
        out2 = out[mask]
#
#--- concatinate the data to the arrays
#
        if k == 0:
            save = out2
        else:
            save = numpy.concatenate((save, out2), axis=0)
#
#--- write out the data into a fits file
#
    if str(save) == '':              #--- occasionally there is no data (e.g. weekly has not been filled)
        return False

    hdu = pyfits.BinTableHDU(data=save)

    rname   = 'Hrcveto_' + htype
    outname = fits.replace('Hrcveto', rname)

    mcf.rm_files(outname)
    hdu.writeto(outname)

    flist.close()

#-----------------------------------------------------------------------------------
#- read_hrc_period: read each active period data file                             --
#-----------------------------------------------------------------------------------

def read_hrc_period(tail):
    """
    read each active period data file
    input:  tail    --- data type either "_week", "_short", or "" 
            read from <house_keeping> directory
    output: hrci/hrcs/hoff  --- time period data list[hrci, hrcs, hoff]
                                each entry has: [[a list of starting time], [list of stopping time]]
    """
#
#--- find today's date
#
    stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
#
#--- find 10 days ago for week data and 380 days ago for the short data. 
#--- otherwise choose the entiere period
#
    if tail == '_week' or tail == 'week':
        cut  = Chandra.Time.DateTime(stday).secs - 86400.0 * 10

    elif tail == '_short' or tail == 'short':
        cut  = Chandra.Time.DateTime(stday).secs - 86400.0 * 380
    else:
        cut  = 68169599.0                       #--- 2000:060:00:00:00

    infile = house_keeping + 'imbpast_list'
    hrci   = separate_data(infile, cut)

    infile = house_keeping + 'sptpast_list'
    hrcs   = separate_data(infile, cut)

    infile = house_keeping + 'hrc_off_list'
    hoff   = separate_data(infile, cut)

    return [hrci, hrcs, hoff]

#-----------------------------------------------------------------------------------
#-- separate_data: separate the data into start and stop time lists               --
#-----------------------------------------------------------------------------------

def separate_data(infile, cut):
    """
    separate the data into start and stop time lists
    input:  infile  --- a file name
            cut     --- the cut time which we need to examine
    output: a list of lists of starting and stopping time
    """
    data   = mcf.read_data_file(infile)
    start  = []
    stop   = []
    for ent in data:
        atemp = re.split(':', ent)
        stime = int(float(atemp[0]))
        if stime > cut:
            start.append(stime)
            stop.append(int(float(atemp[1])))

    return [start, stop]

#-----------------------------------------------------------------------------------
#-- get_hrc_condition: find out hrc i/s active perionds and update the lists      --
#-----------------------------------------------------------------------------------

def get_hrc_condition():
    """
    find out hrc i/s active perionds and update the lists
    input:  none, but read from achieve
    output: <house_keeping>/tscpos_list     #--- location of sim
            <house_keeping>/sptpast_list    #--- hrc s active periods
            <house_keeping>/imbpast_list    #--- hrc i active periods
            <house_keeping>/hrc_off_list    #--- hrc is inactive 
    """
    tsfile = house_keeping + 'tscpos_list'
    spfile = house_keeping + 'sptpast_list'
    imfile = house_keeping + 'imbpast_list'
#
#--- find the last entry time
#
    try:
        tstart = 0
        for infile in (tsfile, spfile, imfile):
            data   = mcf.read_data_file(infile)
            astart = int(float((re.split(':', data[-1])[0])))
            astart = float(astart)
            if astart > tstart:
                tstart = astart

    except:
        tstart = 68169599.0         #--- begining of data set: 2000:060:00:00:00
#
#--- set stopping time to yesterday
#
    stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
    tstop = Chandra.Time.DateTime(stday).secs - 86400.0

    [tsstart, tsstop] = check_condition('3tscpos',  tstart, tstop, 0.0)
    [spstart, spstop] = check_condition('2sptpast', tstart, tstop, 30, achk=1)
    [imstart, imstop] = check_condition('2imbpast', tstart, tstop, 30, achk=1)
#
#--- write out the results
#
    chk = 0
    if len(tsstart) > 0:
        append_data(tsfile, tsstart, tsstop)
        chk += 1
    if len(spstart) > 0:
        append_data(spfile, spstart, spstop)
        chk += 1
    if len(imstart) > 0:
        append_data(imfile, imstart, imstop)
        chk += 1
#
#--- upate off_time list
#
    if chk > 0:
        divide_hrc_data()

#-----------------------------------------------------------------------------------
#-- check_condition: find the periods of the time when the condition is met       --
#-----------------------------------------------------------------------------------

def check_condition(msid, tstart, tstop, condition, achk=0):
    """
    find the periods of the time when the condition is met
    input:  msid        --- msid
            tstart      --- starting time in seconds from 1998.1.1
            tstop       --- stopping time in seconds from 1998.1.1
            condition   --- condition value. if the value is larger than this
                            it is "ON" period
            achk        --- indicator of whether we need data cleaning; achk=1: yes
    output: c_start     --- a list of starting time of the active period
            c_stop      --- a list of stopping time of the active period
    """
    #print(msid + '<-->' + str(tstart) + '<-->' + str(tstop))

    out    = fetch.MSID(msid, tstart, tstop)
    cptime = out.times
    cvals  = out.vals
#
#--- if voltage cases (achk ==1), use only data in the ceratin range
#
    if achk == 1:
        atime   = []
        avals   = []
        for k in range(0, len(cvals)):
            if cvals[k] > 200:
                continue

            if cvals[k] > 5 and cvals[k] < 80:
                continue

            atime.append(cptime[k])
            avals.append(cvals[k])
#
#--- non voltage case
#
    else:
        atime = cptime
        avals = cvals
#
#--- find start and stop time of the period where the condtion is met
#--- if the value is larger than condition, it is "ON".
#
    c_start = []
    c_stop  = []
    chk     = 0
    for k in range(0, len(atime)):

        if chk == 0 and  avals[k] > condition:
            c_start.append(atime[k])
            chk = 1

        elif chk == 1 and avals[k] < condition:
            c_stop.append(atime[k])
            chk = 0

        else:
            continue
#
#--- if the period is not closed, use the last entry to close it
#
    if chk == 1:
            c_stop.append(atime[-1])

    return [c_start, c_stop]

#-----------------------------------------------------------------------------------
#-- append_data: clean up the data and update the data files                      --
#-----------------------------------------------------------------------------------

def append_data(infile, tstart, tstop):
    """
    clean up the data and update the data files
    input:  infile  --- output file name
            tstart  --- a list of starting time
            tstop   --- a list of stopping time
    output: <house_keeping>/tscpos_list     #--- location of sim
            <house_keeping>/sptpast_list    #--- hrc s active periods
            <house_keeping>/imbpast_list    #--- hrc i active periods
    """
    nstart = [tstart[0]]
    nstop  = []
    lcnt   = len(tstart)
#
#--- check the time and the gap is smaller than 10 mins, ignoure
#
    for k in range(0, lcnt):
        if (k+1) >= lcnt:
            break
        diff   = tstart[k+1] - tstop[k]
        if diff > 600:
            nstop.append(tstop[k])
            if (k+1) >=  lcnt:
                break
            nstart.append(tstart[k+1])

    if len(nstart) > len(nstop):
        try:
            nstop.append(nstop[-1])
        except:
            pass
#
#--- if the period is shorter than 5 min, ignore
#
    data  = mcf.read_data_file(infile)

    for k in range(0, len(nstart)):
        try:
            diff = int(nstop[k] - nstart[k])
        except:
            diff = 0
        if diff < 300:
            continue

        line = str(int(nstart[k])) + ':' + str(int(nstop[k])) + ':' + str(diff) 
        data.append(line)

    dlist = []
    adict = {}
    for ent in data:
        if ent == '':
            continue
        atemp = re.split(':',ent)
        val   = int(float(atemp[0]))
        dlist.append(val)
        adict[val] = ent

    dlist  = sorted(dlist, key=int)

    cleaned = []
    try:
        test = adict[dlist[0]]
    except:
        test = ''
    if test != '':
        for ent in dlist:
            val = adict[ent]
            if val != test:
                cleaned.append(val)
                test = val
            else:
                continue
    
        sline = ''
        for line in cleaned:
            sline = sline + line + '\n'

        with open(infile, 'w') as fo:
            fo.write(sline)

#-----------------------------------------------------------------------------------
#-- divide_hrc_data: find hrc is in  non-active period                            --
#-----------------------------------------------------------------------------------

def divide_hrc_data():
    """
    find hrc is in non-active period
    input:  none, but read from <house_keeping>/imbpast_list <house_keeping>/sptpast_list
    output: <house_keeping>/hrc_off_list
    """
#
#--- read hrc i active period
#
    ifile1 = house_keeping + 'imbpast_list'
    data   = mcf.read_data_file(ifile1)
    time_list = []
    time_dict = {}
    hrci_list = []
    hrci_dict = {}
    for ent in data:
        atemp = re.split(':', ent)
        val1 = int(float(atemp[0]))
        val2 = int(float(atemp[1]))
        time_list.append(val1)
        hrci_list.append(val1)
        hrci_dict[val1] = val2
        time_dict[val1] = val2
#
#--- read hrc s active period
#
    ifile2 = house_keeping + 'sptpast_list'
    data   = mcf.read_data_file(ifile2)
    hrcs_list = []
    hrcs_dict = {}
    for ent in data:
        atemp = re.split(':', ent)
        val1 = int(float(atemp[0]))
        val2 = int(float(atemp[1]))
        time_list.append(val1)
        hrcs_list.append(val1)
        hrcs_dict[val1] = val2
        time_dict[val1] = val2

    time_list.sort()
#
#--- find the period either hrc i or hrc s are on
#
    tlen = len(time_list)
    off_start = []
    off_stop  = []
    for k in range(0, tlen):
        off_start.append(time_dict[time_list[k]])
        if (k + 1) >= tlen:
            stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
            tstop = Chandra.Time.DateTime(stday).secs - 86400.0
            off_stop.append(tstop)
        else:
            off_stop.append(time_list[k+1])
#
#--- print out the results
#
    line = ''
    for k in range(0, len(off_start)):
        diff = int(off_stop[k] - off_start[k])
        if diff < 300:
            continue

        line = line + str(int(off_start[k])) + ':' 
        line = line + str(int(off_stop[k]))  + ':' + str(diff) +  '\n'

    infile = imfile = house_keeping + 'hrc_off_list'
    with open(infile, 'w') as fo:
        fo.write(line)

#-----------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- provide the tail indicator: week, short, or full
#
    if len(sys.argv) > 1:
        tail = sys.argv[1].strip()

        if tail == 'full':
            classify_hrc_data()

        else:
            mc = re.search('_', tail)
            if mc is None:
                tail = '_' + tail

            classify_hrc_data(tail)
#
#--- if the tail is not provided, run all
#
    else:
        for tail in ('', '_short', '_week'):
            classify_hrc_data(tail)

