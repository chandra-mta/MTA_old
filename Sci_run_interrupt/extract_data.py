#!/usr/bin/env python

#################################################################################
#                                                                               #
#       extract_data.py: extract data needed for sci. run interruption plots    #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Apr 12, 2013                                       #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import string

#
#--- reading directory list
#

path = '/data/mta/Script/Interrupt/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
#
#--- Science Run Interrupt related funcions shared
#
import interruptFunctions as itrf
#
#---- EPHIN data extraction
#
import extract_ephin as ephin
#
#---- GOES data extraction
#
import extract_goes as goes
#
#---- ACE (NOAA) data extraction
#
import extract_noaa as noaa
#
#---- ACE (NOAA) statistics
#
import compute_ace_stat as astat

#---------------------------------------------------------------------------------------------------------------------
#--- extract_data: extract ephin and GOES data. this is a control and call a few related scripts                   ---
#---------------------------------------------------------------------------------------------------------------------

def extract_data(file):
    
    'extract ephin and GOES data. this is a control and call a few related scripts '

    
    if file == '':
        file = raw_input('Please put the intrrupt timing list: ')

    if file == 'test':
#
#--- if this is a test case, prepare for the test
#
        comp_test = 'test'
        prep_test()
        file = test_web_dir +'test_date'
    else:
#
#--- otherwise, update radiation zone list (rad_zone_list) for given period(s)
#
        comp_test = ''
        itrf.sci_run_add_to_rad_zone_list(file)
#
#--- correct science run interruption time excluding radiation zones
#
    itrf.sci_run_compute_gap(file)

    f    = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        print "EXTRACTING DATA FOR: " + ent

        if not ent:
            break

        atemp = re.split('\s+|\t+', ent)
        event = atemp[0]
        start = atemp[1]
        stop  = atemp[2]
        gap   = atemp[3]
        type  = atemp[4]
#
#--- extract ephin data
#
        ephin.ephinDataExtract(event, start, stop, comp_test)
#
#--- compute ephin statistics
#
        ephin.computeEphinStat(event, start, comp_test)
#
#---- extract GOES data
#
        try:
            goes.extractGOESData(event, start, stop, comp_test)
        except:
            pass
#
#---- compute GOES statistics
#
        try:
            goes.computeGOESStat(event, start, comp_test)
        except:
            pass
#
#---- extract ACE (NOAA) data
#
        try:
            noaa.startACEExtract(event, start, stop, comp_test)
        except:
            pass
#
#---- compute ACE statistics
#
        try:
            astat.computeACEStat(event, start, stop, comp_test)
        except:
            pass


#---------------------------------------------------------------------------------------------------------------------
#--- prep_test: create a couple of directories for test data outupt                                                 --
#---------------------------------------------------------------------------------------------------------------------

def prep_test():
#
#--- if this is a test case, check whether output file exists. If not, creaete it
#   
    for ent in (test_web_dir, test_data_dir, test_plot_dir, test_html_dir, test_stat_dir, test_ephin_dir, test_goes_dir, test_note_dir, test_intro_dir):

        chk   = mcf.chkFile(ent)
        if chk == 0:
            cmd = 'mkdir ' + ent
            os.system(cmd)

#
#--- prepare for test
#
    cmd = 'cp ' + house_keeping + 'Test_prep/test_date ' + test_web_dir + '.'
    os.system(cmd)

#---------------------------------------------------------------------------------------------------------------------
#--- start script                                                                                                  ---
#---------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':

    if len(sys.argv) == 2:
        file = sys.argv[1]
    else:
        file = ''
    extract_data(file)
