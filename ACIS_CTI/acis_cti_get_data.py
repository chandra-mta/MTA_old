#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       acis_cti_get_data.py: extract acis evt1 files which are not processed for CTI observations  #
#                                                                                                   #
#           author: t. isobe(tisobe@cfa.harvard.edu)                                                #
#                                                                                                   #
#           Last Update:    Sep 10, 2014                                                            #
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

#---------------------------------------------------------------------------------------------------
#-- acis_cti_get_data: extract acis evt1 files which are not processed for CTI observations       --
#---------------------------------------------------------------------------------------------------

def acis_cti_get_data():

    """
    extract acis evt1 files which are not processed for CTI observations
    Input:  none, but read from directory: /data/mta/www/mp_reports/photons/acis/cti/*
    Output: <working_dir>/acisf<obsid>*evt1.fits
    """
#
#--- get a new data list
#
    obsid_list = find_new_entry()
#
#--- if there is no new data, just exit
#
    if len(obsid_list) > 0:
#
#--- create a temporary saving directory 
#
        mcf.mk_empty_dir(working_dir)
#    
#--- extract acis event1 file
#
        outdir = working_dir + '/new_entry'     #---- new_entry list will be used later
        f      = open(outdir, 'w')
        for obsid in obsid_list:
            f.write(obsid)
            f.write('\n')
            cnt = 0
            chk = extract_acis_evt1(obsid)
            if chk != 'na':
                cnt += 1
                cmd = 'mv *'+ str(obsid) + '*.fits.gz ' + working_dir
                os.system(cmd)
    
        f.close()
    
        if cnt > 0:
            cmd = 'gzip -d ' + working_dir + '*.gz'
            os.system(cmd)
    else:
        exit(1)

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
    line = line + 'version=last\n'
    line = line + 'filetype=evt1\n'
    line = line + 'obsid=' + str(obsid) + '\n'
    line = line + 'go\n'
    f    = open(zspace, 'w')
    f.write(line)
    f.close()


    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 =  ' echo ' +  hakama + ' |arc4gl -U' + dare + ' -Sarcocc -i' + zspace
    cmd  = cmd1 + cmd2

#
#--- run arc4gl
#
    bash(cmd,  env=ascdsenv)
    mcf.rm_file(zspace)
#
#--- check the data is actually extracted
#
    cmd  = 'ls * > ' + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    mcf.rm_file(zspace)
    f.close()
    data_out = []
    for ent in data:
        m = re.search(str(obsid), ent)
        if m is not None:
            data_out.append(ent)

#
#--- if multiple evt1 files are extracted, don't use it, but keep the record of them 
#
    if len(data_out) > 1:
        cmd  = 'rm *'+ str(obsid) + '*evt1.fits.gz '
        os.system(cmd)

        file = house_keeping + '/keep_entry'
        f    = open(file, 'a')
        f.write(obsid)
        f.write('\n')
        f.close()
        mcf.rm_file(zspace)
     
        return 'na'
    elif len(data_out) == 1:
#
#--- normal case, only one file extracted
#
        mcf.rm_file(zspace)
        line = data_out[0]
        return line
    else:
#
#--- no file is extracted
#
        return 'na'

#---------------------------------------------------------------------------------------------------
#-- find_new_entry: create a list of obsids which have not processed yet                         ---
#---------------------------------------------------------------------------------------------------

def find_new_entry():

    """
    create a list of obsids which have not processed yet
    Input: none, but read from /data/mta/www/mp_reports/photons/acis/cti/*
    Output: obsid_list  --- a list of obsids
    """
#
#--- find currently available data
#
    file = '/data/mta/www/mp_reports/photons/acis/cti/*_*'

    cmd  = "ls -td " + file +  "> " + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)

    current_list = []
    for ent in data:
        m = re.search("\d\d\d\d\d_\d", ent)
        if m is not None:
            current_list.append(ent)
    current_list = current_list[0:5]

    current_obsids = []
    for ent in current_list:
        atemp = re.split('\/', ent)
        btemp = re.split('_', atemp[len(atemp) -1])
        current_obsids.append(btemp[0])
#
#--- read the past entry list
#
    pobsid_list = []
    for ccd in range(0, 10):
        cfile = data_dir + 'Results/ti_ccd' + str(ccd)
        fin   = open(cfile, 'r')
        data  = [line.strip() for line in fin.readlines()]
        fin.close()
        for ent in data:
            atemp = re.split('\s+', ent)
            pobsid_list.append(int(atemp[5]))
    old_list = list(set(pobsid_list))
    old_list = sorted(old_list)

#
#--- create a list of data which have not been processed
#
    new_list   = compare_and_find_new_entry(current_obsids, old_list)

    if len(new_list) > 0:
#
#--- read past excluded obsids
#
        ifile = house_keeping + 'exclude_obsid_list'
        f     = open(ifile, 'r')
        exfile = [line.strip() for line in f.readlines()]
        f.close()
#
#--- extract obsids from the new_list
#
        obsid_list = []
        for ent in new_list:
            test = str(ent)
            chk = 0
            for comp in exfile:
                if test == comp:
                    chk = 1
                    break
            if chk == 1:
                continue
            else:
                obsid_list.append(ent)
    else:
        obsid_list = []

    return obsid_list

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def create_list(pass_list):

    try:
        cmd = 'ls  -td ' + pass_list  + '> ' + zspace
        os.system(cmd)
        f   = open(zspace, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        mcf.rm_file(zspace)
        data = data[0:5]
    except:
        data = []

    return data

#---------------------------------------------------------------------------------------------------
#-- compare_and_find_new_entry: extract the data which are not checked before                    ---
#---------------------------------------------------------------------------------------------------

def compare_and_find_new_entry(current_list, old_list):

    """
    extract the data which are not checked before
    Input:  current_list    --- a current input list
            old_list        --- a past input list
    Output: new_list        --- a list of new input list
    """
    new_list = []
    for ent in current_list:
        test = int(ent)
        chk = 0
        for comp in old_list:
            if test == comp:
                chk = 1
                break

        if chk == 1:
            continue
        else:
            new_list.append(ent)

    return new_list

#---------------------------------------------------------------------------------------------------
#-- obsid_from_mp_report: extract obsid from a given path to the data                             --
#---------------------------------------------------------------------------------------------------

def obsid_from_mp_report(nlist):

    """
    extract obsid from a given path to the data
             entry line looks line: "/data/mta/www/mp_reports/photons/acis/cti/62311_0"
    Input:  nlist      --- a list of data pathes to the data
    Ouput:  obsid_list --- a list of obsids
    """

    obsid_list = []
    for ent in nlist:
        atemp = re.split('/', ent)
        btemp = re.split('_', atemp[len(atemp)-1])
#
#--- check whether the obsid is really number
#
        if mcf.chkNumeric(btemp[0]):
            obsid_list.append(btemp[0])

    return obsid_list
#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_extract_acis_evt1(self):

        obsid = 52675
        extract_acis_evt1(obsid)
        cmd = 'ls *fits.gz > ' + zspace
        os.system(cmd)
        f   = open(zspace, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        mcf.rm_file(zspace)

        chk = 0
        for ent in data:
            atemp = re.split('acisf', ent)
            btemp = re.split('_', atemp[1])
            if btemp[0] == str(obsid):
                chk = 1
                break

        self.assertEquals(chk, 1)

#------------------------------------------------------------

    def test_find_new_entry(self):    

        try:
            obsid_list = find_new_entry()
            chk = 1
        except:
            chk = 0

        self.assertEquals(chk, 1)


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
        acis_cti_get_data()

