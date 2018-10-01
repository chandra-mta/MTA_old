#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################################
#                                                                                                                       #
#       extract_bad_pix.py: find ACIS bad pixels and bad columns and records daily variations                           #
#                                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                                   #
#                                                                                                                       #
#           last update May 13, 2014                                                                                    #
#                                                                                                                       #
#########################################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits as pyfits

comp_test = 'live'
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')

#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat       as tcnv       #---- contains MTA time conversion routines
import mta_common_functions    as mcf        #---- contains other functions commonly used in MTA scripts
import bad_pix_common_function as bcf

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#
#--- setting limits: factors for how much std out from the mean
#
factor     = 5.0        #--- warm pixel 
col_factor = 3.0        #--- warm column 
hot_factor = 1000.0     #--- hot pixel

#
#-- day limits
#
day30 = 2592000.0   #---- (in sec)
day14 = 1209600.0
day7  = 604800.0

#
#--- a couple of things needed
#
dare   = mcf.get_val('.dare',   dir = bdat_dir, lst=1)
hakama = mcf.get_val('.hakama', dir = bdat_dir, lst=1)


#---------------------------------------------------------------------------------------------------
#--- find_bad_pix_main: contorl function to extract bad pixels and bad columns                   ---
#---------------------------------------------------------------------------------------------------

def find_bad_pix_main(dom):

    """
    contorl function to extract bad pixels and bad columns
    Input: comp_test ---- (grobal variable): "live"  --- read data from live data
                                             "<dir>" --- read data from <dir>
                                             "test"  --- perform test 
    Output: updated bad pixel and bad column list files
    """
#
#---check whether "Working_dir" exists
#
    chk = mcf.chkFile('./','Working_dir')
    if chk > 0:
        mcf.rm_file('./Working_dir/*')
    else:
        cmd = 'mkdir ./Working_dir'
        os.system(cmd)

    [start,stop] = set_date(dom)

    get_data_out(start, stop)
#
#--- find which data are new and need to be analyzed
#
    odir = exc_dir + '/Temp_data/'
    main_list = regroup_data(odir)
#
#--- prepare files for analysis
#
    for  data_list in main_list:                #---- data_list contains one day amount of data
#
#--- remove the temporary bad_col_list, warm_list, and hot_list
#
        mcf.rm_file('./Working_dir/*_list')
#
#--- create data lists in ./Working_dir/new_data_ccd<ccd>
#
        int_file_for_day(data_list)
#
#--- check today's bad cols and pixs
#
        dom = setup_to_extract()
#
#--- if there is no data, dom <= 0 
#
        if dom  <= 0:
            continue

        for ccd in range(0, 10):
            warm_data_list = []
            hot_data_list  = []
#
#--- bad pix selected at each quad; so go though all of them and combine them
#
            for quad in range(0, 4):

                (warm_data, hot_data) = select_bad_pix(ccd, quad)

                if quad == 0:
                    warm_data_list = warm_data
                    hot_data_list  =  hot_data
                else:
                    warm_data_list = combine_ccd(warm_data_list, warm_data, quad)
                    hot_data_list  = combine_ccd(hot_data_list,  hot_data,  quad)

            if len(warm_data_list) > 1:
                warm_data_list = mcf.removeDuplicate(warm_data_list,  chk = 0, dosort=0)

            if len(hot_data_list)  > 1:
                hot_data_list =  mcf.removeDuplicate(hot_data_list,   chk = 0, dosort=0)
#
#---- print out newly found warm and hot pixels
#
            print_bad_pix_data(ccd, warm_data_list, 'warm', today_time = dom)
            print_bad_pix_data(ccd, hot_data_list,  'hot',  today_time = dom)
#
#--- find and print bad columns
#
#            cfile = './Worlking_dir/today_bad_col_' + str(ccd)
#            bad_col_list = []
#            chk    = mcf.isFileEmpty(cfile)
#            if chk > 0:
###            bad_col_list = chk_bad_col(ccd)

###            print_bad_col(ccd, bad_col_list, dom)
#
#--- clean up the Exc area
#
    mcf.rm_file('./Working_dir')

#---------------------------------------------------------------------------------------------------
#--- combine_ccd: combine bad pixel positions from a different quad to one CCD coordinate system  --
#---------------------------------------------------------------------------------------------------

def combine_ccd(base, new, quad):
    """
    combine bad pixel positions from a different quad to one CCD coordinate system

    Input:  base -- bad pixel positions already recorded in a CCD coordinates
                    data format: <ccd>:<quad>:<year>:<ydate>:<x>:<y>
            new  -- new bad pixel position listed in quad coordinated
            quad -- quad # 0 - 3
    Output: base -- updated list of bad pixels in CCD coordinates
    """

    for ent in new:
        atemp = re.split(':', ent)
        ccd   = atemp[0]
        mtime = atemp[2] + ':' + atemp[3]
        x     = str(int(atemp[4]) + 256  * int(quad))
        y     = atemp[5]
        line  = ccd + ':' + str(quad) + ':' + mtime + ':' + x + ':' + y
        base.append(line)

    return base

#---------------------------------------------------------------------------------------------------
#--- regroup_data: for the case, data list is given, regroup them for farther analysis           ---
#---------------------------------------------------------------------------------------------------

def regroup_data(input_dir):

    """
    for the case that data list is given, regroup them for farther analysis
    Input:  input_dir --- a directory path to the data
            data_list --- a list of lists which contain data file names
    """
    
    cmd = 'ls ' + input_dir +  '/acisf*bias0.fits >' + zspace
    chk = mcf.processCMD(cmd)
    if chk > 0:
#        print "cannot find data: /acisf*bias0.fits. Exiting...\n"
#        exit(1)
        return []

    bias_bg_comp_list = []

    data =  mcf.readFile(zspace)
