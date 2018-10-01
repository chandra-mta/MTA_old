#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#           create_gyro_drift_ind_page.py: create gryro drift movment html pages                #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Jul 19, 2018                                                       #
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
path = '/data/mta/Script/Gyro/Scripts/house_keeping/dir_list'

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
from kapteyn import kmpfit
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- some data
#
catg_list    = ['roll', 'pitch', 'yaw']


#---------------------------------------------------------------------------------------
#-- create_gyro_drift_ind_page: create gryro drift movment html pages                          --
#---------------------------------------------------------------------------------------

def create_gyro_drift_ind_page():
    """
    create gryro drift movment html pages
    input:  none
    output: <web_dir>/Individual_plots/<GRATING>_<ACTION>/<catg>_<grating>_<action>.html
    """
#
#--- read template
#
    tname    = house_keeping + 'drift_plot_template'
    f        = open(tname, 'r')
    template = f.read()
    f.close()
#
#--- go through all data set to create several sub html pages related to indivisual fitting resluts
#
    for catg in catg_list:
        for grating in ['hetg', 'letg']:
            for action in ['insr', 'retr']:
                ifile = data_dir + 'gyro_drift_' + catg + '_' + grating + '_' + action
                data  = read_data_file(ifile, spliter = '\s+', skip='#')

                create_html_page_for_movement(catg, grating, action, data, template)

#---------------------------------------------------------------------------------------
#-- create_html_page_for_movement: create a html page for given category, grating, and movment 
#---------------------------------------------------------------------------------------

def create_html_page_for_movement(catg, grating, action, data, template):
    """
    create a html page for given category, grating, and movment
    input:  catg        --- category (roll, pitch, yaw)
            grating     --- grating
            action      --- insr or retr
            data        --- a list of lists of data
            template    --- the html tamplate of the pages
    output: <web_dir>/Individual_plots/<GRATING>_<ACTION>/<catg>_<grating>_<action>.html
    """

    line = ''
    for k in range(0, len(data[0])):
        time  = data[0][k]
        dplot = './' + str(int(time)) +  '/deviation_'  + catg + '.png'
        gplot = './' + str(int(time)) +  '/gyro_drift_' + catg + '.png'

        line  = line + create_data_row(data, k, dplot, gplot)
#
#--- insert the data
#
    template = template.replace('#CATG#',  catg.upper())
    template = template.replace('#CATGL#', catg.lower())
    template = template.replace('#GRAT#',  grating.upper())
    template = template.replace('#ACT#',   action.upper())
    template = template.replace('#TABLE#', line)

    if action == 'insr':
        template = template.replace('#ACT2#',   'insertion')
    elif action == 'retr':
        template = template.replace('#ACT2#',   'retraction')

#
#--- output file name
#
    outdir  = web_dir + 'Individual_plots/' + grating.upper() + '_' + action.upper() + '/'
    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)

    outname = outdir  +  catg.lower() + '_' + grating.lower() + '_' + action.lower() +  '.html'
#
#--- print out the result
#
    fo      = open(outname, 'w')
    fo.write(template)
    fo.close()

#---------------------------------------------------------------------------------------
#-- create_data_row: create a table entry of given data                               --
#---------------------------------------------------------------------------------------

def create_data_row(data, k, dplot, gplot):
    """
    create a table entry of given data
    input:  data    --- a list of lists of the data
            k       --- the position of the data row
            dplot   --- the name of the derivative plot
            gplot   --- the name of the gyro drift plot
    output: line    --- the table entry
    """

    results = create_result_table(data, k)
    stime   = data[0][k]
    ltime   = Chandra.Time.DateTime(stime).date

    line    = '<tr>\n'

    line    = line + '<th style="font-size:95%;">' + ltime + '<br />(' +  str(stime) + ')</th>\n'

    line    = line + '<th>\n'
    line    = line + '<a href="javascript:WindowOpener(\'' + gplot + '\')">\n'
    line    = line + '<img src="' + gplot + '" width=90%">\n'
    line    = line + '</a></th>\n'

    line    = line + '<th>\n'
    line    = line + '<a href="javascript:WindowOpener(\'' + dplot + '\')">\n'
    line    = line + '<img src="' + dplot + '" width=90%">\n'
    line    = line + '</a></th>\n'

    line    = line + '<td>' + results + '</td>\n'
    line    = line + '</tr>\n'

    return line

#---------------------------------------------------------------------------------------
#-- create_result_table: create the result table                                      --
#---------------------------------------------------------------------------------------

def create_result_table(data, k):
    """
    create the result table
    input:  data    --- a list of lists of fitting results
            k       --- the position of the data row
    output: line    --- a html element
    """
#
#--- create data table
#
    line = '<table broder=0>\n'
    line = line + '<tr><th style="text-align:left;">Before: </th><td>'         + str(data[1][k])  + '</td></tr>\n'
    line = line + '<tr><th style="text-align:left;">During: </th><td>'         + str(data[2][k])  + '</td></tr>\n'
    line = line + '<tr><th style="text-align:left;">After:  </th><td>'         + str(data[3][k])  + '</td></tr>\n'

    line = line + '<tr><th style="text-align:left;">Before/During:</th><td>  ' + str(data[4][k])  + '</td></tr>\n'
    line = line + '<tr><th style="text-align:left;">After/During: </th><td>  ' + str(data[5][k])  + '</td></tr>\n'
    line = line + '<tr><th style="text-align:left;">Before/After: </th><td>  ' + str(data[6][k])  + '</td></tr>\n'
    line = line + '<tr><th>Duration:     </th><td>  ' + str(data[7][k])  + ' sec</td></tr>\n'
    line = line + '</table>\n'

    return line

#---------------------------------------------------------------------------------------
#-- read_data_file: read a data file                                                  --
#---------------------------------------------------------------------------------------

def read_data_file(ifile, spliter = '', remove=0, skip=''):
    """
    read a data file
    input:  infile  --- input file name
            spliter --- if you want to a list of lists of data, provide spliter, e.g.'\t+'
            remove  --- the indicator of whether you want to remove the data after read it. default=0: no
            skip    --- whether skip the line if marked. default:'' --- don't skip
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
            if skip != '':
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

if __name__ == "__main__":

    create_gyro_drift_ind_page()
