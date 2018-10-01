#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       plot_ephin.py: plot Ephin data                                          #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Apr 29, 2014                                       #
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
#--- append  a path to a privte folder to python directory
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
#--- plotEphinMain: read Ephin data and plot them.                                                             ---
#-----------------------------------------------------------------------------------------------------------------

def plotEphinMain(event, start, stop, comp_test = 'NA'):

    'read Ephin data from data_dir and plot them. Input: event, interruption start and stop time (e.g. 20120313        2012:03:13:22:41        2012:03:14:13:57)'

#
#--- read radiation zone information
#
    radZone = ptrf.readRadZone(event)

#
#--- read EPHIN data
#

    if comp_test == 'test':
        file     = test_data_dir + event + '_eph.txt'
        plot_out = test_ephin_dir
    else:
        file     = data_dir + event + '_eph.txt'
        plot_out = ephin_dir

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    dofy  = []
    prtn1 = []
    prtn2 = []
    prtn3 = []
    dcnt  = 0
    dataset= 0

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



            prtn1.append(math.log10(val1))
            prtn2.append(math.log10(val2))
            prtn3.append(math.log10(val3))
        else:
#
#--- checking which data set, old one: p4, p41, e1300. new one: hrc, e150, e1300
#
            m = re.search('hrc', ent)
            if m is not None:
                    dataset = 1

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
        if year1 < 2014:
            plotEphin(dofy, prtn1, prtn2, prtn3, ydate1, ydate2, plotStart, plotStop, radZone, dataset)
        else:
            plotEphin(dofy, prtn1, 'NA', 'NA', ydate1, ydate2, plotStart, plotStop, radZone, dataset)
        cmd = 'mv ./out.png ' + plot_out + event + '_eph.png'
        os.system(cmd)
#
#--- if the interruption period cannot be covered by one plotting panel, create as many panels as we need to cover the period.
#
    else:
        pstart = plotStart
        prange = pannelNum + 1
        if year1 < 2014:
            for i in range(1, prange):
                pend = pstart + 5
                if i == 1:
                    plotEphin(dofy, prtn1, prtn2, prtn3, ydate1, 'NA', pstart, pend, radZone, dataset)
                    cmd = 'mv ./out.png ' + plot_out + event + '_eph.png'
                    os.system(cmd)
                elif i == pannelNum:
                    plotEphin(dofy, prtn1, prtn2, prtn3, 'NA', ydate2, pstart, pend, radZone, dataset)
                    cmd = 'mv ./out.png ' + plot_out + event + '_eph_pt'+ str(i) +  '.png'
                    os.system(cmd)
                else:
                    plotEphin(dofy, prtn1, prtn2, prtn3, 'NA', 'NA', pstart, pend, radZone, dataset)
                    cmd = 'mv ./out.png ' + plot_out + event + '_eph_pt'+ str(i) +  '.png'
                    os.system(cmd)
                pstart = pend

        else:
            for i in range(1, prange):
                pend = pstart + 5
                if i == 1:
                    plotEphin(dofy, prtn1, 'NA', 'NA', ydate1, 'NA', pstart, pend, radZone, dataset)
                    cmd = 'mv ./out.png ' + plot_out + event + '_eph.png'
                    os.system(cmd)
                elif i == pannelNum:
                    plotEphin(dofy, prtn1, 'NA', 'NA', 'NA', ydate2, pstart, pend, radZone, dataset)
                    cmd = 'mv ./out.png ' + plot_out + event + '_eph_pt'+ str(i) +  '.png'
                    os.system(cmd)
                else:
                    plotEphin(dofy, prtn1, 'NA', 'NA', 'NA', 'NA', pstart, pend, radZone, dataset)
                    cmd = 'mv ./out.png ' + plot_out + event + '_eph_pt'+ str(i) +  '.png'
                    os.system(cmd)
                pstart = pend

#
#--- plot intro page
#
    pend = plotStart + 5
    if year1 < 2014:
        plotIntro(dofy, prtn2, ydate1, ydate2, plotStart, pend, radZone, dataset, year1)
    else:
        plotIntro(dofy, prtn1, ydate1, ydate2, plotStart, pend, radZone, dataset, year1)
    cmd = 'mv ./intro_out.png ' + intro_dir + event + '_intro.png'
    os.system(cmd)




#-----------------------------------------------------------------------------------------------------------------
#--- plotEphin: create three panel plots of Ephin data                                                         ---
#-----------------------------------------------------------------------------------------------------------------

def plotEphin(dofy, prtn1, prtn2, prtn3, start, stop, xmin, xmax,  radZone, dataset):

    'create three panel plots of Ephin data: Input: date (dofy), prtn1, prtn2, prtn3, interruption start/stop (dofy), plotting period(dofy), radZone info'

#
#--- setting the plotting ranges
#
    p4Min    = 0 
    p4Max    = 6

    prtn1Min = 3 
    prtn1Max = 5

    elcMin = -3
    elcMax =  6

    plt.close('all')

