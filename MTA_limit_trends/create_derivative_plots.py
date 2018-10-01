#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           create_derivative_plots.py: create derivative plots                                             #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           last update: Mar 16, 2018                                                                       #
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
#
#--- read argv
#
try:
    option, remainder = getopt.getopt(sys.argv[1:],'t',['test'])
except getopt.GetoptError as err:
     print str(err)
     sys.exit(2)

path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(mta_dir)
sys.path.append(bin_dir)

import convertTimeFormat        as tcnv #---- converTimeFormat contains MTA time conversion routines
import mta_common_functions     as mtac #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import create_html_suppl        as chs  
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- other settings
#
na     = 'na'

[udict, ddict] = ecf.read_unit_list()

#--------------------------------------------------------------------------------------------------------
#-- create_derivative_plots: create derivative plots for all msid listed in msid_list                  --
#--------------------------------------------------------------------------------------------------------

def create_derivative_plots(mfile='', inter =''):
    """
    create derivative plots for all msid listed in msid_list
    input:  mfile   --- a list of msids. if not provided, use full msid_list 
            inter   --- indicator of "week" plots or "short" and "long" plots; default: "" --- short and long.
    output: <web_dir>/<group>/<msid>/Plots/msid_*_dev.png
            <web_dir>/<group>/<msid>/Plots/msid_*_dev_fit_results'
    """
#
#--- get the list of the names of the data files
#
    if mfile == '':
        mfile = house_keeping + 'msid_list'
    else:
        mfile = house_keeping + mfile
        if not os.path.isfile(mfile):
            mfile = house_keeping + 'msid_list'

    data  = ecf.read_file_data(mfile)

    for out in data:
        try:
            [msid, group] = re.split('\s+',  out)
        except:
            atemp = re.split('\s+',  out)
            msid  = atemp[0]
            group = atemp[1]

        print "Processing: " +  msid 
#
#--- checking only crate week plot 
#
        if inter == "":
            l_list =  ('short', 'long')
        else:

            l_list = (str('week'))
#
#--- open a file to save dy/dx fitting lines
#
        ofile = web_dir + group + '/' + msid.capitalize() + '/Plots/' + msid + '_dev_fit_results'
        if not os.path.isfile(ofile):
            continue

        fo    = open(ofile, 'w')
#
#--- there are three different types of data sets; week: week long, short: year long, long: entire period
#
        for ltype in l_list:
            dfile = data_dir + group.capitalize() + '/' + msid + '_data.fits'
#
#--- for short, we create 3 months and one year plots
#
            if ltype == 'short':
                dfile = dfile.replace('_data', '_short_data')
                flist = ['short', 'one']
#
#--- with week data, only one week plot
#
            elif ltype == 'week':
                dfile = dfile.replace('_data', '_week_data')
                flist = [str('week')]
#
#--- long data is for 5 yrs and full range
#
            else:
                flist = ['five', 'long']

            try:
                [pdata, byear]  = read_data(dfile, msid,  ltype)
            except:
                continue

            for otype in flist: 
                for mtype in ('mid', 'min', 'max'):
    
                    out = plot_deviatives(pdata, byear, msid, group, otype, mtype)
    
                    line = ltype + ':' + mtype + ':' + out[0] + ':' + out[1] + ':' + out[2] + ':' + out[3] + '\n'
                    fo.write(line)

        fo.close()

#--------------------------------------------------------------------------------------------------------
#-- plot_deviatives: create derivative plots for given msid                                            --
#--------------------------------------------------------------------------------------------------------

def plot_deviatives(pdata, byear, msid, group, ltype, mtype):
    """
    create derivative plots for given msid
    input:  pdata   --- a two dimensional array of data set; see read_data for details
            byear   --- a base year for the short/weekly plots
            msid    --- msid
            group   --- group name
            ltype   --- data type, such as week, short, one, five, long
            mtye    --- data type, such as mid, min, max
    output: [a,b,d, outname]    --- fitted line  intercept, slope, error, and a png file name
            <web_dir>/<group>/<msid>/Plots/msid_*_dev.png
    """
#
#--- three different data position by mid, min, and max
#
    pos      = find_pos(mtype)

    outname  = web_dir + group.capitalize() + '/' + msid.capitalize() 
    outname  = outname + '/Plots/' + msid + '_' + ltype + '_' + mtype + '_dev.png'
#
#--- step size indicates how many data collected before computing the dy/dx
#
    if ltype in ('five', 'long'):
        step = 20
        xt  = pdata[0]
        yt  = pdata[pos]
        if ltype == 'five':
            [xt, yt] =  cut_the_data(xt, yt, 5.0)       #---- five year interval

    elif ltype  in('short', 'one'):
        step = 700
        xt  = pdata[0]
        yt  = pdata[pos]
        if ltype == 'short':
            [xt, yt] =  cut_the_data(xt, yt,  90.0)     #---- three month interval

    else:                                               #--- week long data
        try:
            step = 700
            xt   = pdata[0]
            yt   = pdata[pos]
        except:
            cmd = 'cp  ' + house_keeping + 'no_data.png ' + outname
            return ['0', '0', '0', outname]