#
#--- this is today's input data list for bias computation
#
    cmd = 'mv ' + zspace + ' ' + house_keeping + '/today_bias_input_data'
    os.system(cmd)

    if len(data) < 1:
        print "There is no bias data in this period... exiting\n"
        exit(1)

    cdate     = -999 
    btemp     = []
    data_list = []
    chk       = 0

    for ent in data:
        dom = bcf.findTimeFromHead(ent)
        if dom == cdate:
            btemp.append(ent)
            chk = 1
        else:
            if cdate == -999:
                btemp.append(ent)
                cdate = dom
            else:
                cdate = dom
                data_list.append(btemp)
                btemp = []
                chk = 0

    if chk == 1:
        data_list.append(btemp)
    return data_list

#---------------------------------------------------------------------------------------------------
#--- int_file_for_day: separate each data into appropriate ccd data list                         ---
#---------------------------------------------------------------------------------------------------

def int_file_for_day(data_list):

    """
    separate each data into appropriate ccd data list
    Input:      data_list --- a list of bias.fits files
    Output:     data_dir + '/Disp_dir/data_used.<ccd> --- a record of which data used for the analysis
                ./Working_dir/new_data_ccd.<ccd>      --- a list of the data which will be used for today's analysis
    """

#
#--- check each data and select out appropriate data
#
    for ent in data_list:
        stime      = bcf.extractTimePart(ent)
        if stime > 0:
            head       = 'acis' + str(int(stime))
            today_time = bcf.findTimeFromHead(ent)
    
            [ccd, readmode, date_obs, overclock_a, overclock_b, overclock_c, overclock_d] = extractCCDInfo(ent)
#
#--- only TIMED data will be used
#
            m = re.search('TIMED', readmode)
            if m is not None:
#
#--- keep the record of which data we used
#
                line = data_dir + '/Disp_dir/data_used.' + str(ccd)
                f    = open(line, 'a')
                line = './Working_dir/new_data_ccd.' + str(ccd)
                fw   = open(line, 'a')
                ntemp= re.split('acisf', ent)

                atemp = re.split('T', date_obs)
                btemp = re.split('-', atemp[0])
                tyear = int(btemp[0])
                tmon  = int(btemp[1])
                tday  = int(btemp[2])
                ydate = tcnv.findYearDate(tyear, tmon, tday)

                line = str(tyear)+':' + str(ydate) + ':acisf' + ntemp[1] + '\n'
                f.write(line)
#
#--- a list of data to be analyzed kept in ./Working_dir
#
                fw.write(ent)
                fw.write("\n")
    
                fw.close()
                f.close()


#---------------------------------------------------------------------------------------------------
#--- setup_to_extract: prepare to extract data                                                    --
#---------------------------------------------------------------------------------------------------

def setup_to_extract():

    """
    prepare to extract data
    Input:  ./Working_dir/new_data_ccd<ccd #>: a list of new data for the ccd. Read from ./Working_dor
    Output: dom --- DOM of the observation (today, unless the original data are given)
            output from a function "extract" written in ./Working_dir
    """

    dom = -999
    for ccd in range(0, 10):
        line       = './Working_dir/new_data_ccd.' + str(ccd)
        todaylist  = mcf.readFile(line)
#
#--- only when data exists, procced
#
        if len(todaylist) > 0:

            file  = todaylist[0]
            stime = bcf.extractTimePart(file)

            if stime > 0:
                ctime = tcnv.convertCtimeToYdate(stime)
                (year, month, date, hours, minutes, seconds, ydate, dom, sectime) = tcnv.dateFormatConAll(ctime)
                date_obs = str(year) + ':' + str(int(ydate))
                head     = 'acis' + str(int(stime))
#
#--- comb.fits is an img fits file combined all image fits files extracted
#
                wfile = './Working_dir/comb.fits'
                mcf.rm_file(wfile) 
                cmd   = 'cp ' + file +  ' ' + wfile
                os.system(cmd)
                f     = pyfits.open(wfile)
                sdata = f[0].data
                hdr   = f[0].header

                sdata[sdata <    0] = 0
                sdata[sdata > 4000] = 0
                pyfits.update(wfile, sdata, hdr)
                f.close()
#
#--- if there are more than one file, merge all fits into one
#
                if len(todaylist) > 1:
                    for j in range(1, len(todaylist)): 

                        f     = pyfits.open(todaylist[j])
                        tdata = f[0].data
                        tdata[tdata <    0] = 0
                        tdata[tdata > 4000] = 0
                        f.close()

                        sdata = sdata + tdata

                    pyfits.update(wfile, sdata, hdr)
#
#--- find dom of the last file
#
                file = todaylist[len(todaylist) -1]
                stime = bcf.extractTimePart(file)
    
                if stime > 0:
                    ctime = tcnv.convertCtimeToYdate(stime)
                    (year, month, date, hours, minutes, seconds, ydate, dom, sectime) = tcnv.dateFormatConAll(ctime)
     
                ccd_dir = house_keeping + '/Defect/CCD' + str(ccd)
#
#---- extract(date_obs, ccd_dir, <fits header>, <input file>, <which quad>, <column position>, <x start>, <x end>)
#
                extract(ccd, date_obs, ccd_dir, head, wfile,  0,   0,   0,  255)
                extract(ccd, date_obs, ccd_dir, head, wfile,  1, 256, 256,  511)
                extract(ccd, date_obs, ccd_dir, head, wfile,  2, 512, 512,  767)
                extract(ccd, date_obs, ccd_dir, head, wfile,  3, 768, 768, 1023)

#
#--- for the test case, set dom to 4953
#
    if comp_test == 'test':
        dom = 4953

    return (int(dom))

#---------------------------------------------------------------------------------------------------
#-- extract: find bad pix and bad column for the data given                                      ---
#---------------------------------------------------------------------------------------------------

