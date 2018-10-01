#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       create_config_plot.py: create configuration plot for monthly report                         #
#                                                                                                   #
#               author: t. isobe    (tisobe@cfa.harvard.edu)                                        #
#                                                                                                   #
#               last update: Dec 09, 2014                                                           #
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
import astropy.io.fits  as pyfits
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/Month/Config//house_keeping/dir_list_py'

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
import extract_radiation_data     as erd        #---- radiation related data reading

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#---- the testing period
#
test_start = 531187196       #--- 2014:305:00:00:00 (Nov  1, 2014)
test_stop  = 532483196       #--- 2014:320:00:00:00 (Nov 15, 2014)

color1 =['red','blue', 'lime', 'green', 'yellow']
color2 =['yellow','blue', 'red', 'green', 'lime']
color3 =['red','blue', 'lime', 'yellow', 'green']
color4 =['maroon','lime', 'red', 'blue', 'fuchsia']

#----------------------------------------------------------------------------------------------------------
#-- plot_data: create a configulation display panel for a give time period                               --
#----------------------------------------------------------------------------------------------------------

def plot_data(start, stop, mag_plot=1):
    """
    create a configulation display panel for a give time period
    input:  start   --- starting time in sec from 1998.1.1
            stop    --- stopping time in sec from 1998.1.1
    """

#
#---- set a few parameters
#
    if mag_plot == 0:
        pnum = 5
    else:
        pnum = 6

    mpl.rcParams['font.size'] = 11 
    mpl.rcParams['font.weight'] = 'strong' 
    props = font_manager.FontProperties(size=6)
    plt.subplots_adjust(hspace=0.05)
    plt.subplots_adjust(wspace=0.12)
#
#--- set a few others
#
    xpos  = stime_to_ydate(stop) + 0.1 
    ystep = 0.2
#
#--- read sim information
#
    [acis_i_start, acis_i_stop, acis_s_start, \
     acis_s_stop,  hrc_i_start, hrc_i_stop,   \
     hrc_s_start,  hrc_s_stop,  hetg_start,   \
     hetg_stop,    letg_start,  letg_stop,    \
     radmon_start, radmon_stop, fmt, time]  = erd.find_sim_position(start, stop)
#
#--- hetg /letg information plot
#
    start_set = [hetg_start, letg_start]
    stop_set  = [hetg_stop,  letg_stop]
    ax1 = plt.subplot(pnum, 1, 1)
    plot_strip_box(ax1,start, stop, start_set, stop_set, color1)

    plt.text(xpos, 0.8, "HETG", color=color1[0])
    plt.text(xpos, 0.6, "LETG", color=color1[1])
#
#--- acis /hrc information plot
#
    start_set = [acis_i_start, acis_s_start, hrc_i_start, hrc_s_start]
    stop_set  = [acis_i_stop,  acis_s_stop,  hrc_i_stop,  hrc_s_stop]
    ax2 = plt.subplot(pnum, 1, 2)
    plot_strip_box(ax2,start, stop, start_set, stop_set, color1)

    plt.text(xpos, 0.9, "ACIS I ", color=color1[0])
    plt.text(xpos, 0.7, "ACIS S ", color=color1[1])
    plt.text(xpos, 0.5, "HRC I ",  color=color1[2])
    plt.text(xpos, 0.3, "HRC S ",  color=color1[3])
#
#--- cti information plot
#
    [cti_start, cti_stop]               = erd.read_ccd_data(start, stop)
    start_set = [cti_start]
    stop_set  = [cti_stop]
    ax3 = plt.subplot(pnum, 1, 3)
    plot_strip_box(ax3, start, stop, start_set, stop_set, color1)
#
#--- altitude information plot
#
    [atime, alt, magx, magy, magz, crm]  = erd.read_orbit_data(start, stop)
    plot_line(ax3, start, stop, atime, alt)

    plt.text(xpos, 0.8, "CTI  ",     color=color1[0])
    plt.text(xpos, 0.7, "Check  ",     color=color1[0])
    plt.text(xpos, 0.4, "Altitude ", color="green")
