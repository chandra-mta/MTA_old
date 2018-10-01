#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Oct 27, 2017                                               #
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
#--- interactive plotting module
#
import mpld3
from mpld3 import plugins, utils
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

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
import convertTimeFormat        as tcnv #---- contains MTA time conversion routines
import mta_common_functions     as mcf  #---- contains other functions commonly used in MTA scripts
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import glimmon_sql_read         as gsr  #---- glimmon database reading
import violation_estimate_data  as ved  #---- save violation estimated times in sqlite database v_table
import find_moving_average      as fma  #---- moving average 
import find_moving_average_bk   as fmab #---- moving average (backword fitting version)
import robust_linear            as rfit #---- robust fit rountine
import create_derivative_plots  as cdp  #---- create derivative plot
#
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

data_dir = './Outdir/'

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def run_script(msid_list, start, stop, step):

    mfile = house_keeping + msid_list
    f     = open(mfile, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        print "MSID: " + msid
        group = atemp[1]
        create_interactive_page(msid, group,  start, stop, step)

#-------------------------------------------------------------------------------------------
#-- create_interactive_page: update all msid listed in msid_list                                 --
#-------------------------------------------------------------------------------------------

def create_interactive_page(msid, group,  start, stop, step):
    """
    create an interactive html page for a given msid
    input:  msid    --- msid
            start   --- start time
            stop    --- stop time
            step    --- bin size in seconds
    """
    start = check_time_format(start)
    stop  = check_time_format(stop)
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
#--- get limit data table for the msid
#
    try:
        tchk  = convert_unit_indicator(udict[msid])
    except:
        tchk  = 0

    glim  = get_limit(msid, tchk, mta_db, mta_cross)
#
#--- extract needed data and save in fits file
#
    try:
        out = fetch.MSID(msid, '2017:001:00:00:00', '2017:002')
    except:
        missed = house_keeping + '/missing_data'
        fo     = open(missed, 'a')
        fo.write(msid)
        fo.write('\n')
        fo.close()

    fits_data = update_database(msid, group,  glim, start, stop, step)

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

    mchk = mta_cross[msid]
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

def update_database(msid, group, glim, pstart, pstop, step):
    """
    update/create fits data files of msid
    input:  msid    --- msid
            pstart  --- starting time in seconds from 1998.1.1
            pstop   --- stopping time in seconds from 1998.1.1
            step    --- time interval of the short time data
    output: <msid>_data.fits, <msid>_short_data.fits
    """

    cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower', 'yupper', 'rlower', 'rupper', 'dcount',\
             'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

    out_dir = data_dir + group + '/'
#
#--- make sure that the sub directory exists
#
    if not os.path.isdir(out_dir):
        cmd = 'mkdir ' + out_dir
        os.system(cmd)

    week_p = get_data_from_archive(msid, pstart, pstop, glim, step)

    fits3 = out_dir + msid + '_week_data.fits'
    create_fits_file(fits3, cols, week_p)

    return fits3

#-------------------------------------------------------------------------------------------
#-- get_data_from_archive: extract data from the archive and compute the stats           ---
#-------------------------------------------------------------------------------------------

def get_data_from_archive(msid, start, stop, glim, step):
    """
    extract data from the archive and compute the stats
    input:  msid    --- msid of the data
            start   --- start time
            stop    --- stop time
            glim    --- a list of limit tables
            step    --- a bin size in seconds
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
    vsave = []
#
#--- extract data from archive
#
    xxx = 9999
    if xxx == 9999:
    ###try:
        out     = fetch.MSID(msid, start, stop)
        tdata   = out.vals
        ttime   = out.times
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
#--- if a full resolution is asked...
#
        if step == 0.0:
            wtime = dtime
            wdata = data
            wmed  = data
            wstd  = [0]* len(data)
            wmin  = data
            wmax  = data
            for m in range (0, len(dtime)):
                vlimits = find_violation_range(glim, dtime[m])
                darray  = numpy.array([data[m]])
                [yl, yu, rl, ru, tot] = find_violation_rate(darray, vlimits)
                wyl.append(yl)
                wyu.append(yu)
                wrl.append(rl)
                wru.append(ru)
                wcnt.append(1)
                wsave.append(vlimits)

#
#--- if asked, devide the data into a smaller period (step size)
#
        else:
            spos  = 0
            spos2 = 0
            chk   = 1
            chk2  = 2
            send2 = dtime[spos2] + step
    
            for k in range(0, len(dtime)):
    
                if dtime[k] < send2:
                    chk2 = 0
                else:
                    sdata = data[spos2:k]
    
                    if len(sdata) <= 0:
                        spos2 = k
                        send2 = dtime[k] + step
                        chk2  = 1
                        continue
    
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
                    send2 = dtime[k] + step
                    chk2  = 1
#
#--- check whether there are any left over; if so add it to the data lists
#
            if chk2 == 0:
                rdata = data[spos2:k]
                if len(rdata) > 0:
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

    else:                   #----REMOVE!!
    ###except:
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

    return week_p


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
    
    #cdata = remove_duplicate(cdata)

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

    mcf.rm_file(fits)
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

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def check_time_format(intime):

    mc1 = re.search('-', intime)
    mc2 = re.search(':', intime)
    
    if mcf.chkNumeric(intime):
        return int(float(intime))
    
    elif mc1 is not None:
        mc2 = re.search('T', intime)
        if mc2 is not None:
            atemp = re.split('T', intime)
            btemp = re.split('-', atemp[0])
            year  = int(float(btemp[0]))
            mon   = int(float(btemp[1]))
            day   = int(float(btemp[2]))
            ctemp = re.split(':', atemp[1])
            hrs   = ctemp[0]
            mins  = ctemp[1]
            secs  = ctemp[2]
    
        else:
            btemp = re.split('-', intime)
            year  = int(float(btemp[0]))
            mon   = int(float(btemp[1]))
            day   = int(float(btemp[2]))
            hrs   = '00'
            mins  = '00'
            secs  = '00'
    
        yday = datetime.date(year, mon, day).timetuple().tm_yday
    
        cyday = str(yday)
        if yday < 10:
            cyday = '00' + cyday
        elif yday < 100:
            cyday = '0' + cyday
     
        ytime = btemp[0] + ':' + cyday + ':' + hrs + ':' + mins + ':' + secs
    
        return Chandra.Time.DateTime(ytime).secs
    
    elif mc2 is not None:
    
        return Chandra.Time.DateTime(intime).secs


#--------------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    msid_list = sys.argv[1]
    start     = sys.argv[2]
    stop      = sys.argv[3]
    step      = int(float(sys.argv[4]))

    run_script(msid_list, start, stop, step)