#
#--- find dy/dx along the time line
#
    [xd, yd, ad] = find_deriv(xt, yt, ltype,  step=step)
#
#--- fit a line to find dy/dx/dx
#
    [nx, ny]     = remove_out_layers(xd, yd)
    [a,  b,  d]  = chs.least_sq(nx, ny, ecomp=1)
#
#--- create a plot
#
    create_scatter_plot(msid, xt, xd,  yd,  ltype, mtype, byear, a,  b,  d,  outname)

    if abs(b) < 0.001:
        a = '%3.3e' % (a)
        b = '%3.3e' % (b)
        d = '%3.3e' % (d)
    else:
        a = '%3.3f' % round(a, 3)
        b = '%3.3f' % round(b, 3)
        d = '%3.3f' % round(d, 3)

    return [a, b, d, outname]

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def remove_out_layers(x, y):

    ay = numpy.array(y)

    ytemp = sort(y)
    xlen  = len(x)
    if xlen > 200:
        pos   = int(0.02 * xlen)
        bot   = ytemp[pos]
        top   = ytemp[-pos]
    else:
        bot   = ytemp[0]
        top   = ytemp[-1]

    avg  = numpy.mean(ay)
    std  = numpy.std(ay)
    test = avg - 3.5 * std
    if test > bot:
        bot = test
    test = avg + 3.5 * std
    if  test < top:
        top = test

    nx = []
    ny = []
    for k in range(0, len(x)):
        if abs(y[k]) > 1e10:            #---- something wrong if the value is this large
            continue

        if y[k] >= bot and y[k] <= top:
            nx.append(x[k])
            ny.append(y[k])

    return [nx, ny]

#--------------------------------------------------------------------------------------------------------
#-- find_pos: set data position depending of the data type                                             --
#--------------------------------------------------------------------------------------------------------

def find_pos(mtype):
    """
    set data position depending of the data type
    input:  mtype   --- mid, min, or max
    output: pos     --- the data position in pdata
    """
    if mtype == 'mid':
        pos = 4
    elif mtype == 'min':
        pos = 7
    elif mtype == 'max':
        pos = 8
    else:
        pos = 4

    return pos
 
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def cut_the_data(x, y, period):

    cut   = x[-1] - period
    index = numpy.where(x > cut)
    xd    = x[index]
    yd    = y[index]

    return [xd, yd]

#--------------------------------------------------------------------------------------------------------
#-- find_deriv: compute the derivative per year                                                        --
#--------------------------------------------------------------------------------------------------------

def find_deriv(x, y, ltype, step=200):
    """
    compute the derivative per year
            the dy/dx is computed similar to that of moving average, but compute slope in that range
    input;  x       --- a list of x values
            y       --- a list of y values
            ltype   --- type of data such as short, long
            step    --- step size; how may data points should be include in the moving average
    output: xd      --- a list of x position
            yd      --- a list of dx/dy; of slope of the fitting
            ad      --- a list of intercept of the fitting
    """

    hstep = int(0.5 * step)
    dlen  = len(x)
#
#--- if the time is in days, convert it into years
#
    if ltype in ('week',  'short', 'one'):
        xt = list(x / 365.0)
    else:
        xt = x

    xd    = []
    yd    = []
    ad    = []
#
#--- moving average but compute slope instead of average
#
    for k in range(hstep, dlen - hstep):
        ks = k - hstep
        ke = k + hstep
        xs = xt[ks:ke]
        ys = y[ks:ke]

        xp = x[ke] -x[ks]
        [a, b, d] = chs.least_sq(xs, ys)
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


#--------------------------------------------------------------------------------------------------------
#-- check_directories: check the existances of directories. if not, create them                       ---
#--------------------------------------------------------------------------------------------------------

def check_directories(msid, group):
    """
    check the existances of directories. if not, create them
    input:  msid    --- msid
            group   --- group name
    output: directries created if there were not before
    """
    p_dir = web_dir + group + '/'
    chs.check_dir_exist(p_dir)

    p_dir = p_dir + msid.capitalize() + '/'
    chs.check_dir_exist(p_dir)

    p_dir = p_dir + 'Plots/'
    chs.check_dir_exist(p_dir)

    return p_dir

#--------------------------------------------------------------------------------------------------------
#-- create_scatter_plot: create interactive trend plot                                                 ---
#--------------------------------------------------------------------------------------------------------

def create_scatter_plot(msid, xo, xb, yb,  ltype, mtype,  byear, a, b, d,  outname = ''):
    """
    create a plot
    input:  msid    --- msid
            xo      --- the original list of x data; used to computer the plotting range
            x       --- the list of x
            y       --- the list of y
            ltype   --- data type, such as short and long
            mtype   --- min, max, mid
            byear   --- if the plot is in year (ltype), byear indicates which year this plot is in
            a       --- the intercept of the fitted line
            b       --- the slope of the fitted line
            d       --- the error of the fitted line
            outname --- the name of png file to be created
    output: outname --- <web_dir>/<group>/<msid>/Plots/msid_*.png
    """
#
#--- cut out 2 out of 3 data points from one year plot and full range plot
#
    if ltype in ('one', 'long'):
        x = xb[0::3]
        y = yb[0::3]
    else:
        x = xb
        y = yb
