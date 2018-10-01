#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       check_disk_space.py:   check /data/mta* space and send out email        #
#                              if it is beyond a limit                          #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Feb 08, 2018                                               #
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

#
#--- set y plotting range
#
ymin = 30
ymax = 100

#-----------------------------------------------------------------------------------------------
#--- check_disk_space: extract disk usegae data-------------------------------------------------
#-----------------------------------------------------------------------------------------------

def check_disk_space():

    """
    this function extracts disk usage data
    Input: none
    Output udated usage table

    """
    line = ''
    chk  = 0;
#
#--- /data/mta/
#
    dName = '/data/mta'
    per0 = find_disk_size(dName)
    if per0 > 91:
        chk += 1
        line = dName + ' is at ' + str(per0) + '% capacity\n'

#
#--- /data/mta1/
#
    dName = '/data/mta1'
    per1 = find_disk_size(dName)
    if per1 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per1) + '% capacity\n'


#
#--- /data/mta2/
#
    dName = '/data/mta2'
    per2 = find_disk_size(dName)
    if per2 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per2) + '% capacity\n'

#
#--- /data/mta4/
#
    dName = '/data/mta4'
    per4 = find_disk_size(dName)
    if per4 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per4) + '% capacity\n'

#
#--- /data/swolk/
#
    dName = '/data/swolk'
    per5 = find_disk_size(dName)
    if per5 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per5) + '% capacity\n'

#
#--- /data/mays/
#
    dName = '/data/mays'
    per6 = find_disk_size(dName)
    if per6 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per6) + '% capacity\n'

#
#--- /data/mta_www/
#
    dName = '/data/mta_www'
    per7 = find_disk_size(dName)
    if per7 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per7) + '% capacity\n'
#
#--- /proj/rac/
#
##    dName = '/proj/rac'
##    per8 = find_disk_size(dName)
##    if per8 > 95:
##        chk += 1
##        line = line + dName + ' is at ' + str(per8) + '% capacity\n'
    per8 = 0
#
#--- if any of the disk capacities are over 95%, send out a warning email
#
    if chk > 0:
        send_mail(line)
#
#--- update data table
#
    per3 = 0;
    update_datatable(per0, per1, per2, per3, per4, per5, per6, per7, per8)
#
#--- plot data
#
    historyPlots()



#-----------------------------------------------------------------------------------------------
#--- find_disk_size: finds a usage of the given disk                                         ---
#-----------------------------------------------------------------------------------------------

def find_disk_size(dName):
    """
    this function finds a usage of the given disk
    Input:   dName --- the name of the disk
    Output:  percent -- the percentage of the disk usage

    """
    cmd  = 'df -k ' + dName + ' > '  + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    cmd = 'rm -rf  ' + zspace
    os.system(cmd)

    percent = 0
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        try:
            float(atemp[1])
            for test in atemp:
                m = re.search('%', test)
                if m is not None:
                    btemp = re.split('\%', test)
                    percent = btemp[0]                      #---- disk capacity in percent (%)
        except:
            pass

    return int(round(float(percent)))

#-----------------------------------------------------------------------------------------------
#--- send_mail: sending a warning emil----------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def send_mail(line):
    """
    this function sends out a warning email
    Input: line (containing a waring)
    Output: email 
    """
    f = open(zspace, 'w')
    f.write('-----------------------\n')
    f.write('  Disk Space Warning:  \n')
    f.write('-----------------------\n\n')
    f.write(line)
    f.close()

#    cmd = 'cat ' + zspace + ' |mailx -s\"Subject: Disk Space Warning\n\" isobe\@head.cfa.harvard.edu  brad\@head.cfa.harvard.edu swolk\@head.cfa.harvard.edu'
    cmd = 'cat ' + zspace + ' |mailx -s\"Subject: Disk Space Warning\n\" isobe\@head.cfa.harvard.edu'
    os.system(cmd)
    cmd = 'rm -rf ' + zspace
    os.system(cmd)


#-----------------------------------------------------------------------------------------------
#--- update_datatable: appends newest data to disk space data table                          ---
#-----------------------------------------------------------------------------------------------

