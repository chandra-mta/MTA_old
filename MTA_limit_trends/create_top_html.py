#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################
#                                                                                   #
#       create_top_html.py: creating the top html page                              #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               last update: Feb 27, 2018                                           #
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
import envelope_common_function as ecf  #---- envelope common functions
#
#---  get dictionaries of msid<-->unit and msid<-->description
#
[udict, ddict] = ecf.read_unit_list()


#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
web_address = 'https://' + web_address

#-----------------------------------------------------------------------------------
#-- create_top_html: create the top html page                                     --
#-----------------------------------------------------------------------------------

def create_top_html():
    """
    create the top html page
    input:  none
    output: <web_dir>/mta_trending_main.html
    """
    dline = '<th colspan=4 class="blue">Full Range</th>\n'
    dline = dline + '<th colspan=4 class="blue">Past 5 Years</th>\n'
    dline = dline + '<th colspan=4 class="blue">Past 1 Year</th>\n'
    dline = dline + '<th colspan=4 class="blue">Quarterly</th>\n'
    dline = dline + '<th colspan=4 class="blue">Weekly</th>\n'
    dline = dline + '</tr>\n'
#
#--- read descriptions of groups and create dictionaries etc
#
    gfile = house_keeping + 'group_descriptions'
    gdata = ecf.read_file_data(gfile)

    g_list  = []
    gn_dict = {}
    gd_dict = {}
    gn_list = []
    g_disc  = []
    p_dict  = {}
    

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

            p_dict[atemp[0].lower()] = atemp[1]

    mlist = ('mid', 'min', 'max')
    mname = ('Avg', 'Min', 'Max')
#
#--- go through each main group
#
    line = ''
    for gval in g_list:
        group_list  = gn_dict[gval]
        discip_list = gd_dict[gval]

        line = line + '<tr><th class="blue">' + gval + '</th>\n'
        line = line + dline

        for k in range(0, len(group_list)):
            gnam = group_list[k].lower()

            if gnam  == 'hrcveto_eph':
                continue

            line = line + '<tr>\n'
            line = line + '<th>' + discip_list[k] + '</th</tr>\n'
            
            mpart = '<td><a href="./' + gnam.capitalize() + '/' + gnam + '_'
    
            for ltype in ('long', 'five', 'one', 'short', 'week'):
                for m in range(0, 3):
                    line = line + mpart +  mlist[m] + '_static_' + ltype 
                    line = line + '_main.html">' + mname[m] + '</a></td>\n'
                line = line + '<td class="blue"></td>\n'

            line = line + '</tr>\n'

        line = line + '<tr><th colspan=21>&#160;</th></tr>\n\n'

    line = line + '</tr>\n'

    jfile    = house_keeping + '/Templates/java_script_deposit'
    f        = open(jfile, 'r')
    j_script = f.read()
    f.close()
#
#--- the template for the main part
#
    template = house_keeping + 'Templates/top_template'
    f        = open(template, 'r')
    page     = f.read()
    top_note = '<p><b><em>This page provides trending and limit predictions for various Chandra subsystems.</em></b></p>'

    page     = page.replace('#JAVASCRIPT#', j_script)
    page     = page.replace('#TITLE#', 'MTA MSID Trending')
    page     = page.replace('#TABLE#', line)
    page     = page.replace('<!-- INTRO -->', top_note)
    page     = page.replace('#EXPLANATIONS#', '')

    page     = page.replace('#OTHER_H#', 'mta_trending_sun_angle_main.html')
    page     = page.replace('#OTHER#', 'Sun Angle Page')

    page     = page.replace('#OTHER_H2#', 'mta_trending_eph_tephin_main.html')
    page     = page.replace('#OTHER2#', 'EPHIN Values vs. Temperature Page')

    page     = page.replace('#OTHER_H3#', 'mta_trending_hrcveto_eph_main.html')
    page     = page.replace('#OTHER3#', 'HRC Shield Rates vs. EPHIN Rates')

    page     = page.replace('#VIO1#', 'yellow_violation.html')
    page     = page.replace('#VIO2#', 'red_violation.html')

    page     = page.replace('#PAGE_EXP#', 'how_to_create_plots.html')
#
#--- add the potential violation candidate table
#
    violation_table = find_future_violation(p_dict)

    if violation_table != 'na':
        page     = page.replace('#VIOLATION#', violation_table)
#
#--- the template for the closing part
#
    template = house_keeping + 'Templates/html_close'
    f        = open(template, 'r')
    pclose   = f.read()

    page     = page + pclose

    outfile  = web_dir + 'mta_trending_main.html'
    fo       = open(outfile, 'w')
    fo.write(page)
    fo.close()
#
#---- update violation pages
#
    find_current_violation()


#---------------------------------------------------------------------------------------------------
#-- find_future_violation: collect potential near future violation and create tables              --
#---------------------------------------------------------------------------------------------------

def find_future_violation(p_dict):
    """
    collect potential near future violation and create tables
    input:  p_dict  --- a dictionary of group name and group description
    output: <house_keeping>/possible_violation
            hline   --- a html table showing the violation
    """
