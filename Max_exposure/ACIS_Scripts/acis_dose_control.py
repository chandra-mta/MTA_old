#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_control.py: monthly acis dose update control script                   #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Jul 06, 2015                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import fnmatch

#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')
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
import acis_dose_monthly_report     as arport
import acis_dose_create_image       as aimg

#-----------------------------------------------------------------------------------------------------------
#-- acis_dose_control: monthly acis dose update contorl script                                           ---
#-----------------------------------------------------------------------------------------------------------

def acis_dose_control(year = 'NA', month = 'NA', comp_test = 'NA'):

    """
    monthly acis dose update control script
    input: optional year and month
    """

    if year == 'NA' or month == 'NA':

        (year, mon, day, hours, min, sec, weekday, yday, dst) = tcnv.currentTime('Local')

        month = mon -1
        if month < 1:
            month = 12
            year -= 1
    else:
        year  = int(year)
        month = int(month)

    syear = str(year)
    smon  = str(month)
    if month < 10:
        smon = '0' + smon

#
#--- extract data
#
    getd.acis_dose_get_data(year, month, year, month)
#
#--- create cumulative data and sectioned data for bot month and cumulative data
#
##    file = 'ACIS_' + smon + '_' + syear + '.fits'
##    file2= 'ACIS_' + smon + '_' + syear + '.fits.gz'
##
##    chk = 0
##    for test in os.listdir('./'):
##        if fnmatch.fnmatch(test, file2):
##            chk = 1
##            break
##
##    if chk == 0:
##       cuml.acis_create_cumulative(file, comp_test)
##       pass
##    else:
##       pass
##       cuml.acis_create_cumulative(file2, comp_test)
#
#--- compute statistics
#
##    astat.acis_dose_extract_stat_data_month(year, month, comp_test)
#
#--- plot data
#
##    aplot.acis_dose_plot_exposure_stat(clean='Yes', comp_test=comp_test)
#
#--- create images (you need to use ds9 to create a better image)
#
##    aimg.create_acis_maps(year, month, comp_test)
#
#--- update html pages
#
##    ahtml.acis_dose_make_data_html(comp_test = comp_test)

#
#--- print monthly output
#
##    arport.acis_dose_monthly_report()



#--------------------------------------------------------------------------------------------------------
#
#--- pylab plotting routine related modules
#
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

#
#--- check whether this is a test case
#
if len(sys.argv) == 2:
    if sys.argv[1] == 'test':               #---- this is a test case
        comp_test = 'test'
    else:
        comp_test = 'real'
else:
    comp_test = 'real'


if __name__ == '__main__':
#
#--- if this is a test case, run for 2013 Jan data
#
    if comp_test == 'test':
        acis_dose_control(2013, 1, comp_test)
    else:
        acis_dose_control()


