#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#######################################################################################
#                                                                                     #
#          create_hrcveto_eph_page.py: create shevart - eph key plot page             #
#                                                                                     #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                 #
#                                                                                     #
#           last update: May 20, 2019                                                 #
#                                                                                     #
#######################################################################################

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
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

web_address = 'https://' + web_address
#
#--- data from ephkey
#
msid_list = ['scct0', 'sce1300', 'sce150', 'sce3000', 'scint']
group = 'Hrcveto_eph'

#-----------------------------------------------------------------------------------
#-- create_hrcveto_eph_page: create ephin - eph quantity page                  --
#-----------------------------------------------------------------------------------

def create_hrcveto_eph_page():
    """
    create ephin - eph quantity page
    input: none
    output: <web_dir>/<group name>/<msid>/<msid>_hrcveto_eph.html
    """
#
#--- get dictionary of msid<-->unit and msid<-->description
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read template
#
    tfile    = house_keeping + 'Templates/slide_template.html'
    with  open(tfile, 'r') as f:
        template = f.read()

    tfile     = house_keeping + 'Templates/html_close'
    with  open(tfile, 'r') as f:
        tail_part = f.read()
#
#--- for each msid, create a html page
#
    for msid in msid_list:

        for ltype in ['mid', 'min', 'max']:
    
            this_year = int(float(time.strftime("%Y", time.gmtime())))
            year_list = range(1999, this_year+1)
    
            tot   = len(year_list)
#
#--- dot click table
#
            line1 = '<tr>\n'
            for k in range(1, tot):
                line1 = line1 + '\t<th>\n'
                line1 = line1 + '\t<span class="dot" onclick="currentSlide(' + str(k+1) +')"></span>'
                line1 = line1 + str(year_list[k]) + '\n\t</th>\n'
    
                if (k < tot) and ((year_list[k] + 1) % 10 == 0):
                    line1 = line1 + '\t</tr>\n\t<tr>\n'
#
#--- sliding figures
#
            line2 = '<div class="slideshow-container">\n'
    
            for k in range(0, tot):
                line2 = line2 + '\t<div class="mySlides xfade">\n'
                line2 = line2 + '\t\t<div class="numbertext">' + str(k+1) + '/' + str(tot) + '</div>\n'
                line2 = line2 + '\t\t<img src="' +  web_address + 'Hrcveto_eph/'
                line2 = line2 + msid.capitalize() + '/Plots/' + msid + '_' + ltype +  '_' + str(year_list[k]) 
                line2 = line2 + '.png" style="width:100%">\n'
                line2 = line2 + '\t\t<!--<div class="text"> Text</div> -->\n'
                line2 = line2 + '\t</div>\n\n'
    
            line2 = line2 + '\t<a class="prev" onclick="plusSlides(-1)">&#10094;</a>\n'
            line2 = line2 + '\t<a class="next" onclick="plusSlides(1)">&#10095;</a>\n'
            line2 = line2 + '</div>\n'
#
#--- replace the variable parts
#
            hpage = template
            hpage = hpage.replace('#MSID#',  msid.upper())
            hpage = hpage.replace('#MSID_L#',  msid.lower())
            hpage = hpage.replace('#GROUP#',  ltype.capitalize())
            hpage = hpage.replace('#Group#', 'Hrcveto_eph/'  )
            hpage = hpage.replace('#GROUP_L#',  group.lower())
            hpage = hpage.replace('#LTYPE#',  ltype.lower())
            hpage = hpage.replace('#DOT_SELECT#',   line1)
            hpage = hpage.replace('#SLID_FIGURES#', line2)
            hpage = hpage.replace('Angle to Sun Center', 'SHEVART')
            hpage = hpage.replace('mta_trending_sun_angle_main', 'mta_trending_hrcveto_eph_main')
            hpage = hpage.replace('_long_sun_angle', '_hrcveto_eph')
            hpage = hpage.replace('Sun Angle', 'Shevart')

            hpage = hpage + tail_part
