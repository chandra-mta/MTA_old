#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       acis_gain_extract_data.py: extract gain data from acis evt1 files                           #
#                                                                                                   #
#           author: t. isobe(tisobe@cfa.harvard.edu)                                                #
#                                                                                                   #
#           Last Update:    Jan 05, 2017                                                            #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits as pyfits
from astropy.table import Table
import unittest

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Gain/house_keeping/dir_list_py'

f= open(path, 'r')
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
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts

from kapteyn import kmpfit

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- a couple of things needed
#
dare   = mcf.get_val('.dare',   dir = bin_data, lst=1)
hakama = mcf.get_val('.hakama', dir = bin_data, lst=1)

working_dir = exc_dir + '/Working_dir/'

#
#---- peak position for peaks are:
#---- $pos2: Al K<---> 1486.70;
#---- $pos3: Ti K<---> 4510.84;
#---- $pos1: Mn K<---> 5898.75;
#
ev = [1486.70, 4510.84, 5898.75]

cselect = ['time', 'ccd_id', 'node_id', 'pha', 'grade']


#---------------------------------------------------------------------------------------------------
#-- acis_gain_get_data: extract acis evt1 files and compute monnth averaged gain and offset       --
#---------------------------------------------------------------------------------------------------

def acis_gain_get_data(year='', month=''):

    """
    extract acis evt1 files and compute month averaged gain and offset
    Input:  year/month:     the month you want to compute. if 0, the last month is used
    Ouput:  <data_dir>/ccd<ccd>_<node>: 
                <s time> <al peak> <mn peak> <ti peak> <slope> <s error> <intercept> <ierro>
    """
#
#--- get a new data list
#
    [obsid_list, start_list, stop_list] = get_input_data_list(year, month)

    tstart = start_list[0]
    tstop  = stop_list[len(stop_list)-1]
    mtime  = int (tstart + 0.5 * (tstop - tstart))

#
#--- if there is no new data, just exit
#
    if len(obsid_list) > 0:
#
#--- extract alldata
#
        data_set  = get_new_data(obsid_list,start_list, stop_list)
#
#--- get pha profile parameter for each ccd and node

        ik = 0
        for ccd in range(0, 10):
            for node in range(0, 4):
#
#--- check whether parameters are computed. if not skip the ccd/node
#
                out =  extract_gain_info(data_set, ccd, node)

                if len(out) <= 1:
                    continue

                [al_cent, mn_cent, ti_cent, b, a, be, ae] = out

                alpos    = str(round(al_cent, 4))
                mnpos    = str(round(mn_cent, 4))
                tipos    = str(round(ti_cent, 4))
                slope    = str(round(b,       4))
                intcept  = str(round(a,       4))
                serr     = str(round(be,      4))
                ierr     = str(round(ae,      4))
#
#--- output file name
#
                out_name = data_dir + 'ccd' + str(ccd) + '_' + str(node)
#
#--- data line
#
                line     = str(mtime) + '\t' + alpos + '\t' + mnpos + '\t' + tipos + '\t'
                line     = line  + slope + '\t' + serr + '\t'  + intcept + '\t' + ierr + '\n'
#
#--- now print
#
                fo = open(out_name, 'a')
                fo.write(line)
                fo.close()

#---------------------------------------------------------------------------------------------------
#-- get_new_data: extract fits for the obsid, then extrat data needed                             --
#---------------------------------------------------------------------------------------------------

def get_new_data(obsid_list, start_list, stop_list):

    """
    extract fits for the obsid, then extrat data needed
    input:  obsid_list  --- a list of obsids
            start_list  --- a list of start time of the observation
            stop_list   --- a list of stop time of the observation
    output: data_set    --- a list of data sets
    """

    data_set = []
#
#--- find middle of the time. it will be used as a time stamp for this data set
#
    tstart = start_list[0]
    tstop  = stop_list[len(stop_list)-1]
    mtime  = int (tstart + 0.5 * (tstop - tstart))
#    
#--- extract acis event1 file and combined all of them
#
    mcf.mk_empty_dir(working_dir)
    pobsid    = []
    fits_list = []
    
    for i in range(0, len(obsid_list)):
        obsid = obsid_list[i]
        start = start_list[i]
        stop  = stop_list[i]