#
#--- radmon information plot
#
    start_set = [radmon_start]
    stop_set  = [radmon_stop]
    ax4 = plt.subplot(pnum, 1, 4)
    plot_strip_box(ax4, start, stop, start_set, stop_set, color1)
#
#--- hrc sheild rate plot
#
    [htime, rate]                       = erd.read_hrc_data(start, stop)
    plot_line(ax4, start, stop, htime, rate)
#
#--- goes p3 rate plot
#
#    [gtime, p1, p2, p3]                 = erd.read_goes_data(start, stop)
#    plot_points(ax4, start, stop, gtime, p3, color='lime', pts=0.5,lw=0)

    plt.text(xpos, 0.8, "Radmon", color=color1[0])
    plt.text(xpos, 0.6, "HRC", color="green")
    plt.text(xpos, 0.5, "Shield", color="green")
    plt.text(xpos, 0.4, "Rate", color="green")
#    plt.text(xpos, 0.2, "GOES P3", color="green")
#
#--- magnetsphere plot
#
    if mag_plot != 0:
        [start_set, stop_set] = find_mag_region(start, stop)
        axm = plt.subplot(6, 1, 5)
        plot_strip_box(axm, start, stop, start_set, stop_set, color1)

#        plt.text(xpos, 0.9, "Solar",    color=color1[0])
#        plt.text(xpos, 0.8, "Wind",     color=color1[0])
        plt.text(xpos, 0.6, "Magneto-", color=color1[1])
        plt.text(xpos, 0.5, "sheath",   color=color1[1])
        plt.text(xpos, 0.3, "Magneto-", color=color1[2])
        plt.text(xpos, 0.2, "sphere",   color=color1[2])
#
#--- often the data are not available; so make a note on the plot
#
#        diff1 = stop - start
#        tlast = time[len(time)-1]
#        diff2 = tlast - start
#        ratio = diff2 / diff1
#        if ratio < 0.7:
#            xnote = 0.5 * (stop - tlast)
#            plt.text(xnote, 0.5, "No Data", color='maroon')
#
#--- FMT format information plot
#
    [start_set, stop_set] = find_fmt_region(start, stop, fmt, time)

    ax5 = plt.subplot(pnum, 1, pnum)
    plot_strip_box(ax5, start, stop, start_set, stop_set,color4)

    plt.text(xpos, 0.9, "FMT1", color=color4[0])
    plt.text(xpos, 0.7, "FMT2", color=color4[1])
    plt.text(xpos, 0.5, "FMT3", color=color4[2])
    plt.text(xpos, 0.3, "FMT4", color=color4[3])
    plt.text(xpos, 0.1, "FMT5", color=color4[4])
#
#--- plot x axis tick label only at the bottom ones
#
    if mag_plot == 0:
        ax_list = [ax1, ax2, ax3, ax4, ax5]
    else:
        ax_list = [ax1, ax2, ax3, ax4, ax5, axm]

    for ax in ax_list:
        for label in ax.get_yticklabels():
            label.set_visible(False)
        if ax != ax5:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            pass
#
#--- x axis label
#
    mid   = int(0.5 * (start + stop))
    ltime = tcnv.axTimeMTA(mid)
    atemp = re.split(':', ltime)
    year  = int(atemp[0])
    ydate = int(atemp[1])
    [mon, day] = tcnv.changeYdateToMonDate(year,ydate)

    xlabel = "Time (DOY) " + str(atemp[0])
    ax5.set_xlabel(xlabel)

#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#   
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(12.0, 10.0)
#
#--- save the plot in png format
#   
    syear = str(year)
    smon  = tcnv.changeMonthFormat(mon)
    smon  = smon.lower()
    outname = 'rad_use_' + smon + syear[2] + syear[3] + '.png'

    plt.savefig(outname, format='png', dpi=100)
    plt.close('all')


#----------------------------------------------------------------------------------------------------------
#-- find_mag_region: find magnetsphere, magnetosheath, and solar wind time periods                       --
#----------------------------------------------------------------------------------------------------------

