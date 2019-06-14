#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#           rerun_week.py: rerun for the week length data recovery                  #
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
import randome
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts3.6/house_keeping/dir_list'
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
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

sp_limt_case_c = ['3faralat','3rctubpt','3tsmxcet', '3tsmxspt', '3tsmydpt', '3tspyfet',\
                  '3tspzdet', '3tspzspt','3ttacs1t', '3ttacs2t', '3ttacs3t', '3ttbrgbt', '3tthrc1t',\
                  '3tthrc2t', '3tthrc3t', '3ttralat', '3ttralct','3ttvalvt', '3btu_bpt']

#-------------------------------------------------------------------------------------------
#-- update_msid_data: update all msid listed in msid_list                                 --
#-------------------------------------------------------------------------------------------

def update_msid_data(msid_list):
    """
    update all msid listed in msid_list
    input:  msid_list   --- a list of msids to processed. default: msid_list_fetch
    output: <msid>_data.fits/<msid>_short_data.fits
    """
    start_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
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
#--- read msid list
#
    mfile = house_keeping + msid_list
    data  = mcf.read_data_file(mfile)

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
            tchk  = convert_unit_indicator(udict[msid])
        except:
            tchk  = 0
        if msid in sp_limt_case_c:
            tchk = 1
        glim  = get_limit(msid, tchk, mta_db, mta_cross)
#
#--- update database
#
#        try:
#            out = fetch.MSID(msid, '2017:001:00:00:00', '2017:002')
#            print("MSID: " + msid)
#        except:
#            out = get_mta_fits_data(msid, '2017:001:00:00:00', '2017:002')
#
#            if out == False:
#                missed = house_keeping + '/missing_data'
#                fo     = open(missed, 'a')
#                fo.write(msid)
#                fo.write('\n')
#                fo.close()
#
#                continue
    
        update_database(msid, group,  glim)
#
#--- test entry to check how long it took
#
    end_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())


    line = "trending plotting: \n"
    line = line + "Started: " + start_time + '\n'
    line = line + "Ended: " + end_time + '\n'

    print(line)

#-------------------------------------------------------------------------------------------
#-- get_limit: find the limit lists for the msid                                          --
#-------------------------------------------------------------------------------------------

def get_limit(msid, tchk, mta_db, mta_cross):
    """
    find the limit lists for the msid
    input:  msid        --- msid
            tchk        --- whether temp conversion needed 0: no/1: degc/2: degf/3: pcs
            mta_db      --- a dictionary of mta msid <---> limist
            mta_corss   --- mta msid and sql msid cross check table
    output: glim        --- a list of lists of lmits. innter lists are:
                            [start, stop, yl, yu, rl, ru]
    """
    try:
        mchk = mta_cross[msid]
    except:
        mchk = 0

    if mchk == 'mta':
        try:
            glim = mta_db[msid]
        except:
            glim = [[0,  3218831995, -9e6, 9e6, -9e6, 9e6]]

    else:
        try:
        #xxx = 9999
        #if xxx == 9999:
            out  = gsr.read_glimmon(mchk, tchk)
            test = str(mchk[-2] + mchk[-1])
            if test.lower() == 'tc':
                glim = []
                for ent in out:
                    for k in range(2,6):
                        ent[k] -= 273.15
                glim.append(ent)
            else:
                glim = out
        except:
        #else:
            glim = [[0,  3218831995, -9e6, 9e6, -9e6, 9e6]]

    return glim


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

    test = str(msid[-2] + msid[-1]).lower()
    if test == 'tc':
        tmsid = msid[:-1]
    else:
        tmsid = msid

    cols  = ['time', tmsid, 'med', 'std', 'min', 'max', 'ylower', 'yupper',\
             'rlower', 'rupper', 'dcount',\
             'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

    stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
    pstop = Chandra.Time.DateTime(stday).secs - 86400.0  
    pstart = pstop - 86400.0 * 14.0           #---- two weeks ago

    pstep  = 300 
    out_dir = './Outdir/' + group.capitalize() + '/'
#
#--- make sure that the sub directory exists
#
    if not os.path.isdir(out_dir):
        cmd = 'mkdir ' + out_dir
        os.system(cmd)

    fits3 = out_dir + tmsid + '_week_data.fits'
    print("FITS: " + str(fits3))

    [week_p, short_p, long_p] = get_data_from_archive(msid, pstart, pstop, glim, step=pstep)
#
    ecf.create_fits_file(fits3, cols, short_p)


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
    step2 = 86400 
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
    xxx = 9999
    #if xxx == 9999:
    try:
        out     = fetch.MSID(msid, start, stop)
        ok      = ~out.bads
        tdata   = out.vals[ok]
        ttime   = out.times[ok]

        tind    = [(tdata > -999) | (tdata <= -1000)]
        tdata   = tdata[tind]
        ttime   = ttime[tind]

    #else:
    except:
        try:
             [ttime, tdata] = get_mta_fits_data(msid, start, stop)
        except:
            rdata = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[-9.0e9],[-9.0e9],[9.0e9],[9.0e9]]

            return rdata

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
    ecf.create_fits_file(fits, cols, udata)


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
        if cunit == 'degc' or cunit == 'c':
            tchk = 1
        elif cunit == 'degf' or cunit == 'f':
            tchk = 2
        elif cunit == 'psia':
            tchk = 3
        else:
            tchk = 0
    except:
        tchk = 0

    return tchk

#--------------------------------------------------------------------------------------------------------
#-- get_mta_fits_data: fetch data from mta local database                                              --
#--------------------------------------------------------------------------------------------------------

def get_mta_fits_data(msid, start, stop):
    """
    fetch data from mta local database
    input:  msid    --- msid
            start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: time    --- time in second from 1998.1.1 for the given period
            vals    --- vals of msid for the given period
    """

#
#--- find which year(s) the requested period falls
#
    date  = Chandra.Time.DateTime(start)
    byear = int(float(date.year))
    date  = Chandra.Time.DateTime(stop)
    eyear = int(float(date.year))

    chk   = 0
    for year in range(byear, eyear+1):
#
#--- find whether the fits data file exists
#
        cmd = 'ls ' + deposit_dir + '*/*/' + msid + '_full_data_' + str(year) + '.fits* > ' + zspace
        os.system(cmd)
        test = str(msid[-2] + msid[-1]).lower()
        if test == 'tc':
            test = str(msid[:-1])
            cmd = 'ls ' + deposit_dir + '*/*/' + test + '_full_data_' + str(year) + '.fits* >> ' + zspace
            os.system(cmd)
            msid = test

        out  = mcf.read_data_file(zspace, remove=1)
        fits = out[0]

        if not os.path.isfile(fits):
            continue
#
#--- extract the data for the given period
#
        f     = pyfits.open(fits)
        data  = f[1].data
        f.close()
        if chk == 0:
            time = data['time']
            vals = data[msid]
            ext  = [(time > start) & (time < stop)]
            time = time[ext]
            vals = vals[ext]
            chk  = 1
        else:
            tmp1 = data['time']
            tmp2 = data[msid]
            ext  = [(tmp1 > start) & (tmp1 < stop)]
            tmp1 = tmp1[ext]
            tmp2 = tmp2[ext]
            time = numpy.append(time, tmp1)
            vals = numpy.append(vals, tmp2)

    if chk > 0:
        return [time, vals]
    else:
#
#--- if no data, return False
#
        return False


#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
            msid_list = sys.argv[1]
            msid_list.strip()
            update_msid_data(msid_list=msid_list)
    else:
        print("rerun_short.py <msid_list>")