def update_datatable(per0, per1, per2, per3, per4, per5, per6, per7, per8):
    """
    this function appends the newest data to the disk space data table
    Input: per0 ... per5: new measures for each disk. currently per3 is empty
    Output: <data_out>/disk_space_data (updated)
    """

#
#--- find out today's date in Local time frame
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
    dom   = round(dom, 3)
#
#--- today's data
#
    line  = str(dom) + '\t' + str(per0) + '\t' + str(per1) + '\t' + str(per2) + '\t' + str(per4) + '\t' + str(per5) + '\t' + str(per6) + '\t' + str(per7) + '\t' + str(per8) + '\t'
#
#--- append to the data table
#
    file = data_out + 'disk_space_data'
    f    = open(file, 'a')
    f.write(line)
    f.write("\n")
    f.close()


#-----------------------------------------------------------------------------------------------
#---historyPlots: plots historical trend of disk usages                                      ---
#-----------------------------------------------------------------------------------------------

def historyPlots():
    """
    this function plots histrical trends of disk usages
    Input: no, but read from <data_out>/disk_space_data
    Output: disk_space1.png / disk_space2.png
    """
#
#--- read data
#
    file = data_out + 'disk_space_data'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    time   = []
    space0 = []         #--- /data/mta/
    space1 = []         #--- /data/mta1/
    space2 = []         #--- /data/mta2/
    space4 = []         #--- /data/mta4/
    space5 = []         #--- /data/swolk/
    space6 = []         #--- /data/mays/
    space7 = []         #--- /data/mta_www/
    space8 = []         #--- /proj/rac/ops/

    ochk   = 0
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        val = float(atemp[0])
        if val > ochk:
            ochk = val
            time.append(val)
            space0.append(float(atemp[1]))
            space1.append(float(atemp[2]))
            space2.append(float(atemp[3]))
            space4.append(float(atemp[4]))
            space5.append(float(atemp[5]))
            space6.append(float(atemp[6]))
            space7.append(float(atemp[7]))
            space8.append(float(atemp[8]))
        else:
            continue
#
#---  x axis plotting range
# 
    xmin  = min(time)
    xmax  = max(time)

    xdiff = xmax - xmin
    xmin  = int(xmin - 0.1 * xdiff)
    xmin  = 1000                                #---- the earliest data starts DOM ~ 1000
    xmax  = int(xmax + 0.1 * xdiff)
#
#--- plot first three
#
    xSets = []
    ySets = []
    for i in range(0, 3):
        xSets.append(time)

    ySets.append(space0)
    ySets.append(space7)
    ySets.append(space4)
    xname = 'Time (DOM)'
    yname = 'Capacity Filled (%)'
    entLabels = ['/data/mta/', '/data/mta_www/', '/data/mta4/']

    plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels)

    cmd = 'mv out.png ' + fig_out + 'disk_space1.png'
    os.system(cmd)

#
#--- plot the rest
#
    xSets = []
    ySets = []
    for i in range(0, 2):
        xSets.append(time)

    ySets.append(space6)
    ySets.append(space5)
    xname = 'Time (DOM)'
    yname = 'Capacity Filled (%)'
    entLabels = ['/data/mays/', '/data/swolk/']

    plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels)

    cmd = 'mv out.png ' + fig_out + 'disk_space2.png'
    os.system(cmd)


    xSets = []
    ySets = []
    for i in range(0, 2):
        xSets.append(time)

    ySets.append(space1)
    ySets.append(space2)
    xname = 'Time (DOM)'
    yname = 'Capacity Filled (%)'
    entLabels = ['/data/mta1/', '/data/mta2/']

    plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels)

    cmd = 'mv out.png ' + fig_out + 'disk_space3.png'
    os.system(cmd)


    xSets = []
    ySets = []
    for i in range(0, 2):
        xSets.append(time)

    ySets.append(space8)
    xname = 'Time (DOM)'
    yname = 'Capacity Filled (%)'
    entLabels = ['/proj/rac/ops/']

    plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels)

    cmd = 'mv out.png ' + fig_out + 'disk_space4.png'
    os.system(cmd)


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
    plt.savefig('out.png', format='png', dpi=140)


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
    plt.savefig('out.png', format='png', dpi=140)


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

check_disk_space()
