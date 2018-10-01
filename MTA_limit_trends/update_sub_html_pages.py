#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################
#                                                                                                       #
#           update_sub_html_pages.py: creates html pages for different categories of msids              #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               last update: Feb 14, 2018                                                               #
#                                                                                                       #
#########################################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
from datetime import datetime
from time import gmtime, strftime, localtime
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import convertTimeFormat        as tcnv #---- converTimeFormat contains MTA time conversion routines
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import violation_estimate_data  as ved  #---- save violation estimated times in sqlite database v_table
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

web_adress = 'https://' + web_address
#
#--- a list of thoese with sub groups
#
sub_list_file  = house_keeping + 'sub_group_list'
sub_group_list = ecf.read_file_data(sub_list_file)


#----------------------------------------------------------------------------------
#-- create_sub_html: creates html pages for different categories of msids        --
#----------------------------------------------------------------------------------

def create_sub_html(inter=''):
    """
    creates html pages for different categories of msids
    input:  inter ---   indicator of which period(s) to be proccessed
                        if "": 'short', 'one', 'five', 'long', otherwise: 'week'
            read from <house_keeping>/sub_html_list_all
    output: <web_dir>/Htmls/<category>_main.html
    """
#
#--- get today's date in fractional year
#
    sec1998 = ecf.find_current_stime()
    ytime   = ecf.stime_to_frac_year(sec1998)
#
#--- create dictionary of unit and dictionary of descriptions for msid
#
    [udict, ddict] = ecf.read_unit_list()

    lfile = house_keeping + 'sub_html_list_all'
    data  = ecf.read_file_data(lfile)
#
#--- create indivisual html pages under each category
#
    for ent in data:
        atemp = re.split('::', ent)
        catg  = atemp[0].lower()
        catg  = catg.capitalize()

        dchk  = web_dir + catg
        if not os.path.isdir(dchk):
            cmd = 'mkdir ' + dchk
            os.system(cmd)

        msids = re.split(':', atemp[1])

        if inter == '':
            l_list = ('short', 'one', 'five', 'long')
        else:
            l_list = ('week', '')

        for ltype in l_list:
            if ltype == '':
                continue

            for mtype in ('mid', 'min', 'max'):
                for ptype in ('static', ''):
                    if ptype == '':              #---- no more interactive page (11/14/17)
                        continue
                    create_html(catg, msids, ytime, udict, ddict, ltype, mtype, ptype)


#----------------------------------------------------------------------------------
#-- create_html: create a html page for category <catg>                         ---
#----------------------------------------------------------------------------------

def create_html(catg, h_list, ytime, udict, ddict, ltype, mtype, ptype):
    """
    create a html page for category <catg>
    input:  catg    --- category of the msids
            h_list  --- a list of msids of the category
            ytime   --- current time
            udict   --- a dictionary of unit: <msid> <---> <unit>
            ddict   --- a dictionary of description: <msid> <---> <description>
            ltype   --- date length: week, short, one, five, long
            mtype   --- data type: mid, min, max
            ptype   --- static or interactive
    output: <catg>_main.html
    """
#
#--- create links to other pages
#

    line = '<!DOCTYPE html>\n<html>\n<head>\n\t<title>Envelope Trending  Plots: ' + catg.upper() + '</title>\n'
    line = line + '</head>\n<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FAEBD7;'
    line = line + 'font-family:Georgia, "Times New Roman", Times, serif">\n\n'

    line = line + '<div style="float:right;padding-right:50px;font-size:120%">\n'
    #line = line + '<a href="' + web_dir + 'mta_trending_main.html" '
    line = line + '<a href="../mta_trending_main.html" '
    line = line + 'style="float:right;padding-right:50px;font-size:80%"><b>Back to Top</b></a><br />\n'

#        other = create_out_name(catg, ltype, mtype, 'inter')
#        olab  = 'Open Interactive'
#    else:
#        other = create_out_name(catg, ltype, mtype, 'static')
#        olab  = 'Open Static'
#
#    line = line + '<a href="'  + other
#    line = line + '" style="float:right;padding-right:50px;font-size:80%"><b>' + olab + '</b></a><br />\n'

    line = line + '</div>\n'

    line = line + '<h3 style="padding-bottom:0px">' + catg.upper() + ' '

    if ptype == 'static':
        line = line + '<br /> Static Version: '
    else:
        line = line + '<br /> Interactive Version: '

    if mtype == 'min':
        line = line +  ' Min --- '
    elif mtype == 'max':
        line = line +  ' Max --- '
    else:
        line = line +  ' Mean --- ' 

    if ltype == 'week':
        line = line +  ' One Week '
    elif ltype == 'short':
        line = line +  ' Last Three Months '
    elif ltype == 'one':
        line = line +  ' Last One Years '
    elif ltype == 'five':
        line = line +  ' Last Five years '
    else:
        line = line +  ' Full Range '

    line = line + '</h3>\n'
