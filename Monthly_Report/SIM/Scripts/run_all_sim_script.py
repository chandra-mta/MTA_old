#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #  
#       run_all_sim_script.py:  run all sim plot related scripts                            #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Sep 10, 2014                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest

import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines
#
#--- reading directory list
#
path = '/data/mta/Script/Month/SIM/house_keeping/dir_list_py'

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
import aorwspd_plot         as aor
import grating_plot         as grat
import sim_plot             as sim


#-----------------------------------------------------------------------------------------
#-- plot_sim_movement: read tsc and fa data and plot their cummulatinve movement        --
#-----------------------------------------------------------------------------------------

def run_all_sim_script():

    grat.plot_grat_movement()
    sim.plot_sim_movement()

    [year, month, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime()
    month -= 1
    if month < 1:
        month = 12
        year -= 1

    aor.plot_aorwspd(year, month)

#-----------------------------------------------------------------------------------------
#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines


if __name__ == '__main__':

    run_all_sim_script()



