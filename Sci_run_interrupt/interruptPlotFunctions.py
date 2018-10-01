#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################
#                                                                                                       #
#       interruptPlotFunctions.py: a collections of python scripts related to science run interruption  #
#                                  ploting routines                                                     #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               last update: Apr  30, 2013                                                              #
#                                                                                                       #
#########################################################################################################

import math
import re
import sys
import os
import string
import numpy as np
#
#--- pylab plotting routine related modules
#
from pylab import *
if __name__ == '__main__':

    mpl.use('Agg')

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

#
#--- reading directory list
#

path = '/data/mta/Script/Interrupt/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a privte folder to python directory
#

sys.path.append(bin_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv

#--------------------------------------------------------------------
#--- plotRadZone: plotting radiation zone marker                  ---
#--------------------------------------------------------------------

def plotRadZone(radZone, xmin, xmax, ymin):

    "For a given radiation zone information, plotting range and ymin of the plotting area, mark radiation zones on the plot"

    for ent in radZone:
        zone = re.split(':', ent)               #--- format is e.g., 90.12321:90.9934 (start and end in ydate)

        zstart = float(zone[0])
        zstop  = float(zone[1])

        if zstart >= xmin and zstart < xmax:
            pstart = zstart
            if zstop < xmax:
                pstop = zstop
            else:
                pstop = xmax

            pstart += 0.02
            pstop  -= 0.02
            xzone = [pstart, pstop]
            yzone = [ymin, ymin]
            plt.plot(xzone, yzone, color='purple', lw=8)

        elif zstart < xmin and zstop> xmin:
            pstart = xmin
            pstop  = zstop

            pstart += 0.02
            pstop  -= 0.02
            xzone = [pstart, pstop]
            yzone = [ymin, ymin]
            plt.plot(xzone, yzone, color='purple', lw=8)



#--------------------------------------------------------------------
#--- readRadZone: read radiation zone period data                ----
#--------------------------------------------------------------------

def readRadZone(event):

    "read radiation zone data from 'rad_zone_list. Format: 20120313    (4614.2141112963,4614.67081268519):(4616.8308428125,4617.31948864583):.."

    file = house_keeping + 'rad_zone_list'

    f = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    
    radZone = []

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        if atemp[0] == event:
            btemp = re.split(':', atemp[1])
            for line in btemp:
                ctemp = re.split('\(', line)
                dtemp = re.split('\)', ctemp[1])
                etemp = re.split('\,', dtemp[0])

                (year1, ydate1) = tcnv.DOMtoYdate(float(etemp[0]))   #--- function from convertTimeFormat.py: change dom to ydate
                (year2, ydate2) = tcnv.DOMtoYdate(float(etemp[1]))   
                if year1 == year2:
                    line = str(ydate1) + ':' + str(ydate2)
                    radZone.append(line) 
                else:
                    chk = 4.0 * int(0.25 * year1)
                    if chk == year1:
                        base = 366
                    else:
                        base = 365

                    temp = ydate2 + base
                    line = str(ydate1) + ':' + str(temp)
                    radZone.append(line)

    return radZone


#--------------------------------------------------------------------------
#--- yTixs: create a y tix label skipping every other interger           --
#--------------------------------------------------------------------------

def makeTixsLabel(min, max):

    'for given min and max, return a list of tix label skipping every other integer.'

    j = 1
    tixRow = []
    for i in range(int(min), int(max+1)):
        if j % 2 == 0:
            tixRow.append(i)
        else:
            tixRow.append('')
        j += 1

    return tixRow










