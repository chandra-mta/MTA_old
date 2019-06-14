#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################
#                                                                                   #
#      create_ephin_leak_html_page.py: create tephin - eph quantity page            #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 21, 2019                                               #
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
import create_html_suppl        as chs
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

web_address = 'https://' + web_address

#-----------------------------------------------------------------------------------
#-- create_ephin_leak_html_page: create ephin - eph quantity page                  --
#-----------------------------------------------------------------------------------

def create_ephin_leak_html_page():
    """
    create ephin - eph quantity page
    input: none, but read from <house_keeping>/msid_list__eph_tephin
    output: <web_dir>/<group name>/<msid>/<msid>_eph_tephin.html
    """
#
#--- get dictionary of msid<-->unit and msid<-->description
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read msid lists
#
    ifile = house_keeping + 'msid_list_eph_tephin'
    data  = mcf.read_data_file(ifile)
#
#--- read template
#
    template = chs.read_template('slide_template.html')

    tail_part= chs.read_template('html_close')

    tail_part = tail_part.replace("#JAVASCRIPT#", '')
#
#--- for each msid, create a html page
#
    msid_list  = []
    group_list = []
    g_dict     = {}
    gchk       = ''
    m_save     = []

    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        group = atemp[1]
#
#--- we don't need to compare with itself
#
        if msid == '5ephint':
            continue

        msid_list.append(msid)
        group_list.append(group)
#
#--- create group name <---> msid list dictionary
#
        if gchk == "":
                gchk = group
                m_save.append(msid)
        
        elif gchk != group:
                g_dict[gchk] = m_save
                m_save = [msid]
                gchk   = group
        
        else:
                m_save.append(msid)

        if len(m_save) > 0:
            g_dict[group] = m_save


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
                line1 = line1 + '\t<span class="dot" onclick="currentSlide(' 
                line1 = line1 + str(k+1) +')"></span>'
                line1 = line1 + str(year_list[k]) + '\n\t</th>\n'
    
                if (k < tot) and ((year_list[k] + 1) % 10 == 0):
                    line1 = line1 + '\t</tr>\n\t<tr>\n'
#
#--- sliding figures
#
            line2 = '<div class="slideshow-container">\n'
    
            for k in range(0, tot):
                line2 = line2 + '\t<div class="mySlides xfade">\n'
                line2 = line2 + '\t\t<div class="numbertext">' + str(k+1) 
                line2 = line2 + '/' + str(tot) + '</div>\n'
                line2 = line2 + '\t\t<img src="' +  web_address + 'Eleak/'
                line2 = line2 + msid.capitalize() + '/Plots/' + msid + '_' 
                line2 = line2 + ltype +  '_' + str(year_list[k]) 
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
            hpage = hpage.replace('#GROUP#',  group.capitalize())
            hpage = hpage.replace('#Group#', 'Eleak/'  )
            hpage = hpage.replace('#GROUP_L#',  group.lower())
            hpage = hpage.replace('#LTYPE#',  ltype.lower())
            hpage = hpage.replace('#DOT_SELECT#',   line1)
            hpage = hpage.replace('#SLID_FIGURES#', line2)
            hpage = hpage.replace('Angle to Sun Center', 'Tephin')
            hpage = hpage.replace('mta_trending_sun_angle_main', 'mta_trending_eph_tephin_main')
            hpage = hpage.replace('_long_sun_angle', '_eph_tephin')
            hpage = hpage.replace('Sun Angle', 'Tephin')

#
#--- print out the html page
#
            oname = web_dir + 'Eleak/' + msid.capitalize() + '/' 
            if not os.path.isdir(oname):
                cmd = 'mkdir ' + oname
                os.system(cmd)

            oname = oname   + msid  + '_' +ltype+ '_eph_tephin.html'
    
            hpage = hpage + tail_part

            try:
                with  open(oname, 'w') as fo:
                    fo.write(hpage)

            except:
                print("cannot create: " + oname)
#
#--- create the mid level (group level) web pages
#
    head_part = chs.read_template('html_head')
    
    head_part = head_part.replace("#MSID#", 'Tephin - EPH')
    head_part = head_part.replace("#JAVASCRIPT#", '')

    for group in group_list:

        msids = g_dict[group]

        for mtype in ['mid', 'min', 'max']:

            line = ''
            if mtype == 'mid':
                mdisc = 'Mean'
            else:
                mdisc = mtype.capitalize()

            line = line + '<h2>' + group.upper() + ' --- ' + mdisc +  '</h2>\n'

            line = line + '<div style="float:right;padding-right:50px;">'
            line = line + '<a href="' + web_address + 'mta_trending_eph_tephin_main.html">'
            line = line + '<b>Back to Top</b></a>\n'
            line = line + '</div>\n'

            line = line + '<table border=1 cellpadding=2 cellspacing=1><tr>\n'
            tlink = web_address +  'Eleak/' + group.lower()
            if mtype == 'mid':
                line = line + '<th>Mean</th>\n'
                line = line + '<th><a href="' + tlink + '_max_eph_tephin.html">Max</a></th>\n'
                line = line + '<th><a href="' + tlink + '_min_eph_tephin.html">Min</a></th>\n'
            elif mtype == 'max':
                line = line + '<th><a href="' + tlink + '_max_eph_tephin.html">Mean</a></th>\n'
                line = line + '<th>Max</th>\n'
                line = line + '<th><a href="' + tlink + '_min_eph_tephin.html">Min</a></th>\n'
            elif mtype == 'min':
                line = line + '<th><a href="' + tlink + '_min_eph_tephin.html">Mean</a></th>\n'
                line = line + '<th><a href="' + tlink + '_max_eph_tephin.html">Max</a></th>\n'
                line = line + '<th>Min</th>\n'
            line = line + '</tr></table>\n'
            line = line + '<br /><br />\n'

            line = line + '<p>Please click a msid to open the tephin - eph page.</p>\n'

            line = line + '<table border=1 cellpadding=2 cellspacing=1 '
            line = line + 'style="margin-left:auto;margin-right:auto;text-align:center;">\n'
            line = line + '<tr><th>MSID</th><th>Description</th></tr>\n'

            for msid in msids:
                pfile = web_address +  'Eleak/' + msid.capitalize() + '/' + msid 
                pfile = pfile + '_' + mtype + '_eph_tephin.html'
                try:
                    dtext = ddict[msid]
                except:
                    dtext = ''

                line = line + '<tr><th><a href="' + pfile + '">' + msid + '</a></th>\n'
                line = line + '<td style="text-align:center;">' + dtext + '</td></tr>'

            line = line + '</table>\n'

            oline = head_part + line + tail_part

            oname = web_dir + 'Eleak/' +  group.lower() + '_' +  mtype  + '_eph_tephin.html'
            with  open(oname, 'w') as fo:
                fo.write(oline)

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    create_ephin_leak_html_page()