#
#--- check whether this data is already extreacted. if so, don't re-extrad the data
#
        chk = 0
        for comp in pobsid:
            if obsid == comp:
                chk = 1
                break

        if chk == 0:
            fits   = extract_acis_evt1(obsid)
            pobsid.append(obsid)
            if fits != 'na':
                fits_list.append(fits)
        else:
            fits = 'na'
            for ent in fits_list:
                m1 = re.search(obsid, ent)
                if m1 is not None:
                    fits = ent
                    break

        if fits == 'na':
                continue
#
#--- "Table.read" opens fits file and read fits table data
#
        rfits = working_dir + fits
        tdata = Table.read(rfits, hdu=1)
        tdiff = stop - start
#
#--- extract specified time range, pha range, and chipy
#
        mask  = (tdata.field('time') >= start) & (tdata.field('time') <= stop) & (tdata.field('pha')  <= 4000) & (tdata.field('chipy') <= 20) 
        tdata = tdata[mask]
        if len(tdata) < 1000:
            continue
        tdata = tdata[cselect]
#
#--- grade
#
        mask  = (tdata.field('grade') <= 6) & (tdata.field('grade') != 1) & (tdata.field('grade') != 5)
        tdata = tdata[mask]

        data_set.append(tdata)

    return data_set

#---------------------------------------------------------------------------------------------------
#-- extract_gain_info: create pha count profile from given data sets and fit model parameters    ---
#---------------------------------------------------------------------------------------------------

def extract_gain_info(data_set, ccd, node):

    """
    create pha count profile from given data sets and fit model parameters
    input: data_set         --- a list of extracted fits data
           ccd              --- ccd #
           node             --- node #
    output: d_list : [al_cent, mn_cent, ti_cent, b, a, be, ae]
                    al_cent --- center of al line
                    mn_cent --- center of mn line
                    ti_cent --- center of ti line
                    b       --- slope of the fitted line
                    a       --- intercept of the fitted line
                    be      --- the error of the slope
                    ae      --- the error of the intercept
    """

#
#--- create a histgram data for specified CCD / Node combination
#
    hist = extract_hist_data(data_set, ccd, node)
#
#--- if the hist data is empty, just add an empty list for house keeping
#
    if hist == 'na':
        return []
#
#--- Mn K alpha
#
    y      = hist[1200:2500]

    ymax   = max(y)
    xpos   = y.index(ymax) + 1200
    hwidth = 200
#
#--- if the count rate is too low, we cannot fit the data; so limit data larger than 20 counts
#
    start  = xpos - hwidth
    stop   = xpos + hwidth
    ybin   = hist[start:stop]
    chk    = 0
    for ent in ybin:
        chk += int(ent)

    if chk < 20:
        return []

    [mn_amp, mn_cent, mn_width, floor] = fit_pmodel(hist, ymax, xpos, hwidth)
#
#--- AL K alpha
#
    ymax   = 0.5  * mn_amp
    xpos   = 0.25 * mn_cent
    hwidth = 50

    [al_amp, al_cent, al_width, floor] = fit_pmodel(hist, ymax, xpos, hwidth)
#
#--- Ti K alpha
#
    ymax   = 0.5   * mn_amp
    xpos   = 0.765 * mn_cent
    hwidth = 100

    [ti_amp, ti_cent, ti_width, floor] = fit_pmodel(hist, ymax, xpos, hwidth)

#
#--- fit a straight line
#
    pos      = [al_cent, ti_cent, mn_cent]
    p0       = [0, 1]
    fitobj   = kmpfit.simplefit(lmodel, p0, ev, pos)
    [a, b]   = fitobj.params
    [ae,be]  = fitobj.stderr

    d_list   = [al_cent, mn_cent, ti_cent, b, a, be, ae]

    return d_list        
    
#---------------------------------------------------------------------------------------------------
#-- extract_hist_data: extract histgram data for given ccd and node                              ---
#---------------------------------------------------------------------------------------------------

def extract_hist_data(data_set, ccd, node):

    """
    extract histgram data for given ccd and node
    input:  data_set    ---- mixed data
            ccd         ---- ccd id
            node        ---- node #
    output: hist        ---- histgram profile data
    """

    hist = [0 for x in range(0, 4000)]

    for tdata in data_set:
        mask  = tdata.field('ccd_id') == ccd
        tdata = tdata[mask]

        if len(tdata) == 0:
            continue

        mask  = tdata.field('node_id') == node
        tdata = tdata[mask]

        if len(tdata) == 0:
            continue

        hdata = list(tdata['pha'])

        for ent in hdata:
            try:
                k = int(ent) 
                if k < 4000:
                    hist[k] += 1
            except:
                pass
