#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       disk_space_read_dusk.py: check /data/mta space and subdirectories       #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Oct 27, 2014                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import numpy as np



#
#--- reading directory list
#
path = '/data/mta/Script/Disk_check/house_keeping/dir_list_py'
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

#
#--- temp writing file name
#

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def disk_space_read_dusk():

    diskName = '/data/mta/'
    nameList = ['Script','DataSeeker','Test','CAL']
    duskName = 'dusk_mta'
    pastData = data_out + 'disk_data_mta'
    plot_dusk_result(diskName, duskName, nameList, pastData)

    diskName = '/data/mta4/'
    nameList = ['CUS','www','Deriv']
    duskName = 'dusk_mta4'
    pastData = data_out + 'disk_data_mta4'
    plot_dusk_result(diskName, duskName, nameList, pastData)

    diskName = '/data/mays/'
    nameList = ['MTA']
    duskName = 'dusk_mays'
    pastData = data_out + 'disk_data_mays'
    plot_dusk_result(diskName, duskName, nameList, pastData)

    diskName = '/data/mta_www/'
    nameList = ['ap_report', 'mp_reports','mta_max_exp']
    duskName = 'dusk_www'
    pastData = data_out + 'disk_data_www'
    plot_dusk_result(diskName, duskName, nameList, pastData)

    diskName = '/proj/rac/ops/'
    nameList = ['CRM2', 'CRM', 'ephem', 'CRM3']
    duskName = 'proj_ops'
    pastData = data_out + 'disk_proj_ops'
    plot_dusk_result(diskName, duskName, nameList, pastData)

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def plot_dusk_result(diskName, duskName, nameList, pastData):

#
#--- find the disk capacity of the given disk
#
    disk_capacity = diskCapacity(diskName)

#
#--- read the output from dusk
#
    line = run_dir + duskName
    f    = open(line, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    capacity = {}               #---- make a dictionary
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        try:
            val = 100.0 * float(atemp[0]) /disk_capacity
            val =  round(val, 2)
            capacity[atemp[1]] = val 
        except:
            pass
#
#--- today's date
#
    today   = tcnv.currentTime('local')
    year    = today[0]
    month   = today[1]
    day     = today[2]
    hours   = today[3]
    minutes = today[4]
    seconds = today[5]
#
#--- convert to dom
#
    dom   = tcnv.findDOM(year, month, day, hours, minutes,seconds)
    dom   = round(dom, 2)
#
#--- append the new data to the data table
#
    f   = open(pastData, 'a')
    f.write(str(dom))
    for dName in nameList:
        f.write(':')
        string = str(capacity[dName])
        f.write(string)
    f.write('\n')
    f.close()

#
#---- start plotting history data
#
    try:
        plot_history_trend(diskName, duskName, nameList, pastData)
    except:
        pass

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def plot_history_trend(diskName, duskName, nameList, pastData):

#
#--- read past data
#
    f    = open(pastData, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    colNum = len(nameList)

    domTime = []
    for ent in nameList:
        vnam = ent + '_dat'
        exec "%s = []" % (vnam)
    
    prev = 0
    for ent in data:
        atemp = re.split(':', ent)
        domTime.append(float(atemp[0]))
        for i in range(0, colNum):
            vnam  = nameList[i] + '_dat'
            try:
               val  = float(atemp[i+1]) 
               prev = val
            except:
                val = prev

            exec "%s.append(val)" % (vnam)


    xSets = [domTime]
#    xmin  = min(domTime)
#    xdiff = xmax - xmin
#    xmin  = int(xmin - 0.1 * xdiff)
    xmin  = 1000                                #---- the earliest data starts DOM ~ 1000
    xmax  = max(domTime)
    xdiff = xmax - xmin
    xmax  = int(xmax + 0.1 * xdiff)
    xname = 'Time (DOM)'
    yname = 'Disk Capacity Used (%)'

    for ent in nameList:
        vnam = ent + '_dat'
        exec "yval = %s" % (vnam)

        ymin  = min(yval)
        ymax  = max(yval)
        ydiff = ymax - ymin
        if ydiff == 0:
            ymin = 0
            if ymax < 1:
                ymax == 5

#        ymin  = int(ymin - 0.1 * ydiff)
#        if ymin < 0:
#            ymin = 0
        ymin  = 0
        ymaxt = int(ymax + 0.1 * ydiff) 

        if ymaxt < ymax:
            ymax += 2
            ymax = int(ymax)
        else:
            ymax = ymaxt


        ySets     = [yval]
        entLabels = [ent]

        plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels)

        out_name =  ent.lower() + '_disk.png'

        cmd = 'mv out.png ' + fig_out +  out_name
        os.system(cmd)

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def diskCapacity(diskName):

    cmd = 'df -k ' + diskName + '> ' + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    disk_capacity = 'na'

    for ent in data:
        try:
            atemp  = re.split('\s+', ent)
            val = float(atemp[1])
            for test in atemp:
                m = re.search('%', test)
                if m is not None:
                    disk_capacity = val
                    break
        except:
            pass

    return disk_capacity



#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------







#-----------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                       ---
#-----------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels):

    """
    This function plots multiple data in separate panels.
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            xname: a name of x-axis
            yname: a name of y-axis
            entLabels: a list of the names of each data

    Output: a png plot: out.png
    """
#
#--- set line color list
#
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
#
#--- clean up the plotting device
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
    for i in range(0, tot):
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
        exec "%s.set_ylim(ymin=ymin, ymax=ymax, auto=False)" % (axNam)

        xdata  = xSets[i]
        ydata  = ySets[i]
  
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], lw =1.5)

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
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

disk_space_read_dusk()
