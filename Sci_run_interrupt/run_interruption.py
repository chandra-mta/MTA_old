#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       run_interruption.py: run all sci run interrupt scripts                  #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Nov 07, 2017                                       #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import string
import numpy as np

#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')
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
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv
#
#--- Science Run Interrupt related funcions shared
#
import interruptFunctions as itrf
#
#--- Science Run Interrupt plot  related funcions shared
#
import interruptPlotFunctions as ptrf
#
#--- extracting data
#
import extract_data as edata
#
#--- Ephin ploting routines
#
import plot_ephin as ephin
#
#---- GOES ploting routiens
#
import plot_goes as goes
#
#---- NOAA plotting routines
#
import plot_noaa_rad as noaa
#
#---- extract xmm data and plot
#
import compute_xmm_stat_plot_for_report as xmm
#
#---- update html page
#
import sci_run_print_html as srphtml

#-------------------------------------------------------------------------------------
#-- run_interrupt: run all sci run plot routines                                    --
#-------------------------------------------------------------------------------------

def run_interrupt(file):
    
    """
    run all sci run plot routines
    input:  file                --- input file name. if it is not given, the script will ask
    output: <plot_dir>/*.png    --- ace data plot
            <ephin_dir>/*.png   --- ephin data plot
            <goes_dir>/*.png    --- goes data plot
            <xmm_dir>/*.png     --- xmm data plot
            <html_dir>/*.html   --- html page for that interruption
            <web_dir>/rad_interrupt.html    --- main page
    """
#
#--- check input file exist, if not ask
#
    test = exc_dir + file
    if not os.path.isfile(test):
        file = raw_input('Please put the intrrupt timing list: ')
    
    if file == 'test':
#
#--- if this is a test case, prepare for the test
#
        comp_test = 'test'
        file = test_web_dir +'test_date'
    else:
        comp_test = 'NA'
#
#--- extract data
#
    print "Extracting Data"
    edata.extract_data(file)

    f     = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        event = atemp[0]
        start = atemp[1]
        stop  = atemp[2]
        gap   = atemp[3]
        type  = atemp[4]

        print "PLOTING: " + str(event)
#
#--- plot Ephin data
#
        print "EPHIN"
        ephin.plotEphinMain(event, start, stop, comp_test)
#
#---- plot GOES data
#
        print "GOES"
        goes.plotGOESMain(event, start, stop, comp_test)
#
#---- plot other radiation data (from NOAA)
#
        print "NOAA"
        noaa.startACEPlot(event, start, stop, comp_test)
#
#---- extract and plot XMM data
#
        print "XMM"
        xmm.read_xmm_and_process(event)

#
#---- create indivisual html page
#
    print "HTML UPDATE"
    srphtml.printEachHtmlControl(file)
#
#---- update main html page
#
    srphtml.printEachHtmlControl()

#-------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 2:
        file = sys.argv[1]
    else:
        file = 'interruption_time_list'

    run_interrupt(file)

