#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#########################################################################################
#                                                                                       #
#       tephin_leak_data.py: create tephin vs msid plot and derivative plot             #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: May 23, 2019                                                   #
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
import robust_linear            as rbl  #---- robust linear fitting
import create_html_suppl        as chs
import create_derivative_plots  as cdp
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------
#-- tephin_leak_data: create msid vs tephin  plot and derivative plot            ---
#-----------------------------------------------------------------------------------

def tephin_leak_data(inyear, lupdate = 0):
    """
    create tephin vs msid plot and derivative plot
    input:  inyear      --- the year you want to create the plot; if '', create 1999 to current
            lupdate     --- if 1, update y plotting range. Otherwise, 
                            use the previous one or don't synch for all years
    output: <web_dir>/<group name>/<msid>/Plots/<msid>_<ltype>_<year>.png
    """

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

    msid_list = 'msid_list_eph_tephin'
    ifile  = house_keeping + msid_list
    with open(ifile, 'r') as f:
        data   = [line.strip() for line in f.readlines()]
    
    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        if msid == '5ephint':
            continue

        mc    = re.search('#', msid)
        if mc is not None:
            continue

        group = atemp[1]
        try:
            ymin  = float(atemp[2])
            ymax  = float(atemp[3])
        except:
            ymin  = -999
            ymax  = -999

        try: 
            ydrange = float(atemp[4])
        except:
            ydrange = 0.01

        print("msid: " + msid)

        for year in year_list:
            print("Year: " + str(year))
            fits = data_dir + 'Eleak/' + '/' + msid.capitalize() + '/'
            fits = fits + msid + '_data' + str(year) + '.fits'
            if not os.path.isfile(fits):
                continue

            data  = ecf.read_fits_col(fits, ['tephin', msid, 'min', 'max'])
            sdata = data[0]

            oname = web_dir + 'Eleak/' + msid.capitalize() 
            if not os.path.isdir(oname):
                cmd = 'mkdir ' + oname
                os.system(cmd)

            oname = oname + '/Plots/'
            if not os.path.isdir(oname):
                cmd = 'mkdir ' + oname
                os.system(cmd)
#
#--- to save the plotting time, use only 1 out of 10 data points
#
            stemp = sdata[::10]
            ofile = oname   + msid + '_mid_' + str(year) + '.png'
            mdata = data[1]
            mtemp = mdata[::10]
            plot_data(stemp, mtemp, year, msid, ofile, ymin, ymax, ydrange, msid_list, lupdate)

            ofile = oname   + msid + '_min_' + str(year) + '.png'
            mdata = data[2]
            mtemp = mdata[::10]
            plot_data(stemp, mtemp, year, msid, ofile, ymin, ymax, ydrange, msid_list, lupdate)

            ofile = oname   + msid + '_max_' + str(year) + '.png'
            mdata = data[3]
            mtemp = mdata[::10]
            plot_data(stemp, mtemp, year, msid, ofile, ymin, ymax, ydrange, msid_list, lupdate)


#-----------------------------------------------------------------------------------
#-- plot_data: create two panel plots for tephin vs msid and its deviation        --
#-----------------------------------------------------------------------------------

