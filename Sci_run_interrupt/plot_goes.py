#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       plot_goes.py: plot GOES data                                            #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Apr 29, 2013                                       #
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

from pylab import *

if __name__ == '__main__':

    mpl.use('Agg')

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

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


#-----------------------------------------------------------------------------------------------------------------
#--- plotGOESMain: read GOES data and plot them.                                                               ---
#-----------------------------------------------------------------------------------------------------------------

def plotGOESMain(event, start, stop, comp_test='NA'):

    'read GOES data from data_dir and plot them. Input: event, interruption start and stop time (e.g. 20120313        2012:03:13:22:41        2012:03:14:13:57)'

#
#--- read radiation zone information
#
    radZone = ptrf.readRadZone(event)

#
#--- read GOES data
#

    if comp_test == 'test':
        file = test_data_dir + event + '_goes.txt'
        plot_out = test_goes_dir
    else:
        file = data_dir + event + '_goes.txt'
        plot_out = goes_dir

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    dofy  = []
    p1    = []
    p2    = []
    p5    = []
    dcnt  = 0

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        btemp = re.split('\.', atemp[0])
        if ent and btemp[0].isdigit():

            dofy.append(atemp[0])

            val1 = float(atemp[1])
            if val1 <= 0:
                val1 = 1e-5

            val2 = float(atemp[2])
            if val2 <= 0:
                val2 = 1e-5

            val3 = float(atemp[3])
            if val3 <= 0:
                val3 = 1e-5

            p1.append(math.log10(val1))
            p2.append(math.log10(val2))
            p5.append(math.log10(val3))

#
#--- modify date formats
#
    begin = start + ':00'
    (year1, month1, date1, hours1, minutes1, seconds1, ydate1, dom1, sectime1) = tcnv.dateFormatConAll(begin)
    end   = stop  + ':00'
    (year2, month2, date2, hours2, minutes2, seconds2, ydate2, dom2, sectime2) = tcnv.dateFormatConAll(end)

#
#--- find plotting range
#

    (pYearStart, periodStart, pYearStop, periodStop, plotYearStart, plotStart, plotYearStop, plotStop, pannelNum) \
                 = itrf.findCollectingPeriod(year1, ydate1, year2, ydate2)

#
#--- if the interuption go over two years, adjust the ending ydate to that of the previous year
#
    if year2 > year1:
        chk = 4.0 * int(0.25 * year1)
        if chk == year1:
            base = 366
        else:
            base = 365

        ydate2 += base

#
#--- plot data
#
    if pannelNum == 1:
        plotGOES(dofy, p1, p2, p5, ydate1, ydate2, plotStart, plotStop, radZone)
        cmd = 'mv ./out.png ' + plot_out + event + '_goes.png'
        os.system(cmd)
#
#--- if the interruption period cannot be covered by one plotting panel, create as many panels as we need to cover the period.
#
    else:
        pstart = plotStart
        prange = pannelNum + 1
        for i in range(1, prange):
            pend = pstart + 5
            if i == 1:
                plotGOES(dofy, p1, p2, p5, ydate1, 'NA', pstart, pend, radZone)
                cmd = 'mv ./out.png ' + plot_out + event + '_goes.png'
                os.system(cmd)
            elif i == pannelNum:
                plotGOES(dofy, p1, p2, p5, 'NA', ydate2, pstart, pend, radZone)
                cmd = 'mv ./out.png ' + plot_out + event + '_goes_pt'+ str(i) +  '.png'
                os.system(cmd)
            else:
                plotGOES(dofy, p1, p2, p5, 'NA', 'NA', pstart, pend, radZone)
                cmd = 'mv ./out.png ' + plot_out + event + '_goes_pt'+ str(i) +  '.png'
                os.system(cmd)
            pstart = pend

#-----------------------------------------------------------------------------------------------------------------
#--- plotGOES: create three panel plots of GOES data                                                         ---
#-----------------------------------------------------------------------------------------------------------------

def plotGOES(dofy, p1, p2, p5, start, stop, xmin, xmax,  radZone):

    'create three panel plots of GOES data: Input: date (dofy), p1, p2, p5, interruption start/stop (dofy), plotting period(dofy), radZone info'