def extract(ccd, date_obs, ccd_dir, head, infile, quad, cstart, rstart, rend):

    """
    find bad pix and bad column for the data given
    Input:  ccd      --- ccd #
            date_obs --- observation date
            ccd_dir  --- the location of ccd<ccd #> data kpet
            head     --- header for the file
            infile   --- the data fits file location
            quad     --- quad # (0 - 3)
            cstart   --- column postion
            rstart   --- column starting postion
            rend     --- column ending position
    Output:  output from find_bad_col (warm/hot column locations)
             output from find_bad_pix_candidate (warm/hot pixel positions)
    """
#
#--- create data files; it could be empty at the end, but it will be used for bookkeeping 
#
    max_file     = head + '_q' + str(quad) + '_max'
    hot_max_file = head + '_q' + str(quad) + '_hot'
#
#--- extract the region we need 
#
    f      = pyfits.open(infile)
    sdata  = f[0].data
    varray = sdata[0:1023,int(rstart):int(rend)]
    f.close()
#
#---- find bad columns
#
    wout_dir     = './Working_dir/today_bad_col_' + str(ccd)
    mcf.rm_file(wout_dir)

    find_bad_col(varray, ccd, cstart, ccd_dir, head)
#
#--- find today's warm and hot pixel candidates
#
    find_bad_pix_candidate(varray, ccd, quad, date_obs, ccd_dir, max_file, hot_max_file)

#---------------------------------------------------------------------------------------------------
#--- mv_old_data: move the older data to the achive directory                                    ---
#---------------------------------------------------------------------------------------------------

def mv_old_data(ccd):
#
#--- find when is the 7 days ago in second from 1998.1.1
#
    today    = tcnv.currentTime("SEC1998")
#    cut_date = today - day7
    cut_date = today - day30
#
#--- get the list in the directory
#
    dfile = house_keeping + 'Defect/CCD' + str(ccd) + '/'
#
#--- check whether the directory is empty
#
    if not os.listdir(dfile):
        cmd = 'ls ' + house_keeping + 'Defect/CCD' + str(ccd) + '/* > ' +  zspace
        os.system(cmd)

        data = mcf.readFile(zspace)
        mcf.rm_file(zspace)
#
#--- compare the time stamp to the cut off time and if the file is older 
#--- than that date, move to gzip it and move to a save directory
#
        for ent in data:
            try:
                atemp = re.split('acis', ent)
                btemp = re.split('_',    atemp[1])
                bdate = float(btemp[0])
                if bdate < cut_date:
                    cmd = 'gzip ' + ent
                    os.system(cmd)
                    cmd = 'mv ' + ent + '.gz ' + data_dir + 'Old_data/CCD' + str(ccd) + '/.'
                    os.system(cmd)
            except:
                pass

#---------------------------------------------------------------------------------------------------
#--- find_bad_col: find warm columns                                                             ---
#---------------------------------------------------------------------------------------------------

def find_bad_col(varray, ccd, cstart, ccd_dir, head ):

    """
    find warm columns
    Input:  varray  --- data in 2 dim form [y, x] (numpy array)
            ccd     --- ccd #
            cstart  --- starting column #. the data are binned between 0 and 255.
            ccd_dir --- location of data saved
            head    --- header of the file
    Output: <ccd_dir>/<head>col --- a file which keeps a list of warm columns
    """
#
#--- set a data file name to record actual today's bad column positions
#
    bad_col_name = head + '_col'
    outdir_name  = ccd_dir + '/' + bad_col_name
#
#--- today's bad column list name at a working directory
#
    wout_dir     = './Working_dir/today_bad_col_' + str(ccd)
#
#--- bad column list for ccd
#
    bad_cols = bad_col_list[ccd]
    bcnt     = len(bad_cols)
    bList    = []
#
#---- make a list of just column # (no starting /ending row #)
#
    if bcnt > 0:
        for ent in bad_cols:
            atemp = re.split(':', ent)
            bList.append(int(atemp[0]))
#
#--- create a list of averaged column values
#
    avg_cols = create_col_avg(varray)
#
#--- set a global limit to find outlyers
#
    cfactor = col_factor
    climit = find_local_col_limit(avg_cols, 0, 255, cfactor)

    bcnum = 0
    for i in range(0, 255):
#
#--- check the row is a known bad column
#
        cloc = cstart + i                       #---- modify to the actual column position on the CCD
        chk  = 0
        if bcnt > 0:
            for comp in bList:
                if cloc == comp:
                    chk = 1
                    break
        if chk == 1:
            continue
#
#--- find the average of the column and if the column is warmer than the limit, check farther
#
        if avg_cols[i] > climit:
#
#--- local limit
#
            (llow, ltop) = find_local_range(i)
            cfactor      = 2.0
            l_lim        = find_local_col_limit(avg_cols, llow, ltop, cfactor, ex = i)
#
#--- if the column is warmer than the local limit, record it
#
            if avg_cols[i] > l_lim:
                if cloc != 0:
                    print_result(outdir_name, cloc)
                    bcnum += 1
#
#---- clean up the file (removing duplicated lines)
#
    if bcnum > 0:
        mcf.removeDuplicate(outdir_name, dosort=0)
#
#--- record today's bad column list name at a working directory
#
        print_result(wout_dir, bad_col_name)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def find_local_range(i):
#
#--- setting a local area range
#
    llow  = i - 5
    ltop  = i + 5
#
#--- at the edge of the area, you still want to keep 10 column length
#
    if llow < 0:
        ltop -= llow
        llow  = 0

    if ltop > 255:
        llow -= ltop - 255
        ltop  = 255

    return(llow, ltop)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def create_col_avg(varray):

    avg_cols = [0 for x in range(0, 255)]
    for i in range(0, 255):
        l_mean = numpy.mean(varray[:,i])
        avg_cols[i] = l_mean

    return avg_cols


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def find_local_col_limit(avg_cols, llow, ltop, cfactor,  ex=-999):

    sum  = 0
    tot  = 0
    for i in range(llow,ltop):
        if i == ex:
            continue
    
        sum   += avg_cols[i]
        tot   += 1
    
    lavg = sum / tot

    sum2 = 0
    tot  = 0
    for i in range(llow,ltop):
        if i == ex:
            continue
    
        ldiff  = avg_cols[i] - lavg
        sum2  += ldiff * ldiff
        tot   += 1
    
    lstd = math.sqrt(sum2 / tot)
    