def plot_data(sdata, mdata, year, msid, oname, ymin, ymax, ydrange, msid_list, lupdate):
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
            lupdate     --- if 1, update y plotting range.
    output: oname in png format
    """

    plt.close('all')

    fig, ax = plt.subplots(1, figsize=(8,6))
    props   = font_manager.FontProperties(size=14)
    mpl.rcParams['font.size']   = 14
    mpl.rcParams['font.weight'] = 'bold'

    xmin  = 260
    xmax  = 360

    if ymax == -999:
        [ymin, ymax, ypos] = chs.set_y_plot_range(mdata)
#
#--- since we want to all years to be in the same plotting range, this scripts adjust
#--- the plotting range. you may need to run a couple of times for the full range to
#--- adjust plotting range for the all plot
#
        [ymin, ymax, ydev] = update_yrange(msid_list, msid, ymin=ymin, ymax=ymax, ydev=ydrange)
    else:
        ydiff = ymax - ymin
        ypos  = ymax - 0.1 * ydiff

    ax1 = plt.subplot(211)

    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(ymin, ymax)

    ax1.set_xlabel("5ephin (K)")
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
    period = 1.0
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

    plt.text(270, ypos, str(year))

#
#---- derivative plot
#
    [xd, yd, ad]          = cdp.find_deriv(sdata, mdata, 'xxx', step=20)
    [dymin, dymax, dypos] = chs.set_y_plot_range(yd)

    if lupdate == 1:
        if abs(dymin) > abs(dymax):
            dymax = abs(dymin)

        if dymax > ydrange:
            update_yrange(msid_list, msid, ymin=ymin, ymax=ymax, ydev=dymax)
            ydrange = dymax

    ymax = ydrange
    ymin = -1.0 * abs(ymax)
#
#---------------------------------------------------------
#---- temporarily set ymin <--> ymax value (Jan 24, 2018)
#
    ymin = -50.0
    ymax =  50.0
    mc = re.search('sc', msid)
    if mc is not None:
        ymin = -300.0
        ymax =  300.0

    if msid in ['scp25gm', 'scp4gm', 'scp8gm']:
        ymin = -3000.0
        ymax =  3000.0
    elif msid in ['sce150', 'sce300']:
        ymin = -30000.0
        ymax =  30000.0

#---------------------------------------------------------

    ydiff = ymax - ymin
    ypos  = ymax - 0.1 * ydiff


    ax2 = plt.subplot(212)

    ax2.set_xlim(xmin, xmax)
    ax2.set_ylim(ymin, ymax)

    ax2.set_xlabel("5ephin (K)")
    line = msid + '/ K'
    ax2.set_ylabel(line)

    points = ax2.scatter(xd, yd, marker='o', s=4 ,lw=0)

    if mc is not None:
        try:
            #[xs, ys]  = chs.remove_extreme_vals(xd, yd, 96)
            [xs, ys]  = chs.remove_extreme_vals(xd, yd, 75)
            [a, b, e] = rbl.robust_fit(xs, ys)
        except:
            [a, b, e] = chs.least_sq(xd, yd, remove=1)
    else:
        try:
            [a, b, e] = rbl.robust_fit(xd, yd)
        except:
            [a, b, e] = chs.least_sq(xd, yd)
#
#--- if b == 999, it means that it could not get the slope; so set it to 0
#
    if b == 999.0:
        a = 0
        b = 0

    ys = a + b * xmin
    ye = a + b * xmax
    ax2.plot([xmin, xmax], [ys, ye], color='green', lw=3)

    line = 'Slope: ' + "%3.3e" % (b)
    mpl.rcParams['font.size']   = 12
    plt.title('dy / d(Temp)', loc='left')
    plt.text(270, ypos, line)
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
#-- update_yrange: updating the derivative plotting range in msid_list           ---
#-----------------------------------------------------------------------------------

def update_yrange(msid_list, msid, ymin=-999, ymax=-999, ydev=-999):
    """
    updating the derivative plotting range in msid_list
    input:  msid_list   --- a file name which contains the list of msid
            msid        --- msid
            ydev        --- the value of derivative y range value
    output: updated <house_keeping>/<msid_list>
    Note: this is needed to keep all yearly plot to the same y range. you may need to
          run this script (tephin_plot.py) twice to make the plotting range for
          all to be sych.
    """

    ymin = float(ymin)
    ymax = float(ymax)
    try:
        ydev = float(ydev)
    except:
        ydev = -999

    if ydev != -999:
        ydev = float("%2.2e" % (ydev * 1.05))

    mfile = house_keeping + msid_list
    f     = open(mfile, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    fo    = open(zspace, 'w')
    for ent in data:
        atemp = re.split('\s+', ent)
        if atemp[0] == msid:

            try:
                ymint = atemp[2]
                if ymin !=-999:
                    if ymint > ymin:
                        ymint = ymin
            except:
                ymint = 0
                if ymin != -999:
                    ymint = ymin


            try:
                ymaxt = atemp[3]
                if ynax != -999:
                    if ymaxt < ymax:
                        ymaxt = ymax
            except:
                ymaxt = 999
                if ymax != -999:
                    ymaxt = ymax
            
            try:
                ydevt  = atemp[4]
                if ydev != -999:
                    if ydevt < ydev:
                        ydevt = ydev 
            except:
                ydevt  = 10
                if ydev != -999:
                    ydevt = ydev 

            line = atemp[0] + '\t' + atemp[1] + '\t' 
            line = line + "%.3f" % round(float(ymint),3) + '\t' 
            line = line + "%.3f" % round(float(ymaxt),3) + '\t' 
            if ydevt < 1.0:
                line = line + "%3e"  % float(ydevt) + '\n'
            else:
                line = line + "%.3f" % round(float(ydevt),3) + '\n'

            fo.write(line)
        else:
            fo.write(ent)
            fo.write('\n')

    fo.close()
    mcf.rm_files(zspace)

    return [ymint, ymaxt, ydevt]

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

    tephin_leak_data(year, chk)

    #for year in range(1999, 2019):
    #    tephin_leak_data(year, 0)
