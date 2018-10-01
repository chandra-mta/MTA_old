#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#       plot_bias_trend.py: plotting bias - overclock trend                                                 #
#                                                                                                           #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                           #
#                   Last update: May 13, 2014                                                               #
#                                                                                                           #
#############################################################################################################

import os
import sys
import re
import string
import random
import operator
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

#
#--- check whether this is a test case
#
comp_test = 'live'
if len(sys.argv) == 2:
    if sys.argv[1] == 'test':                   #---- test case
        comp_test = 'test'
    elif sys.argv[1] == 'live':                 #---- automated read in
        comp_test = 'live'
    else:
        comp_test = sys.argv[1].strip()         #---- input data name
else:
    comp_test = ''
#
#--- reading directory list
#
if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/bias_dir_list_test_py'
else:
    path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/bias_dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
import find_moving_average  as fmv
#
#--- temp writing file name
#

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#-- generate_all_plot: a control function to create bias - overclock plots                      ----
#---------------------------------------------------------------------------------------------------

def generate_all_plot():

    """
    a control function to create bias - overclock plots
    Input:  None but read from:
            <data_dir>/Bias_save/CCD<ccd>/quad<quad>

    Output: <web_dir>/Plots/Sub2/bias_plot_ccd<ccd>_quad<quad>.png
    """

    for ccd in range(0, 10):
        for quad in range(0, 4):
#
#--- set input and output file names
#
            file     = data_dir + 'Bias_save/CCD'      + str(ccd) + '/quad' + str(quad)
            outname  = web_dir  + 'Plots/Sub2/bias_plot_ccd' + str(ccd) + '_quad' + str(quad) + '.png'
#
#--- read data
#
            data = mcf.readFile(file)

            x     = []          #---- original x
            y     = []          #---- original y

            for ent in data:
                atemp = re.split('\s+|\t+', ent)
                try:
                    valx = (float(atemp[0]) - 48902399.0)/86400.0
                    valy = float(atemp[1]) - float(atemp[3])
#
#--- if the difference si too large, drop it
#
                    if abs(valy) > 10:
                        continue
                    x.append(valx)
                    y.append(valy)
                except:
                    pass
#
#--- compute moving average and upper and lower envelopes
#--- here, we set moving interval to 50 days and asked 5th degree polynomial fit for smoothing
#
            moving_avg = fmv.find_moving_average(x, y, 50.0, 5)
#
#--- plot the data and fittings
#
            plot_bias_trend(x, y, moving_avg, outname, ccd, quad)

#---------------------------------------------------------------------------------------------------
#-- plot_bias_trend: plotting bias data, moving average, top and bottom envelops to the data      --
#---------------------------------------------------------------------------------------------------

def plot_bias_trend(x, y, moving_avg, outname, ccd, quad):

    """
     plotting bias data, moving average, top and bottom envelops to the data
     Input:     x          --- independent variable
                y          --- dependent varialbes
                moving_avg --- a list of list containing:
                    [xcent, movavg, sigma, min_sv, max_sv, y_avg, y_min, y_max, y_sig]
                outname    --- output name
                ccd        --- ccd #
                quad       --- quad #
    Output:     png plots named: outname
    """
#
#--- extract moving average etc data from list
#
    mx = moving_avg[0]      #---- moving average x
    my = moving_avg[1]      #---- moving average y
    ma = moving_avg[5]      #---- moving average polinomial fit
    mb = moving_avg[6]      #---- lower envelop estimate
    mt = moving_avg[7]      #---- upper envelop estimate
#
#--- set plotting range
#
    xmin = min(x)
    xmax = max(x)
    diff = xmax - xmin
    xmin -= 0.05 * diff
    xmin = int(xmin)
    if xmin < 0:
        xmin = 0
    xmax += 0.05 * diff
    xmax = int(xmax)
#
#--- y range is set to the average +/- 1.5
#
    ymean = mean(y)
    ymin  = ymean - 1.5
    ymin  = round(ymin, 2)
    ymax  = ymean + 1.5
    ymax  = round(ymax, 2)
#
#--- clean up all plotting param
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)
#
#---- set a panel
#
    ax = plt.subplot(111)
    ax.set_autoscale_on(False)      #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)        #---- they are necessary for the older version to set

    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
#
#--- original data
#
    p, = plt.plot(x, y, color='black', lw =0 , marker='.', markersize=0.5)
#
#--- moving average
#
    plt.plot(mx, my, color='blue', lw =1 , marker='.', markersize=0.5)
#
#--- moving averge smoothed
#
    plt.plot(mx, ma, color='red', lw =1.5 )
#
#--- lower envelope
#
    plt.plot(mx, mb, color='green', lw =1.5 )
#
#--- upper envelope
#
    plt.plot(mx, mt, color='green', lw =1.5 )
#
#--- add legend
#
    title = 'CCD' + str(ccd) +'_q' + str(quad)

    leg = legend([p],  [title], prop=props, loc=2)
    leg.get_frame().set_alpha(0.5)

    ax.set_xlabel("Time (DOM)", size=8)
    ax.set_ylabel("Bias - Overclock", size=8)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=100)
#
#--- clean up all plotting param
#
    plt.close('all')

#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':
    
    generate_all_plot()