#    l_lim = lavg + col_factor * lstd
    l_lim = lavg + cfactor * lstd
    
    return(l_lim)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def print_result(outdir_name, line):

    fo3 = open(outdir_name, 'a')
    fo3.write(str(line))
    fo3.write('\n')
    fo3.close()

#---------------------------------------------------------------------------------------------------
#--- chk_bad_col: find bad columns for a given ccd                                               ---
#---------------------------------------------------------------------------------------------------

def chk_bad_col(ccd):

    """
    find bad columns for a given ccd
    Input:  ccd      --- ccd #
    Output: bad_cols --- a list of bad columns
    """
    bad_cols = []

    dfile = house_keeping + 'Defect/CCD' + str(ccd) + '/'

    if  os.listdir(dfile):
        cmd     = 'ls -rt ' + dfile + '/* > ' + zspace
        os.system(cmd)
        test = open(zspace).read()
        mcf.rm_file(zspace)
        m1 = re.search('col', test)
        if m1 is not None:
            chk = 1
        else:
            chk = 0
    else:
        chk = 0

    if chk == 1:

        cmd     = 'ls -rt ' + dfile + '/*col > ' + zspace
        os.system(cmd)
        collist = mcf.readFile(zspace)
        mcf.rm_file(zspace)
#
#--- if there is more than three col files and if we have new bad col today, procced the process
#
        dlen = len(collist)
    
        if dlen > 2:
            file  = collist[dlen-1]
            file1 = mcf.readFile(file)
    
            file  = collist[dlen-2]
            file2 = mcf.readFile(file)
    
            colcand = []
            for ent in file1:
                try:
                    val = float(ent)            #--- try to weed out none digit entries
                    for comp in file2:
                        if ent == comp:
                            colcand.append(ent)
                            break
                except:
                    pass
#
#--- if columns appear in both files, try the third
#
            if len(colcand) > 0: 
    
                file  = collist[dlen-2]
                file3 = mcf.readFile(file)
    
                for ent in colcand:
                    for comp in file3:
                        if ent == comp:
                            bad_cols.append(ent)
                            break
    
    
                if len(bad_cols) > 0:
                    bad_cols = mcf.removeDuplicate(bad_cols,  chk = 0, dosort=0)

    return bad_cols

 
#---------------------------------------------------------------------------------------------------
#--- print_bad_col: update bad column output files                                               ---
#---------------------------------------------------------------------------------------------------

def print_bad_col(ccd, bad_col_list, dom):

    """
    update bad column output files
    Input:  ccd          --- ccd #
            bad_col_list --- a list of bad columns on the ccd
            dom          --- today's (or given data's) DOM
    Output: Disp_dir/col<ccd#>     --- today's bad columns
            Disp_dir/hit_col<ccd#> --- history of bad columns
    """

    blen          = len(bad_col_list)
    dom           = int(dom)
    (year, ydate) = tcnv.DOMtoYdate(dom)
    date          = str(year) + ':' + str(int(ydate))

    line  = data_dir + 'Disp_dir/col' + str(ccd)
    f1    = open(line, 'w')
    line2 = data_dir + 'Disp_dir/hist_col' + str(ccd)
    f2    = open(line2, 'a')
#
#--- even if there is no data, update history file
#
    if blen == 0:
        line = str(dom) + '<>' + date + '<>:\n'
        f2.write(line)
    else:
#
#--- if there are bad col, update history file and update col<ccd> file
#
        line = str(dom) + '<>' + date + '<>' 
        for ent in bad_col_list:
            f1.write(ent)
            f1.write('\n')

            line = line + ':' + ent

        line  = line + '\n'
        f2.write(line)

    mcf.removeDuplicate(line2, chk =1, dosort=0)
 
#---------------------------------------------------------------------------------------------------
#--- find_bad_pix_candidate: find bad pixel candidates for the next step                        ----
#---------------------------------------------------------------------------------------------------

def  find_bad_pix_candidate(varray, ccd, quad, date_obs, ccd_dir, max_file, hot_max_file):

    """
    find dad pixel candidates for the next step... they are bad pixel for just today's data
    Input:  varray       --- 2x2 data surface  [y, x] (numpy array)
            ccd          --- ccd #
            quad         --- quad 0 - 3
            date_obs     --- obs date
            ccd_dir      --- data location
            max_file     --- <head>_<quad>_max: a file name which will contain warm pixel data  (e.g. acis485603580_q1_max)
            hot_max_file --- <head>_<quad>_hot: a file name which will contain hot pixel data (e.g. acis485603580_q1_hot)
    Output: <ccd_dir>/max_file     --- file contains warm pixel list
            <ccd_dir>/hot_max_file --- file contains hot pixel list

    """
#
#--- set a couple of arrays
#
    warm_list = []
    hot_list  = []
    wsave     = ''
    hsave     = ''
#
#--- divide the quad to 8x32 areas so that we can compare the each pix to a local average
#
    for ry in range(0, 32):
        ybot  = 32 * ry
        ytop  = ybot + 31
        ybot2 = ybot
        ytop2 = ytop
#
#--- even if the pixel is at the edge, use 8 x 32 area
#
        if ytop > 1023:
            diff   = ytop -1023 
            ytop2  = 1023
            ybot2 -= diff

        for rx in range (0, 8):
            xbot  = 32 * rx
            xtop  = xbot + 31
            xbot2 = xbot
            xtop2 = xtop

            if xtop > 255:
                diff   = xtop - 255
                xtop2  = 255
                xbot2 -= diff

            lsum  = 0.0
            lsum2 = 0.0
            lcnt  = 0.0
            for ix in range(xbot2, xtop2):
                for iy in range(ybot2, ytop2):
                    lsum  += varray[iy, ix]
                    lcnt  += 1

            if lcnt < 1:
                continue

            lmean = float(lsum) / float(lcnt)

            for ix in range(xbot2, xtop2):
                for iy in range(ybot2, ytop2):
                    lsum2 += (varray[iy, ix]  - lmean) * (varray[iy, ix]  - lmean)

            lstd  = math.sqrt(lsum2 / float(lcnt))
            warm  = lmean + factor * lstd
            hot   = lmean + hot_factor

            for ix in range(xbot, xtop2):
                for iy in range(ybot, ytop2):
                    if varray[iy, ix]  >= warm:
                        (cwarm, chot, cmean, cstd) = local_chk(varray, ix, iy, lmean, lstd, warm , hot)
