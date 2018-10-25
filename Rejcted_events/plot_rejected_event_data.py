#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           plot_rejected_event_data.py: plot rejected event data                                           #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           last update: Oct 24, 2018                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import numpy
import getopt
import os.path
import time
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- interactive plotting module
#
import mpld3
from mpld3 import plugins, utils
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')
from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines


path = '/data/mta/Script/ACIS/Rej_events/Scripts/house_keeping/dir_list'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(bin_dir)
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def plot_rej_evt_data():

    for ccd in range(0, 10):
        print "CCD: " + str(ccd)
        ifile = data_dir + 'CCD' + str(ccd) + '_rej.dat'
        data  = read_data_file(ifile )
        set1  = [[], [],[],[],[],[],[]]
        set2  = [[], [],[],[],[],[],[]]
        for dline in data[1:]:
            ent = re.split('\s+', dline)
            ytime = convert_sec_to_frq_year(ent[0])
            if float(ent[-2]) > 50000:
                set1[0].append(ytime)
                set1[1].append(float(ent[1]))
                set1[2].append(float(ent[3]))
                set1[3].append(float(ent[7]))
                set1[4].append(float(ent[9]))
            else:
                set2[0].append(ytime)
                set2[1].append(float(ent[1]))
                set2[2].append(float(ent[3]))
                set2[3].append(float(ent[7]))
                set2[4].append(float(ent[9]))

        plot_data(set1, ccd, 'cti')
        plot_data(set2, ccd, 'sci')

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def convert_sec_to_frq_year(stime):

        date  = Chandra.Time.DateTime(stime).date
        atemp = re.split(':', date)
        year  = float(atemp[0])
        yday  = float(atemp[1])
        hh    = float(atemp[2])
        mm    = float(atemp[3])
        ss    = float(atemp[4])

        if isLeapYear(year) == 1:
            base = 366
        else:
            base = 365

        year += (yday + hh / 24.0 + mm / 1440.0 + ss / 86400.0) / base

        return year

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def plot_data(data_set, ccd, part):

    #ylab_list = ['EVTSENT', 'DROP_AMP', 'DROP_POS', 'DROP_GRD', 'THR_PIX', 'BERR_SUM']
    #ymax_list = [300, 300, 2, 700, 3e4, 0.2]
    ylab_list = ['EVTSENT', 'DROP_AMP', 'DROP_GRD', 'THR_PIX']
    ymax_list = [300, 300, 700, 3e4]
    now = convert_sec_to_frq_year(time.strftime("%Y:%j:%H:%M:%S", time.gmtime()))
    xmin = 2000.0
    now += 1.4
    xmax = int(round(now , 1))

    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 10 
    mpl.rcParams['font.weight'] = 'medium'
    props = font_manager.FontProperties(size=10)
    props = font_manager.FontProperties(weight='medium')
    plt.subplots_adjust(hspace=0.08)

    for ax in range(0, 4):
        axnam = 'ax' + str(ax)
        j     = ax + 1
        line  = '61' + str(j)

        exec "%s = plt.subplot(%s)"       % (axnam, line)
        exec "%s.set_autoscale_on(False)" % (axnam)  
        exec "%s.set_xbound(xmin,xmax)"   % (axnam)
        exec "%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axnam)
        exec "%s.set_ylim(ymin=0, ymax=%s, auto=False)" % (axnam, str(ymax_list[ax]))

        #plt.plot(data_set[0], data_set[j], marker='*', markersize='4', lw=0)
        plt.plot(data_set[0], data_set[j],marker='.', markerfacecolor='red', lw=0)
        ylabel(ylab_list[ax], fontweight='medium')
#
#--- add x ticks label only on the last panel
#
    for i in range(0, 4):
       axnam = 'ax' + str(i)
       if i != 3:
           exec "line = %s.get_xticklabels()" % (axnam)
           for label in  line:
               label.set_visible(False)
       else:
           pass

    xlabel('Time (Year)', fontweight='medium')
#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0,8.0)
#
#--- save the plot in png format
#
    outname = html_dir + 'Plots/ccd' + str(ccd) + '_' + part  + '.png'
    plt.savefig(outname, format='png', dpi=200, bbox_inches='tight')

    plt.close('all')


#--------------------------------------------------------------------------------------------------------
#-- read_data_file: read data file and return a list of data                                           --
#--------------------------------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):
    """
    read data file and return a list of data
    input:  ifile   --- file name
            remove  --- if 1, remove the file after reading it
    output: data    --- a list of data
    """
    try:
        f    = open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        if remove == 1:
            cmd = 'rm ' + ifile
            os.system(cmd)
    except:
        data = []

    return data

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def isLeapYear(year):

    """
    chek the year is a leap year
    Input:year   in full lenth (e.g. 2014, 813)
    
    Output:   0--- not leap year
    1--- yes it is leap year
    """

    year = int(float(year))
    chk  = year % 4 #---- evry 4 yrs leap year
    chk2 = year % 100   #---- except every 100 years (e.g. 2100, 2200)
    chk3 = year % 400   #---- excpet every 400 years (e.g. 2000, 2400)
    
    val  = 0
    if chk == 0:
        val = 1
    if chk2 == 0:
        val = 0
    if chk3 == 0:
        val = 1
    
    return val

#---------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_rej_evt_data()
