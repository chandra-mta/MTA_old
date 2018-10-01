#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       plot_noaa_rad.py: plot NOAA radiation datai                                     #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Apr 29, 2014                                               #
#                                                                                       #
#########################################################################################

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
#--- append a  path to a privte folder to python directory
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

#-----------------------------------------------------------------------------------
#---startACEPlot: the main function to plot NOAA data                            ---
#-----------------------------------------------------------------------------------

def startACEPlot(event, start, stop, comp_test = 'NA'):


    'for a gien event, start and stop data, initiate ACE plottings.'

#
#--- change time format to year and ydate (float)
#
    begin = start + ':00'                #---- need to add "seconds" part to dateFormtCon to work correctly
    end   = stop  + ':00'

    (year1, month1, day1, hours1, minutes1, seconds1, ydate1) = tcnv.dateFormatCon(begin)
    (year2, month2, day2, hours2, minutes2, seconds2, ydate2) = tcnv.dateFormatCon(end)

#
#--- plot ACE Data
#
    aceDataPlot(event, year1, ydate1, year2, ydate2, comp_test)


#-----------------------------------------------------------------------------------
#--- aceDataPlot: ACE data plotting manager                                      ---
#-----------------------------------------------------------------------------------

def aceDataPlot(name, startYear, startYday, stopYear, stopYday, comp_test = 'NA'):

    'manage ACE data plot routines. Input: event name, interruption starting time, and interruption ending time in year:yday format'

#
#--- check whether this is a test case
#
    if comp_test == 'test':
        plot_out = test_plot_dir
    else:
        plot_out = plot_dir

#
#--- set the plotting range
#

    (pYearStart, periodStart, pYearStop, periodStop, plotYearStart, plotStart, plotYearStop, plotStop, period) \
                = itrf.findCollectingPeriod( startYear, startYday, stopYear, stopYday)

#
#--- read radation zone information
#

    radZone = ptrf.readRadZone(name)

#
#--- initialize data lists and read in the data
#
    dofy  = []
    e38   = []
    e175  = []
    p47   = []
    p112  = []
    p310  = []
    p761  = []
    p1060 = []
    ani   = []

    readACEData(name, dofy, e38, e175, p47, p112, p310, p761, p1060, ani, comp_test)
#
#--- if the ending data is in the following year
#
    if stopYear > startYear:
       chk = 4.0 * int (0.25 * startYear)
       if chk == startYear:
           base = 366
       else:
           base = 365
       stopYday += base
#
#--- plot data
#

    if period == 1:
        if startYear < 2014:
            plotACE(dofy, e38, e175, p47, p112, p310, p761, p1060, ani, startYday, stopYday, plotStart, plotStop, radZone)
        else:
            plotACE(dofy, e38, e175, p47, p112, p310, p761, p1060, 'NA', startYday, stopYday, plotStart, plotStop, radZone)

        cmd = 'mv ./out.png ' + plot_out + name + '.png'
        os.system(cmd)