#
#--- print out the html page
#
            oname = web_dir + 'Hrcveto_eph/' + msid.capitalize() + '/' 
            if not os.path.isdir(oname):
                cmd = 'mkdir ' + oname
                os.system(cmd)

            oname = oname   + msid  + '_' +ltype+ '_hrcveto_eph.html'
    
            try:
                with  open(oname, 'w') as fo:
                    fo.write(hpage)
            except:
                print("cannot create: " + oname)
#
#--- create the mid level (group level) web pages
#
    hfile     = house_keeping + 'Templates/html_head'
    with  open(hfile, 'r') as f:
        head_part = f.read()
    
    head_part = head_part.replace("#MSID#", 'Shevart - Eph Rate')
    head_part = head_part.replace("#JAVASCRIPT#", '')

    for mtype in ['mid', 'min', 'max']:

        line = ''
        if mtype == 'mid':
            mdisc = 'Mean'
        else:
            mdisc = mtype.capitalize()

        line = line + '<h2>' + group.upper() + ' --- ' + mdisc +  '</h2>\n'

        line = line + '<div style="float:right;padding-right:50px;">'
        line = line + '<a href="' + web_address + 'how_to_create_hrcveto_eph.html">How the plots are created</a><br />\n'
    
        line = line + '<a href="' + web_address + 'mta_trending_hrcveto_eph_main.html"><b>Back to Top</b></a>\n'
        line = line + '</div>\n'

        line = line + '<table border=1 cellpadding=2 cellspacing=1><tr>\n'
        tlink = web_address +  'Hrcveto_eph/' + group.lower()
        if mtype == 'mid':
            line = line + '<th>Mean</th>\n'
            line = line + '<th><a href="' + tlink + '_max_hrcveto_eph.html">Max</a></th>\n'
            line = line + '<th><a href="' + tlink + '_min_hrcveto_eph.html">Min</a></th>\n'
        elif mtype == 'max':
            line = line + '<th><a href="' + tlink + '_mid_hrcveto_eph.html">Mean</a></th>\n'
            line = line + '<th>Max</th>\n'
            line = line + '<th><a href="' + tlink + '_min_hrcveto_eph.html">Min</a></th>\n'
        elif mtype == 'min':
            line = line + '<th><a href="' + tlink + '_mid_hrcveto_eph.html">Mean</a></th>\n'
            line = line + '<th><a href="' + tlink + '_max_hrcveto_eph.html">Max</a></th>\n'
            line = line + '<th>Min</th>\n'
        line = line + '</tr></table>\n'
        line = line + '<br /><br />\n'

        line = line + '<p>This page shows the replation between  '
        line = line + '<a href="https://cxc.cfa.harvard.edu/mta/MSID_Trends/Hrcveto/Shevart/shevart_mid_static_long_plot.html">shevart</a>\n'
        line = line + '(shield events) and ephin key rates.</p>\n'
        line = line + '<p>The data are divided into one-year length to show the possible time evolution\n'
        line = line + 'of the relation between the shevart and the msid.</p>\n'

        line = line + '<table border=1 cellpadding=2 cellspacing=1 style="margin-left:auto;margin-right:auto;text-align:center;">\n'
        line = line + '<tr><th>MSID</th><th>Description</th></tr>\n'

        for msid in msid_list:
            pfile = web_address +  'Hrcveto_eph/' + msid.capitalize() + '/' + msid 
            pfile = pfile + '_' + mtype + '_hrcveto_eph.html'
            try:
                dtext = ddict[msid]
            except:
                dtext = ''

            line = line + '<tr><th><a href="' + pfile + '">' + msid + '</a></th>\n'
            line = line + '<td style="text-align:center;">' + dtext + '</td></tr>'

        line = line + '</table>\n'

        oline = head_part + line + tail_part

        oname = web_dir + 'Hrcveto_eph/' +  group.lower() + '_' +  mtype  + '_hrcveto_eph.html'
        with  open(oname, 'w') as fo:
            fo.write(oline)
#
#--- update the top page
#
    top_template = house_keeping + 'Templates/mta_trending_hrcveto_eph_main_template'
    with  open(top_template, 'r') as f:
    top_page     = f.read()
    
    top_page     = top_page + tail_part

    top_out      = web_dir + 'mta_trending_hrcveto_eph_main.html'
    with  open(top_out, 'w') as fo:
        fo.write(top_page)

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    create_hrcveto_eph_page()