#
#--- find this year and the next
#
    this_year = int(float(time.strftime("%Y", time.localtime())))
    next_year = this_year + 1
#
#--- find violation files
#
    cmd  = 'ls -d ' + web_dir + '/*/violations > ' + zspace
    os.system(cmd)
    vlist = ecf.read_file_data(zspace, remove=1)

    line  = ''
    hline = ''
    for vfile in vlist:
        atemp = re.split('\/', vfile)
        group = atemp[-2].lower()
#
#--- find the potential violations which may happen this year and the next
#
        cmd  = 'cat ' + vfile + ' |grep ' +  str(this_year) + " > "  + zspace
        os.system(cmd)
    
        cmd  = 'cat ' + vfile + ' |grep ' +  str(next_year) + " >> " + zspace
        os.system(cmd)

        data = ecf.read_file_data(zspace, remove=1)
#
#--- print out the violation time in a file and also crate input to the top html page
#
        for ent in data:
            atemp = re.split('\s+', ent)
            msid  = atemp[0]
            mc    = re.search('br', ent)
            if mc is not None:
                btemp = re.split('<br />', ent)
                ctemp = re.split(':', btemp[0])
                dtemp = re.split(':', btemp[1])
                try:
                    e1    = float(ctemp[-1])
                except:
                    e1    = 1e10
                try:
                    e2    = float(dtemp[-1])
                except:
                    e2    = 1e10
                if e1 > e2:
                    vtime = str(e2)
                else:
                    vtime = str(e1)
            else:
                btemp = re.split(': ',  ent)
                vtime = btemp[-1]
    
            if len(msid) < 8:
                line = line + msid + '\t\t' + group + '\t' + str(vtime) + '\n'
            else:
                line = line + msid + '\t'   + group + '\t' + str(vtime) + '\n'
    
    
            hline = hline + '<tr><th><a href="' + web_address + group.capitalize() + '/' + msid.capitalize() + '/'
            hline = hline + msid + '_mid_static_long_plot.html">' + msid + '</a></th>\n'
            hline = hline + '<td style="text-align:center">' 
            hline = hline + '<a href="' + web_address + group.capitalize() + '/' + group.lower()
            try:
                hline = hline + '_mid_static_long_main.html">' +  p_dict[group.lower()]  + '</a></td>\n'
            except:
                hline = hline + '_mid_static_long_main.html">' +  group.capitalize()  + '</a></td>\n'
            hline = hline + '<td style="text-align:center">' + str(vtime) + '</td</tr>\n'
    
    ofile = house_keeping + 'possible_violation'
    fo1   = open(ofile,  'w')
    fo1.write(line)
    fo1.close()
#
#--- only when there are potential violation, we add the violation table
#
    if line == '':
        return 'na'
    else:
        tline = '<h3>Potential Near Future Violations</h3>\n'
        tline = tline + '<table border=1 cellspacing=2>\n'
        tline = tline + '<tr><th class="blue">MSID</th><th class="blue">Group</th><th class="blue">Time (year)</th></tr>\n'
        hline = tline + hline + '</table>\n'
        hline = hline + '<div style="padding-bottom:20px;"></div>\n'

    return hline


#---------------------------------------------------------------------------------------------------
#-- find_current_violation: collect current violation and create tables                           --
#---------------------------------------------------------------------------------------------------

def find_current_violation():
    """
    collect current violation and create tables
    input:  none
    output: <web_dir>/<pos>_<color>_violation.html; pos: lower/upper, color: yellow/red
            
    """
    ursave = ""
    lrsave = ""
    uysave = ""
    lysave = ""

    ttop  = '<table border=1 cellpadding=2>'
    ttail = '</table>\n<div style="padding-bottom:10px;"></div>\n'
#
#---  go through each group name to find violations
#
    gfile = house_keeping + 'sub_html_list_all'
    out   = ecf.read_file_data(gfile)

    wline = ''
    for ent in out:
        atemp = re.split('::', ent)
        group = atemp[0].capitalize()

        vfile = web_dir + group + '/violations'
        if not os.path.isfile(vfile):
            continue

        data = ecf.read_file_data(vfile)
        if len(data) == 0:
            continue
#
#--- if there are violations, start making a table 
#
        bline = '<tr><th colspan=2 class="blue" style=";"><a href="' 
        bline = bline + web_address + group + '/' + group.lower() + '_mid_static_long_main.html">'
        bline = bline + group +  '</a></th></tr>\n'
        bline = bline + '<tr><th>MSID</th><th>Description</th></tr>\n'


        urline = ""
        lrline = ""
        uyline = ""
        lyline = ""
