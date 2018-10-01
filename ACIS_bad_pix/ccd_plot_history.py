#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#       ccd_plot_history.py: create  various history plots for warm pixels and warm columns                 #
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
#
#--- reading directory list
#
if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py_test'
else:
    path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'

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
import convertTimeFormat       as tcnv
import mta_common_functions    as mcf
import bad_pix_common_function as bcf
#
#--- temp writing file name
#

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)

#
#--- set a dimension for an array: set slightly larger than today's DOM.
#
[dyear, dmon, dday, dhours, dmin, dsec, dweekday, dyday, ddst] = tcnv.currentTime()
ddom = tcnv.findDOM(dyear, dmon, dday, dhours, dmin, dsec)
adim = int(ddom + 100)

#---------------------------------------------------------------------------------------------------
#--- plot_ccd_history: plotting warm pixel history                                               ---
#---------------------------------------------------------------------------------------------------

def plot_ccd_history():

    """
    plotting warm pixel history  
    Input: None but read from:
            <data_dir>/Disp_dir/ccd<ccd>_cnt
            <data_dir>/Disp_dir/bad_ccd<ccd>_cnt
            <data_dir>/Disp_dir/cum_ccd<ccd>_cnt
    Output: <plot_dir>hist_plot<ccd>.png
    """

    for ccd in range(0, 10):
#
#--- set input file names
#
        file = data_dir + '/Disp_dir/ccd' + str(ccd) + '_cnt'
#
#--- read data and put in one basket
#
        [xMinSets, xMaxSets, yMinSets, yMaxSets, xSets, ySets] = readData(file)
        xmin = min(xMinSets)
        xmax = max(xMaxSets)
#
#--- x-axis name and y-axis name
#
        xname = "Time (DOM)"
        yname = "Counts"
#
#--- titles
#
        entLabels = []
        pname = 'Cumulative Numbers of Warm Pixels: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Daily Warm Pixels: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Persisting Warm Pixels: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Potential Warm Pixels (Real Warm + Flickering): CCD ' + str(ccd)
        entLabels.append(pname)
#
#--- plotting: create three panel plots
#
        pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=0.0, lwidth=1.5)
        if pchk > 0:
            cmd  = 'mv out.png ' + web_dir + 'Plots/hist_plot_ccd' + str(ccd) + '.png'
            os.system(cmd)




#---------------------------------------------------------------------------------------------------
#--- plot_hccd_history: plotting hot pixel history                                               ---
#---------------------------------------------------------------------------------------------------

def plot_hccd_history():

    """
    plotting warm pixel history  
    Input: None but read from:
            <data_dir>/Disp_dir/ccd<ccd>_cnt
            <data_dir>/Disp_dir/bad_ccd<ccd>_cnt
            <data_dir>/Disp_dir/cum_ccd<ccd>_cnt
    Output: <plot_dir>hist_plot<ccd>.png
    """

    for ccd in range(0, 10):
#
#--- set input file names
#
        file = data_dir + '/Disp_dir/hccd' + str(ccd) + '_cnt'
#
#--- read data and put in one basket
#
        [xMinSets, xMaxSets, yMinSets, yMaxSets, xSets, ySets] = readData(file)
        xmin = min(xMinSets)
        xmax = max(xMaxSets)
#
#--- x-axis name and y-axis name
#
        xname = "Time (DOM)"
        yname = "Counts"
#
#--- titles
#
        entLabels = []
        pname = 'Cumulative Numbers of Hot Pixels: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Daily Hot Pixels: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Persisting Hot Pixels: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Potential Hot Pixels (Real Hot + Flickering): CCD ' + str(ccd)
        entLabels.append(pname)
#
#--- plotting: create three panel plots
#
        pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=0.0, lwidth=1.5)
        if pchk > 0:
            cmd  = 'mv out.png ' + web_dir + 'Plots/hist_plot_hccd' + str(ccd) + '.png'
            os.system(cmd)



#---------------------------------------------------------------------------------------------------
#--- plot_col_history: plot warm column history                                                  ---
#---------------------------------------------------------------------------------------------------

def plot_col_history():

    """
    plot warm column history 
    Input: None but read from:
            <data_dir>/Disp_dir/col<ccd>_cnt
            <data_dir>/Disp_dir/bad_col<ccd>_cnt
            <data_dir>/Disp_dir/cum_col<ccd>_cnt
    Output: <plot_dir>/hist_plot_col<ccd>.png
    """

    for ccd in range(0, 10):
#
#--- set input file names
#
        file = data_dir + '/Disp_dir/col' + str(ccd) + '_cnt'