#
#--- hot pix check
#
                        if varray[iy, ix] > chot:
                            line = ccd_dir + '/' + hot_max_file
                            hot_list.append(line)

                            f     = open(line, 'a')
#
#--- adjusting to correction position
#
                            mix   = ix + 1
                            miy   = iy + 1
                            aline = str(mix) + '\t' + str(miy) + '\t' + str(varray[iy, ix]) + '\t' + date_obs + '\t' + str(cmean) + '\t' + str(cstd) + '\n'
                            f.write(aline)
                            f.close()
#
#--- warm pix check
#
                        elif varray[iy, ix] > cwarm:
                            line = ccd_dir + '/' + max_file
                            warm_list.append(line)

                            f     = open(line, 'a')
                            mix   = ix + 1
                            miy   = iy + 1
                            aline = str(mix) + '\t' + str(miy) + '\t' + str(varray[iy, ix]) + '\t' + date_obs + '\t' + str(cmean) + '\t' + str(cstd) + '\n'
                            f.write(aline)
                            f.close()
#
#--- remove dupulicated line.
#
    if len(warm_list) > 0:
        today_warm_list = mcf.removeDuplicate(warm_list, chk = 0, dosort=0)
    else:
        today_warm_list = []

    if len(hot_list) > 0:
        today_hot_list  = mcf.removeDuplicate(hot_list,  chk = 0, dosort=0)
    else:
        today_hot_list  = []
#
#--- print out the data; even if it is empty, we still create a file
#
    line = ccd_dir + '/' + max_file
    try:
        if len(today_warm_list) > 0:
#
#--- keep the record of today's data
#
            aline = './Working_dir/today_bad_pix_' + str(ccd) + '_q' + str(quad)
            f     = open(aline,  'a')
            f.write(line)
            f.write("\n")
            f.close()
    except:
        pass

    line = ccd_dir + '/' + hot_max_file
    try:
        if len(today_hot_list) > 0:

            aline = './Working_dir/today_hot_pix_' + str(ccd) + '_q' + str(quad)
            f     = open(aline,  'a')
            f.write(hot_max_file)
            f.write("\n")
            f.close()
    except:
        pass

#---------------------------------------------------------------------------------------------------
#--- select_bad_pix: find bad pixels                                                             ---
#---------------------------------------------------------------------------------------------------

def select_bad_pix(ccd, quad):

    """
    find bad pixels for a given ccd/quad
    Input:  ccd   --- ccd #
            quad  --- quad #
    Output: output from identifyBadEntry
            warm_data_list
            hot_data_list
    """
#
#--- warm pixels
#
    warm_data_list = identifyBadEntry(ccd, quad, 'today_bad_pix', '_max')
#
#--- hot pixels
#
    hot_data_list  = identifyBadEntry(ccd, quad, 'today_hot_pix', '_hot')

    return(warm_data_list, hot_data_list)

#---------------------------------------------------------------------------------------------------
#--- identifyBadEntry: find which pixels are warm/hot the last three observations                 --
#---------------------------------------------------------------------------------------------------

def identifyBadEntry(ccd, quad, today_list, ftail):

    """
    find which pixels are warm/hot the last three observations
    Input:  ccd        --- ccd #
            quad       --- quad #
            today_list --- today's list
            ftail      ---  pix (warm case)/hot (hot_case)
    Output: bad_list   --- warm/hot pixel list
    """
    bad_list = []
#
#--- check whether we have any bad pixels/columns in today's data
#
    line = './Working_dir/' + today_list +  '_' + str(ccd) + '_q' + str(quad)

    bad  = mcf.readFile(line)
    if len(bad) > 0:

        for i in range(0, len(bad)):
            chk   = mcf.isFileEmpty(bad[i])
            nfile = bad[i]
#
#--- if there are, check the past data, and find two previous records
#
            if chk > 0:
                cmd  = 'ls ' + house_keeping + '/Defect/CCD' + str(ccd) + '/acis*_q' + str(quad) + ftail + '>' + zspace
                os.system(cmd)

                data = mcf.readFile(zspace)
                mcf.rm_file(zspace)

                lcnt  = len(data)
                if lcnt == 0:
                    continue

                lcnt1 = lcnt -1
                for i in range(0, lcnt):
                    j = lcnt1 - i
                    if data[j] == nfile:                                    #--- Ok we located today's data in the data directory
                        if j > 1:
                            chk2 = mcf.isFileEmpty(data[j-1])               #--- check whether one before is empty or not
                            if chk2 > 0:
                                chk3 = mcf.isFileEmpty(data[j-2])           #--- if it is not, empty, check whether one before is empty or not
                                if chk3 > 0:
#
#--- three consecuitve data sets are not empty, let check whether 
#--- any pixels are warm three consecutive time.
#
                                    file1 = nfile 
                                    file2 = data[j-1]
                                    file3 = data[j-2]
 
                                    bad_list = find_bad_pix(ccd, quad, file1, file2, file3)

    return (bad_list)

#---------------------------------------------------------------------------------------------------
#-- print_bad_pix_data: update bad pixel data files                                              ---
#---------------------------------------------------------------------------------------------------

