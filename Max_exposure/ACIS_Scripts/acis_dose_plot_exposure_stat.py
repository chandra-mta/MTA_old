#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_plot_exposure_stat.py:  plotting trendings of avg, min, 10th bright,  #
#                                       and max counts of each quadrant of I2, I3,      #
#                                       S2, and S3.                                     #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Apr 04, 2018                                                       #
#                                                                                       #
#########################################################################################


import sys
import os
import string
import re
import copy
import numpy as np
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

#
#--- reading directory list
#

path = '/data/mta/Script/Exposure/house_keeping/acis_dir_list'
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
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv

#
#--- Exposure related funcions shared
#

import exposureFunctions as expf

#------------------------------------------------------------------------------------------------------------------------
#--- acis_dose_plot_exposure_stat: read hrc database, and plot history of exposure                                     ---
#------------------------------------------------------------------------------------------------------------------------

def acis_dose_plot_exposure_stat(indir = 'NA', outdir = 'NA', clean = 'NA', comp_test = 'NA'):

    'read acis database, and plot history of exposure. input: data directory path, output directory path '
#
#--- setting indir and outdir if not given
#
    if indir   == 'NA':
        indir   = data_out

    if outdir  == 'NA':
        outdir  = plot_dir
#
#--- clean up the data sets before reading
#
    if clean != 'NA':
        expf.clean_data(indir)

#
#--- start plotting data
#
    for ccd in ('i_2', 'i_3', 's_2', 's_3'):
        for sec in range(0, 4):

            inst = ccd + '_n_' + str(sec)
        
            [date,  mean_dff, min_dff, max_dff, s1_dff, s2_dff, s3_dff] =  read_data(indir, inst, 'dff')
            [date,  mean_acc, min_acc, max_acc, s1_acc, s2_acc, s3_acc] =  read_data(indir, inst, 'acc')

#
#--- plot data
#
            plot_acis_dose(date, mean_acc, min_acc, max_acc, s1_acc, s2_acc, s3_acc, mean_dff, min_dff, max_dff, s1_dff, s2_dff, s3_dff)

#
#--- move to the plot directory
#
            outfile = inst + '.png'
#            cmd     = 'mv acis.png ' + plot_dir +  outfile
#            os.system(cmd)
            if comp_test == 'test':
                cmd = 'convert acis.png -trim ' + test_plot_dir +  outfile
            else:
                cmd = 'convert acis.png -trim ' + plot_dir +  outfile

            os.system(cmd)
            os.system('rm acis.png')


#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------

def read_data(indir, inst, part):

    date = []
    avg  = []
    smin = []
    smax = []
    s1   = []
    s2   = []
    s3   = []

    file = indir + inst + '_' + part + '_out'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    for ent in data:
        atemp = re.split('\s+', ent)
        try:
            avg.append(float(atemp[2]))
            smin.append(float(atemp[4]))
            smax.append(float(atemp[6]))
            s1.append(float(atemp[8]))
            s2.append(float(atemp[9]))
            s3.append(float(atemp[10]))
        except:
            continue

        time  = float(atemp[0]) + float(atemp[1])/12.0 + 0.5
        date.append(time)

    return [date,  avg, smin, smax, s1, s2, s3]


#------------------------------------------------------------------------------------------------------------------------
#--- plot_acis_dose: plot 6 panels of hrc quantities.                                                                   --
#------------------------------------------------------------------------------------------------------------------------

def plot_acis_dose(date, amean, amin, amax, accs1, accs2, accs3, dmean, dmin, dmax, dffs1, dffs2, dffs3):

    """
    plot 6 panels of acis quantities. Input: date, diff, mean, min, max, 1 acc, mean, min, max
    input : date dmean, dmin, dmax, amean, amin, amax
    """

    plt.close('all')

#
#---- set a few parameters
#

    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=6)
    plt.subplots_adjust(hspace=0.05)
    plt.subplots_adjust(wspace=0.12)

#
#--- mean
#
    ax1 = plt.subplot(4,2,1)
    try:
        plot_panel(date, dmean, 'Average', ax1)
    except:
        pass

#
#--- mean cumulative
#
    ax2 = plt.subplot(4,2,2)
    try:
        plot_panel(date, amean, 'Average Cumulative', ax2)
    except:
        pass
#
#--- min
#
    ax3 = plt.subplot(4,2,3)
    try:
        plot_panel(date, dmin, 'Minimum', ax3)
    except:
        pass
#
#--- min cumulative
#
    ax4 = plt.subplot(4,2,4)
    try:
        plot_panel(date, amin, 'Minimum Cumulative', ax4)
    except:
        pass
#
#--- max
#
    ax5 = plt.subplot(4,2,5)
    try:
        plot_panel(date, dmax, 'Maximum', ax5)
    except:
        pass
#
#--- max cumulative
#
    ax6 = plt.subplot(4,2,6)
    try:
        plot_panel(date, amax, 'Maximum Cumulative', ax6)
    except:
        pass


