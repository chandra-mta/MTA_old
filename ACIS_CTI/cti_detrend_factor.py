#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       cti_detrend_factor.py: create detrended cti tables                                          #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Sep 16, 2014                                                               #
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
import pyfits
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

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
temp_dir    = exc_dir + '/Temp_dir/'

#---------------------------------------------------------------------------------------------------
#-- cti_detrend_factor: update detrend factor table, then update detrend data table              ---
#---------------------------------------------------------------------------------------------------

def cti_detrend_factor():

    """
    update detrend factor table, then update detrend data table
    Input:  none
    Output: amp_avg_list    --- detrend factor table kept in <house_keeping>
            detrended data table, e.g. Det_Results/<elm>_ccd<ccd#>
    """

#
#--- update detrend factor table (amp_avg_list)
#
    update_detrend_factor_table()
#
#--- update detrend data tables 
#
    make_detrended_data_table()


#---------------------------------------------------------------------------------------------------
#-- cti_detrend_factor: extract information about amp_avg values and update amp_avg_list         ---
#---------------------------------------------------------------------------------------------------

def update_detrend_factor_table():

    """
    extract information about amp_avg values and update <house_keeping>/amp_avg_list
    Input:  none
    Output: <house_keeping>/amp_avg_list
    """
#
#--- clean up temp_dir so that we can put new fits files
#
    mcf.mk_empty_dir(temp_dir)
#
#--- extract stat fits files
#
    new_entry = get_new_entry()
#
#--- if files are extracted, compute amvp_avg values for the obsid
#
    if len(new_entry) > 0:
        processed_list = update_amp_avg_list(new_entry)
#
#--- clean up "keep_entry" and amp_avg_list 
#
        update_holding_list(new_entry, processed_list)
        cleanup_amp_list()


#---------------------------------------------------------------------------------------------------
#-- update_amp_avg_list: extract amp_avg information from a fits file for a given obsid           --
#---------------------------------------------------------------------------------------------------

def update_amp_avg_list(new_entry):

    """
    extract update amp_avg_list information 
    Input:  new_entry    --- a list of obsids
    Output: amp_avg_lst  --- a list of avg_amp kept in hosue_keeping dir 
                             (format: 2013-10-27T06:11:52 0.218615253807107   53275)
            processed_list - a list of obsid which actually used to generate avg_amp
    """

    [processed_list, amp_data_list] = get_amp_avg_data(new_entry)

    file = house_keeping + '/amp_avg_list'
    f = open(file, 'a')
    for line in amp_data_list:
        f.write(line)
    f.close()

    return processed_list


#---------------------------------------------------------------------------------------------------
#-- update_amp_avg_list: extract amp_avg information from a fits file for a given obsid           --
#---------------------------------------------------------------------------------------------------

def get_amp_avg_data(new_entry):

    """
    extract amp_avg information from a fits file for a given obsid
    Input:  new_entry    --- a list of obsids
    Output: amp_data_lst  --- a list of avg_amp kept in hosue_keeping dir 
                             (format: 2013-10-27T06:11:52 0.218615253807107   53275)
            processed_list - a list of obsid which actually used to generate avg_amp
    """
#
#--- remove dupilcated entries of obsid
#
    new_entry = mcf.removeDuplicate(new_entry, chk=0)
    processed_list = []
    amp_data_list = []

    for obsid in new_entry:
#
#--- extract fits file(s)
#
        fits_list = extract_stat_fits_file(obsid, out_dir=temp_dir)
        for fits in fits_list:
#
#--- read header entry
#
            dout = pyfits.open(fits)
            date = dout[0].header['DATE-OBS']
            date.strip()
#
#--- extreact column data for ccd_id and drop_amp
#
            data     = pyfits.getdata(fits, 1)
            ccdid    = data.field('ccd_id')
            drop_amp = data.field('drop_amp')

            amp_data = []
            sum      = 0
            for i in range(0, len(ccdid)):
#
#--- amp data is computed from when ccd 7 drop_amp
#
                if int(ccdid[i]) == 7:
                    val = float(drop_amp[i])
                    amp_data.append(val)
                    sum += val

            if len(amp_data) > 0:
                norm_avg = 0.00323 * sum / float(len(amp_data))     #--- 0.00323 is given by cgrant (03/07/05)

                line = date + '\t' + str(norm_avg) + '\t' + str(obsid) + '\n'
            else:
                line = date + '\t' + '999999'      + '\t' + str(obsid) + '\n'

            processed_list.append(obsid)
            amp_data_list.append(line)

    return [processed_list, amp_data_list]

#---------------------------------------------------------------------------------------------------
#-- get_new_entry: create a list of obsids which need to be proccessed                            --
#---------------------------------------------------------------------------------------------------

def get_new_entry():

    """
    create a list of obsids which need to be proccessed
    Input: amp_avg_list --- a list kept in <house_keeping> directory
           new_entry    --- a list newly created during this session
    Output: a list of obsid which are not proccessed yet
    """
#
#--- prepare a data list file
#
    cmd = 'cp ' + house_keeping + '/amp_avg_list ' + house_keeping + '/amp_avg_list~'
    os.system(cmd)