#
#--- link to the other plot category
#
    line = line + create_link_names(catg, ltype, mtype, ptype)

    line = line + '<p style="margin-left:35px; margin-right:35px;">'
    line = line + '<em><b>Delta/Yr</b></em> below is a slope of the liear fitting over the data of the period. '
    line = line + '<em><b>Delta/Yr/Yr</b></em> is a slope of the liner fitting over the devivative data '
    line = line + 'of the period. <em><b>Slope</b></em> listed on a linked plot is the slope computed on '
    line = line + 'the last few periods of the  data to show the direction of the trend, and different '
    line = line + 'from that of Delta/Yr.</p>'
    line = line + '<div style="padding-bottom:30px;"></div>'

    line = line + '<div style="text-align:center">\n\n'
    line = line + '<table border=1 cellspacing=2 style="margin-left:auto;margin-right:auto;text-align:center;">\n'
    line = line + '<th>MSID</th><th>Mean</th><th>RMS</th><th>Delta/Yr</th><th>Delta/Yr/Yr</th>'
    line = line + '<th>Unit</th><th>Description</th><th>Limit Violation</th>\n'
#
#--- create a table with one row for each msid
#
    violation_save = []
    for ent in h_list:
        atemp = re.split('_plot', ent)
        msid  = atemp[0]
#
#--- read fitting results
#
        try:
            [a, b, d, avg, std, da, db, dd] = extract_data(catg, msid, ltype, mtype)
        except:
            [a, b, d, avg, std, da, db, dd] = [0, 0, 0, 0, 0, 0, 0, 0]
#
#--- check whether plot html file exist
#
        cfile = check_plot_existance(msid, catg, ltype, mtype, ptype)
        if cfile == False:
            continue
#
#--- hrc has 4 different entries (all, hrc i, hrc s, and off cases) but share the same unit and descriptions
#
        msidp = msid.replace('_i', '')
        msidp = msidp.replace('_s', '')
        msidp = msidp.replace('_off', '')
        try:
            unit  = udict[msidp]
            discp = ddict[msidp]
#
#--- convert all F and most C temperature to K, exception: if the uint is "C", leave as it is
#
            if unit == 'DEGF':
                unit = 'K'
            elif unit == 'DEGC':
                if msid[:-2].lower() != 'tc':
                    unit = 'K'
        except:
            unit  = '---'
            discp = msid
#
#--- check violation status; if it is 'na', there is no data
#
        [vnote, color] = create_status(msid, catg, ytime)
#
#--- save the violation description if msid is in the violation range
#
        if color != 'black':
            violation_save.append([msid, vnote])

        cfile = check_plot_existance(msid, catg, ltype, mtype, ptype)

        if (abs(float(b)) > 100) or (abs(float(b)) < 0.001):
            fline = ecf.modify_slope_dicimal(float(b), float(d))
        else:
            fline =  b + '+/-' + d

        fline = check_na_std(fline)

        if (abs(float(db)) > 100) or (abs(float(db)) < 0.001):
            dline = ecf.modify_slope_dicimal(float(db), float(dd))
        else:
            dline =  db + '+/-' + dd

        dline = check_na_std(dline)

        if cfile == False:
            line = line + '<tr>\n<th>' + msid +'</a></th>'
            line = line + '<td>' + avg + '</td><td>' + std + '</td><td>' + fline + '</td>'
            line = line + '<td>' + dline + '</td><td>' + unit +'</td><td>' + discp + '</td>'
            line = line + '<th style="font-size:90%;color:#B22222;padding-left:10px;padding-right:10px">No Data</th>\n</tr>\n'
        else:
            xfile = cfile.replace('www\/','')
            ctemp = re.split('\/', cfile)
            xfile = ctemp[-2] + '/' + ctemp[-1]
            line = line + '<tr>\n<th><a href="'+ xfile  +  '">' + msid +'</a></th>'
            line = line + '<td>' + avg + '</td><td>' + std + '</td><td>' + fline + '</td>'
            line = line + '<td>' + dline + '</td><td>' + unit +'</td><td>' + discp + '</td>'
            line = line + '<th style="font-size:90%;color:' + color + ';padding-left:10px;padding-right:10px">' + vnote + '</th>\n</tr>\n'

    line = line + '</table>\n'

    line = line + '</div>\n'

    bfile = house_keeping + 'Templates/html_close'
    f     = open(bfile, 'r')
    fout  = f.read()
    f.close()
    line = line +  fout