#
#--- read data and put in one basket
#
        [xMinSets, xMaxSets, yMinSets, yMaxSets, xSets, ySets] = readData(file)
        xmin = min(xMinSets)
        xmax = max(xMaxSets)
#
#--- x-axis name and y-axis name
#
        xname = "Time (DOM)"
        yname = "Counts"
#
#--- titles
#
        entLabels = []
        pname = 'Cumulative Numbers of Warm Columns: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Daily Warm Columns: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Persisting Warm Columns: CCD ' + str(ccd)
        entLabels.append(pname)
        pname = 'Numbers of Potential Warm Columns (Real Warm + Flickering): CCD ' + str(ccd)
        entLabels.append(pname)
#
#--- plotting
#
        pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=0.0, lwidth=1.5)
        if pchk > 0:
            cmd  = 'mv out.png ' + web_dir + 'Plots/hist_plot_col' + str(ccd) + '.png'
            os.system(cmd)


#---------------------------------------------------------------------------------------------------
#--- plot_front_ccd_history: plot history of combined warm pixel counts of all front CCDs        ---
#---------------------------------------------------------------------------------------------------

def plot_front_ccd_history():

    """
    plot history of combined warm pixel counts of all front CCDs
    CCD #: 0, 1, 2, 3, 4, 6, 8, 9
    Input: None, but read from:
            <data_dir>/Disp_dir/ccd<ccd>_cnt
            <data_dir>/Disp_dir/bad_ccd<ccd>_cnt
            <data_dir>/Disp_dir/cum_ccd<ccd>_cnt
    Output: <plot_dir>hist_plot_front_side.png
    """

#
#--- set input file names
#
    file = data_dir + '/Disp_dir/front_side_ccd_cnt'
#
#--- read data and put in one basket
#
    [xMinSets, xMaxSets, yMinSets, yMaxSets, xSets, ySets] = readData(file)
    xmin = min(xMinSets)
    xmax = max(xMaxSets)
#
#--- x-axis name and y-axis name
#
    xname = "Time (DOM)"
    yname = "Counts"
#
#--- titles
#
    entLabels = []
    pname = 'Cumulative Numbers of Warm Pixels: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Daily Warm Pixels: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Persisting Warm Pixels: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Potential Warm Pixels (Real Warm + Flickering): Front Side CCDs '
    entLabels.append(pname)
#
#--- plotting: create three panel plots
#
    pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=0.0, lwidth=1.5)
    if pchk > 0:
        cmd  = 'mv out.png ' + web_dir + 'Plots/hist_ccd_plot_front_side.png'
        os.system(cmd)




#---------------------------------------------------------------------------------------------------
#--- plot_front_hccd_history: plot history of combined hot pixel counts of all front CCDs        ---
#---------------------------------------------------------------------------------------------------

def plot_front_hccd_history():

    """
    plot history of combined warm pixel counts of all front CCDs
    CCD #: 0, 1, 2, 3, 4, 6, 8, 9
    Input: None, but read from:
            <data_dir>/Disp_dir/ccd<ccd>_cnt
            <data_dir>/Disp_dir/bad_ccd<ccd>_cnt
            <data_dir>/Disp_dir/cum_ccd<ccd>_cnt
    Output: <plot_dir>hist_plot_front_side.png
    """

#
#--- set input file names
#
    file = data_dir + '/Disp_dir/front_side_hccd_cnt'
#
#--- read data and put in one basket
#
    [xMinSets, xMaxSets, yMinSets, yMaxSets, xSets, ySets] = readData(file)
    xmin = min(xMinSets)
    xmax = max(xMaxSets)
#
#--- x-axis name and y-axis name
#
    xname = "Time (DOM)"
    yname = "Counts"
#
#--- titles
#
    entLabels = []
    pname = 'Cumulative Numbers of Warm Pixels: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Daily Warm Pixels: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Persisting Warm Pixels: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Potential Warm Pixels (Real Warm + Flickering): Front Side CCDs '
    entLabels.append(pname)
#
#--- plotting: create three panel plots
#
    pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=0.0, lwidth=1.5)
    if pchk > 0:
        cmd  = 'mv out.png ' + web_dir + 'Plots/hist_hccd_plot_front_side.png'
        os.system(cmd)


#---------------------------------------------------------------------------------------------------
#--- plot_front_col_history: plot history of combined warm column counts of all front CCDs       ---
#---------------------------------------------------------------------------------------------------

def plot_front_col_history():

    """
    plot history of combined warm column counts of all front CCDs
    CCD #: 0, 1, 2, 3, 4, 6, 8, 9
    Input: None, but read from:
            <data_dir>/Disp_dir/col<ccd>_cnt
            <data_dir>/Disp_dir/bad_col<ccd>_cnt
            <data_dir>/Disp_dir/cum_col<ccd>_cnt
    Output: <plot_dir>hist_col_plot_front_side.png
    """
    file = data_dir + '/Disp_dir/front_side_col_cnt'