def print_bad_pix_data(ccd, data_list, bind, today_time = 'NA'):

    """
    update bad pixel data files
    Input:  ccd   --- ccd #
            data_list  --- bad pixel list
            bind       --- warm/hot
            today_time --- DOM of the data
    Output: totally_new<ccd>
            all_past_bad_pix<ccd>
            new_ccd<ccd>
            ccd<ccd>
            hist_ccd<ccd>

            similar output for hot pixel data
    """
    if comp_test == 'test':
        dom = 4953
    elif today_time != 'NA':
        dom  = today_time
    else:
        dom  = int(tcnv.currentTime(format = 'DOM'))

    line = tcnv.DOMtoYdate(dom)
    date = str(line[0]) + ':' + str(int(line[1]))
#
#--- check any pixels are listed in totally_new<ccd> list (which lists new bad pix occured only in the last two weeks)
#
    if bind == 'warm':
        file5 = data_dir + 'Disp_dir/hist_ccd'         + str(ccd)
    else:
        file5 = data_dir + 'Disp_dir/hist_hccd'        + str(ccd)

    pline = str(dom) + '<>' + date +  '<>'

    if len(data_list) > 0:
        for ent in data_list:
            atemp = re.split(':', ent)
            pline = pline + ':(' + atemp[4] + ',' + atemp[5] + ')' 

        pline = pline + '\n'

    else:
        pline = pline + ':' + '\n'
#
#--- add to history data
#--- first check whether this is a duplicated date, if so, just ignore
#
    data  = mcf.readFile(file5)

    chk = 0
    if len(data) > 0:
        fn =open(file5, 'w')
        for ent in data:
            atemp = re.split('<>', ent)
            try:
                float(atemp[0])
                ldom  = int(atemp[0])
            except:
                continue
            if ldom < dom:
                fn.write(ent)
                fn.write("\n")
            else:
                fn.write(pline)
                chk = 1
                break
        fn.close()

    if chk == 0:
        fn =open(file5, 'a')
        fn.write(pline)
        fn.close()

#---------------------------------------------------------------------------------------------------
#--- find_bad_pix: find bad pixel by comparing three consecutive data                            ---
#---------------------------------------------------------------------------------------------------

def  find_bad_pix(ccd, quad,  file1, file2, file3):

    """
    find bad pixel by comparing three consecutive data
    Input:  ccd     --- ccd #
            quad    --- quad #
            file1   --- first data file
            file2   --- second data file
            file3   --- thrid data file
    Output: cleaned --- bad pixel list
    """
    out_file = []

    [x1, y1, line1] = readBFile(ccd, file1)
    [x2, y2, line2] = readBFile(ccd, file2)
#
#--- comparing first two files to see whether there are same pixels listed
#--- if they do, save the information $cnt_s will be > 0 if the results are positive
#
    if len(x1) > 0 and len(x2) > 0:
        [xs, ys, ls ] = pickSamePix(x1, y1, line1, x2, y2, line2)

        if len(xs) > 0:
            [x3, y3, line3] = readBFile(ccd, file3)
            [xs2, ys2, ls2] = pickSamePix(xs, ys, ls, x3, y3, line3)

            if len(xs2) > 0:
                for i in range(0, len(xs2)):
                    try:
                        val   = float(xs2[i])                         #---- checking whether there is actually values
                        atemp = re.split('\s+|\t+', ls2[i])
                        line  = str(ccd) + ':' + str(quad) + ':' + atemp[3] + ':' + xs[i] + ':' + ys[i]
                        out_file.append(line)

                    except:
                        pass

    if len(out_file) > 0:
        cleaned = mcf.removeDuplicate(out_file, chk = 0, dosort=0)
    else:
        cleaned = []
    return cleaned

#---------------------------------------------------------------------------------------------------
#---  readBFile: read out ccd data file                                                         ----
#---------------------------------------------------------------------------------------------------

def readBFile(ccd, file):

    """
    read out ccd data file
    Input:  ccd  --- ccd #
            file --- file name
    Output: a list of (x position list, y position list, value list)
    """
    data = mcf.readFile(file)

    xa = []
    ya = []
    la = []
    if len(data) > 0:
        for ent in data:
            atemp = re.split('\s+|\t+', ent)
            xa.append(atemp[0])
            ya.append(atemp[1])
            la.append(ent)

    return (xa, ya, la)

#---------------------------------------------------------------------------------------------------
#--- pickSamePix: find pixels appear in two files given                                          ---
#---------------------------------------------------------------------------------------------------

def pickSamePix(x1, y1, line1, x2, y2, line2):

    """
    find pixels appear in two files given
    Input:  x1    --- x coordinates of the first file
            y1    --- y coordinates of the first file
            line1 --- all data information associates to x1, y1 pixel
            x2    --- x coordinates of the second file
            y2    --- y coordinates of the second file
            line2 --- all data information associates to x2, y2 pixel
    Output: list of [x coordinates, y coordinates, pixel info]
    """
    x_save = []
    y_save = []
    l_save = []

    for i in range(0, len(x1)):
        for j in range(0, len(x2)):
            if x1[i] == x2[j] and y1[i] == y2[j] and x1[i] != '':
                x_save.append(x1[i])
                y_save.append(y1[i])
                l_save.append(line1[i])
                break
    return (x_save, y_save, l_save)

#---------------------------------------------------------------------------------------------------
#--- local_chk: compute local mean, std, warm limit and hot limit                                ---
#---------------------------------------------------------------------------------------------------

def local_chk(varray, ix, iy, lmean, lstd, warm, hot):

    """
    compute local mean, std, warm limit and hot limit 
    Input:  varray --- data array (2D) [y, x] (numpy array)
            ix     --- x coordinate of the pixel of interest
            iy     --- y coordinate of the pixel of interest
            lmean  --- mean value of the area
            lstd   --- standard deviation of the area
            warm   --- warm limit of the area
            hot    --- hot limit of the area
    Output: leanm  --- mean value of the local area
            lstd   --- standard deviation of the local area
            warm   --- warm limit of the local area
            hot    --- hot limit of the local area
    """
