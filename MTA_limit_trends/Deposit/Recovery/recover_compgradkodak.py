#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#       recover_compgradkodak.py: reconver all compgradodak full resolutiond data   #
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
import datetime
import random
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
import fits_operation           as mfo
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

mon_list1 = [1, 32, 60, 91, 121, 152, 192, 213, 244, 274, 305, 335]
mon_list2 = [1, 32, 61, 92, 122, 153, 193, 214, 245, 275, 306, 336]

out_dir = './Outdir/'

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_compgradkodak(start):

    if start == "":
        start = 1999
    else:
        start = int(float(start))

    tyear = int(float(time.strftime("%Y", time.gmtime())))
    yday  = int(float(time.strftime("%j", time.gmtime())))
    nyear = tyear + 1

    for year in range(start, nyear):

        if mcf.is_leapyear(year):
            dlast = 367
        else:
            dlast = 366

        for day in range(1, dlast):
            cday = str(day)
            if day < 10:
                cday = '00' + cday
            elif day < 100:
                cday = '0'  + cday

            if year == 1999:
                if day < 213:
                    continue
            if year == tyear:
                if day >= yday:
                    break

            start =  str(year) + ':' + cday + ':00:00:00'
            stop  =  str(year) + ':' + cday + ':23:59:59'

            get_data(start, stop, year)

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def get_data(start, stop, year):

    print(str(start) + '<-->' + str(stop))

    empty  = [0]

    rt7  = []
    for k  in range(0, 12):
        if k < 10:
            msid = '4rt70' + str(k) + 't'
        else:
            msid = '4rt7'  + str(k) + 't'

        try:
            out   = fetch.MSID(msid, start, stop)
            data  = out.vals
            ttime = out.times
            tlist = list(ttime)
            rt7.append(data)
        except:
            rt7.append(empty)


    out    = fetch.MSID('4rt575t', start, stop)
    rt575  = out.vals

    tlen   = len(ttime)
    empty  = numpy.zeros(tlen)
    ohrthr = [empty]
    oobthr = [empty]

    for k in range(1, 65):
        if k < 10:
            msid = 'ohrthr0' + str(k)
        else:
            msid = 'ohrthr'  + str(k)
        try:
            out   = fetch.MSID(msid, start, stop)
            data  = out.vals
            otime = out.times

            adata = fill_gaps(ttime, otime, data)

            ohrthr.append(adata)
        except:
            ohrthr.append(empty)

        if k < 10:
            msid = 'oobthr0' + str(k)
        else:
            msid = 'oobthr'  + str(k)
        try:
            out   = fetch.MSID(msid, start, stop)
            data  = out.vals
            otime = out.times

            adata = fill_gaps(ttime, otime, data)

            oobthr.append(adata)
        except:
            oobthr.append(empty)


    hrmaavg         = []
    hrmacav         = []
    hrmaxgrd        = []
    hrmaradgrd      = []
    obaavg          = []
    obaconeavg      = []
    
    fwblkhdt        = []
    aftblkhdt       = []
    obaaxgrd        = []
    
    mzobacone       = []
    pzobacone       = []
    obadiagrad      = []
    
    hrmarange       = []
    tfterange       = []
    hrmastrutrnge   = []
    scstrutrnge     = []
#----    
    t_hrmaavg       = []
    t_hrmacav       = []
    t_hrmaxgrd      = []
    t_hrmaradgrd    = []
    t_obaavg        = []
    t_obaconeavg    = []
    
    t_fwblkhdt      = []
    t_aftblkhdt     = []
    t_obaaxgrd      = []
    
    t_mzobacone     = []
    t_pzobacone     = []
    t_obadiagrad    = []
    
    t_hrmarange     = []
    t_tfterange     = []
    t_hrmastrutrnge = []
    t_scstrutrnge   = []
    
    for k in range(0, tlen):
        out = compute_hrmaavg(ohrthr, k )
        if out != 'na':
            hrmaavg.append(out)
            t_hrmaavg.append(tlist[k])

#-------------------------
        out = compute_hrmacav(ohrthr, k )
        if out != 'na':
            hrmacav.append(out)
            t_hrmacav.append(tlist[k])
#-------------------------
        out = compute_hrmaxgrd(ohrthr, k )
        if out != 'na':
            hrmaxgrd.append(out)
            t_hrmaxgrd.append(tlist[k])
#------------------------ 
        out = compute_hrmaradgrd(ohrthr, k )
        if out != 'na':
            hrmaradgrd.append(out)
            t_hrmaradgrd.append(tlist[k])
#------------------------ 
        out = compute_obaavg(oobthr, k )
        if out != 'na':
            obaavg.append(out)
            t_obaavg.append(tlist[k])
#------------------------     
        out = compute_obaconeavg(oobthr, k )
        if out != 'na':
            obaconeavg.append(out)
            t_obaconeavg.append(tlist[k])
#------------------------     
        out = compute_fwblkhdt(oobthr, rt7, k )
        chk1 = 0
        if out != 'na':
            fwblkhdt.append(out)
            t_fwblkhdt.append(tlist[k])
            chk1 = 1