#
#--- read data and put in one basket
#
    [xMinSets, xMaxSets, yMinSets, yMaxSets, xSets, ySets] = readData(file)
    xmin = min(xMinSets)
    xmax = max(xMaxSets)
#
#--- x-axis name and y-axis name
#
    xname = "Time (DOM)"
    yname = "Counts"
#
#--- titles
#
    entLabels = []
    pname = 'Cumulative Numbers of Warm Columns: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Daily Warm Columns: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Persisting Warm Columns: Front Side CCDs '
    entLabels.append(pname)
    pname = 'Numbers of Potential Warm Columns (Real Warm + Flickering): Front Side CCDs '
    entLabels.append(pname)
#
#--- plotting: create three panel plots
#
    pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=0.0, lwidth=1.5)
    if pchk > 0:
        cmd  = 'mv out.png ' + web_dir + 'Plots/hist_col_plot_front_side.png'
        os.system(cmd)


#---------------------------------------------------------------------------------------------------
#--- addupVal: add a value to an arry at a given location                                        ---
#---------------------------------------------------------------------------------------------------

def addupVal(barray, xval, yval):

    """
    add a value to an arry at a given location
    Input:      barray: one dim array of length len(xval) which contains the original data values
                xval:   one dim array of length len(xval) which contains the array location info
                yval:   one dim array of length len(xval) which contains the adding values
    Output:     barray: updated array 
    """

    for i in range(0, len(xval)):
        x = int(xval[i])
        y = int(yval[i])
        barray[x] += y


    return barray
    
#---------------------------------------------------------------------------------------------------
#---  readData: read data and set plotting range                                                 ---
#---------------------------------------------------------------------------------------------------

def readData(dataname):

    """
    read data and set plotting range
    Input: dataname  --- data file name (need a full path to the file)
    Output: xval     --- an array of independent values (dom)
            cval     --- cumulative counts
            dval     --- daily counts
            bval     --- actual bad point counts
            pval     --- potential bad point counts
    """

#
#--- read data
#
    data = mcf.readFile(dataname)

    xval = []
    cval = []
    dval = []
    bval = []
    pval = []

    prev = 0
    for ent in data:
        atemp = re.split('<>', ent)
        try:
            val = float(atemp[0])
            if val < 0:
                continue
            if val == prev:
                continue

            xval.append(int(val))
        
            val1  = float(atemp[2])
            val2  = float(atemp[3])
            val3  = float(atemp[4])
            val4  = float(atemp[5])
            cval.append(val1)
            dval.append(val2)
            bval.append(val3)
            pval.append(val3 + val4)
        except:
            pass
#
#-- find plotting ranges and make a list of data lists
#
    xmin_list = []
    xmax_list = []
    ymin_list = []
    ymax_list = []
    x_list    = []
    y_list    = []

    (xmin, xmax, ymin, ymax) = findPlottingRange(xval, cval)
    xmin_list.append(xmin)
    xmax_list.append(xmax)
    ymin_list.append(ymin)
    ymax_list.append(ymax)
    x_list.append(xval)
    y_list.append(cval)

    (xmin, xmax, ymin, ymax) = findPlottingRange(xval, dval)
    xmin_list.append(xmin)
    xmax_list.append(xmax)
    ymin_list.append(ymin)
    ymax_list.append(ymax)
    x_list.append(xval)
    y_list.append(dval)

    (xmin, xmax, ymin, ymax) = findPlottingRange(xval, bval)
    xmin_list.append(xmin)
    xmax_list.append(xmax)
    ymin_list.append(ymin)
    ymax_list.append(ymax)
    x_list.append(xval)
    y_list.append(bval)

    (xmin, xmax, ymin, ymax) = findPlottingRange(xval, pval)
    xmin_list.append(xmin)
    xmax_list.append(xmax)
    ymin_list.append(ymin)
    ymax_list.append(ymax)
    x_list.append(xval)
    y_list.append(pval)

    return [xmin_list, xmax_list, ymin_list, ymax_list, x_list, y_list]

#---------------------------------------------------------------------------------------------------
#--- findPlottingRange: setting plotting range                                                   ---
#---------------------------------------------------------------------------------------------------

def findPlottingRange(xval, yval):

    """
    setting plotting range
    Input:  xval --- an array of x-axis
            yval --- an array of y-axis
    Output: xmin --- the lower boundary of x axis plotting range
            xmax --- the upper boundary of x axis plotting range
            ymin --- the lower boundary of y axis plotting range
            ymax --- the upper boundary of y axis plotting range
    """
