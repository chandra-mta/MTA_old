#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#       tephin_leak_data_update.py: update tephin - ephin rate/leak current data    #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Feb 13, 2018                                               #
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
#--- create msid <---> unit dictionary
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read mta database
#
    mta_db = read_mta_database()
#
#--- read mta msid <---> sql msid conversion list
#
    mta_cross = read_cross_check_table()
#
#--- extract tephin data
#
    tchk  = convert_unit_indicator(udict['tephin'])
    glim  = get_limit('tephin', tchk, mta_db, mta_cross)
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
            tchk  = convert_unit_indicator(udict[msid])
        except:
            tchk  = 0
        glim  = get_limit(msid, tchk, mta_db, mta_cross)
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
            start = find_the_last_entry_time(tephin)
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
            lstart = find_the_last_entry_time(ltephin)
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
            glim  = gsr.read_glimmon(mchk, tchk)
        except:
            glim = [[0,  3218831995, -9e6, 9e6, -9e6, 9e6]]

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
#-- read_cross_check_table: read the mta msid and sql database msid cross table          ---
#-------------------------------------------------------------------------------------------

def read_cross_check_table():
    """
    read the mta msid and sql database msid cross table
    input: none but read from <house_keeping>/msid_cross_check_table
    output: mta_cross   --- a dictionary of mta msid and sql database msid
                        note: if there is no correspondece, it will return "mta"
    """

    ifile = house_keeping + 'msid_cross_check_table'
    f     = open(ifile, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    mta_cross = {}
    for ent in data:
        atemp = re.split('\s+', ent)
        mta_cross[atemp[0]] = atemp[1]

    return mta_cross

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
    if sdata == '':
        [week_p] = get_data_from_archive(msid, pstart, pstop, glim)

        if os.path.isfile(fits):
            update_fits_file(fits, cols, week_p)
        else:
            create_fits_file(fits, cols, week_p)

        return week_p[1]
#
#--- all others
#
    else:
        [week_p] = get_data_from_archive(msid, pstart, pstop, glim)
#
#--- adding tephin data into the second column position
#
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
            update_fits_file(fits, cols2, new)
        else:
            create_fits_file(fits, cols2, new)

#-------------------------------------------------------------------------------------------
#-- get_data_from_archive: extract data from the archive and compute the stats           ---
#-------------------------------------------------------------------------------------------

def get_data_from_archive(msid, start, stop, glim, step = 300.0):
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
    """
#
#--- 5 min step data
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
    wsave = []

    try:
        out     = fetch.MSID(msid, start, stop)
        tdata   = out.vals
        ttime   = out.times
        data    = []
        dtime   = []

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

        spos  = 0
        chk   = 1
        send  = dtime[spos]  + step

        for k in range(0, len(dtime)):

            if dtime[k] < send:
                chk = 0
            else:
                sdata = data[spos:k]
                avg   = sdata.mean()
                med   = numpy.median(sdata)
                sig   = sdata.std()
                amin  = sdata.min()
                amax  = sdata.max()
                ftime = dtime[spos + int(0.5 * (k-spos))]
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

                spos = k
                send = dtime[k] + step
                chk  = 1
#
#--- check whether there are any left over; if so add it to the data lists
#
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

            wtime.append(dtime[spos + int(0.5 * (k-spos))])
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

    except:
        pass

    week_p  = [wtime, wdata, wmed, wstd, wmin, wmax, wyl, wyu, wrl, wru, wcnt]
#
#--- adding limits to the table
#
    vtemp   = [[], [], [], []]
    for k in range(0, len(wsave)):
        for m in range(0, 4):
            vtemp[m].append(wsave[k][m])
    week_p = week_p + vtemp

    return [week_p]


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

    mcf.rm_file(fits)
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
    dlist = []
    for k in range(0, len(cols)):
        aent = numpy.array(cdata[k])
        dcol = pyfits.Column(name=cols[k], format='E', array=aent)
        dlist.append(dcol)

    dcols = pyfits.ColDefs(dlist)
    tbhdu = pyfits.BinTableHDU.from_columns(dcols)

    mcf.rm_file(fits)
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

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        year = int(sys.argv[1])
    else:
        year = ''

    tephin_leak_data_update(year)