#
#--- check which violation is recorded
#
        for ent2 in data:
            mc1   = re.search('Already', ent2)
            mc2   = re.search('Upper',   ent2)
            mc3   = re.search('Red',     ent2)

            atemp = re.split('\s+', ent2)
            msid  = atemp[0].lower()
            try:
                msid_disc = ddict[msid]
            except:
                msid_disc = msid.capitalize()
        
            if mc1 is None:
                continue

            if mc2 is not None:
                if mc3 is not None:
                    urline = urline + create_link_line(group, msid, msid_disc)
                else:
                    uyline = uyline + create_link_line(group, msid, msid_disc)

            else:
                if mc3 is not None:
                    lrline = lrline + create_link_line(group, msid, msid_disc)
                else:
                    lyline = lyline + create_link_line(group, msid, msid_disc)

        if urline != "":
            ursave = ursave + bline + urline + '<tr><td colspan=2>&#160;</td></tr>\n'

        if lrline != "":
            lrsave = lrsave + bline + lrline + '<tr><td colspan=2>&#160;</td></tr>\n'

        if uyline != "":
            uysave = uysave + bline + uyline + '<tr><td colspan=2>&#160;</td></tr>\n'

        if lyline != "":
            lysave = lysave + bline + lyline + '<tr><td colspan=2>&#160;</td></tr>\n'


    update_violation_page(lrsave, ursave, 'red')
    update_violation_page(lysave, uysave, 'yellow')



#---------------------------------------------------------------------------------------------------
#-- create_link_line: construct the table entry with a link to the main page                      --
#---------------------------------------------------------------------------------------------------

def create_link_line(group, msid, descript):
    """
    construct the table entry with a link to the main page
    input:  group       --- group name
            msid        --- msid
            descript    --- msid description
    output: line        --- table entry
    """

    line = '<tr><th><a href="' + web_address + group + '/' + msid.capitalize() + '/' 
    line = line + msid + '_mid_static_long_plot.html">' + msid + '</a></td>'
    line = line + '<td style="text-align:center;">' + descript + '</td></tr>\n'

    return line

#---------------------------------------------------------------------------------------------------
#-- update_violation_page: update violation pages                                                 --
#---------------------------------------------------------------------------------------------------

def update_violation_page(line, line2, color):
    """
    update violation pages
    input:  line    --- table contents
            pos     --- lower or upper
            color   --- yellow or red
    output: <house_keeping>/<pos>_<color>_violation.html
    """

    jscript = read_template('java_script_deposit')
    style   = jscript = read_template('java_script_deposit')

    page  = web_dir +  color + '_violation.html'
    title = color.capitalize() + ' Violation'

    mcf.rm_file(page)
    fo = open(page, 'w')

    ifile = house_keeping + 'Templates/html_head'
    f     = open(ifile, 'r')
    head  = f.read()
    f.close()
    head  = head.replace('#MSID#', title)
    head  = head.replace('#JAVASCRIPT#',jscript )

    sfile = house_keeping + 'Templates/two_col_style'
    f     = open(sfile, 'r')
    tstyle= f.read()
    f.close()
    head  = head.replace('#STYLE#',tstyle)


    ifile = house_keeping + 'Templates/html_close'
    f     = open(ifile, 'r')
    tail  = f.read()
    f.close()

    if color == 'yellow':
        ocolor= 'red'
        other = 'Go to Red Violation'
    else:
        ocolor= 'yellow'
        other = 'Go to Yellow Violation'

    tline = head  + '<h2 style="background-color:' + color +';">' + title + '</h2>\n'
    tline = tline + '<div style="text-align:right;">\n'
    tline = tline + '<a href="https://cxc.cfa.harvard.edu/mta/MSID_Trends/mta_trending_main.html">Back to Top</a>\n'
    tline = tline + '<br />\n'
    tline = tline + '<a href="https://cxc.cfa.harvard.edu/mta/MSID_Trends/' + ocolor + '_violation.html">' 
    tline = tline + other + '</a>\n'
    tline = tline + '</div>\n'
    tline = tline + '<div class="row">\n'
    tline = tline + '<div class="column">\n'
    tline = tline + '<h3>Lower Violation</h3>\n'
    tline = tline + '<table border=1 cellpadding=2>\n'
    tline = tline + line
    tline = tline + '</table>\n'
    tline = tline + '</div>\n'
    tline = tline + '<div class="column2">\n'
    tline = tline + '<h3>Upper Violation</h3>\n'
    tline = tline + '<table border=1 cellpadding=2>\n'
    tline = tline + line2
    tline = tline + '</table>\n'
    tline = tline + '</div>\n'
    tline = tline + '</div>\n'
    tline = tline + tail

    fo.write(tline)
    fo.close()
#----------------------------------------------------------------------------------
#-- read_template: read template                                                 --
#----------------------------------------------------------------------------------

def read_template(fname, repl=[]):
    """
    read template
    input:  fname   --- template file name
    repl--- a list of lists:[<tag to be replaced>, <replacing value>]
    output: out --- template read
    """
    
    infile = house_keeping + 'Templates/' + fname
    f  = open(infile, 'r')
    out= f.read()
#
#--- if substitue strings are given, replace them before return
#
    if len(repl) > 0:
        for rset in repl:
            out = out.replace(rset[0], rset[1])
    
    return out



#----------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_top_html()