#
#--- category html has the tail of "_main.html"
#
    try:
        name = create_out_name(catg, ltype, mtype, ptype)
        fo   = open(name, 'w')
        fo.write(line)
        fo.close()
    except:
        pass

    vout = web_dir + catg + '/violations'
    if len(violation_save) ==  0:
        mcf.rm_file(vout)
    else:
        fo  = open(vout, 'w')
        for ent in violation_save:
            if len(ent[0]) < 8:
                line = ent[0] + '\t\t' + ent[1] + '\n'
            else:
                line = ent[0] + '\t' + ent[1] + '\n'
            fo.write(line)
        fo.close()
        
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def check_na_std(line):

    mc1 = re.search('999', line)
    mc2 = re.search('99.9', line)
    mc3 = re.search('9.99', line)

    if (mc1 is not None) or (mc2 is not None) or (mc3 is not None):

        atemp = re.split('\+\/\-', line)
        mc2 = re.search('\)', atemp[1])
        if mc2 is not None:
            btemp = re.split('\)', atemp[1])

            line = atemp[0] + '+/-na)' + btemp[1]
        else:
            line = atemp[0] + '+/-na'

    return line




#----------------------------------------------------------------------------------
#-- read fitting results: read fitting results                                   --
#----------------------------------------------------------------------------------

def extract_data(catg, msid, ltype, mtype):
    """
    read fitting results
    input:  catg    --- category of the msids
            msid    --- msid
            ltype   --- data length: week, short, one, five, long
            mtype   --- min, max, med
    output: [a, b, d, avg, std, da, db, dd], fitting results and their errors
    """
    sfile = web_dir + catg + '/' + msid.capitalize() + '/Plots/' + msid + '_fit_results'
    sdata = ecf.read_file_data(sfile)
    dfile = web_dir + catg + '/' + msid.capitalize() + '/Plots/' + msid + '_dev_fit_results'
    ddata = ecf.read_file_data(dfile)

    a   = '0'
    b   = '0'
    d   = '0'
    avg = '0'
    std = '0'
    da  = '0'
    db  = '0'
    dd  = '0'
    for ent in sdata:
        mc1 = re.search(ltype, ent)
        mc2 = re.search(mtype, ent)
        if (mc1 is not None) and (mc2 is not None):
            atemp = re.split(':', ent)
            a    = atemp[2]
            b    = atemp[3]
            d    = atemp[4]
            avg  = atemp[5]
            std  = atemp[6]
            break

    for ent in ddata:
        mc1 = re.search(ltype, ent)
        mc2 = re.search(mtype, ent)
        if (mc1 is not None) and (mc2 is not None):
            atemp = re.split(':', ent)
            da    = atemp[2]
            db    = atemp[3]
            dd    = atemp[4]
            break

    return [a, b, d, avg, std, da, db, dd]

#----------------------------------------------------------------------------------
#-- create_out_name: create html page name for given condition                   --
#----------------------------------------------------------------------------------

def create_out_name(catg, ltype, mtype, ptype):
    """
    create html page name for given condition
    input:  catg    --- category of the msids
            ltype   --- data length: week, one, five or "" (full)
            mtype   --- min, max, med
            ptype   --- static or inter (interactive)
    output: name    --- html page name (with a full path)
    """
    if ptype == 'static':
        ppart = '_static_'
    else:
        ppart = '_inter_'

    name = web_dir + catg + '/' +  catg.lower() + '_' + mtype + ppart  + ltype +  '_main.html'

    return name

#----------------------------------------------------------------------------------
#-- create_link_names: create html page link code for given condition            --
#----------------------------------------------------------------------------------

def create_link_names(catg, ltype, mtype, ptype):
    """
    create html page link code for given condition
    input:  catg    --- category of the msids
            ltype   --- data length: week, one, five or "" (full)
            mtype   --- min, max, med
            ptype   --- static or inter (interactive)
    output: line    --- html link code
    """
    link     = []
    discript = []

    for ltype_t in ('week', 'short', 'one', 'five', 'long'):
        if ltype == ltype_t:
            this = ''
        else:
            this = create_out_name(catg, ltype_t, mtype, ptype)

        if ltype_t == 'week':
            text = 'One Week'
        elif ltype_t == 'short':
            text = 'Three Month '
        elif ltype_t == 'one':
            text = 'One Year'
        elif ltype_t == 'five':
            text = 'Five Year'
        else:
            text = 'Full Range'

        link.append(this)
        discript.append(text)

    for mtype_t in ('mid', 'min', 'max'):
        if mtype == mtype_t:
            this = ''
        else:
            this = create_out_name(catg, ltype, mtype_t, ptype)

        if mtype_t == 'max':
            text = 'Max'
        elif mtype_t == 'min':
            text = 'Min'
        else:
            text = 'Average'
        link.append(this)
        discript.append(text)

    for ptype_t in ('static', 'inter'):
        if ptype == ptype_t:
                continue

        this = create_out_name(catg, ltype, mtype, ptype_t)
