#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       tephin_leak_data.py: create tephin vs msid plot and derivative plot                         #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Feb 13, 2018                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
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

#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
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
import convertTimeFormat        as tcnv #---- converTimeFormat contains MTA time conversion routines
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import find_moving_average      as fma  #---- moving average 
import find_moving_average_bk   as fmab #---- moving average (backword fitting version)
import robust_linear            as rbl  #---- robust linear fitting

#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------
#-- tephin_leak_data: create msid vs tephin  plot and derivative plot            ---
#-----------------------------------------------------------------------------------

def tephin_leak_data(inyear, lupdate = 0):
    """
    create tephin vs msid plot and derivative plot
    input:  inyear      --- the year you want to create the plot; if '', create 1999 to current
            lupdate     --- if 1, update y plotting range. Otherwise, use the previous one or don't synch for 
                            all years
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
    f      = open(ifile, 'r')
    data   = [line.strip() for line in f.readlines()]
    f.close()
    
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

        print "msid: " + msid

        for year in year_list:
            print "Year: " + str(year)
            fits = data_dir + 'Eleak/' + '/' + msid.capitalize() + '/'
            fits = fits + msid + '_data' + str(year) + '.fits'
            if not os.path.isfile(fits):
                continue

            data  = read_fits(fits, ['tephin', msid, 'min', 'max'])
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
        [ymin, ymax, ypos] = set_y_plot_range(mdata)
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
    [xd, yd, ad]          = find_deriv(sdata, mdata, 'xxx', step=20)
    [dymin, dymax, dypos] = set_y_plot_range(yd)

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
            #[xs, ys]  = remove_extreme_vals(xd, yd, 96)
            [xs, ys]  = remove_extreme_vals(xd, yd, 75)
            [a, b, e] = rbl.robust_fit(xs, ys)
        except:
            [a, b, e] = least_sq(xd, yd, remove=1)
    else:
        try:
            [a, b, e] = rbl.robust_fit(xd, yd)
        except:
            [a, b, e] = least_sq(xd, yd)
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
    [x, y]     = select_y_data_range(sdata, mdata, period, top=2)
    [xmc, ymc] = get_moving_average_fit(x, y, period)
#
#--- bottom
#
    [x, y]     = select_y_data_range(sdata, mdata, period, top=0)
    [xmb, ymb] = get_moving_average_fit(x, y, period)
#
#--- top
#
    [x, y]     = select_y_data_range(sdata, mdata, period, top=1)
    [xmt, ymt] = get_moving_average_fit(x, y, period)
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

#----------------------------------------------------------------------------------
#-- get_moving_average_fit: get moving average                                   --
#----------------------------------------------------------------------------------

def get_moving_average_fit(x, y, period):
    """
    get moving average 
    input:  x   --- a list of x values
    y   --- a list of y values
    period  --- a period of the step
    output: [tx1, tx2]  --- a list of lists of x and y values of moving average
    """
#
#--- first find moving average forward, then find moving average backward from the end
#
    try:
        out1 = fma.find_moving_average(x,  y, period , 0)
    except:
        out1 = [[],[]]
    try:
        out2 = fmab.find_moving_average(x, y, period , 0)
    except:
        out2 = [[],[]]
#
#--- combined two of them so that fill all the way
#
    tx1 = out1[0]
    ty1 = out1[1]
    
    tx2 = out2[0]
    ty2 = out2[1]
    
    tx3 = []
    ty3 = []
    for k in range(0, len(tx2)):
        if tx2[k] > tx1[-1]:
            tx3.append(tx2[k])
            ty3.append(ty2[k])
    
    tx1 = tx1 + tx3
    ty1 = ty1 + ty3
    
    return [tx1, ty1]

#----------------------------------------------------------------------------------
#-- select_y_data_range: select data based on middle, top 25%, or bottom 25% area -
#----------------------------------------------------------------------------------

def select_y_data_range(xtime, yval, period, top=1):
    """
    select data based on middle, top 25%, or bottom 25% area 
    input:  xtime   --- a list of x values
    yval--- a list of y values
    period  --- a compartment size
    top --- position of the selction: 0: bottom 25%, 1: top 25%, other middle 96%
    output: xadjust --- a list of x data in the selected range
    yadjust --- a list of y data in the selected range
    """
#
#--- set percentaile limit values
#
    if top == 0:
        p1 = 2
        p2 = 25
    elif top == 1:
        p1 = 75
        p2 = 98
    else:
        p1 = 2
        p2 = 98
    
    xt   = numpy.array(xtime)
    yt   = numpy.array(yval)
    aind = xt.argsort()
    xt   = xt[aind[::]]
    yt   = yt[aind[::]]
    xadjust = []
    yadjust = []
#
#--- set step size and numbers of periods: select the data span to 20% of the period given 
#--- so that the bottom and top spans do not change much during the data selection period
#
    step  = 0.2 * period
    start = xt[0]
    stop  = xt[-1]
    snum  = int((stop - start) / step) + 1
    
    begin = 0
    for k in range(0, snum):
#
#--- select the data in that period
#
        xs = []
        ys = []
        sn = 0
        lstop = (k+1) * step + start
        for m in range(begin, len(xt)):
            if xt[m] > lstop:
                break
            else:
                xs.append(xt[m])
                ys.append(yt[m])
                sn += 1
#
#--- reset the starting spot for the next round
#
    begin += sn
#
#--- find given percentaile range
#
    limb = percentile(ys, p1)
    limt = percentile(ys, p2)
    lavg = 0.5 * (limb + limt)

    for n in range(0, len(xs)):
#
#--- if the data is in the range, use the value
#
        if (ys[n] >= limb) and (ys[n] <= limt):
            xadjust.append(xs[n])
            yadjust.append(ys[n])
#
#--- if not, use the average
#
        else:
            xadjust.append(xs[n])
            yadjust.append(lavg)
    
    return [xadjust, yadjust]


#----------------------------------------------------------------------------------
#-- set_y_plot_range: find plotting y range                                     ---
#----------------------------------------------------------------------------------

def set_y_plot_range(y):

    lcnt  = len(y)
    if lcnt > 5:
        p = int(0.02 * lcnt)
        test  = y[p:lcnt-p]
    else:
        test = y

    if len(y) < 1:
        return [0,0,0]
    
    ymin  = min(test)
    ymax  = max(test)

    if ymin == ymax:
        ymax = ymin + 0.5
        ymin = ymin - 0.5
    else:
        ydiff = ymax - ymin
        ymin -= 0.2 * ydiff
        ymax += 0.2 * ydiff
    
    ydiff = ymax - ymin
    ypos  = ymax - 0.1 * ydiff
    
    return  [ymin, ymax, ypos]

#--------------------------------------------------------------------------------------------------------
#-- find_deriv: compute the derivative per year                                                        --
#--------------------------------------------------------------------------------------------------------

def find_deriv(x, y, ltype, step=200):
    """
    compute the derivative per year
    the dy/dx is computed similar to that of moving average, but compute slope in that range
    input;  x   --- a list of x values
    y   --- a list of y values
    ltype   --- type of data such as short, long
    step--- step size; how may data points should be include in the moving average
    output: xd  --- a list of x position
    yd  --- a list of dx/dy; of slope of the fitting
    ad  --- a list of intercept of the fitting
    """

    hstep = int(0.5 * step)
    dlen  = len(x)
#
#--- sort by x
#
    xa = numpy.array(x)
    ya = numpy.array(y)
    s  = numpy.argsort(xa)
    x  = list(xa[s])
    y  = list(ya[s])
    
    xd= []
    yd= []
    ad= []
#
#--- moving average but compute slope instead of average
#
    for k in range(hstep, dlen - hstep):
        ks = k - hstep
        ke = k + hstep
        xs = x[ks:ke]
        ys = y[ks:ke]
    
        [a, b, d] = least_sq(xs, ys)
#
#--- rare occasion, fits fail, skip the ponit
#
        if b == 999:
            continue
        else:
            xd.append(x[k])
            yd.append(b)
            ad.append(a)
    
    xd = numpy.array(xd)
    xd = xd.astype(float)
    
    yd = numpy.array(yd)
    yd = yd.astype(float)
    
    ad = numpy.array(ad)
    ad = ad.astype(float)
    
    return [xd, yd, ad]

#---------------------------------------------------------------------------------------------------
#-- least_sq: compute a linear fit parameters using least sq method  ---
#---------------------------------------------------------------------------------------------------

def least_sq(xval, yval, ecomp = 0, remove=0):

    """
    compute a linear fit parameters using least sq method
    Input:  xval--- a list of independent variable
    yval--- a list of dependent variable
    ecomp   --- indicator whether to compute the slope error; 0: no, >0: yes
    remove  --- remove outlyers if 1
    Output: aa  --- intersect
    bb  --- slope
    be  --- slope error
    """
    if remove == 1:
        [xval, yval] = remove_extreme_vals(xval, yval, 96)  #--- remove extreme 2% from both end
    
    itot= len(xval)
    tot = float(itot)
    sx  = 0.0
    sy  = 0.0
    sxy = 0.0
    sxx = 0.0
    syy = 0.0
    
    for j in range(0, itot):
        sx  += xval[j]
        sy  += yval[j]
        sxy += xval[j] * yval[j]
        sxx += xval[j] * xval[j]
        syy += yval[j] * yval[j]
    
    delta = tot * sxx - sx * sx
    
    try:
        aa = (sxx * sy  - sx * sxy) / delta
        bb = (tot * sxy - sx * sy)  / delta
    except:
        aa = 999
        bb = 999
    be = 0.0
    
    if ecomp > 0:
        ss = (syy + tot*aa*aa + bb*bb*sxx - 2.0 *(aa*sy - aa*bb*sx + bb*sxy)) /(tot - 2.0)
        be = math.sqrt(tot * ss / delta)
    
    return (aa, bb, be)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def remove_extreme_vals(x, y, p=98):
    """
    remove outlayers
    input:  x   --- x values
    y   --- y values
    p   --- how much include in the data in percentage; e.g.98-- remove top and bottom 1%
    """
    
    xa = numpy.array(x)
    ya = numpy.array(y)
    
    cut= 100 - p
    bcut   =  0.5 * cut
    tcut   = p + bcut
    blim   = numpy.percentile(ya, bcut)
    tlim   = numpy.percentile(ya, tcut)
    select = [(ya > blim) & (ya < tlim)]
    
    xo = list(xa[select])
    yo = list(ya[select])
    
    return [xo, yo]


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
    mcf.rm_file(zspace)

    return [ymint, ymaxt, ydevt]

#-----------------------------------------------------------------------------------

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines


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