#
#--- create a list of obsids which are already proccessed before
#
    file = house_keeping + '/amp_avg_list'
    amp  = mcf.get_val(file, lst=0)
    camp = []
    for ent in amp:
        atemp = re.split('\s+|\t+', ent)
        camp.append(atemp[2])
#
#--- read a new obsid list
#
    file =  working_dir + '/new_entry'
    test = mcf.get_val(file, lst=0)

#
#--- add a list of old obsids which have not been proccessed.
#
    file  = house_keeping + '/keep_entry'
    test2 = mcf.get_val(file, lst=0)
    test  = test + test2
#
#--- find which obsids are new ones
#
    return mcf.find_missing_elem(test, camp)

#---------------------------------------------------------------------------------------------------
#-- extract_stat_fits_file: extract acis stat fits files using arc4gl                            ---
#---------------------------------------------------------------------------------------------------

def extract_stat_fits_file(obsid, out_dir='./'):

    """
    extract acis stat fits files using arc4gl
    Input:  obsid   --- obsid
            out_dir --- a directory in which the fits file is deposited. default is "./"
    Output: acis stat fits file (decompressed) in out_dir
            data    --- a list of fits files extracted
    """

    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=1\n'
    line = line + 'filetype=expstats\n'
    line = line + 'obsid=' + str(obsid) + '\n'
    line = line + 'go\n'

    f    = open(zspace, 'w')
    f.write(line)
    f.close()

    try:
        cmd1 = '/usr/bin/env PERL5LIB=""'
        cmd2 = ' echo ' + hakama + '|arc4gl -U' + dare + ' -Sarcocc -i' + zspace 
        cmd  = cmd1 + cmd2
        bash(cmd, env=ascdsenv)
        mcf.rm_file(zspace)
    
        cmd  = 'ls ' + exc_dir + '> ' + zspace
        os.system(cmd)
        test = open(zspace).read()
        mcf.rm_file(zspace)
    
        m1   = re.search('stat1.fits.gz', test)
        if m1 is not None:
            cmd  = 'mv ' + exc_dir +'/*stat1.fits.gz ' + out_dir + '/.'
            os.system(cmd)
            cmd  = 'gzip -d ' + out_dir + '/*stat1.fits.gz'
            os.system(cmd)
     
            cmd  = 'ls ' + out_dir + '/*' + str(obsid) + '*stat1.fits > ' + zspace
            os.system(cmd)
     
            f    = open(zspace, 'r')
            data = [line.strip() for line in f.readlines()]
            f.close()
            mcf.rm_file(zspace)
    
            return data
        else:
            return []
    except:
        mcf.rm_file(zspace)
        return []

#---------------------------------------------------------------------------------------------------
#-- update_holding_list: update <hosue_keeping>/keep_entry list                                  ---
#---------------------------------------------------------------------------------------------------

def update_holding_list(new_entry, processed_list):

    """
    update <hosue_keeping>/keep_entry list
    Input:  new_entry      --- a list of obsids used
            processed_list --- a list of obsids actually processed
    Output: <hosue_keeping>/keep_entry list
    """
#
#-- find whether any of obsids were not proccessed
#
    missing = mcf.find_missing_elem(new_entry, processed_list)
    file    = house_keeping + 'keep_entry'

    f    = open(file, 'w')

    if len(missing) > 0:
#
#--- if so, print them out
#
        missing = mcf.removeDuplicate(missing, chk=0)

        for ent in missing:
            f.write(ent)
            f.write('\n')

    f.close()

#---------------------------------------------------------------------------------------------------
#-- cleanup_amp_list: remove duplicated obsid entries: keep the newest entry only                ---
#---------------------------------------------------------------------------------------------------

def cleanup_amp_list():

    """
    remove duplicated obsid entries: keep the newest entry only
    Input:  read from: <hosue_keeping>/amp_avg_lst
    Output: updated <hosue_keeping>/amp_avg_lst
    """

    file = house_keeping + 'amp_avg_list'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- reverse the list so that we can check from the newest entry
#
    data.reverse()
#
#--- find out which obsids are listed multiple times
#
    obsidlist = []
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        obsid = int(atemp[2])
        obsidlist.append(obsid)

    obsidlist.sort()

    obsidmulti = []
    comp = obsidlist[0]
    for i in range(1, len(obsidlist)):
        if comp == obsidlist[i]:
            obsidmulti.append(obsidlist[i])
        else:
            comp = obsidlist[i]
#
#--- if there are multiple obsid entries, keep the newest one and remove older ones
#
    cleaned   = []
    if len(obsidmulti) > 0:
        obsidmulti = mcf.removeDuplicate(obsidmulti)
#
#--- "marked" is a marker which indicates whether a specific obsid is already listed
#
        for i in range(0, len(obsidmulti)):
            marked[i] = 0

        for ent in data:
            atemp = re.split('\s+', ent)
            obsid = int(atemp[2])
            chk   = 0
            for i in range(0, len(obsidmulti)):
                if (obsid == obsidmulti[i]) and (marked[i] == 0):
                    marked[i] = 1
                    break
                elif (obsid == obsidmulti[i]) and (marked[i] > 0):
                    chk = 1
                    break

            if chk == 0:
                cleaned.append(ent)
    else: 
        cleaned = data 
