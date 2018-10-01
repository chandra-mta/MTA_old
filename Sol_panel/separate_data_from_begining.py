#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       separate_data_from_begining.py: create angle separated data file from begining          #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Jul 03, 2018                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
import pyfits
import unittest
from datetime import datetime
from time import gmtime, strftime, localtime
import Chandra.Time
import Ska.engarchive.fetch as fetch
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; punlearn dataseeker  ', shell='tcsh')
#
#--- plotting routine
#
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
path = '/data/mta/Script/Sol_panel/Scripts/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a couple of lists
#
angle_list = [40, 60, 80, 100, 120, 140, 160]
header     = 'time\tsuncent\ttmysada\ttpysada\ttsamyt\ttsapyt\ttfssbkt1\ttfssbkt2\ttpc_fsse\telbi\telbv\tobattpwr\tohrmapwr\toobapwr'


#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def run_data_sepration():

    cmd = 'rm -rf ' + data_dir + 'solar_panne_angle_*'
    os.system(cmd)
#
#--- read the data
#
    ifile = data_dir + "solar_panel_all_data"
    data  = read_data_file(ifile, spliter = '\s+', skip='#')
    #for k in range(0, len(data)):
    #    data[k] = data[k][2:]

    separate_data_into_angle_step(data, 0)

#---------------------------------------------------------------------------------------
#-- separate_data_into_angle_step: separate a full data set into several angle interval data sets 
#---------------------------------------------------------------------------------------

def separate_data_into_angle_step(data, tstart=0):
    """
    separate a full data set into several angle interval data sets
    input:  data    --- data matrix of <col numbers> x <data length>
            tstart  --- starting time in seconds from 1998.1.1
    output: <data_dir>/solar_panel_angle_<angle>
    """
#
#--- set a few things
#
    alen  = len(angle_list)             #--- the numbers of angle intervals
    clen  = len(data)                   #--- the numbers of data columns
    save  = []                          #--- a list of lists to sve the data
    for k in range(0, alen):
        save.append([])
#
#--- go through all time entries, but ignore time before tstart
#
    for k in range(0, len(data[0])):
        if data[0][k] < tstart:
            continue

        for m in range(0, alen):
#
#--- set angle interval; data[1] is the column to keep sun center angle
#
            abeg = angle_list[m]
            aend = abeg + 20
            if (data[1][k] >= abeg) and (data[1][k] < aend):
                line = create_data_line(data, clen, k)
                save[m].append(line)
                break
#
#--- create/update the data file for each angle interval
#
    for k in range(0, alen):
        outname = data_dir + 'solar_panel_angle_' + str(angle_list[k])

        if os.path.isfile(outname):
            fo  = open(outname, 'a')
#
#--- if this is the first time, add the header
#
        else:
            fo   = open(outname, 'w')
            line = "#" + header + '\n'
            line = line + '#' + '-'*120 + '\n'
            fo.write(line)
#
#--- print the data
#
        if len(save[k]) == 0:
            continue

        for ent in save[k]:
            fo.write(ent)
            fo.write('\n')
        fo.close()

#---------------------------------------------------------------------------------------
#-- create_data_line: create output data line                                         --
#---------------------------------------------------------------------------------------

def create_data_line(data, clen, k):
    """
    create output data line
    input:  data    --- data matrix of clen x len(data[0])
    output: line    --- a line of data of clen elements
    """

    line = str(data[0][k])
    for m in range(1, clen):
        line = line + '\t' + str(data[m][k])

    return line

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def read_data_file(ifile, spliter = '', remove=0, skip=''):
    """
    read a data file
    input:  infile  --- input file name
            spliter --- if you want to a list of lists of data, provide spliter, e.g.'\t+'
            remove  --- the indicator of whether you want to remove the data after read it. default=0: no
    output: data    --- either a list of data lines or a list of lists
    """


    try:
        f    = open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    except:
        return []

    if remove > 0:
        mcf.rm_file(ifile)

    if spliter != '':
        atemp = re.split(spliter, data[0])
        alen  = len(atemp)
        save  = []
        for k in range(0, alen):
            save.append([])

        for ent in data:
            if skip !='':
                if ent[0] == skip:
                    continue
            atemp = re.split(spliter, ent)
            for k in range(0, alen):
                try:
                    val = float(atemp[k])
                except:
                    val = atemp[k].strip()

                save[k].append(val)
        return save
    else:
        return data

#---------------------------------------------------------------------------------------

if __name__ == '__main__':

    run_data_sepration()