def find_mag_region(start, stop):
    """
    find magnetsphere, magnetosheath, and solar wind time periods
    input:  start   --- starting time in sec from 1998.1.1
            stop    --- stopping time in sec from 1998.1.1
    ouput:  [start_set, stop_set]
                start_set = [wind_start, shth_start, sphr_start]
                stop_set  = [wind_stop,  shth_stop,  sphr_stop]
    """

    [time, alt, magx, magy, magz, crm]   = erd.read_orbit_data(start, stop)
    wind_start = []
    wind_stop  = []
    shth_start = []
    shth_stop  = []
    sphr_start = []
    sphr_stop  = []
#
#--- find the starting condition
#
    if crm[0] == 1:
        wind_start.append(time[0])
    elif crm[0] == 2:
        shth_start.append(time[0])
    elif crm[0] == 3:
        sphr_start.append(time[0])
#
#--- find changing time and mark the new period
#
    prev  = crm[0]
    for k in range(1, len(crm)):

        if crm[k] == prev:
            continue 

        if prev == 1:
            wind_stop.append(time[k-1])
        elif prev == 2:
            shth_stop.append(time[k-1])
        elif prev == 3:
            sphr_stop.append(time[k-1])

        if crm[k] == 1:
            wind_start.append(time[k])
        elif crm[k] == 2:
            shth_start.append(time[k])
        elif crm[k] == 3:
            sphr_start.append(time[k])

        prev  = crm[k]
#
#-- close the last set
#
    klast = len(crm) -1
    if crm[klast] == 1:
        wind_stop.append(time[klast])
    elif crm[klast] == 2:
        shth_stop.append(time[klast])
    elif crm[klast] == 3:
        sphr_stop.append(time[klast])


    start_set = [wind_start, shth_start, sphr_start]
    stop_set  = [wind_stop,  shth_stop,  sphr_stop]

    return [start_set, stop_set]

#----------------------------------------------------------------------------------------------------------
#-- find_fmt_region: find fmt changing periods                                                           --
#----------------------------------------------------------------------------------------------------------

def find_fmt_region(start, stop, fmt, time):
    """
    find fmt changing periods
    input:  start   --- starting time in sec from 1998.1.1
            sopt    --- stopping time in sec from 1998.1.1
            fmt     --- a list of fmt values
            time    --- a list of time coresponding to fmt list
    output: [start_set, stop_set]
            start_set = [fmt1_start, fmt2_start, fmt3_start, fmt4_start, fmt5_start]
            stop_set  = [fmt1_stop,  fmt2_stop,  fmt3_stop,  fmt4_stop,  fmt5_stop]
    """

    for i in range(1, 6):
        exec "fmt%s_start = []" % (str(i))
        exec "fmt%s_stop  = []" % (str(i))

    prev       = fmt[0].lower()
    exec '%s_start.append(%5.4f)' % (fmt[0].lower(), time[0])
    for i in range(1, len(fmt)):
        if fmt[i].lower() == prev:
            continue
        else:
            exec '%s_stop.append(%5.4f)' % (prev, time[i])
            exec '%s_start.append(%5.4f)' % (fmt[i].lower(), time[i])
            prev = fmt[i].lower()
    flast = fmt[len(fmt)-1].lower()
    ftime = time[len(fmt)-1]
    exec '%s_stop.append(%5.4f)' % (flast, ftime)

    start_set = [fmt1_start, fmt2_start, fmt3_start, fmt4_start, fmt5_start]
    stop_set  = [fmt1_stop,  fmt2_stop,  fmt3_stop,  fmt4_stop,  fmt5_stop]

    return [start_set, stop_set]

#----------------------------------------------------------------------------------------------------------
#-- plot_strip_box: plotting shaded boxes on a panel                                                     --
#----------------------------------------------------------------------------------------------------------

def plot_strip_box(ax, start, stop, bstart_set, bstop_set, color=['red','blue', 'yellow', 'green', 'lime']):
    """
    plotting shaded boxes on a panel
    input:  ax          --- panel name
            start       --- xmin
            stop        --- xmax
            bstart_set  --- a list of lists of the beginning positions
            bstop_set   --- a list of lists of the ending positions
            color       --- a list of color. default is ['red','blue', 'yellow', 'green', 'lime']
    """

    xmin = int(stime_to_ydate(start))+1
    xmax = int(stime_to_ydate(stop))
    ymin = 0
    ymax = 1.0
    ax.set_autoscale_on(False) 
    ax.set_xbound(xmin,xmax) 
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
#
#--- go through each data set
#
    for i in range(0, len(bstart_set)):
        bset = bstart_set[i]
        eset = bstop_set[i]