#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=6)
    plt.subplots_adjust(hspace=0.08)

#--------------------------------
#---- first panel: HRC/P4 Shield Rate
#--------------------------------

#
#--- set plotting range
#
    if dataset == 1:
        ymin = prtn1Min
        ymax = prtn1Max
    else:
        ymin = p4Min
        ymax = p4Max

    if prtn2 != 'NA':
        ax1 = plt.subplot(311)
    else:
        ax1 = plt.subplot(111)

    ax1.set_autoscale_on(False)                     #---- these three may not be needed for the new pylab, but 
    ax1.set_xbound(xmin,xmax)                       #---- they are necessary for the older version to set

    ax1.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax1.set_ylim(ymin=ymin, ymax=ymax, auto=False)

#
#--- plot line
#
    p0, =plt.plot(dofy,prtn1, color='black',   lw=0, marker='.', markersize=0.5)

#
#--- plot radiation zone makers
#
    ptrf.plotRadZone(radZone, xmin, xmax, ymin)

#
#--- plot trigger level
#

    if dataset == 0:
        plt.plot([xmin, xmax], [2.477,2.477], color='red', lw = 1)
    else:
        plt.plot([xmin, xmax], [4.80, 4.80], color='red', linestyle='--', lw=1.0)

#
#--- put lines to indicate the interrupted time period
#

    if start != 'NA':
        plt.plot([start, start], [ymin, ymax], color='red', lw=2)

        xdiff = xmax - xmin
        ydiff = ymax - ymin
        xtext = start + 0.01 * xdiff
        ytext = ymax - 0.2 * ydiff

        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
#
#--- mark y axis
#
    if dataset == 1:
        ax1.set_ylabel('Log(HRC Shield Rate)', size=8)
    else:
        ax1.set_ylabel('Log(p4 Rate)', size=8)



#----------------------------
#--- second panel: E150/p41 rate
#----------------------------

    if prtn2 != 'NA':
#
#--- set plotting range
#
        ymin = elcMin
        ymax = elcMax

        ax2 = plt.subplot(312, sharex=ax1)
    
        ax2.set_autoscale_on(False)
        ax2.set_xbound(xmin,xmax)
    
        ax2.set_xlim(xmin, xmax, auto=False)
        ax2.set_ylim(ymin, ymax, auto=False)

#
#--- skip every other y tix label so that easy to read
#

        tixRow = ptrf.makeTixsLabel(ymin, ymax)
        ax2.set_yticklabels(tixRow)

#
#--- plot line
#

        p0, = plt.plot(dofy, prtn2, color='black',    lw=0, marker='.', markersize=0.5)

#
#--- plot radiation zone makers
#
        ptrf.plotRadZone(radZone, xmin, xmax, ymin)

#
#--- plot trigger level
#

        plt.plot([xmin, xmax], [2,2], color='red', lw = 1)

#
#--- put lines to indicate the interrupted time period
#

        if start != 'NA':
            plt.plot([start, start], [ymin, ymax], color='red', lw=2)

            xdiff = xmax - xmin
            ydiff = ymax - ymin
            xtext = start + 0.01 * xdiff
            ytext = ymax - 0.2 * ydiff
    
            plt.text(xtext, ytext, r'Interruption', color='red')
    
        if stop  != 'NA':
            plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
    
#
#--- label y axis
#
        if dataset == 1:
            ax2.set_ylabel('Log(e150  Rate)')
        else:
            ax2.set_ylabel('Log(p41 Rate)')

#----------------------
#--- third Panel: E1300
#----------------------

#
#--- set plotting range
#
        ymin = elcMin
        ymax = elcMax

        ax3 = plt.subplot(313, sharex=ax1)
    
        ax3.set_autoscale_on(False)
        ax3.set_xbound(xmin,xmax)
    
        ax3.set_xlim(xmin, xmax, auto=False)
        ax3.set_ylim(ymin, ymax, auto=False)
    
#
#--- skip every other y tix label so that easy to read
#

        tixRow = ptrf.makeTixsLabel(ymin, ymax)
        ax3.set_yticklabels(tixRow)


#
#--- plot line
#
        p0, = plt.plot(dofy, prtn3, color='black',    lw=0, marker='.', markersize=0.5)

#
#--- plot radiation zone makers
#
        ptrf.plotRadZone(radZone, xmin, xmax, ymin)

#
#--- plot trigger level
#

        plt.plot([xmin, xmax], [1.301,1.301], color='red', lw = 1)

#
#--- put lines to indicate the interrupted time period
#

        if start != 'NA':
            plt.plot([start, start], [ymin, ymax], color='red', lw=2)
    
            xdiff = xmax - xmin
            ydiff = ymax - ymin
            xtext = start + 0.01 * xdiff
            ytext = ymax - 0.2 * ydiff
    
            plt.text(xtext, ytext, r'Interruption', color='red')
    
        if stop  != 'NA':
            plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)