#
#
#--- open and set plotting surface
#
#
    plt.close('all')

    fig, ax = plt.subplots(1, figsize=(8,6))

    props = font_manager.FontProperties(size=14)
    mpl.rcParams['font.size']   = 14
    mpl.rcParams['font.weight'] = 'bold'
#
#--- set plotting axes
#
    [xmin, xmax, xpos] = chs.set_x_plot_range(xo, ltype)    #--- use the original plotting range for x
    [ymin, ymax, ypos] = chs.set_y_plot_range(x, y, ltype)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    [xlabel, ylabel] = set_axes_label(msid,  ltype, byear)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if ltype == 'five':
        labels = []
        for lval in range(xmin, xmax):
            labels.append(lval)
        ax.set_xticklabels(labels)

#    ax.yaxis.labelpad = 30 
#
#--- set the size of plot
#
    fig.set_size_inches(10.0, 5.0)
    fig.tight_layout()

#
#---- trending plots
#
    points = ax.scatter(x, y, marker='o', s=20 ,lw=0)
#
#---- slope note
#
    ys   = a + b * xmin
    ye   = a + b * xmax
    plt.plot([xmin, xmax], [ys, ye], color='green', lw=3)

    if abs(b) < 0.001 or abs(b) > 100:
        line = 'Slope: ' +  ecf.modify_slope_dicimal(b, d)
    else:
        slp  = "%2.3f" % round(b, 3)
        err  = "%2.3f" % round(d, 3)
        line = 'Slope: ' + slp +'+/-' + err

    plt.text(xpos, ypos, line)
#
#--- set the size of plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
    fig.tight_layout()
    plt.savefig(outname, format='png', dpi=100)

    plt.close('all')

#----------------------------------------------------------------------------------
#-- set_axes_label: set axes labels                                              --
#----------------------------------------------------------------------------------

def set_axes_label(msid, ltype, byear):
    """
    set axes labels
    input:  msid    --- msid
            unit    --- unit
            ltype   --- short or long type plot indicator
            byear   --- the year of the short plot
    output: xlabel  --- x axis label
            ylabel  --- y axis label
    """

    try:
        unit = udict[msid]
    except:
        unit = msid


    if ltype in ('five', 'long'):
        xlabel = 'Time (year)'
    else:
        xlabel = 'Time (yday of ' + str(int(byear)) + ')'

    if unit != '':
        if unit in ('DEGF', 'DEGC'):
            unit = 'K'
        ylabel =  unit + '/Year'
    else:
        ylabel =  msid + '/Year'

    return [xlabel, ylabel]


#----------------------------------------------------------------------------------
#-- read_data: read the data of msid                                            ---
#----------------------------------------------------------------------------------

def read_data(dfile, msid,  ltype):
    """
    read the data of msid
    input:  dfile   --- data file name
            msid    --- msid
            ltype   --- data type long or short
    output: pdata   --- a two dimensional array  of data
                        xtime  = pdata[0]
                        dnum   = pdata[1]
                        avg    = pdata[4]
                        med    = pdata[5]
                        std    = pdata[6]
                        dmin   = pdata[7]
                        dmax   = pdata[8]
            byear   --- base year for short term plot
    """
    f     = pyfits.open(dfile)
    data  = f[1].data
    f.close()

    if len(data) == 0:
        return na

    temp   = list(data['time'])
    xtime  = []
    byear  = 1999
    for ent in temp:
        date = Chandra.Time.DateTime(ent)
        year = float(date.year)
        yday = float(date.yday)
        hrs  = float(date.hour)
        mins = float(date.min)
        secs = float(date.sec)
        if tcnv.isLeapYear(year) == 1:
            base = 366
        else:
            base = 365
        ytime = year + (yday + hrs / 24.0 + mins / 1440.0 + secs / 86400.0) / base
        if ltype in ('week', 'short'):
            if xtime == []:
                byear = year
    
            ytime -= byear
            ytime *= base
    
        xtime.append(ytime)

    xtime  = numpy.array(xtime)

    dnum   = data['dcount']
    avg    = data[msid]
    med    = data['med']
    std    = data['std']
    dmin   = data['min']
    dmax   = data['max']

#
#--- if the avg is totally flat, the plot wil bust; so change tiny bit at the last entry
#
    test = numpy.std(avg)
    if test == 0:
        alen = len(avg) - 1
        avg[alen] = avg[alen] * 1.0001
#
#--- put a couple of dummy array to match with other data reading script
#
    plist = [xtime, dnum, xtime, xtime,  avg, med, std, dmin, dmax]
    pdata = numpy.array(plist)
    pdata = pdata.astype(float)

    return [pdata, byear]


#--------------------------------------------------------------------------------------------------------

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':

    if len(sys.argv) == 2:
        mlist = sys.argv[1]
        create_derivative_plots(mlist) 

    elif len(sys.argv) == 3:
        mlist = sys.argv[1]
        inter = sys.argv[2]
        create_derivative_plots(mfile=mlist, inter=inter) 

    else:
        create_derivative_plots()