#
#--- set ploting range.
#
    xmin = min(xval)
    xmax = max(xval)
    xdff = xmax - xmin
    xmin -= 0.1 * xdff
    if xmin < 0.0:
        xmin = 0
    xmax += 0.1 * xdff
#
#--- since there is a huge peak during the first year, avoid that to set  y plotting range
#
    ytemp = []
    for i in range(0, len(yval)):
        if xval[i] < 300:
            continue
        ytemp.append(yval[i])

    ymin = min(ytemp)
    ymax = max(ytemp)

    ydff = ymax - ymin
    if ydff == 0:
        ymin = 0
        if ymax == 0:
            ymax = 2
    else:
        ymin -= 0.1 * ydff
        if ymin < 0.0:
            ymin = 0
        ymax += 0.1 * ydff

    ymin = int(ymin)
    ymax = int(ymax) + 2

    return(xmin, xmax, ymin, ymax)


#---------------------------------------------------------------------------------------------------
#--- fillGaps: fill missing values                                                               ---
#---------------------------------------------------------------------------------------------------

def fillGaps(yval):

    """
    fill missing values
    Input:  yval
    Output: yval (modified)
    """

    prev = 0
    for i in range(0, len(yval)):
        if yval[i] == 0:
            yval[i] = prev
        else:
            prev = yval[i]

    return yval


#---------------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                           ---
#---------------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=1.0, lwidth=1.5):

    """
    This function plots multiple data in separate panels
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            yMinSets: a list of ymin 
            yMaxSets: a list of ymax
            entLabels: a list of the names of each data
            mksize:     a size of maker
            lwidth:     a line width

    Output: a png plot: out.png
    """
#
#--- set line color list
#
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
#
#--- close all opened plot
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    tot = len(entLabels)
#
#--- start plotting each data
#
    for i in range(0, len(entLabels)):
        axNam = 'ax' + str(i)
#
#--- setting the panel position
#
        j = i + 1
        if i == 0:
            line = str(tot) + '1' + str(j)
        else:
            line = str(tot) + '1' + str(j) + ', sharex=ax0'
            line = str(tot) + '1' + str(j)

        exec "%s = plt.subplot(%s)"       % (axNam, line)
        exec "%s.set_autoscale_on(False)" % (axNam)      #---- these three may not be needed for the new pylab, but 
        exec "%s.set_xbound(xmin,xmax)"   % (axNam)      #---- they are necessary for the older version to set

        exec "%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam)
        exec "%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (axNam)

        xdata  = xSets[i]
        ydata  = ySets[i]
  
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], marker='.', markersize=mksize, lw = lwidth)

#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec "%s.set_ylabel(yname, size=8)" % (axNam)

#
#--- add x ticks label only on the last panel
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        if i != tot-1: 
            exec "line = %s.get_xticklabels()" % (ax)
            for label in  line:
                label.set_visible(False)
        else:
            pass

    xlabel(xname)

#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=100)

    return mcf.chkFile('./out.png')

#-----------------------------------------------------------------------------------------------
#-- plotPanel2: plotting multiple data in a single panel                                     ---
#-----------------------------------------------------------------------------------------------

def plotPanel2(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels):

    """
    This function plots multiple data in a single panel.
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            xname: a name of x-axis
            yname: a name of y-axis
            entLabels: a list of the names of each data

    Output: a png plot: out.png
    """

    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
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

    tot = len(entLabels)
#
#--- start plotting each data set
#
    lnamList = []
    for i in range(0, tot):
        xdata  = xSets[i]
        ydata  = ySets[i]

        if tot > 1:
            lnam = 'p' + str(i)
            lnamList.append(lnam)
            exec "%s, = plt.plot(xdata, ydata, color=colorList[i], lw =1 , marker='.', markersize=0.5, label=entLabels[i])" % (lnam)
        else:
#
#--- if there is only one data set, ignore legend
#
            plt.plot(xdata, ydata, color=colorList[i], lw =1 , marker='.', markersize=0.5)

#
#--- add legend
#
    if tot > 1:
        line = '['
        for ent in lnamList:
            if line == '[':
                line = line + ent
            else:
                line = line +', ' +  ent
        line = line + ']'

        exec "leg = legend(%s,  entLabels, prop=props)" % (line)
        leg.get_frame().set_alpha(0.5)

    ax.set_xlabel(xname, size=8)
    ax.set_ylabel(yname, size=8)


#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=100)


#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':

    plot_ccd_history()
    plot_front_ccd_history()

    plot_hccd_history()
    plot_front_hccd_history()

    plot_col_history()
    plot_front_col_history()