#
#--- reverse back to the original order
#
    cleaned.reverse()
#
#--- print out the cleaned list
#
    f = open(file, 'w')
    for ent in cleaned:
        f.write(ent)
        f.write('\n')
    f.close()


#---------------------------------------------------------------------------------------------------
#-- make_detrended_data_table: update detrended cti tables                                       ---
#---------------------------------------------------------------------------------------------------

def make_detrended_data_table():

    """
    update detrended cti tables
    Input:  none, but read from data_dir/Results/<elm>_ccd<ccd#> and <house_keeping>/amp_avg_list
    Output: <data_dir>/Det_Results/<elm>_ccd<ccd#>
    """

#
#--- read detrending factor table
#
    detrend_factors = read_correction_factor()      #--- detrend_factors is a dictionary
#
#--- go through all imaging ccds for each element
#
    for elm in ('al', 'mn', 'ti'):

        for ccd in (0, 1, 2, 3, 4, 6, 8, 9):
#
#--- read original data table
#
            infile  = data_dir + '/Results/'     + elm + '_ccd' + str(ccd)

            f       = open(infile, 'r')
            data    = [line.strip() for line in f.readlines()]
            f.close()
#
#--- open output detrended table
#
            outfile = data_dir + '/Det_Results/' + elm + '_ccd' + str(ccd)
            fo      = open(outfile, 'w')

            for ent in data:
                atemp = re.split('\s+|\t+', ent)
#
#--- find a corresponding correction foactor
#
                try:
                    det_val = detrend_factors[atemp[5]]
                except:
                    det_val = 999
#
#--- if the detrending value is found and acceptable, correct cti values
#
                if det_val < 999:

                    fo.write(atemp[0])                   #---- starting date
                    fo.write('\t')

                    for i in range(1, 5):
                        corrected = correct_det(atemp[i], det_val)
                        fo.write(corrected)
                        fo.write('\t')

                    fo.write(atemp[5])              #--- obsid
                    fo.write('\t')
                    fo.write(atemp[6])              #--- ending date
                    fo.write('\t')
                    fo.write(atemp[7])              #--- avg focal temperature
                    fo.write('\t')
                    fo.write(atemp[8])              #--- sigma for the focal temperature
                    fo.write('\t')
                    fo.write(atemp[9])              #---  min focal temperature
                    fo.write('\t')
                    fo.write(atemp[10])              #--- max focal temperature
                    fo.write('\t')
                    fo.write(atemp[11])              #--- starting time in sec
                    fo.write('\t')
                    fo.write(atemp[12])              #--- ending time in sec
                    fo.write('\n')

            fo.close()

#---------------------------------------------------------------------------------------------------
#-- read_correction_factor: read a detrend correction factor table and create a dictionary       ---
#---------------------------------------------------------------------------------------------------

def read_correction_factor():

    """
    read a detrend correction factor table and create a dictionary with obsid <---> factor
    Input:  none, but read from <hosue_keeping>/amp_avg_list
    Outupt: detrend_factors --- a dictionary obsid <---> factor
    """
#
#--- read correction factor table
#
    line = house_keeping + '/amp_avg_list'
    f    = open(line, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- create a dictionary
#
    detrend_factors = {}
    for ent in data:
        atemp = re.split('\s+|\t+', ent)

        detrend_factors[atemp[2]] = float(atemp[1])

    return detrend_factors


#---------------------------------------------------------------------------------------------------
#--  correct_det: correct cti with a given detrending factor                                     ---
#---------------------------------------------------------------------------------------------------

def correct_det(quad, det_val):

    """
    correct cti with a given detrending factor
    Input:  quad    --- cti value +/- error
            det_val --- detrending factor
    Output: cti     --- corrected cti +/- error
    """
    
    m = re.search('99999', quad)
    if m is not None:
        return quad
    else:
        atemp = re.split('\+\-', quad)
        val   = float(atemp[0]) + det_val
        val   = round(val, 3)
        val   = str(val)
        vcnt  = len(val)
        if vcnt < 5:
            for i in range(vcnt, 5):
                val = val + '0'
        cti   = str(val) + '+-' + atemp[1]

        return cti
        
#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#------------------------------------------------------------

    def test_get_amp_avg_data(self):

        new_entry           = [52675]
        processed_list_test = [52675]
        amp_data_test       = ['2014-06-27T04:21:09\t0.199661945312\t52675\n']

        [processed_list, amp_data_list] = get_amp_avg_data(new_entry)

        self.assertEquals(processed_list, processed_list_test)
        self.assertEquals(amp_data_list,  amp_data_test)


#--------------------------------------------------------------------

#
#--- if there is any aurgument, it will run normal mode
#
chk =   0
if len(sys.argv) >= 2:
    chk  = 1


if __name__ == '__main__':

    if chk == 0:
        unittest.main()
    else:
        cti_detrend_factor()