#
#--- check the case, when the pixel is located at the coner, and cannot
#--- take 16x16 around it.  if that is the case, shift the area
#
    x1 = ix - 8
    x2 = ix + 8
    if(x1 < 0):
        x2 += abs(x1)
        x1  = 0
    elif x2 > 255:
        x1 -= (x2 - 255)
        x2  = 255

    y1 = iy - 8
    y2 = iy + 8
    if(y1 < 0):
        y2 += abs(y1)
        y1  = 0
    elif y2 > 1023:
        y1 -= (y2 - 1023)
        y2  = 1023 

    csum  = 0.0
    csum2 = 0.0
    ccnt  = 0.0
    for xx in range(x1, x2+1):
        for yy in range(y1, y2+1):
            try:
                cval = float(varray[yy, xx])
                cval = int(cval)
            except:
                cval = 0
            csum  += cval
            csum2 += cval * cval 
            ccnt  += 1
    try: 
        cmean = float(csum) /float(ccnt)
        cstd  = math.sqrt(float(csum2) / float(ccnt) - cmean * cmean)
        cwarm = cmean + factor * cstd
        chot  = cmean + hot_factor
        return (cwarm, chot, cmean, cstd)
    except:
        cwarm = lmean + factor * lstd
        chot  = lmean + hot_factor
        return (lmean, lstd, warm, hot)

#---------------------------------------------------------------------------------------------------
#--- extractCCDInfo: extract CCD information from a fits file                                    ---
#---------------------------------------------------------------------------------------------------

def extractCCDInfo(file):

    """
    extreact CCD infromation from a fits file
    Input:  file        --- fits file name
    Output: ccd_id      --- ccd #
            readmode    --- read mode
            date_obs    --- observation date
            overclock_a --- overclock a 
            overclock_b --- overclock b 
            overclock_c --- overclock c 
            overclock_d --- overclock d 
    """
#
#--- read fits file header
#
    try:
        f           = pyfits.open(file)
        hdr         = f[0].header
        ccd_id      = hdr['CCD_ID']
        readmode    = hdr['READMODE']
        date_obs    = hdr['DATE-OBS']
        overclock_a = hdr['INITOCLA']
        overclock_b = hdr['INITOCLB']
        overclock_c = hdr['INITOCLC']
        overclock_d = hdr['INITOCLD']
    
        return [ccd_id, readmode, date_obs, overclock_a, overclock_b, overclock_c, overclock_d]
    except:
        return ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']

#---------------------------------------------------------------------------------------------------
#--- read_bad_pix_list: read knwon bad pixel list                                                ---
#---------------------------------------------------------------------------------------------------

def read_bad_pix_list():

    """
    read knwon bad pixel list
    Input: house_keeping + '/Defect/bad_pix_list'
    Output: bad_pix_list --- a list of lists of bad pixels separated by CCD
    """

    line = house_keeping + '/Defect/bad_pix_list'
    data = mcf.readFile(line)
#
#--- initialize the list
#
    for i in range(0, 10):
        exec "badpix%s = []" % (i)
#
#--- separate bad pixels into different CCDs
#
    for ent in data:
        m = re.search('#', ent)
        if m is None:
            atemp = re.split(':', ent)
            line = '"' + str(atemp[2]) + ':' + str(atemp[3]) + '"'
            exec "badpix%s.append(%s) " % (str(atemp[0]), line)
#
#--- put all bad pix lists into one list
#
    bad_pix_list = []
    for i in range(0, 10):
        exec "bad_pix_list.append(badpix%s)" % (str(i))

    return bad_pix_list


#---------------------------------------------------------------------------------------------------
#---  read_bad_col_list: read in known bad column lists                                          ---
#---------------------------------------------------------------------------------------------------

def read_bad_col_list():

    """
    read in known bad column lists
    Input:  house_keeping + '/Defect/bad_col_list
    Output: bad_col_list --- a list of list of bad columns separated by CCDs
    """

    line = house_keeping + '/Defect/bad_col_list'
    data = mcf.readFile(line)
#
#--- initialize the list
#
    for i in range(0, 10):
        exec "badcol%s = []" % (str(i))
#
#--- separate bad columns  into different CCDs
#
    for ent in data:
        m = re.search('#', ent)
        if m is None:
            atemp = re.split(':', ent)
            line = '"' + str(atemp[3]) + ':' + str(atemp[2]) + ':' + str(atemp[3]) + '"'
            exec "badcol%s.append(%s) " % (str(atemp[0]), line)
#
#--- put all bad col lists into one list
#
    bad_col_list = []
    for i in range(0, 10):
        exec "bad_col_list.append(badcol%s)" % (str(i))

    return bad_col_list

#---------------------------------------------------------------------------------------------------
#--- removeIncompteData: removing files which indicated "imcoplete"                             ----
#---------------------------------------------------------------------------------------------------

def removeIncompteData(cut_time):

    """
    remove files which are indicated "imcoplete" by cut_time (if the file is created after cut_time)
    Input:  cut_time: the cut time which indicates when to remove the data file
    Output: None, but delete files
    """

    for ccd in range(0, 10):
        file = data_dir + 'Disp_dir/data_used' + str(ccd)
        trimFile(file, cut_time, 0)
        
    for head in ('change_ccd', 'change_col', 'imp_ccd', 'new_ccd', 'imp_col', 'new_col'):
        for ccd in range(0, 10):
            file  =  data_dir + 'Disp_dir/' + head + str(ccd)
            trimFile(file, cut_time, 1)

    for ccd in range(0, 10):
        file = data_dir + 'Disp_dir/hist_ccd' + str(ccd)
        trimFile(file, cut_time, 1)

#---------------------------------------------------------------------------------------------------
#---  trimFile: drop the part of the data from the file if the data is created after cut_time     --
#---------------------------------------------------------------------------------------------------

