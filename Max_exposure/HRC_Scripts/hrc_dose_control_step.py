#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       hrc_dose_control_step.py: control hrc prcoesses                                 #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Apr 11, 2013                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re

#
#--- reading directory list
#

path = '/data/mta/Script/Exposure/house_keeping/hrc_dir_list'
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
#--- import HRC related scripts/functions
#

import convertTimeFormat                as tcnv                 #--- MTA time conversion routines
import exposureFunctions                as expf                 #--- exposure related functions
import hrc_dose_get_data_full_rage      as hgdata               #--- getting data
import hrc_dose_extract_stat_data_month as hstat                #--- hrc statistics
import hrc_dose_make_data_html          as hhtml                #--- html related
import hrc_dose_plot_exposure_stat      as hplot                #--- plot related
import hrc_dose_create_image            as himg                 #--- image creation
import hrc_dose_plot_monthly_report     as monthly              #--- plotting monthly report plot

#--------------------------------------------------------------------------------------------------------------
#--- hrc_dose_run: run all needed HRC scripts to extract data and create images                             ---
#--------------------------------------------------------------------------------------------------------------

def hrc_dose_run_step():

    """
    run selected HRC processes by asking which one the user want to run
    """

    print 'Please specify the year and the month you want to run the scripts for.'
    syear  = raw_input('Year: ')
    lyear  = int(syear)
    smonth = raw_input('Month: ')
    lmonth = int(smonth)

    print 'Please choose which processes you want to run\n'

    chk0 = raw_input('Do you want to run the entire process(y/n)?: ')
    m = re.search('y', chk0)
    if m is not None:
        chk1 = 'y'
        chk2 = 'y'
        chk3 = 'y'
        chk4 = 'y'
        chk5 = 'y'
        chk6 = 'y'
        chk7 = 'y'
    else:
        chk1 = raw_input('Extracting Data (y/n): ')
        chk2 = raw_input('Compute Statistics (y/n): ')
        chk3 = raw_input('Updata HTML pages (y/n): ')
        chk4 = raw_input('Plot History Data (y/n): ')
        chk5 = raw_input('Create Images (y/n): ')
        chk6 = raw_input('Plotting Monthly Report Trend (y/n): ')
        chk7 = raw_input('Copying Data to mays (y/n): ')

    m = re.search('y', chk1)
    if m is not None:
        hgdata.hrc_dose_get_data(lyear, lmonth, lyear, lmonth)          #---- extracting data
    m = re.search('y', chk2)
    if m is not None:
        hstat.hrc_dose_extract_stat_data_month(lyear, lmonth)           #---- computing statistics
    m = re.search('y', chk3)
    if m is not None:
        hhtml.hrc_dose_make_data_html()                                 #---- creating html pages
    m = re.search('y', chk4)
    if m is not None:
        hplot.hrc_dose_plot_exposure_stat()                             #---- plotting histories
    m = re.search('y', chk5)
    if m is not None:
        himg.create_hrc_maps(lyear, lmonth)                             #---- creating map images
    m = re.search('y', chk6)
    if m is not None:
        monthly.hrc_dose_plot_monthly_report()                          #---- plotting monthly report trend

#
#--- change the group to mtagroup
#
    cmd = 'chgrp mtagroup ' + hrc_full_data + '*/*'
    os.system(cmd)
    cmd = 'chgrp mtagroup ' + web_dir + 'HRC/*'
    os.system(cmd)
    cmd = 'chgrp mtagroup ' + web_dir + 'HRC/*/*'
    os.system(cmd)

#
#--- copying data to mays
#
    if chk7 == 'y':
        syear = str(lyear)
        smon  = str(lmonth)
        if lmonth  < 10:
            smon = '0' + smon
    
        new_data = '*' + smon + '_' + syear + '*' 
    
        cmd = 'cp ' + mon_dir_hrc_full +  new_data + ' ' +  mays_dir + 'Month_hrc/.'
        os.system(cmd)
        cmd = 'cp ' + cum_dir_hrc_full +  new_data + ' ' +  mays_dir + 'Cumulative_hrc/.'
        os.system(cmd)



#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    hrc_dose_run_step()