#
#--- 68, 95, and 99.6% levels
#
    labels = ["68% Value ", "95% Value", "99.7% Value"]
    ax7 = plt.subplot(4,2,7)
    try:
        plot_panel2(date, dffs1, dffs2, dffs3,  labels, ax7)
    except:
        pass
#
#--- 68, 95, and 99.6% cumulative
#
    ax8 = plt.subplot(4,2,8)
    try:
        plot_panel2(date, accs1, accs2, accs3, labels, ax8)
    except:
        pass

#
#--- plot x axis tick label only at the bottom ones
#
    for ax in ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8:
        if ax != ax7 and ax != ax8:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            pass

#
#--- putting axis names
#
        ax3.set_ylabel('Counts per Pixel')
        ax7.set_xlabel('Year')
        ax8.set_xlabel('Year')
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#   
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 12.0)
#
#--- save the plot in png format
#   
    plt.savefig('acis.png', format='png', dpi=100)

    plt.close('all')



#------------------------------------------------------------------------------------------------------------------------
#---   plot_panel: plotting each panel for a given "ax"                                                               ---
#------------------------------------------------------------------------------------------------------------------------

def plot_panel(x, y, label, ax, ymin = 'NA', ymax = 'NA'):

    'plotting each panel for a given "ax". Input: x, y, label, ax (designation of the plot), ymin ="NA" ymax = "NA". '

#
#--- x axis setting: here we assume that x is already sorted
#
    xmin = x[0]
    xmax = x[len(x) -1]
    diff = xmax - xmin
    xmin = xmin - 0.05 * diff
    xmax = xmax + 0.05 * diff
    xbot = xmin + 0.05 * diff
#
#--- y axis setting
#
    tymin = 1e8
    tymax = 1.0
    for i in range(0, len(y)):
        if y[i] > tymax: 
            tymax = y[i]
        if y[i] < tymin:
            tymin = y[i]

    if ymin == 'NA':
        ymin = tymin

    if ymax == 'NA':
        ymax = tymax

#
#--- for the case,  ymin == ymax, 
#
    if ymin == ymax:
        ymax += 1

    diff = ymax - ymin
    ymin = ymin - 0.01 * diff

    if ymin < 0:
        ymin = 0

    ymax = ymax + 0.1 * diff
    ytop = ymax - 0.12 * diff

#
#--- setting panel 
#

    ax.set_autoscale_on(False)         #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)           #---- they are necessary for the older version to set

    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

#
#--- plot line
#
    plt.plot(x, y, color='blue',   lw=1, marker='+', markersize=1.5)

    plt.text(xbot, ytop, label)





#------------------------------------------------------------------------------------------------------------------------
#---   plot_panel: plotting each panel for a given "ax"                                                               ---
#------------------------------------------------------------------------------------------------------------------------

def plot_panel2(x, s1, s2, s3, labels, ax, ymin = 'NA', ymax = 'NA'):

    'plotting each panel for a given "ax". Input: x, s1, s2, s3, label, ax (designation of the plot), ymin ="NA" ymax = "NA". '

#
#--- x axis setting: here we assume that x is already sorted
#
    xmin = x[0]
    xmax = x[len(x) -1]
    diff = xmax - xmin
    xmin = xmin - 0.05 * diff
    xmax = xmax + 0.05 * diff
    xbot = xmin + 0.05 * diff
#
#--- y axis setting
#
    tymin = 1e8
    tymax = 1e-8
    for i in range(0, len(s3)):
        if s3[i] > tymax: 
            tymax = s3[i]
        if s3[i] < tymin:
            tymin = s3[i]

    if ymin == 'NA':
        ymin = tymin

    if ymax == 'NA':
        ymax = tymax

#
#--- for the case,  ymin == ymax, 
#
    if ymin == ymax:
        ymax += 1

    diff = ymax - ymin
    ymin = ymin - 0.01 * diff

    if ymin < 0:
        ymin = 0

    ymax = ymax + 0.1 * diff
    ytop = ymax - 0.12 * diff

#
#--- setting panel 
#

    ax.set_autoscale_on(False)         #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)           #---- they are necessary for the older version to set

    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

#
#--- plot line
#
    p1, = plt.plot(x, s1, color='blue',  lw=1, marker='', markersize=0.0)
    p2, = plt.plot(x, s2, color='green', lw=1, marker='', markersize=0.0)
    p3, = plt.plot(x, s3, color='orange',lw=1, marker='', markersize=0.0)

    legend([p1, p2, p3], [labels[0], labels[1], labels[2]], loc=2, fontsize=9)




#--------------------------------------------------------------------------------------------------------
#
#--- pylab plotting routine related modules
#
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

#
#--- check whether this is a test case
#
if len(sys.argv) == 2:
    if sys.argv[1] == 'test':               #---- this is a test case
        comp_test = 'test'
    else:
        comp_test = 'real'
else:
    comp_test = 'real'

if __name__ == '__main__':

    if comp_test == 'test':
        acis_dose_plot_exposure_stat(clean ='Yes', comp_test='test')
    else:
        acis_dose_plot_exposure_stat(clean ='Yes')