#
#--- make sure that it actually has data
#
    test = 0
    for k in range(0, 4000):
        test += hist[k]
    if test == 0:
        return 'na'
    else:
        return hist

#---------------------------------------------------------------------------------------------------
#-- fit_pmodel: for a given histgram data, fit a gaussian distribution                           ---
#---------------------------------------------------------------------------------------------------

def fit_pmodel(hist, ymax, xpos, hwidth):
    """
    for a given histgram data, fit a gaussian distribution
    input:  hist    --- hist data
            ymax    --- initial guess height of the profile
            xpos    --- initial guess center postion
            hwidth  --- initial guess sigma

    Output: amp     --- estimated height of the profile
            cent    --- estimated center postion
            width   --- estimated sigma
            floor   --- estimated floor level
    """

    start  = int(xpos) - hwidth
    stop   = int(xpos) + hwidth

    ybin   = hist[start:stop]
    xbin   = [x for x in range(start, stop)]
    err    = numpy.ones(2 * hwidth)

    p0 = [ymax, xpos, 10, 0]
    fitobj = kmpfit.Fitter(residuals=residualsG, data=(xbin,ybin,err))
    fitobj.fit(params0=p0)
    [amp, cent, width, floor] = fitobj.params
    return [amp, cent, width, floor]

#---------------------------------------------------------------------------------------------------
#--- lmodel: linear model for data fitting                                                        --
#---------------------------------------------------------------------------------------------------

def lmodel(p, x):

    """
    linear model for data fitting
    Input:  p --- (a, b): intercept and slope
            x --- independent variable values
    Oputput: estimated y values
    """
    a, b = p
    y = a + b*x
    return y


#---------------------------------------------------------------------------------------------------
#-- extract_acis_evt1: extract acis evt1 file                                                     --
#---------------------------------------------------------------------------------------------------

def extract_acis_evt1(obsid):

    """
    extract acis evt1 file 
    Input: obsid    --- obsid of the data
    Output: acisf<obsid>*evt1.fits.gz
            file name if the data is extracted. if not ''
    """
#
#--- write  required arc4gl command
#
    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=1\n'
    line = line + 'filetype=evt1\n'
    line = line + 'obsid=' + str(obsid) + '\n'
    line = line + 'go\n'
    f    = open(zspace, 'w')
    f.write(line)
    f.close()


    cmd1 = "/usr/bin/env PERL5LIB="
#    cmd2 =  ' echo ' +  hakama + ' |/bin/nice -n15 arc4gl -U' + dare + ' -Sarcocc -i' + zspace
#    cmd2 =  ' echo ' +  hakama + ' |arc4gl -U' + dare + ' -Sarcocc -i' + zspace
    cmd2 = ' /proj/axaf/simul/bin/arc5gl -user isobe -script ' + zspace
    cmd  = cmd1 + cmd2

    try:
#
#--- run arc4/5gl
#
        bash(cmd,  env=ascdsenv)

        mcf.rm_file(zspace)
#
#--- check the data is actually extracted
#
        try:
            cmd  = 'ls *'+ str(obsid) + '*evt1.fits.gz >' + zspace
            os.system(cmd)
            f    = open(zspace, 'r')
            data = [line.strip() for line in f.readlines()]
            f.close()
        except:
            mcf.rm_file(zspace)
            return 'na'
#
#--- if multiple evt1 files are extracted, don't use it, but keep the record of them 
#
        if len(data) > 1:
            cmd  = 'rm *'+ str(obsid) + '*evt1.fits.gz '
            os.system(cmd)
    
            file = house_keeping + '/keep_entry'
            f    = open(file, 'a')
            f.write(obsid)
            f.write('\n')
            f.close()
            mcf.rm_file(zspace)
     
            return 'na'
    
        elif len(data) == 1:
#
#--- normal case, only one file extracted
#
            mcf.rm_file(zspace)
            line = data[0]
            line = line.replace('.gz', '')
    
            cmd  = 'chmod 755 *evt1.fits*'
            os.system(cmd)
            cmd  = 'mv *evt1.fits* ' + working_dir
            os.system(cmd)
            cmd  = 'gzip -d ' + working_dir + '*gz'
            os.system(cmd)
    
            return line
        else:
#
#--- no file is extracted
#
            mcf.rm_file(zspace)
        return 'na'
    except:
        mcf.rm_file(zspace)
        return 'na'

