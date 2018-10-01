#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_control_step.py: monthly acis dose update control script              #
#                                  this one is an interactive version                   #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Mar 11, 2013                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import fnmatch

#
#--- reading directory list
#

path = '/data/mta/Script/Exposure/house_keeping/acis_dir_list'
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

sys.path.append(mta_dir)
sys.path.append(bin_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv

#
#--- Exposure related funcions shared
#

import exposureFunctions            as expf
import acis_dose_get_data           as getd
import acis_create_cumulative       as cuml
import acis_compute_stat            as astat
import acis_dose_plot_exposure_stat as aplot
import acis_dose_make_data_html     as ahtml
import acis_dose_monthly_report     as areport
import acis_dose_create_image       as aimg


#-----------------------------------------------------------------------------------------------------------
#-- acis_dose_control: monthly acis dose update contorl script                                           ---
#-----------------------------------------------------------------------------------------------------------

def acis_dose_control_step():

    """
    monthly acis dose update control script
    input: optional year and month
    """

    print 'Please specify the year and the month you want to run the scripts for.'
    syear = raw_input('Year: ')
    year  = int(syear)
    smonth= raw_input('Month: ')
    month = int(smonth)

    smon  = str(month)
    if month < 10:
        smon = '0' + smon

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
    else:
        chk1 = raw_input('Extracting Data (y/n): ')
        chk2 = raw_input('Compute Statistics (y/n): ')
        chk3 = raw_input('Plot Data (y/n): ')
        chk4 = raw_input('Create Images (y/n): ')
        chk5 = raw_input('Updata HTML pages (y/n): ')
        chk6 = raw_input('Create Table for Monthly Report (y/n): ')
#
#--- extract data
#
    m = re.search('y', chk1)
    if m is not None:
        getd.acis_dose_get_data(year, month, year, month)
#
#--- create cumulative data and sectioned data for bot month and cumulative data
#
        file = 'ACIS_' + smon + '_' + syear + '.fits'
        file2= 'ACIS_' + smon + '_' + syear + '.fits.gz'

        chk = 0
        for test in os.listdir('./'):
            if fnmatch.fnmatch(test, file2):
                chk = 1
                break
    
        if chk == 0:
            cuml.acis_create_cumulative(file)
        else:
            cuml.acis_create_cumulative(file2)
            
#
#--- compute statistics
#
    m = re.search('y', chk2)
    if m is not None:
        astat.acis_dose_extract_stat_data_month(year, month)
#
#--- plot data
#
    m = re.search('y', chk3)
    if m is not None:
        aplot.acis_dose_plot_exposure_stat(clean='Yes')
#
#--- create images (you need to use ds9 to create a better image)
#
    m = re.search('y', chk4)
    if m is not None:
        aimg.create_acis_maps(year, month)
#
#--- update html pages
#
    m = re.search('y', chk5)
    if m is not None:
        ahtml.acis_dose_make_data_html()

#
#--- print monthly output
#
    m = re.search('y', chk6)
    if m is not None:
        areport.acis_dose_monthly_report()



#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    acis_dose_control_step()