#
#--- setting the plotting ranges
#
    ymin = -3
    ymax =  5

    plt.close('all')

#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=6)
    plt.subplots_adjust(hspace=0.08)

#--------------------------------
#---- first panel: P1
#--------------------------------

#
#--- set plotting range
#
    ax1 = plt.subplot(311)

    ax1.set_autoscale_on(False)                     #---- these three may not be needed for the new pylab, but 
    ax1.set_xbound(xmin,xmax)                       #---- they are necessary for the older version to set

    ax1.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax1.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    tixRow = ptrf.makeTixsLabel(ymin, ymax)
    ax1.set_yticklabels(tixRow)

#
#--- plot line
#
    p0, =plt.plot(dofy,p1, color='black', lw=0, marker='.', markersize=0.8)

#
#--- plot radiation zone makers
#
    ptrf.plotRadZone(radZone, xmin, xmax, ymin)

#
#--- put lines to indicate the interrupted time period
#

    if start != 'NA':
        plt.plot([start, start], [ymin, ymax], color='red', lw=2)

        xdiff = xmax - xmin
        ydiff = ymax - ymin
        xtext = start + 0.01 * xdiff
        ytext = ymax - 0.2 * xdiff

        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)

#
#--- mark y axis
#
    ax1.set_ylabel('Log(p1 Rate)')


#----------------------------
#--- second panel:  P2
#----------------------------

#
#--- set plotting range
#
    ax2 = plt.subplot(312, sharex=ax1)

    ax2.set_autoscale_on(False)
    ax2.set_xbound(xmin,xmax)


    ax2.set_xlim(xmin, xmax, auto=False)
    ax2.set_ylim(ymin, ymax, auto=False)

    tixRow = ptrf.makeTixsLabel(ymin, ymax)
    ax2.set_yticklabels(tixRow)
#
#--- plot line
#

    p0, = plt.plot(dofy, p2, color='black', lw=0, marker='.', markersize=0.8)

#
#--- plot radiation zone makers
#
    ptrf.plotRadZone(radZone, xmin, xmax, ymin)

#
#--- put lines to indicate the interrupted time period
#

    if start != 'NA':
        plt.plot([start, start], [ymin, ymax], color='red', lw=2)

        xdiff = xmax - xmin
        ydiff = ymax - ymin
        xtext = start + 0.01 * xdiff
        ytext = ymax - 0.2 * xdiff

        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop  != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
#
#--- draw trigger level
#
    plt.plot([xmin,xmax],[2.0, 2.0], color='red', linestyle='--', lw=1.0)

#
#--- label y axis
#
    ax2.set_ylabel('Log(p2 Rate)')

#----------------------
#--- third Panel: P5
#----------------------

#
#--- set plotting range
#
    ax3 = plt.subplot(313, sharex=ax1)

    ax3.set_autoscale_on(False)
    ax3.set_xbound(xmin,xmax)


    ax3.set_xlim(xmin, xmax, auto=False)
    ax3.set_ylim(ymin, ymax, auto=False)

    tixRow = ptrf.makeTixsLabel(ymin, ymax)
    ax3.set_yticklabels(tixRow)

#
#--- plot line
#
    p0, = plt.plot(dofy, p5, color='black', lw=0, marker='.', markersize=0.8)

#
#--- plot radiation zone makers
#
    ptrf.plotRadZone(radZone, xmin, xmax, ymin)

#
#--- put lines to indicate the interrupted time period
#

    if start != 'NA':
        plt.plot([start, start], [ymin, ymax], color='red', lw=2)

        xdiff = xmax - xmin
        ydiff = ymax - ymin
        xtext = start + 0.01 * xdiff
        ytext = ymax - 0.2 * xdiff

        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop  != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
#
#--- draw trigger level
#
    plt.plot([xmin,xmax],[-0.155, -0.155], color='red', linestyle='--', lw=1.0)

#
#--- label axes
#
    ax3.set_ylabel('Log(p5 Rate)')
    xlabel('Day of Year')

#
#--- plot x axis tick label only at the third panel
#
    for ax in ax1, ax2, ax3:
        if ax != ax3:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            pass

#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=100)

