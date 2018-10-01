#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       plot_aiming_point_data.py: plot aiming point trend data                                 #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Jul 02, 2018                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
import pyfits
import unittest
from datetime import datetime
from time import gmtime, strftime, localtime
import Chandra.Time
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; punlearn dataseeker  ', shell='tcsh')
#
#--- plotting routine
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines
#
#--- reading directory list
#
path = '/data/mta/Script/ALIGNMENT/Abs_pointing/Scripts/house_keeping/dir_list'

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
import robust_linear              as robust

#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------
#-- plot_aiming_trend_data: read data and plot data of aiming point                   --
#---------------------------------------------------------------------------------------

def plot_aiming_trend_data():
    """
    read data and plot data of aiming point 
    input: none but read from <data_dir>/aics_i etc
    output: <web_dir>/Plots/<inst>_<ychoice>.png
    """

    year = int(float(time.strftime("%Y", time.gmtime())))
    xmax = year + 1

    for inst in ('acis_i', 'acis_s', 'hrc_i', 'hrc_s'):
        ifile = data_dir + inst + '_data'
        data  = read_data_file(ifile, '\t+')

        atime = data[0][:2]                     #---- skip the header part
        atime = convert_time_to_year(atime)
        dy    = data[7][:2]
        dz    = data[8][:2]

        [atime, dy, dz] = remove_extreme(atime, dy, dz)

        plot_data(atime, dy, 1999, xmax, -2, 2, inst, 'y')
        plot_data(atime, dz, 1999, xmax, -2, 2, inst, 'z')

#---------------------------------------------------------------------------------------
#-- plot_data: plot data                                                              --
#---------------------------------------------------------------------------------------

def plot_data(x, y, xmin, xmax, ymin, ymax, inst, ychoice):
    """
    plot data
    input:  x   --- a list of independent variable
            y   --- a list of dependent variable
            xmin    --- x min
            xmax    --- x max
            ymin    --- y min
            ymax    --- y max
            inst    --- instrument name
            ychoice --- y or z
    output: <web_dir>/Plots/inst_<ychoice>.png
    """
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size'] = 16
    props = font_manager.FontProperties(size=16)
#
#--- set plotting range
#
    ax  = plt.subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
#
#--- plot data
#
    plt.plot(x, y, color='blue', marker='.', markersize=8, lw=0)
#
#--- put y = 0 line
#
    plt.plot([xmin, xmax], [0, 0], color='black', linestyle='-.', lw=1)
#
#--- fit a line
#
    (sint, slope, serr) = robust.robust_fit(x, y)
    ybeg = sint + slope * xmin
    yend = sint + slope * xmax
    plt.plot([xmin, xmax], [ybeg, yend], color='red', lw=2)
#
#--- add text
#
    line = 'Slope: %3.2f' % (slope)

    xpos = xmin + 0.05 * (xmax - xmin)
    ypos = 1.6
    plt.text(xpos, ypos, line, color='red')

    plt.xlabel('Time (Year)')
    ylabel = ychoice.upper() + ' Axis Error (arcsec)'
    plt.ylabel(ylabel)
#
#--- save the plot in png format
#
    width      = 10.0
    height     = 5.0
    resolution = 200
    outname    = web_dir + 'Plots/' + inst + '_' + ychoice + '.png'

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=resolution)
    
    plt.close('all')

#---------------------------------------------------------------------------------------
#-- convert_time_to_year: converting Chandra time to fractional year                  --
#---------------------------------------------------------------------------------------

def convert_time_to_year(tlist):
    """
    converting Chandra time to fractional year
    input:  tlist   --- a list of time in format of seconds from 1998.1.1
    output: save    --- a list of time in format of fractional year
    """
    save = []
    for ent in tlist:
        ldate = Chandra.Time.DateTime(ent).date
        atemp = re.split(':', ldate)
        year  = float(atemp[0])
        yday  = float(atemp[1])
        hh    = float(atemp[2])
        mm    = float(atemp[3])
        ss    = float(atemp[4])

        if tcnv.isLeapYear(year) == 1:
            base = 366.0
        else:
            base = 365.0

        fyear = year + (yday + hh / 24.0 + mm / 1440.0 + ss / 86400.0) / base
        save.append(fyear)

    return save

#---------------------------------------------------------------------------------------
#-- remove_extreme: remove data points larger than 3                                  --
#---------------------------------------------------------------------------------------

def remove_extreme(atime, dy, dz):
    """
    remove data points larger than 3
    input: atime    --- time
            dy      --- dy
            dz      --- dz
    output: atime   --- cleaned atime
            dy      --- cleaned dy
            dz      --- cleaned dz
    """

    at = numpy.array(atime)
    ay = numpy.array(dy)
    az = numpy.array(dz)

    index = [(ay > -3) & (ay < 3)]
    at    = at[index]
    ay    = ay[index]
    az    = az[index]

    index = [(az > -3) & (az < 3)]
    at    = at[index]
    ay    = ay[index]
    az    = az[index]

    at    = list(at)
    ay    = list(ay)
    az    = list(az)

    return [at, ay, az]

#---------------------------------------------------------------------------------------
#-- read_data_file: read a data file                                                  --
#---------------------------------------------------------------------------------------

def read_data_file(ifile, spliter = '', remove=0):
    """
    read a data file
    input:  infile  --- input file name
            spliter --- if you want to a list of lists of data, provide spliter, e.g.'\t+'
            remove  --- the indicator of whether you want to remove the data after read it. default=0: no
    output: data    --- either a list of data lines or a list of lists
    """

    try:
        f    = open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    except:
        return []

    if remove > 0:
        mcf.rm_file(ifile)

    if spliter != '':
        atemp = re.split(spliter, data[0])
        alen  = len(atemp)
        save  = []
        for k in range(0, alen):
            save.append([])

        for ent in data:
            atemp = re.split(spliter, ent)
            for k in range(0, alen):
                try:
                    val = float(atemp[k])
                except:
                    val = atemp[k].strip()

                save[k].append(val)
        return save
    else:
        return data

#---------------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_aiming_trend_data()