#---------------------------------------------------------------------------------------------------
#--- get_input_data_list: read obsid and the period where the focal temperature is < -119.7C from CTI data
#---------------------------------------------------------------------------------------------------

def get_input_data_list(year = 0, mon = 0):

    """
    read obsid and the period where the focal temperature is < -119.7C from CTI data and 
    makes a list of input data for a given year/month. if year/month is not given, the last
    month is used. 
    Input:  year/month  --- the year/month that data will be collected if 0, the last month is used.
    Ouput: a list of lists: [obsid, start, stop]
    """

    if year == 0 and mon == 0:
        tlist = tcnv.currentTime()
        year  = int(tlist[0])
        mon   = int(tlist[1])
        mon  -= 1
#
#--- for the case, that the last month is the last year
#
        if mon < 1:
            mon   = 12
            year -= 1

#
#--- we need only data with the focal temp <= -119.7C before May 2006 and <= -119.0C from May 2006
#--- and observation interval longer than 1000 sec
#
    if year > 2006:
        tlimit = -119.0
    elif (year == 2006) and (mon >= 5):
        tlimit = -119.0
    else:
        tlimit = -119.7

    save    = []
    for ccd in range(0, 10):
        file = cti_dir + 'ti_ccd' + str(ccd)
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        for ent in data:
            atemp = re.split('\s+', ent)
            time  = float(atemp[12]) - float(atemp[11])
            temp  = float(atemp[7])
            if temp <= tlimit:
                if time > 1000:
                    line  = atemp[0] + '\t' + atemp[5] + '\t' + str(time) + '\t' + atemp[7] + '\t' 
                    line  = line + atemp[11] + '\t' + atemp[12]
                    save.append(line)

    clist = list(set(save))
    clist = sorted(clist)
    fo      = open('input_list', 'w')
    obsid = []
    start = []
    stop  = []
    for ent in clist:
        fo.write(ent)
        fo.write('\n')

        atemp = re.split('-', ent)
#
#--- setlect out the data for year/month
#
        cyear = int(atemp[0])
        cmon  = int(atemp[1])
        if (cyear == year) and (cmon == mon):
            atemp = re.split('\t+|\s+', ent)
            obsid.append(atemp[1])
            start.append(int(atemp[4]))
            stop.append(int(atemp[5]))

    fo.close()

    return [obsid, start, stop]

#----------------------------------------------------------------------------------
#-- funcG: Model function is a gaussian                                         ---
#----------------------------------------------------------------------------------

def funcG(p, x):
    """
    Model function is a gaussian
    Input:  p   --- (A, mu, sigma, zerolev) 
            x  
    Output: estimated y values
    """
    A, mu, sigma, zerolev = p
    return( A * numpy.exp(-(x-mu)*(x-mu)/(2*sigma*sigma)) + zerolev )

#----------------------------------------------------------------------------------
#-- residualsG: Return weighted residuals of Gauss                              ---
#----------------------------------------------------------------------------------

def residualsG(p, data):

    """
    Return weighted residuals of Gauss
    Input:  p --- parameter list (A, mu, sigma, zerolev) see above
            x, y --- data
    Output:  array of residuals
    """

    x, y, err = data
    return (y-funcG(p,x)) / err

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_get_input_data_list(self):

        [obsid, start, stop] = get_input_data_list(2014, 1)
        test_out = ['53117', '62674', '53102', '53089', '53082', '53069', '53061']

        self.assertEquals(obsid, test_out)

#--------------------------------------------------------------------

    def test_get_new_data(self):

        obsid = ['53117', '62674'] 
        start = [504955553, 505683278]
        stop  = [504968158, 505803066]

        data_set  = get_new_data(obsid, start, stop)
        info_save = extract_gain_info(data_set, 3, 1)

        test_out  = [377.71818836179369, 1496.9270128895018, 1145.878719890527, 0.25372580295403135, \
                     0.7093958711330367, 0.00025627917431867857, 1.1205577882714126]

        self.assertEquals(info_save, test_out)

#--------------------------------------------------------------------


get_new_data

if __name__ == '__main__':
#
#--- check whether year and month are provided
#
    if len(sys.argv) == 1:
        unittest.main()

    elif len(sys.argv) == 3:
        year  = int(sys.argv[1])
        month = int(sys.argv[2])

        acis_gain_get_data(year, month)
    else:
        year  = 0 
        month = 0 

        acis_gain_get_data(year, month)