def trimFile(file, cut_time, dtype):

    """
    drop the part of the data from the file if the data is created after cut_time
    Input:  file     --- file name
            cut_time --- the cut time
            dtype    --- how to find a dom, if dtype == 0: the time is in form of 20013:135. otherwise, in DOM
    Output: file     --- updated file
    """

    try:
        data = mcf.readFile(file)
        if len(data) > 0:
    
            f    = open(zspace, 'w')
            for  ent in data:
                try:
                    if dtype == 0:
                        atemp = re.split(':', ent)
                        year  = float(atemp[0])         #--- checking whether they are in digit
                        ydate = float(atemp[1])
                        year  = int(year)
                        ydate = int(ydate)
                        dtime = tcnv.findDOM(year, ydate, 0, 0, 0)  
                    else:
                        atemp = re.split('<>', ent)
                        dtime = int(atemp[0])
                    if dtime >= cut_time:
                        break
                    else:
                        f.write(ent)
                        f.write('\n')
                except:
                    pass

            f.close()
            cmd = 'mv ' + zspace + ' ' + file
            os.system(cmd)
    except:
        pass

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def set_date(dom):

    [year, ydate] = tcnv.DOMtoYdate(dom)
    [month, date]   = tcnv.changeYdateToMonDate(year, ydate)
    lyear = str(year)

    cmon = str(month)
    if int(month) < 10:
        cmon = '0' + cmon
    cdate = str(date)
    if int(date) < 10:
        cdate = '0' + cdate
    cyear = lyear[2] + lyear[3]
    start = cmon + '/' + cdate + '/' + cyear + ',00:00:00'
    lyear = str(year)

    dom_next = dom + 1
    [year, ydate] = tcnv.DOMtoYdate(dom_next)
    [month, date]   = tcnv.changeYdateToMonDate(year, ydate)

    cmon = str(month)
    if int(month) < 10:
        cmon = '0' + cmon
    cdate = str(date)
    if int(date) < 10:
        cdate = '0' + cdate
    cyear = lyear[2] + lyear[3]
    stop = cmon + '/' + cdate + '/' + cyear + ',00:00:00'

    return(start,stop)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def get_data_out(start, stop):

    fdir = exc_dir + 'Temp_data/'
    cmd  = 'rm  -rf ' + fdir
    os.system(cmd)

    cmd  = 'mkdir ' + fdir
    os.system(cmd)
#
#--- write  required arc4gl command
#
    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=0\n'
    line = line + 'filetype=bias0\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop='  + str(stop) + '\n'
    line = line + 'go\n'
    f= open(zspace, 'w')
    f.write(line)
    f.close()

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 =  ' echo ' +  hakama + ' |/bin/nice -n17 arc4gl -U' + dare + ' -Sarcocc -i' + zspace 
    cmd  = cmd1 + cmd2

    try:
#
#--- run arc4gl
#
        bash(cmd,  env=ascdsenv)
        mcf.rm_file(zspace)
    
        cmd = 'ls * > ' + zspace
        os.system(cmd)
        ltest = open(zspace, 'r').read()
        mcf.rm_file(zspace)
        m1    = re.search('bias0.fits', ltest)
        if m1 is not None:
            cmd = "mv *fits* " + exc_dir + "/Temp_data/."
            os.system(cmd)
    
            cmd = "/bin/nice -n17 gzip -d " + exc_dir +  "/Temp_data/*gz"
            os.system(cmd)
    
            cmd = 'ls ' + exc_dir + '/Temp_data/*fits > '+  zspace
            os.system(cmd)
    
            fx = open(zspace, 'r')
            fdata = [line.strip() for line in fx.readlines()]
            fx.close()
            mcf.rm_file(zspace)
            return fdata
        else:
            return 'na'

    except:
        mcf.rm_file(zspace)
        return 'na'


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def find_data_collection_interval():

    tlist = tcnv.currentTime(format='UTC')
    tyear = tlist[0]
    tyday = tlist[7]
    tdom  = tcnv.YdateToDOM(tyear, tyday)

    file  = data_dir + 'Disp_dir/hist_ccd3'
    f     = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    chk   = 0
    k     = 1
    while(chk == 0):
        atemp = re.split('<>', data[len(data)-k])
        ldom  = atemp[0]
        if mcf.chkNumeric(ldom) == True:
            ldom = int(ldom)
            chk = 1
            break
        else:
            k += 1

    ldom += 1
    return(ldom, tdom)


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def mv_old_file(dom):

    dom -= 30
    if dom > 0:
        [year, ydate] = tcnv.DOMtoYdate(dom)
        sydate = str(ydate)
        if ydate < 10:
            sydate = '00' + sydate
        elif ydate < 100:
            sydate = '0' + sydate

        atime = str(year) + ':' + sydate + ':00:00:00'
        stime = tcnv.axTimeMTA(atime)

        cmd = 'ls ' + house_keeping + '/Defect/CCD*/* > ' + zspace
        os.system(cmd)
        fs = open(zspace, 'r')
        ldata = [line.strip() for line in fs.readlines()]
        fs.close()
        mcf.rm_file(zspace)
        for ent in ldata:
            atemp = re.split('\/acis', ent)
            btemp = re.split('_', atemp[1])
            if int(btemp[0]) < stime:
                out = ent
                out = out.replace('Defect', 'Defect/Save')
                cmd = 'mv ' + ent + ' ' + out 
                os.system(cmd)


#--------------------------------------------------------------------

if __name__ == '__main__':
#
#--- if this is a test case, prepare the test output directory
#
    if comp_test == 'test':
        test_prep()
#
#--- read known bad pixels / columns
#
    bad_pix_list = read_bad_pix_list()
    bad_col_list = read_bad_col_list()
#
#--- run the control function; first find out data colleciton interval
#
    if len(sys.argv) == 3:
        start = sys.argv[1]
        start.strip()
        start = int(start)
        stop  = sys.argv[2]
        stop.strip()
        stop  = int(stop)
    else:
        (start, stop) = find_data_collection_interval()

    for dom in range(start, stop):

        find_bad_pix_main(dom)
        mv_old_file(dom)