#
#--- if the interruption period cannot be covered by one plotting panel, create as many panels as we need to cover the period.
#

    else:
        pstart = plotStart 
        prange = period + 1
        if startYear < 2014:
            for i in range(1, prange):
                pend = pstart + 5
                if i == 1:
                    plotACE(dofy, e38, e175, p47, p112, p310, p761, p1060, ani, startYday, 'NA', pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_out + name + '.png'
                    os.system(cmd)
                elif i == period:
                    plotACE(dofy, e38, e175, p47, p112, p310, p761, p1060, ani, 'NA', stopYday, pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_out + name + '_pt'+ str(i) + '.png'
                    os.system(cmd)
                else:
                    plotACE(dofy, e38, e175, p47, p112, p310, p761, p1060, ani, 'NA', 'NA', pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_out + name + '_pt'+ str(i) + '.png'
                    os.system(cmd)
    
                pstart  = pend

        else:
            for i in range(1, prange):
                pend = pstart + 5
                if i == 1:
                    plotACE(dofy, e38, e175, p47, p112, p310, p761, p1060, 'NA', startYday, 'NA', pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_out + name + '.png'
                    os.system(cmd)
                elif i == period:
                    plotACE(dofy, e38, e175, p47, p112, p310, p761, p1060, 'NA', 'NA', stopYday, pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_out + name + '_pt'+ str(i) + '.png'
                    os.system(cmd)
                else:
                    plotACE(dofy, e38, e175, p47, p112, p310, p761, p1060, 'NA', 'NA', 'NA', pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_out + name + '_pt'+ str(i) + '.png'
                    os.system(cmd)
    
                pstart  = pend


#-----------------------------------------------------------------------------------
#--- readACEData: reading ACE Data from ACE data table                           ---
#-----------------------------------------------------------------------------------

def readACEData(file, dofy, elec38, elec175, proton47, proton112, proton310, proton761, proton1060, aniso, comp_test):

    'reading an ACE data file located in a Interrupt Data_dir'

    if comp_test == 'test':
        input = test_data_dir + file + '_dat.txt'       #--- test data file
    else:
        input = data_dir + file + '_dat.txt'            #--- data file format is e.g.: 20120313_dat.txt

    f     = open(input, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    total = 0
    for ent in data:
        if ent:
            atemp = re.split('\s+|\t+', str(ent))
            btemp = re.split('\.', str(atemp[0]))

            if str.isdigit(str(btemp[0])):

                if atemp[1] and atemp[2] and atemp[3] and atemp[4] and atemp[5] and atemp[6] and atemp[7] and atemp[8]:
                    atemp[1] = float(atemp[1])
                    atemp[2] = float(atemp[2])
                    atemp[3] = float(atemp[3])
                    atemp[4] = float(atemp[4])
                    atemp[5] = float(atemp[5])
                    atemp[6] = float(atemp[6])
                    atemp[7] = float(atemp[7])
                    atemp[8] = float(atemp[8])

		    for m in range(1, 8):
		        if atemp[m] <= 0:
			    atemp[m] = 1e-5
    
                    dofy.append(float(atemp[0]))
    
                    elec38.append(math.log10(atemp[1]))
                    elec175.append(math.log10(atemp[2]))
                    proton47.append(math.log10(atemp[3]))
                    proton112.append(math.log10(atemp[4]))
                    proton310.append(math.log10(atemp[5]))
                    proton761.append(math.log10(atemp[6]))
                    proton1060.append(math.log10(atemp[7]))
                    aniso.append(atemp[8])

    return total

#-----------------------------------------------------------------------------------
#--- plotACE: plotting routine                                                   ---
#-----------------------------------------------------------------------------------

def plotACE(xdata, ydata0, ydata1, ydata2, ydata3, ydata4, ydata5, ydata6, ydata7, start, stop, xmin, xmax, radZone):

    "actual plotting of ACE data are done with this fuction. Input data are time (in ydate), elec38, elec175, proton47, proton 112, prton310, prton 761, proton1060, anisotrophy index, interrutionp starting time, interrutiopn ending time, plotting range (xmin, mnax), and radiation zone interval datea "

#
#--- setting the plotting ranges for each plot
#

    electronMin = 1.0
    electronMax = 6.0
    protonMin   = 1.0
    protonMax   = 6.0
    anisoMin    = 0.
    anisoMax    = 2.


    plt.close('all')                                    #--- clean up the previous plotting 
#
#--- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=6)
    plt.subplots_adjust(hspace=0.08)

#---------------------------------
#--- first panel : electron data
#---------------------------------

    if ydata7 !='NA':
        ax1  = plt.subplot(311)
    else:
        ax1  = plt.subplot(211)

#
#--- set plotting range
#

    ymin = electronMin 
    ymax = electronMax

    ax1.set_autoscale_on(False)                     #---- these three may not be needed for the new pylab, but 
    ax1.set_xbound(xmin,xmax)                       #---- they are necessary for the older version to set

    ax1.set_xlim(xmin, xmax, auto=False)
    ax1.set_ylim(ymin, ymax, auto=False)

    tixRow = ptrf.makeTixsLabel(ymin, ymax)
    ax1.set_yticklabels(tixRow)
#
#-- plot lines
#

    xval = []
    yval = []
    itrf.removeNoneData(xdata, ydata0, xval, yval, -5)
    for xxx in yval:
        if xxx <= 0:
           print xxx

    p0, =plt.plot(xval, yval, color='red', lw=1)

    xval = []
    yval = []
    itrf.removeNoneData(xdata, ydata1, xval, yval, -5)
    p1, =plt.plot(xval, yval, color='blue',lw=1)
#
#--- plot radiation zone markers
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
        ytext = ymax - 0.1 * ydiff
    
        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop  != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)

#
#--- add legend
#
    leg = legend([p0,p1], ['Electron30-53','Electron75-315'], prop=props)
    leg.get_frame().set_alpha(0.5)

#
#--- mark y axis
#
    ax1.set_ylabel('Electron/cm2-q-sr-Mev')

#---------------------------------
#---- second panel: proton data 
#---------------------------------

    if ydata7 != 'NA':
        ax2 = plt.subplot(312, sharex=ax1)
    else:
        ax2 = plt.subplot(212, sharex=ax1)

#
#--- set plotting range
#
    ymin = protonMin
    ymax = protonMax
    ax2.set_autoscale_on(False)                     #---- these three may not be needed for the new pylab, but 
    ax2.set_xbound(xmin,xmax)                       #---- they are necessary for the older version to set

    ax2.set_xlim(xmin, xmax, auto=False)
    ax2.set_ylim(ymin, ymax, auto=False)

    tixRow = ptrf.makeTixsLabel(ymin, ymax)
    ax2.set_yticklabels(tixRow)

#
#--- plot lines
#


    xval = []
    yval = []
    itrf.removeNoneData(xdata, ydata2, xval, yval, -5)
    p0, = plt.plot(xval, yval, color='red',   lw=1)

    xval = []
    yval = []
    itrf.removeNoneData(xdata, ydata3, xval, yval, -5)
    p1, = plt.plot(xval, yval, color='blue',  lw=1)

    xval = []
    yval = []
    itrf.removeNoneData(xdata, ydata4, xval, yval, -5)
    p2, = plt.plot(xval, yval, color='green', lw=1)

    xval = []
    yval = []
    itrf.removeNoneData(xdata, ydata5, xval, yval, -5)
    p3, = plt.plot(xval, yval, color='aqua',  lw=1)

    xval = []
    yval = []
    itrf.removeNoneData(xdata, ydata6, xval, yval, -5)
    p4, = plt.plot(xval, yval, color='teal',  lw=1)

#
#--- plot radiation zone markers
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
        ytext = ymax - 0.1 * ydiff
    
        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop  != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)

#
#--- draw trigger level
#
    plt.plot([xmin, xmax], [4.70, 4.70], color='red', linestyle='--', lw=1.0)
#
#--- add legend
#
    leg = legend([p0, p1, p2, p3, p4], ['Proton47-65','Proton112-187', 'Proton310-580','Proton781-1220','Prton1080-1910'], prop=props)
    leg.get_frame().set_alpha(0.5)

#
#--- label y axis

    ax2.set_ylabel('Proton/cm2-q-sr-Mev')

#-----------------------------------
#--- third panel: anisotropy index 
#-----------------------------------

    if ydata7 != 'NA':
        ax3 = plt.subplot(313, sharex=ax1)

#
#--- set plotting range
#
        ymin = anisoMin
        ymax = anisoMax

        ax3.set_autoscale_on(False)                     #---- these three may not be needed for the new pylab, but 
        ax3.set_xbound(xmin,xmax)                       #---- they are necessary for the older version to set
    
        ax3.set_xlim(xmin, xmax, auto=False)
        ax3.set_ylim(ymin, ymax, auto=False)

#       tixRow = ptrf.makeTixsLabel(ymin, ymax)
#       ax3.set_yticklabels(tixRow)


#
#--- check the case the data is not available (no data: -1.0 )
#
        if len(ydata7) == 0:
            xtpos = xmin + 0.1 * (xmax - xmin)
            ytpos = 1.5
            plt.text(xtpos, ytpos, r'No Data', color='red', size=12)
    
        else:
            avg = math.fsum(ydata7) / len(ydata7)
    
            if avg < -0.95 and avg  > -1.05:
                xtpos = xmin + 0.1 * (xmax - xmin)
                ytpos = 1.5
                plt.text(xtpos, ytpos, r'No Data', color='red', size=12)
    
            else:
#
#---- plot line
#

                xval = []
                yval = []
                itrf.removeNoneData(xdata, ydata7, xval, yval, 0, 2)
                p0, = plt.plot(xval, yval, color='red', lw=1)

#
#--- plot radiation zone markers
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
            ytext = ymax  - 0.1  * ydiff
     
            plt.text(xtext, ytext, r'Interruption', color='red')
    
        if stop  != 'NA':
            plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
     
    
        ax3.set_ylabel('Anisotropy Index')
    
#
#--- plot x axis tick label only at the third panel
#

    xlabel('Day of Year')
    if ydata7 != 'NA':
        for ax in ax1, ax2, ax3:
            if ax != ax3:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
            else:
                pass
    else:
        for ax in ax1, ax2:
            if ax != ax2:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
            else:
                pass

#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    if ydata7 != 'NA':
        fig.set_size_inches(10.0, 5.0)
    else:
        fig.set_size_inches(10.0, 3.33)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=100)