#------------------------     
        out = compute_aftblkhdt(oobthr, k )
        chk2 = 0
        if out != 'na':
            aftblkhdt.append(out)
            t_aftblkhdt.append(tlist[k])
            chk2 = 1
#------------------------     
        if (chk1 == 1) and (chk2 == 1):
            out = compute_obaaxgrd(fwblkhdt[-1], aftblkhdt[-1])
            if out != 'na':
                obaaxgrd.append(out)
                t_obaaxgrd.append(tlist[k])
#------------------------     
        out = compute_mzobacone(oobthr, rt575, k )
        chk1 = 0
        if out != 'na':
            mzobacone.append(out)
            t_mzobacone.append(tlist[k])
            chk1 = 1
#------------------------     
        out = compute_pzobacone(oobthr, k )
        chk2 = 0
        if out != 'na':
            pzobacone.append(out)
            t_pzobacone.append(tlist[k])
            chk2 = 1
#------------------------     
        if (chk1 == 1) and (chk2 == 1):
            out = compute_obadiagrad(mzobacone[-1], pzobacone[-1])
            if out != 'na':
                obadiagrad.append(out)
                t_obadiagrad.append(tlist[k])
#------------------------     
        out = compute_hrmarange(ohrthr, k )
        if out != 'na':
            hrmarange.append(out)
            t_hrmarange.append(tlist[k])
#------------------------     
        out = compute_tfterange(oobthr, k )
        if out != 'na':
            tfterange.append(out)
            t_tfterange.append(tlist[k])
#------------------------     
        out = compute_hrmastrutrnge(oobthr, k )
        if out != 'na':
            hrmastrutrnge.append(out)
            t_hrmastrutrnge.append(tlist[k])
#------------------------     
        out = compute_scstrutrnge(oobthr, k )
        if out != 'na':
            scstrutrnge.append(out)
            t_scstrutrnge.append(tlist[k])

    for col in ['hrmaavg', 'hrmacav', 'hrmaxgrd', 'hrmaradgrd', 'obaavg', 'obaconeavg', 'fwblkhdt',\
                'aftblkhdt', 'obaaxgrd', 'mzobacone', 'pzobacone', 'obadiagrad', 'hrmarange',\
                'tfterange', 'hrmastrutrnge', 'scstrutrnge']:

        exec("odata = %s"   % (col))
        exec("tdata = t_%s" % (col))

        olen  = len(odata)

        tdata = numpy.array(tdata)
        odata = numpy.array(odata)

        cdata = [tdata, odata]
        cols  = ['time', col]

        fits  = out_dir + col + '_full_data_' + str(year) + '.fits'
        if os.path.isfile(fits):
            update_fits_file(fits, cols, cdata)
        else:
            create_fits_file(fits, cols, cdata)

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

    udata = []
    chk   = 0
    for k in range(0, len(cols)):
        try:
            nlist   = list(data[cols[k]]) + list(cdata[k])
            udata.append(numpy.array(nlist))
        except:
            chk = 1
            pass

    if chk == 0:
        try:
            create_fits_file(fits, cols, udata)
        except:
            pass

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
        dcol = pyfits.Column(name=cols[k], format='F', array=aent)
        dlist.append(dcol)

    dcols = pyfits.ColDefs(dlist)
    tbhdu = pyfits.BinTableHDU.from_columns(dcols)

    mcf.rm_files(fits)
    tbhdu.writeto(fits)

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_hrmaavg(ohrthr, pos):

    olist    = range(2,14) + range(21,31) + [33, 36, 37, 42] + range(44,48) + range(49,54) + [55, 56]
    hrmaavg  = take_sum(olist, ohrthr, pos, achk=1)

    return hrmaavg

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_hrmacav(ohrthr, pos):

    olist   = range(6,16)+ [17, 25, 26] + range(29,32) + range(33,38) +[39, 40] + range(50,59) + [60, 61]
    hrmacav = take_sum(olist, ohrthr, pos, achk=1)

    return hrmacav

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_hrmaxgrd(ohrthr, pos):

    olist1    = [10, 11, 34, 35, 55, 56]
    olist2    = [12, 13, 36, 37, 57, 58]
    hrmaxgrd1 = take_sum(olist1, ohrthr, pos, achk=1)
    hrmaxgrd2 = take_sum(olist2, ohrthr, pos, achk=1)

    try:
        hrmaxgrd  = hrmaxgrd1 - hrmaxgrd2
    except:
        hrmaxgrd  = 'na'

    return hrmaxgrd

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_hrmaradgrd(ohrthr, pos):

    olist1     = [8, 31, 33, 52]
    olist2     = [9, 53, 54]
    hrmarad1   = take_sum(olist1, ohrthr, pos, achk=1)
    hrmarad2   = take_sum(olist2, ohrthr, pos, achk=1)

    try:
        hrmaradgrd = hrmarad1 - hrmarad2
    except:
        hrmaradgrd = 'na'

    return hrmaradgrd

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_obaavg(oobthr, pos):

    olist  = range(8,16) + range(17,32) + range(33,42) + [44, 45, 11, 12, 36]
    obaavg = take_sum(olist, oobthr, pos, achk=1)

    return obaavg 


