#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#########################################################################################
#                                                                                       #
#   hrcveto_eph_plot.py: create shevart vs eph key value plot and derivative plot       #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: May 21, 2019                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import math
import sqlite3
import unittest
import time
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import find_moving_average      as fma  #---- moving average 
import find_moving_average_bk   as fmab #---- moving average (backword fitting version)
import create_html_suppl        as chs
import create_derivative_plots  as cdp
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- data from ephkey
#
y_data_list = ['scct0', 'sce1300', 'sce150', 'sce3000', 'scint']
#
#--- deriv plotting range
#
y_drange    = [0.15, 18.00, 600.0, 0.30, 0.30]

#-----------------------------------------------------------------------------------
#-- hrcveto_eph_plot: create shevart vs eph key value plot and derivative plot   ---
#-----------------------------------------------------------------------------------

def hrcveto_eph_plot(inyear, lupdate = 0):
    """
    create create shevart vs eph key value plot and derivative plot
    input:  inyear      --- the year you want to create the plot; if '', create 1999 to current
            lupdate     --- if 1, update y plotting range. Otherwise, 
                            use the previous one or don't synch for all years
    output: <web_dir>/<group name>/<msid>/Plots/<msid>_<ltype>_<year>.png
    """
#
#--- set plotting year in a list form
#
    if inyear == '':
        this_year = int(float(time.strftime("%Y", time.gmtime())))
        yday      = int(float(time.strftime("%j", time.gmtime())))

        if lupdate  == 0:
            if yday < 8:
                last_year = this_year - 1
                year_list = [last_year, this_year]
            else:
                year_list = [this_year]

        else:
            year_list = range(1999, this_year+1)
    else:
        year_list = [inyear]
#
#--- read shevart values
#
    fits = data_dir + 'Hrcveto/shevart_data.fits'
    [sh_time, shevart] = read_fits(fits, ['time', 'shevart'])
#
#--- get eph key values
#
    mlen = len(y_data_list)
    for m in range(0, mlen):
        msid = y_data_list[m]
        print "msid: " + msid

        fits  = data_dir + 'Ephkey/' + msid + '_data.fits'
        out   = read_fits(fits, ['time', msid, 'max', 'min'])
#
#--- separate time data and main value, min value and max value
#
        etime = out[0]
        eout  = out[1:]
        enom  = ['mid', 'max', 'min']

        for k in range(0, 3):
            data = eout[k]
            print "Type: "  + enom[k]
#
#--- set max to 98% percentile so that we can remove the extreme values
#
            ymax = numpy.percentile(data, 98)
            ymax = round_up(ymax)
            
            if ymax > 1000:
                ymin = -100
            else:
                ymin = -10

            for year in year_list:
#
#--- extract the data for the given year
#
                [xdata, ydata] = select_data(shevart, sh_time, data, etime,  year)
    
                oname = web_dir + 'Hrcveto_eph/' + msid.capitalize() 
                if not os.path.isdir(oname):
                    cmd = 'mkdir ' + oname
                    os.system(cmd)
    
                oname = oname + '/Plots/'
                if not os.path.isdir(oname):
                    cmd = 'mkdir ' + oname
                    os.system(cmd)
    
                ofile = oname   + msid + '_' + enom[k] + '_' + str(year) + '.png'
#
#--- plot the data
#
                plot_data(xdata, ydata,  year, msid, ofile, ymin, ymax, y_drange[m], y_data_list)
    

#-----------------------------------------------------------------------------------
#-- round_up: round up the value to two top digit                                 --
#-----------------------------------------------------------------------------------

def round_up(val):
    """
    round up the value to two top digit; e.g. 23134 ---> 24000
    input:  val     --- value to be round up
    output: val     --- cleaned up value
    """

    atemp = str(int(val))
    val1  = int(float(atemp[0]))
    val2  = int(float(atemp[1]))
    val2 += 1
    if val2 == 10:
        val2  = 0
        val1 += 1

    val   = val1 * 10 + val2
    vlen  = len(atemp) - 2
    val  *= 10**vlen

    return val

#-----------------------------------------------------------------------------------
#-- select_data: extract data for the given year                                  --
#-----------------------------------------------------------------------------------

def select_data(data1, time1,  data2, time2, year):
    """
    extract data for the given year
    input:  data1   --- data of set 1
            time1   --- time of set 1
            data2   --- data of set 2
            timew   --- time of set 2
            year    --- the year of which the data will be extracted
    output: xdata   --- the selected data from data1
            ydata   --- the selected data from data2
    """
#
#--- set the span with seconds from 1998.1.1
#
    start = str(year)      + ':001:00:00:00'
    start = Chandra.Time.DateTime(start).secs
    stop  = str(year + 1)  + ':001:00:00:00'
    stop  = Chandra.Time.DateTime(stop).secs
#
#--- select the data using indexing
#
    index = [(time1 >= start) & (time1 < stop)]
    xdata = data1[index]

    index = [(time2 >= start) & (time2 < stop)]
    ydata = data2[index]
    
    xlen  = len(xdata)
    ylen  = len(ydata)
#
#--- just in a case the output side is different; adjust the array size
#
    if xlen > ylen:
        xdata = xdata[:ylen]
    elif xlen < ylen:
        ydata = ydata[:xlen]

    return [xdata, ydata]

#-----------------------------------------------------------------------------------
#-- read_fits: read fits file                                                     --
#-----------------------------------------------------------------------------------

def read_fits(fits, col_list):
    """
    read fits file
    input:  fits        --- file name
            col_list    --- a list of column names to be extracted 
    output: out         --- a list of data arrays corresponding to the column list
    """
    f = pyfits.open(fits)
    data = f[1].data
    f.close()

    out = []
    for col in col_list:
        out.append(data[col])

    return out