#        if ptype_t == 'static':
#            text = 'Static'
#        else:
#            text = 'Interactive'
#        link.append(this)
#        discript.append(text)

    line = '<table border=1 cellpadding=2><tr>\n'
    for k in range(0, len(link)):
        if link[k] == '':
            line = line + '<th>' +  discript[k] + '</th>\n'
        else:
            slink = link[k].replace(web_dir, '\.\/mta\/MSID_Trends\/')
            line = line + '<th><a href="' + slink + '">' + discript[k] + '</a></th>\n'

    line = line + '</tr>\n</table>\n'
    line = line + '<div style="padding-bottom:10px;"></div>'

    return line


#----------------------------------------------------------------------------------
#-- check_plot_existance: check whether a html file exist for the given msid and/or interactive plot exists
#----------------------------------------------------------------------------------

def check_plot_existance(msid, catg, ltype, mtype, ptype):
    """
    check whether a html file exist for the given msid and/or interactive plot exists
    input:  msid    --- msid
            ltype   --- week, short, one, five, long
            mtyp    --- mid, min, max
            ptype   --- static or inter
    output: True/False
    """
    if ptype == 'static':
        ppart = '_static_'
    else:
        ppart = '_inter_'

    cfile = web_dir + catg  + '/' + msid.capitalize() + '/' +  msid  + '_' + mtype
    cfile = cfile   + ppart + ltype +  '_plot.html'

    if os.path.isfile(cfile):
        return cfile
    else:
        return False

#----------------------------------------------------------------------------------
#-- create_status: check the status of the msid and return an appropriate comment -
#----------------------------------------------------------------------------------

def create_status(msid, group,  ytime):
    """
    check the status of the msid and return an appropriate comment
    input:  msid    --- msid
            group   --- group name
            ytime   --- corrent time
    output: [<comment>, <font color>]
    """
#
#--- read violation status of the msid
#
    if group in sub_group_list:
        tmsid = msid + '_' + group.lower()
    else:
        tmsid = msid

    out   = ved.read_v_estimate(tmsid)
#
#--- if there is no data, tell so and return
#
    if len(out) < 4:
        return ["No Violation Check", 'black']
#
#--- if all entries are "0", no violation
#
    chk = 0
    for k in range(0, 4):
        if out[k] != 0.0:
            chk =1
            break

    if chk == 0:
        return ["No Violation", 'black']
#
#--- if there are violation, create the description and choose a color for it
#
    else:
        line  = ''
        line0 = ''
        line1 = ''
        line2 = ''
        line3 = ''
        color = 'black'
        if out[0] != 0:
            if out[0] < ytime:
                line0 = 'Already Lower Yellow Violation'
                color = '#FF8C00'
            else:
                line0 = "Yellow Lower Violation: " + clean_the_input(out[0])
                color = '#FF8C00'

        if out[1] != 0:
            if out[1] < ytime:
                line1 = 'Already Upper Yellow Violation'
                color = '#FF8C00'
            else:
                line1 = "Yellow Upper Violation: " + clean_the_input(out[1])
                color = '#FF8C00'

        if out[2] != 0:
            if out[2] < ytime:
                line2 = 'Already Lower Red Violation'
                color = 'red'
            else:
                line2 = "Red Lower Violation: " + clean_the_input(out[2])
                color = 'red'

        if out[3] != 0:
            if out[3] < ytime:
                line3 = 'Already Upper Red Violation'
                color = 'red'
            else:
                line3 = "Red Upper Violation: " + clean_the_input(out[3])
                color = 'red'

        if line2 != '':
            line =  line2
            color = 'red'
        else:
            if line0 != '':
                line = line0
                color = '#FF8C00'


        if line3 != '':
            if line != '':
                line = line + '<br />' + line3
                color = 'red'
            else:
                line = line3
                color = 'red'
        else:
            if line1 != '':
                if line != '':
                    line = line + '<br />' + line1
                    if color == 'black':
                        color = '#FF8C00'
                else:
                    line = line1
                    color = '#FF8C00'


        return [line, color]

#----------------------------------------------------------------------------------
#-- clean_the_input: check the input is numeric and if so, round to two decimal   -
#----------------------------------------------------------------------------------

def clean_the_input(line):
    """
    check the input is numeric and if so, round to two decimal
    input:  line    --- input quantity
    output: line    --- if it is a numeric value, a value of two decimal, 
                        otherwise, just return the value as it was
    """

    if mcf.chkNumeric(line):
        line = str(ecf.round_up(float(line)))

    return line
        

#---------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        l_list = sys.argv[1]
    else:
        l_list = ''

    create_sub_html(l_list)
