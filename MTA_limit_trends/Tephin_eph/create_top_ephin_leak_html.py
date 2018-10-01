#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################
#                                                                                   #
#      create_top_ephin_leak_html.py: creating the top ephin-eph   html page        #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               last update: Feb 02, 2018                                           #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import random
import math
import sqlite3
import unittest
import time
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
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
import convertTimeFormat        as tcnv #---- converTimeFormat contains MTA time conversion routines
import mta_common_functions     as mcf  #---- mta common functions

#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

web_address = 'https://' + web_address

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def create_top_html():
    dline = '<th colspan=4 class="blue">Full Range</th>\n'
    """
    dline = dline + '<th colspan=4 class="blue">Past 5 Years</th>\n'
    dline = dline + '<th colspan=4 class="blue">Past 1 Year</th>\n'
    dline = dline + '<th colspan=4 class="blue">Quarterly</th>\n'
    dline = dline + '<th colspan=4 class="blue">Weekly</th>\n'
    """
    dline = dline + '</tr>\n'

    """
    gfile = house_keeping + 'sub_html_list_eph_tephin'
    f     = open(gfile, 'r')
    mdata = [line.strip() for line in f.readlines()]
    f.close()

    ms_dict = {}
    for ent in mdata:
        atemp   = re.split('::', ent)
        rout    = atemp[1].replace('_plot.html', '')
        ms_list = re.split(':',  rout)
        ms_dict[atemp[0]] = ms_list
    """

    gfile = house_keeping + 'group_descriptions_eph_tephin'
    f     = open(gfile, 'r')
    gdata = [line.strip() for line in f.readlines()]
    f.close()

    g_list  = []
    gn_dict = {}
    gd_dict = {}
    gn_list = []
    g_disc  = []
    

    for ent in gdata:
        mc  = re.search('#', ent)
        if mc is not None:
            ent = ent.replace('#', '')
            g_list.append(ent)
            gname = ent
        elif ent == "":
            gn_dict[gname] = gn_list
            gd_dict[gname] = g_disc
            gn_list = []
            g_disc  = []

        else:
            atemp = re.split('::', ent)
            gn_list.append(atemp[0])
            g_disc.append(atemp[1])


    mlist = ('mid', 'min', 'max')
    mname = ('Avg', 'Min', 'Max')


    for gval in g_list:
        group_list  = gn_dict[gval]
        discip_list = gd_dict[gval]

        line = line + '<tr><th class="blue">' + gval + '</th>\n'
        line = line + dline

        for k in range(0, len(group_list)):
            line = line + '<tr>\n'
            line = line + '<th>' + discip_list[k] + '</th</tr>\n'
            gnam = group_list[k].lower()
            
            mpart = '<td><a href="./' + 'Eleak/' + gnam + '_'
    
            for m in range(0, 3):
                line = line + mpart +  mlist[m]  
                line = line + '_eph_tephin.html">' + mname[m] + '</a></td>\n'

            line = line + '</tr>\n'

        line = line + '<tr><th colspan=4>&#160;</th></tr>\n\n'

    line = line + '</tr>\n'

    jfile    = house_keeping + '/Templates/java_script_deposit'
    f        = open(jfile, 'r')
    j_script = f.read()
    f.close()

    template = house_keeping + 'Templates/top_header'
    f        = open(template, 'r')
    page     = f.read()

    page     = page.replace('#JAVASCRIPT#', j_script)
    page     = page.replace('#TITLE#', 'EPHIN Rates/Leakage Current vs. Temperature  Trend')
    page     = page.replace('#TABLE#', line)
    page     = page.replace('#EXPLANATIONS#', '')
    page     = page.replace('how_to_create_plots.html', 'how_to_create_eph_tephin.html')

    page     = page.replace('#OTHER_H#', 'mta_trending_main.html')
    page     = page.replace('#OTHER#', 'Open MSID Trending Page')

    page     = page.replace('#OTHER_H2#', '')
    page     = page.replace('#OTHER2#', '')

    page     = page.replace('#OTHER_H3#', '')
    page     = page.replace('#OTHER3#', '')

    page     = page.replace('#PAGE_EXP#', 'how_to_create_eph_tephin.html')

    etext    = '<p>This page shows the relation between 5ephin (ephin senosr housing temperature) ' 
    etext    = etext + 'and Ephin temperatures, voltages, and key background rates.</p>\n'
    etext    = etext + ' <p>The data are divided into one-year length to show the possible '
    etext    = etext + 'time evolution of the relation between the 5ephin and the msid.</p>\n'

    page     = page.replace('<!-- EXTRA -->', etext)

    template = house_keeping + 'Templates/html_close'
    f        = open(template, 'r')
    end_line = f.read()

    page     = page + end_line



    #outfile  = web_dir + 'test.html'
    outfile  = web_dir + 'mta_trending_eph_tephin_main.html'
    fo       = open(outfile, 'w')
    fo.write(page)
    fo.close()


#----------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_top_html()