#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_obaconeavg(oobthr, pos):

    olist      = range(8,16) + range(17,31) + range(57,62)
    obaconeavg = take_sum(olist, oobthr, pos, achk=1)

    return obaconeavg

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_fwblkhdt(oobthr, rt7, pos):

    olist   = [62, 63]
    oobtsum = take_sum(olist, oobthr, pos, achk=1)

    olist   = range(0,12) 
    rt7sum  = take_sum(olist, rt7, pos, achk=1)

    if oobtsum == 'na':
        if rt7sum == 'na':
            fwblkhdt = 'na'
        else:
            fwblkhdt =  rt7sum
    else:
        if rt7sum == 'na':
            fwblkhdt = oobtsum
        else:
            fwblkhdt = (oobtsum * 2 + rt7sum * 12) / 14.0

    return fwblkhdt

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_aftblkhdt(oobthr, pos):

    olist     = [31, 33, 34]
    aftblkhdt = take_sum(olist, oobthr, pos, achk=1)

    return aftblkhdt

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_obaaxgrd(fwblkhdt, aftblkhdt):

    if (fwblkhdt != 'na') and (aftblkhdt != 'na'):
        obaaxgrd = fwblkhdt - aftblkhdt
    else:
        obaaxgrd = 'na'

    return obaaxgrd

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_mzobacone(oobthr, rt575, pos):

    olist = [8, 19, 26, 31, 57, 60]
    msum  = take_sum(olist, oobthr, pos, achk=1)

    if msum == 'na':
        if rt575[pos] == 0:
            mzobacone = 'na'
        else:
            mzobacone = rt575[pos]
    else:
        if rt575[pos] == 0:
            mzobacone = msum 
        else:
            mzobacone = (msum * 6.0 + rt575[pos]) / 7.0

    return mzobacone

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_pzobacone(oobthr, pos):

    olist = [13, 22, 23, 28, 29, 61]

    pzobacone = take_sum(olist, oobthr, pos, achk=1)

    return pzobacone

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_obadiagrad(mzobacone, pzobacone):

    if (mzobacone != 'na') and (pzobacone != 'na'):
        obadiagrad = mzobacone - pzobacone
    else:
        obadiagrad = 'na'

    return obadiagrad

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_hrmarange(ohrthr, pos):

    olist = range(2,14) + range(21,28) + [29, 30, 33, 36, 37, 42] + range(44,48) +  range(49,54) +[55, 56]

    hrmarange  = find_range(olist, ohrthr, pos)

    return hrmarange

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_tfterange(oobthr, pos):

    olist     = [42, 43, 44]
    tfterange = find_range(olist, oobthr, pos)

    return tfterange

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_hrmastrutrnge(oobthr, pos):

    olist         = range(2,8)
    hrmastrutrnge = find_range(olist, oobthr, pos)

    return hrmastrutrnge


#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def compute_scstrutrnge(oobthr, pos):

    olist       = range(49,55)
    scstrutrnge = find_range(olist, oobthr, pos)

    return scstrutrnge


#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def take_sum(olist, data, pos, achk=0):

    asum = 0.0
    tot  = 0.0
    for k in olist:
        try:
            val = data[k][pos]
            if val > 0:
                asum += data[k][pos]
                tot  += 1.0
        except:
            pass

    if achk == 0:
        return asum

    else:
        try:
            avg = asum / tot
        except:
            avg = 'na'

        return avg

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def find_range(olist, data, pos):
    amin = ''
    amax = ''
    for k in olist:
        try:
            val = data[k][pos]
            if amin == '':
                amin = val
                amax = val
            else:
                if val > amax:
                    amax = val
                if val < amin:
                    amin = val
        except:
            pass
    
    if amin == '':
        range = 'na'
    else:
        range = amax - amin
    
    return range

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def fill_gaps(ttime, otime, data):
#
#--- convert numpy array to list
#
    ttime = list(ttime)
    data  = list(data)
    otime = list(otime)

    tlen  = len(ttime)
    mlen  = len(otime)

    adata = []
    n     = 0
    chk   = 0
    for m in range(0, tlen):
        if ttime[m] > otime[n]:
            while ttime[m] > otime[n]:
                n += 1
                if n >= mlen:
                    diff = tlen - len(adata)
                    for nk in range(0, diff):
                        adata.append(data[n-1])
                    chk = 1
                    break
                else:
                    if ttime[m] == otime[n]:
                        adata.append(data[n])
                        break
        elif ttime[m] < otime[n]:
            adata.append(data[n])
        else:
            adata.append(data[n])
            n += 1
            if n >= mlen:
                diff = tlen - len(adata)
                for nk in range(0, diff):
                    adata.append(data[n-1])
                chk = 1
        if chk == 1:
            break

    adata = numpy.array(adata)

    return adata

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        start = sys.argv[1]
    else:
        start = ''

    compute_compgradkodak(start)