#
#--- go through each begining and ending pair to create shaded area
#
        for j in range(0, len(bset)):
            begin = stime_to_ydate(bset[j])
            end   = stime_to_ydate(eset[j])

            p = plt.axvspan(begin, end, facecolor=color[i], alpha=0.5)


#----------------------------------------------------------------------------------------------------------
#-- plot_line: plotting a line for a given x and y data set                                             ---
#----------------------------------------------------------------------------------------------------------

def plot_line(ax, start, stop, x, y, color='green'):
    """
    plotting a line for a given x and y data set
    input:  ax      ---- panel name
            start   ---- xmin
            stop    ---- xmax
            color   ---- color of the line; default: green
            x       ---- a list of x values
            y       ---- a list of y values
    output: a  line on panel ax. 
    """

    xmin = int(stime_to_ydate(start))+1
    xmax = int(stime_to_ydate(stop))
    ymin = 0
    ymax = 1.0
    ax.set_autoscale_on(False) 
    ax.set_xbound(xmin,xmax) 
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    pmax = max(y)
    pmin = min(y)
    xval = []
    yval = []
    for i in range(0, len(x)):
        tx = stime_to_ydate(x[i])
        ty = (float(y[i])-pmin) / (pmax-pmin)

        xval.append(tx)
        yval.append(ty)

    plt.plot(xval, yval, color=color, lw=2)

#----------------------------------------------------------------------------------------------------------
#-- plot_points: plotting a scattered diagram for a given x and y data set                              ---
#----------------------------------------------------------------------------------------------------------

def plot_points(ax, start, stop, x, y, color='green',pts=1.5, lw='0'):
    """
    plotting a scattered diagram for a given x and y data set
    input:  ax      ---- panel name
            start   ---- xmin
            stop    ---- xmax
            color   ---- color of the points; default: green
            pts     ---- marker size; default: 1.5
            lw      ---- line width: default: 0
            x       ---- a list of x values
            y       ---- a list of y values
    output: a scattered diagram on panel ax. 
    """
    xmin = int(stime_to_ydate(start))+1
    xmax = int(stime_to_ydate(stop))
    ymin = 0
    ymax = 1.0
    ax.set_autoscale_on(False) 
    ax.set_xbound(xmin,xmax) 
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    pmax = max(y)
    xval = []
    yval = []
    for i in range(0, len(x)):
        tx = stime_to_ydate(x[i])
        ty = float(y[i]) / pmax

        xval.append(tx)
        yval.append(ty)

    plt.plot(xval, yval, color=color, lw=lw, marker='*', markersize=pts)


#----------------------------------------------------------------------------------------------------------
#-- stime_to_ydate: convert time in sec from 1998.1.1 to ydate                                          ---
#----------------------------------------------------------------------------------------------------------

def stime_to_ydate(stime):
    """
    convert time in sec from 1998.1.1 to ydate. no year info
    input: stime        ---- time in sec from 1998.1.1
    output: ydate       ---- ydate
    """

    time = tcnv.axTimeMTA(int(stime))
    atemp = re.split(':', time)
    ydate = float(atemp[1]) + float(atemp[2])/24.0 + float(atemp[3])/1440.0 + float(atemp[4]) / 86400.0

    return ydate


#-------------------------------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
from matplotlib.transforms import Bbox

mag_plot = 1

if len(sys.argv) == 3:
    start = sys.argv[1]
    stop  = sys.argv[2]
else:
    print "Input: start stop in the format of 2014:204:00:00:00 or in seconds from 1998.1.1"
    exit(1)

if __name__ == "__main__":

    try:
        start = int(float(start))
        stop  = int(float(stop))
    except:
        start = tcnv.axTimeMTA(start)
        stop  = tcnv.axTimeMTA(stop)

    plot_data(start, stop, mag_plot)
