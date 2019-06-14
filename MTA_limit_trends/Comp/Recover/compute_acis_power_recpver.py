#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#           compute_acis_power.py: compute acis power and fill data                 #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 20, 2019                                               #
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
import random

#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts3.6/house_keeping/dir_list'
with open(path, 'r') as:
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
#
#--- set a temporary file name
#
rtail  = int(time.time() * random*random())
zspace = '/tmp/zspace' + str(rtail)

data_dir = './Outdir/'

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
#--- create msid <---> unit dictionary
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read mta database
#
    mta_db = read_mta_database()

    group = 'Compacispwr'

    for msid in ['1dppwra', '1dppwrb']:
#
#--- get limit data table for the msid
#
        try:
            tchk  = convert_unit_indicator(udict[msid])
        except:
            tchk  = 0

        glim  = get_limit_for_acis_power(msid, mta_db)
#
#--- update database
#
        update_database(msid, group,  glim)

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
#-- read_mta_database: read the mta limit database                                        --
#-------------------------------------------------------------------------------------------

def read_mta_database():
    """
    read the mta limit database
    input:  none, but read from /data/mta4/MTA/data/op_limits/op_limits.db
    output: mta_db  --- dictionary of msid <--> a list of lists of limits
                        the inner list is [start, stop, yl, yu, rl, ru]
    """

    tmin = 0
    tmax = 3218831995
    f    = open('/data/mta4/MTA/data/op_limits/op_limits.db', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    mta_db = {}
    prev   = ''
    save   = []
    for ent in data:
        if len(ent) == 0:
            continue
        if ent[0] == '#':
            continue

        atemp = re.split('\s+', ent)
        msid  = atemp[0].lower()

        try:
            out  = mta_db[msid]
            yl   = float(atemp[1])
            yr   = float(atemp[2])
            rl   = float(atemp[3])
            ru   = float(atemp[4])
            ts   = float(atemp[5])
            olim = [ts, tmax, yl, yr, rl, ru]
            out[-1][1] = ts
            out.append(olim)
            mta_db[msid] = out
        except:
            yl   = float(atemp[1])
            yr   = float(atemp[2])
            rl   = float(atemp[3])
            ru   = float(atemp[4])
            ts   = float(atemp[5])
            olim = [ts, tmax, yl, yr, rl, ru]
            out  = [olim]
            mta_db[msid] = out

    return mta_db

#-------------------------------------------------------------------------------------------
#-- update_database: update/create fits data files of msid                                --
#-------------------------------------------------------------------------------------------

def update_database(msid, group, glim, pstart=0, pstop=0, step=3600.0):
    """
    update/create fits data files of msid
    input:  msid    --- msid
            pstart  --- starting time in seconds from 1998.1.1; defulat = 0 (find from the data)
            pstop   --- stopping time in seconds from 1998.1.1; defulat = 0 (find from the data)
            step    --- time interval of the short time data set:default 3600.0
    output: <msid>_data.fits, <msid>_short_data.fits
    """

    mon   = ['001', '032', '060', '091', '121', '152', '182', '213', '244', '274', '305', '335']

    cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower', 'yupper', 'rlower', 'rupper', 'dcount',\
             'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

    out_dir = data_dir + group + '/'
#
#--- make sure that the sub directory exists
#
    if not os.path.isdir(out_dir):
        cmd = 'mkdir ' + out_dir
        os.system(cmd)

    fits  = out_dir + msid + '_data.fits'
    fits2 = out_dir + msid + '_short_data.fits'
    fits3 = out_dir + msid + '_week_data.fits'
#
#-- if the starting time and stopping time are given, use them. 
#-- otherwise find from the data for the starting time and today's date -1 for the stopping time
#
    if pstart == 0:
        stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
        stday = Chandra.Time.DateTime(stday).secs - 86400.0     #--- set the ending to the day before
    else:
        stday = pstop 

    if pstart == 0:
        start = 48988799                    #--- 1999:203:00:00:00
        stop  = stday
    else:
        start = pstart
        stop  = pstop

    start = 48988799
    stop  = 55036799
    [week_p, short_p, long_p] = get_data_from_archive(msid, start, stop, glim, step=300)
    create_fits_file(fits3, cols, week_p)

    for year in range(1999, 2018):
        lyear = year
        for month in range(1, 13):
            if year == 1999 and month < 10:
                continue
            elif year == 2017 and month > 11:
                break

            lstart = str(year) + ':'  + mon[month-1] + ':00:00:00'
            start = Chandra.Time.DateTime(lstart).secs
            test  = month + 1
            if test > 12:
                lyear += 1
                month = 0

            lstop  = str(lyear) + ':'  + mon[month] + ':00:00:00'
            stop  = Chandra.Time.DateTime(lstop).secs

            print("Span: " + str(start) + '<-->' + str(stop) + ":  " + lstart + '<-->' + lstop)

            [week_p, short_p, long_p] = get_data_from_archive(msid, start, stop, glim, step=300)
            update_fits_file(fits3, cols, week_p)

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def cut_the_data(data, cut):

    pos = 0
    for k in range(0, len(data[0])):
        if data[0][k] < cut:
            continue
        else:
            pos = k
            break

    save = []
    for k in range(0, len(data)):
        save.append(data[k][pos:])

    return save


#-------------------------------------------------------------------------------------------
#-- get_data_from_archive: extract data from the archive and compute the stats           ---
#-------------------------------------------------------------------------------------------

def get_data_from_archive(msid, start, stop, glim, step = 3600.0):
    """
    extract data from the archive and compute the stats
    input:  msid    --- msid of the data
            start   --- start time
            stop    --- stop time
            glim    --- a list of limit tables
            step    --- interval of the data. defalut: 3600 sec
    output: a list of two lists which contain:
            week_p:
                wtime   --- a list of time in sec from 1998.1.1
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
            short_p:
                btime   --- a list of time in sec from 1998.1.1
                bdata   --- a list of the  mean of each interval
                bmed    --- a list of the median of each interval
                bstd    --- a list of the std of each interval
                bmin    --- a list of the min of each interval
                bmax    --- a list of the max of each interval
                byl     --- a list of the rate of yellow lower violation
                byu     --- a list of the rate of yellow upper violation
                brl     --- a list of the rate of red lower violation
                bru     --- a list of the rate of red upper violation
                bcnt    --- a list of the total data counts
                byl     --- a list of the lower yellow limits
                byu     --- a list of the upper yellow limits
                brl     --- a list of the lower red limits
                bru     --- a list of the upper red limits
            long_p:
                    --- all in one element list form
                ftime   --- a mid time of the entier extracted data period
                fdata   --- the mean of the entire extracted data 
                fstd    --- the std of the entire extracted data
                fmin    --- the min of the entire extracte data
                fmax    --- the max of the entire extracte data
                ylow    --- the reate of yellow lower violation
                yupper  --- the reate of yellow upper violation
                rlow    --- the reate of red lower violation
                rupper  --- the reate of red upper violation
                tcnt    --- the total counts of the data
                ylow    --- the lower yellow limit
                yup     --- the upper yellow limit
                rlow    --- the lower red limit
                rup     --- the upper red limit
    """
#
#--- week long data 5 min step
#
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
    step2 = 300
    wstart= stop - 86400.0 * 14.0           #---- two weeks ago

#
#--- one year long data 1 hr step
#
    btime = []
    bdata = []
    bmed  = []
    bstd  = []
    bmin  = []
    bmax  = []
    byl   = []
    byu   = []
    brl   = []
    bru   = []
    bcnt  = []

    wsave = []
    vsave = []
#
#--- extract data from archive
#
    if msid == '1dppwra':
        msid_v = '1dp28avo'
        msid_a = '1dpicacu'
    else:
        msid_v = '1dp28bvo'
        msid_a = '1dpicbcu'

    try:
        out     = fetch.MSID(msid_v, start, stop)
        tdata_v   = out.vals
        ttime   = out.times
        out     = fetch.MSID(msid_a, start, stop)
        tdata_a = out.vals

        tdata   = tdata_v * tdata_a

        data    = []
        dtime   = []
#
#--- if the data is not given, the database desplay it as -999.999 (or similar); so drop them
#
        for k in range(0, len(tdata)):

            try:
                test = int(float(tdata[k]))
            except:
                continue

            if int(abs(tdata[k])) == 999:
                continue

            data.append(tdata[k])
            dtime.append(ttime[k])

        data  = numpy.array(data)
        dtime = numpy.array(dtime)
#
#--- get stat for the entire period
#
        ftime   = dtime.mean()
        fdata   = data.mean()
        fmed    = numpy.median(data)
        fstd    = data.std()
        fmin    = data.min()
        fmax    = data.max()
#
#--- find the violation limits of that time
#
        vlimits = find_violation_range(glim, ftime)
#
#--- get the violation rate of the entier period
#
        [ylow, yupper, rlow, rupper, tcnt] = find_violation_rate(data, vlimits)
#
#--- if asked, devide the data into a smaller period (step size)
#
        if step != 0:
            spos  = 0
            spos2 = 0
            chk   = 1
            chk2  = 2
            send  = dtime[spos]  + step
            send2 = dtime[spos2] + step2

            for k in range(0, len(dtime)):

                if dtime[k] > wstart:
                    if dtime[k] < send2:
                        chk2 = 0
                    else:
                        sdata = data[spos2:k]
                        avg   = sdata.mean()
                        med   = numpy.median(sdata)
                        sig   = sdata.std()
                        amin  = sdata.min()
                        amax  = sdata.max()
                        ftime = dtime[spos2 + int(0.5 * (k-spos2))]
                        vlimits = find_violation_range(glim, ftime)
                        [yl, yu, rl, ru, tot] = find_violation_rate(sdata, vlimits)
     
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
     
                        spos2 = k
                        send2 = dtime[k] + step2
                        chk2  = 1
                else:
                    send2 = dtime[spos2] + step2



                if dtime[k] < send:
                    chk = 0
                else:
                    rdata = data[spos:k]
                    avg   = rdata.mean()
                    med   = numpy.median(rdata)
                    sig   = rdata.std()
                    amin  = rdata.min()
                    amax  = rdata.max()
                    ftime = dtime[spos + int(0.5 * (k-spos))]
                    vlimits = find_violation_range(glim, ftime)
                    [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)
    
                        
                    btime.append(ftime)
                    bdata.append(avg)
                    bmed.append(med)
                    bstd.append(sig)
                    bmin.append(amin)
                    bmax.append(amax)
                    byl.append(yl)
                    byu.append(yu)
                    brl.append(rl)
                    bru.append(ru)
                    bcnt.append(tot)
                    vsave.append(vlimits)
    
                    spos = k
                    send = dtime[k] + step
                    chk  = 1
#
#--- check whether there are any left over; if so add it to the data lists
#
            if chk2 == 0:
                rdata = data[spos2:k]
                avg   = rdata.mean()
                med   = numpy.median(rdata)
                sig   = rdata.std()
                amin  = rdata.min()
                amax  = rdata.max()
                ftime = dtime[spos2 + int(0.5 * (k-spos2))]
                vlimits = find_violation_range(glim, ftime)
                [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)
    
                wtime.append(dtime[spos2 + int(0.5 * (k-spos2))])
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

            if chk == 0:
                rdata = data[spos:k]
                avg   = rdata.mean()
                med   = numpy.median(rdata)
                sig   = rdata.std()
                amin  = rdata.min()
                amax  = rdata.max()
                ftime = dtime[spos + int(0.5 * (k-spos))]
                vlimits = find_violation_range(glim, ftime)
                [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)
    
                btime.append(dtime[spos + int(0.5 * (k-spos))])
                bdata.append(avg)
                bmed.append(med)
                bstd.append(sig)
                bmin.append(amin)
                bmax.append(amax)
                byl.append(yl)
                byu.append(yu)
                brl.append(rl)
                bru.append(ru)
                bcnt.append(tot)
                vsave.append(vlimits)
    except:
        ftime = 0
        fdata = 0
        fmed  = 0
        fstd  = 0
        fmin  = 0
        fmax  = 0
        ylow  = 0
        yupper= 0
        rlow  = 0
        rupper= 0
        tcnt  = 0

        vlimits = [-9.0e9, -9.0e9, 9.0e9, 9.0e9]

    week_p  = [wtime, wdata, wmed, wstd, wmin, wmax, wyl, wyu, wrl, wru, wcnt]
    short_p = [btime, bdata, bmed, bstd, bmin, bmax, byl, byu, brl, bru, bcnt]
#
#--- adding limits to the table
#
    vtemp   = [[], [], [], []]
    for k in range(0, len(wsave)):
        for m in range(0, 4):
            vtemp[m].append(wsave[k][m])
    week_p = week_p + vtemp
#
    vtemp   = [[], [], [], []]
    for k in range(0, len(vsave)):
        for m in range(0, 4):
            vtemp[m].append(vsave[k][m])
    short_p = short_p + vtemp

    long_p  = [[ftime], [fdata], [fmed], [fstd], [fmin], [fmax]]
    long_p  = long_p + [[ylow], [yupper], [rlow], [rupper], [tcnt]]
    long_p  = long_p + [[vlimits[0]], [vlimits[1]], [vlimits[2]], [vlimits[3]]]

    return [week_p, short_p, long_p]


#-------------------------------------------------------------------------------------------
#-- update_fits_file: update fits file                                                    --
#-------------------------------------------------------------------------------------------

def update_fits_file(fits, cols, cdata):
    """
    update fits file
    input:  fits    --- fits file name
            cols    --- a list of column names
            cdata   --- a list of lists of data values
    output: updated fits file
    """

    f     = pyfits.open(fits)
    data  = f[1].data
    f.close()

    udata= []
    for k in range(0, len(cols)):
        nlist   = list(data[cols[k]]) + cdata[k]
        udata.append(nlist)

    mcf.rm_files(fits)
    create_fits_file(fits, cols, udata)

#-------------------------------------------------------------------------------------------
#-- create_fits_file: create a new fits file for a given data set                         --
#-------------------------------------------------------------------------------------------

def create_fits_file(fits, cols, cdata):
    """
    create a new fits file for a given data set
    input:  fits    --- fits file name
            cols    --- a list of column names
            cdata   --- a list of lists of data values
    output: newly created fits file "fits"
    """
    
    #cdata = remove_duplicate(cdata)

    dlist = []
    for k in range(0, len(cols)):
        aent = numpy.array(cdata[k])
        dcol = pyfits.Column(name=cols[k], format='E', array=aent)
        dlist.append(dcol)

    dcols = pyfits.ColDefs(dlist)
    tbhdu = pyfits.BinTableHDU.from_columns(dcols)

    mcf.rm_files(fits)
    tbhdu.writeto(fits)

#-------------------------------------------------------------------------------------------
#-- remove_duplicate: remove duplicated entry by time (the first entry)                   --
#-------------------------------------------------------------------------------------------

def remove_duplicate(cdata):
    """
    remove duplicated entry by time (the first entry)
    input:  cdata   --- a list of lists; the first entry must be time stamp
    output: ndat    --- a cealn list of lists
    """
    clen  = len(cdata)          #--- the numbers of the lists in the list
    dlen  = len(cdata[0])       #--- the numbers of elements in each list
    tdict = {}
    tlist = []
#
#--- make a dictionary as time as a key
#
    for k in range(0, dlen):
        tdat = []
        for m in range(0, clen):
            tdat.append(cdata[m][k])

        tdict[cdata[0][k]] = tdat
        tlist.append(cdata[0][k])
#
#--- select the uniqe time stamps
#
    tset  = set(tlist)
    tlist = list(tset)
    tlist.sort()
#
#--- create a uniqu data set
#
    ndata = []
    for m in range(0, clen):
        ndata.append([])

    for ent in tlist:
        out = tdict[ent]
        for  m in range(0, clen):
            ndata[m].append(out[m])

    return ndata

#-------------------------------------------------------------------------------------------
#-- remove_old_data: remove the data older the cut time                                   --
#-------------------------------------------------------------------------------------------

def remove_old_data(fits, cols, cut):
    """
    remove the data older the cut time
    input:  fits    --- fits file name
            cols    --- a list of column names
            cut     --- cut time in seconds from 1998.1.1
    output: updated fits file
    """

    f     = pyfits.open(fits)
    data  = f[1].data
    f.close()
#
#--- find where the cut time
#
    pos   = 0
    dtime = list(data['time'])
    for k in range(0, len(dtime)):
        if dtime[k] >= cut:
            pos = k
            break
#
#--- remove the data before the cut time
#
    udata = []
    for k in range(0, len(cols)):
        udata.append(list(data[cols[k]][pos:]))

    mcf.rm_files(fits)
    create_fits_file(fits, cols, udata)


#-------------------------------------------------------------------------------------------
#-- find_the_last_entry_time: find the last logged time                                   --
#-------------------------------------------------------------------------------------------

def find_the_last_entry_time(fits):
    """
    find the last logged time
    input:  fits    --- fits file name
    output: ctime   --- the last logged time
    """

    f = pyfits.open(fits)
    data = f[1].data
    f.close()

    ctime = numpy.max(data['time']) 

    return ctime

#-------------------------------------------------------------------------------------------
#-- find_violation_range: set violation range                                             --
#-------------------------------------------------------------------------------------------

def find_violation_range(glim, time):
    """
    set violation range
    input:  glim    --- a list of lists of violation set [start, stop, yl, yu, rl, ru]
            time    --- time of the violation check
    output: vlimit  --- a four element list of [yl, yu, rl, ru]
    """

    vlimit = [-9.0e9, -9.0e9, 9.0e9, 9.0e9]

    for lim_set in glim:
        start = float(lim_set[0])
        stop  = float(lim_set[1])
        if (time >= start) and (time < stop):
            vlimit = [lim_set[2], lim_set[3], lim_set[4], lim_set[5]]

    return vlimit

#-------------------------------------------------------------------------------------------
#-- find_violation_rate: find rate of yellow, red violations in both lower and upper limits 
#-------------------------------------------------------------------------------------------

def find_violation_rate(carray, limits):
    """
    find rate of yellow, red violations in both lower and upper limits
    input:  carray  --- numpy array of the data
            limits  --- a list of limit [yellow lower, yellow upper, red lower, red upper]
    output: [yl, yu, rl, ru, tot]:  rate of yellow lower
                                    rate of yellow upper
                                    rate of red lower
                                    rate of red upper
                                    totla number of the data
    """
    tot  = len(carray)
    ftot = float(tot)

    yl  = find_num_of_elements(carray, limits[0], side=0)
    yu  = find_num_of_elements(carray, limits[1], side=1)
    rl  = find_num_of_elements(carray, limits[2], side=0)
    ru  = find_num_of_elements(carray, limits[3], side=1)
    yl -= rl
    yu -= ru

    yl /= ftot
    yu /= ftot
    rl /= ftot
    ru /= ftot

    return [yl, yu, rl, ru, tot]

#-------------------------------------------------------------------------------------------
#-- find_num_of_elements: find the numbers of elements above or lower than limit comparing to the total data #
#-------------------------------------------------------------------------------------------

def find_num_of_elements(carray, lim, side=0):
    """
    find the numbers of elements above or lower than limit comparing to the total data #
    input:  carray  --- numpy array of the data
            lim     --- the limit value
            side    --- lower:0 or upper:1 limit
    output: cnt     --- the numbers of the values beyond the limit
    """
#
#--- assume that the huge limit value means that there is no limit
#
    if abs(lim) > 1e6:
        return 0


    if side == 0:
        out = numpy.where(carray < lim)
    else:
        out = numpy.where(carray > lim)

    try:
        cnt = len(out[0])
    except:
        cnt = 0

    return cnt 

#-------------------------------------------------------------------------------------------
#-- convert_unit_indicator: convert the temperature unit to glim indicator                --
#-------------------------------------------------------------------------------------------

def convert_unit_indicator(cunit):
    """
    convert the temperature unit to glim indicator
    input: cunit    --- degc, degf, or psia
    output: tchk    --- 1, 2, 3 for above. all others will return 0
    """
    
    try:
        cunit = cunit.lower()
        if cunit == 'degc':
            tchk = 1
        elif cunit == 'degf':
            tchk = 2
        elif cunit == 'psia':
            tchk = 3
        else:
            tchk = 0
    except:
        tchk = 0

    return tchk

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

        compute_acis_power()