#-----------------------------------------------------------------------------------
#-- plot_data: create two panel plots for tephin vs msid and its deviation        --
#-----------------------------------------------------------------------------------

def plot_data(sdata, mdata, year, msid, oname, ymin, ymax, ydrange, msid_list):
    """
    create two panel plots for tephin vs msid and its deviation
    input:  sdata   --- a list of tephin data
            mdata   --- a list of msid data (mid/min/max)
            year    --- year of the plot
            msid    --- msid
            oname   --- output name
            ymin    --- y min of the first plot
            ymax    --- y max of the first plot
            ydrange --- the range of the deviation y axis
            msid_list   --- msid list
    output: oname in png format
    """
    plt.close('all')

    fig, ax = plt.subplots(1, figsize=(8,6))
    props   = font_manager.FontProperties(size=14)
    mpl.rcParams['font.size']   = 14
    mpl.rcParams['font.weight'] = 'bold'

    xmin  = 1.5e4
    xmax  = 3.5e4
    ydiff = ymax - ymin
    ypos  = ymax - 0.1 * ydiff

    ax1 = plt.subplot(211)

    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(ymin, ymax)

    ax1.set_xlabel("Shevart (cnts)")
    ax1.set_ylabel(msid.upper())
#
#--- set the size of plot
#
    fig.set_size_inches(10.0, 5.0)
    fig.tight_layout()
#
#---- trending plots
#
    points = ax1.scatter(sdata, mdata, marker='o', s=4 ,lw=0)
#
#---- envelope
#
    period = 500
    [xmc, ymc, xmb, ymb, xmt, ymt] = create_trend_envelope(sdata, mdata, period)
#
#--- trending area
#
    try:
        ax1.fill_between(xmc, ymb, ymt, facecolor='#00FFFF', alpha=0.3, interpolate=True)
    except:
        pass
#
#--- center moving average
#
    ax1.plot(xmc, ymc, color='#E9967A', lw=4)

    plt.text(16500, ypos, str(year))

#
#---- derivative plot
#
    [xd, yd, ad]          = cdp.find_deriv(sdata, mdata, 'xxx', step=20)
    [dymin, dymax, dypos] = chs.set_y_plot_range(yd)

    ymax = ydrange
    ymin = -1.0 * abs(ymax)

    ydiff = ymax - ymin
    ypos  = ymax - 0.1 * ydiff


    ax2 = plt.subplot(212)

    ax2.set_xlim(xmin, xmax)
    ax2.set_ylim(ymin, ymax)

    ax2.set_xlabel("Shevart (cnts)")
    line = msid + '/ cnts'
    ax2.set_ylabel(line)

    points = ax2.scatter(xd, yd, marker='o', s=4 ,lw=0)

    try:
        [xx, yy]  = chs.remove_extreme_vals(xd, yd, p=96)
        [a, b, e] = rbl.robust_fit(xx, yy)
    except:
        [a, b, e] = chs.least_sq(xd, yd, remove=1)

    ys = a + b * xmin
    ye = a + b * xmax

    ax2.plot([xmin, xmax], [ys, ye], color='green', lw=3)

    line = 'Slope: ' + "%3.3e" % (b)
    mpl.rcParams['font.size']   = 12
    plt.title('dy / d(Cnts)', loc='left')
    plt.text(16500, ypos, line)
#
#--- set the size of plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 10.0)
    fig.tight_layout()
    plt.savefig(oname, format='png', dpi=100)

    plt.close('all')

#-----------------------------------------------------------------------------------
#-- create_trend_envelope: create moving average to be used to create envelope    --
#-----------------------------------------------------------------------------------

def create_trend_envelope(sdata, mdata, period):
    """
    create moving average to be used to create envelope
    input:  sdata   --- a list of the tehpin data
            mdata   --- a list of msid data (mid/min/max)
            period  --- a moving average step size
    output: xmc     --- a list of x values for the center moving average
            ymc     --- a list of y values of the center moving average
            xmb     --- a list of x values of the bottom moving average
            ymb     --- a list of y values of the bottom moving average
            xmt     --- a list of x values of the top moving average
            ymt     --- a list of y values of the top moving average
    """
#
#--- center
#
    [x, y]     = chs.select_y_data_range(sdata, mdata, period, top=2)
    [xmc, ymc] = chs.get_moving_average_fit(x, y, period)
#
#--- bottom
#
    [x, y]     = chs.select_y_data_range(sdata, mdata, period, top=0)
    [xmb, ymb] = chs.get_moving_average_fit(x, y, period)
#
#--- top
#
    [x, y]     = chs.select_y_data_range(sdata, mdata, period, top=1)
    [xmt, ymt] = chs.get_moving_average_fit(x, y, period)
#
#---- adjust length of lists
#
    xlen  = len(xmc)
    yblen = len(ymb)
    ytlen = len(ymt)

    if xlen < yblen:
        ymb = ymb[:xlen]
    elif xlen > yblen:
        diff  = xlen - yblen
        for k in range(0, diff):
            ymb.append(ymb[-1])
    
    if xlen < ytlen:
        ymt = ymt[:xlen]
    elif xlen > ytlen:
        diff  = xlen - ytlen
        for k in range(0, diff):
            ymt.append(ymt[-1])

    return [xmc, ymc, xmb, ymb, xmt, ymt]

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        mc = re.search('lupdate', sys.argv[1])
        if mc is not None:
            year = ''
            chk  = 1
        else:
            year = int(float(sys.argv[1]))
            chk  = 0

    elif len(sys.argv) == 3:
        year = int(float(sys.argv[1]))
        chk  = int(float(sys.argv[2]))

    else:
        year = ''
        chk  = 0

    hrcveto_eph_plot(year, chk)