#
#--- label axes
#
        ax3.set_ylabel('Log(e1300 Rate)')

#
#--- plot x axis tick label only at the third panel
#
        for ax in ax1, ax2, ax3:
            if ax != ax3:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
            else:
                pass

    xlabel('Day of Year')
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    if prtn2 != 'NA':
        fig.set_size_inches(10.0, 5.0)
    else:
        fig.set_size_inches(10.0, 1.7)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=100)









#-----------------------------------------------------------------------------------------------------------------
#--- plotIntro create an intro page prtn2 plot                                                       ---
#-----------------------------------------------------------------------------------------------------------------

def plotIntro(dofy, prtn, start, stop, xmin, xmax,  radZone, dataset, syear):

    'create an intro page prtn plot: Input: date (dofy), prtn, interruption start/stop (dofy), plotting period(dofy), radZone info'

#
#--- before year 2014 use E150 or P41 -------
#
    if syear < 2014:
#
#--- setting the plotting ranges
#
        elcMin = -3
        elcMax =  6
    
        plt.close('all')

#
#---- set a few parameters
#
        mpl.rcParams['font.size'] = 9
        props = font_manager.FontProperties(size=6)
        plt.subplots_adjust(hspace=0.10)

#
#--- set plotting range
#
        ymin = elcMin
        ymax = elcMax

        ax = plt.subplot(111, autoscale_on=False)

#    ax.set_autoscale_on(False)
#    ax.set_xbound(xmin,xmax)

        ax.set_xlim(xmin, xmax, auto=False)
        ax.set_ylim(ymin, ymax, auto=False)

#
#--- skip every other y tix label so that easy to read
#

        tixRow = ptrf.makeTixsLabel(ymin, ymax)
        ax.set_yticklabels(tixRow)

#
#--- plot line
#

        xval = []
        yval = []
        itrf.removeNoneData(dofy, prtn, xval, yval, -4)
        plt.plot(xval, yval, color='black',    lw=0,  marker='.', markersize=0.8)

#
#--- plot radiation zone makers
#
        ptrf.plotRadZone(radZone, xmin, xmax, ymin)

#
#--- plot trigger level
#

        plt.plot([xmin, xmax], [2,2], color='red', lw = 1)

#
#--- put lines to indicate the interrupted time period
#

        if start != 'NA':
            plt.plot([start, start], [ymin, ymax], color='red', lw=2)
    
            xdiff = xmax - xmin
            ydiff = ymax - ymin
            xtext = start + 0.01 * xdiff
            ytext = ymax - 0.2 * ydiff
    
            plt.text(xtext, ytext, r'Interruption', color='red')
    
        if stop  != 'NA':
            plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
    
#
#--- label x and y axis
#
        ax.set_xlabel('Day of Year')
        xlabel("Day of Year")
        if dataset == 1:
            ax.set_ylabel('Log(e150 Rate)')
        else:
            ax.set_ylabel('Log(p41 Rate)')
    
        plt.tight_layout()


    else:
#
#--- use HRC plot after year 2014 --------------------------------------
#
        prtnMin = 3
        prtnMax = 5
    
        plt.close('all')

#
#---- set a few parameters
#
        mpl.rcParams['font.size'] = 9
        props = font_manager.FontProperties(size=6)
        plt.subplots_adjust(hspace=0.10)
#
#--- set plotting range
#
        if dataset == 1:
            ymin = prtnMin
            ymax = prtnMax
        else:
            ymin = p4Min
            ymax = p4Max
    
        ax = plt.subplot(111, autoscale_on=False)
    
        ax.set_autoscale_on(False)                     #---- these three may not be needed for the new pylab, but 
        ax.set_xbound(xmin,xmax)                       #---- they are necessary for the older version to set
    
        ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
        ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
    
#
#--- plot line
#
        p0, =plt.plot(dofy,prtn, color='black',   lw=0, marker='.', markersize=0.5)

#
#--- plot radiation zone makers
#
        ptrf.plotRadZone(radZone, xmin, xmax, ymin)

#
#--- plot trigger level
#

        if dataset == 0:
            plt.plot([xmin, xmax], [2.477,2.477], color='red', lw = 1)
        else:
            plt.plot([xmin, xmax], [4.80, 4.80], color='red', lw=1)

#
#--- put lines to indicate the interrupted time period
#

        if start != 'NA':
            plt.plot([start, start], [ymin, ymax], color='red', lw=2)
    
            xdiff = xmax - xmin
            ydiff = ymax - ymin
            xtext = start + 0.01 * xdiff
            ytext = ymax - 0.2 * ydiff
    
            plt.text(xtext, ytext, r'Interruption', color='red')
    
        if stop != 'NA':
            plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
            
#
#--- mark axes
#
        ax.set_ylabel('Log(HRC Shield Rate)', size=8)
        ax.set_xlabel('Day of Year')
        xlabel("Day of Year")



#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 2.0)
#
#--- save the plot in png format
#
    plt.savefig('intro_out.png', format='png', dpi=100)


