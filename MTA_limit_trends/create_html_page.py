#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#######################################################################################
#                                                                                     #
#       create_html_page.py: create indivisual html pages for all msids in database   #
#                                                                                     #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                 #
#                                                                                     #
#           last update: May 29, 2019                                                 #
#                                                                                     #
#######################################################################################

import sys
import os
import string
import re
import numpy
import getopt
import os.path
import time
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

#
#--- read argv
#
try:
    option, remainder = getopt.getopt(sys.argv[1:],'t',['test'])
except getopt.GetoptError as err:
     print(str(err))
     sys.exit(2)

path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import create_derivative_plots  as cdp  #---- create derivative plot
import create_html_suppl        as chs  #---- supplemental functions to crate html page
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- other settings
#
na     = 'na'
#
#--- read category data
#
cfile         = house_keeping + 'sub_html_list_all'
category_list = mcf.read_data_file(cfile)
#
#--- set several values used in the plots
#
color_table  = ['blue', 'red', '#FFA500']
marker_table = ['s',   '*',    '^',     'o']
marker_size  = [50,    80,     70,      50]

css = """
    p{
        text-align:left;
    }
"""
#
#---  get dictionaries of msid<-->unit and msid<-->description
#
[udict, ddict] = ecf.read_unit_list()
#
#---  a list of groups excluded from interactive page creation
#
efile = house_keeping + 'exclude_from_interactive'
exclude_from_interactive = mcf.read_data_file(efile)
#
#--- the top web page address
#
web_address = 'https://' + web_address
#
#--- alias dictionary
#
afile  = house_keeping + 'msid_alias'
data   = mcf.read_data_file(afile)
alias  = {}
alias2 = {}
for ent in data:
    atemp = re.split('\s+', ent)
    alias[atemp[0]]  = atemp[1]
    alias2[atemp[1]] = atemp[0]
#
#--- a list of thoese with sub groups
#
sub_list_file  = house_keeping + 'sub_group_list'
sub_group_list = mcf.read_data_file(sub_list_file)

#------------------------------------------------------------------------------------
#-- create_html_page: create indivisual html pages for all msids in database       --
#------------------------------------------------------------------------------------

def create_html_page(qtype='static', msid_list='', ds='all', ms='all'):
    """
    create indivisual html pages for all msids in database
    input:  qtype       --- whether to create interactive link; default:inter--- yes
            msid_list   --- a name of msid_list to be run. if "", 
                            <house_keeping>/msid_list is used
            ds          --- data set name. if 'all', ['week', 'short', 'long'] is used.
            ms          --- category name. if 'all', ['mid', 'min', max'] is used.
    output: <web_dir>/<msid>_plot.html etc
    """
#
#--- check whether interactive page is requested
#
    if qtype == 'inter':
        print("Create Both Interactive/Static Versions")
        ptype = 'inter'

    else:
        print("Create Static Version Only")
        ptype = 'static'
#
#--- set which data set to run
#
    if ds == 'all':
        data_sets = ['week', 'short', 'long']
    else:
        data_sets = [ds]
#
#--- set which category of plots to create
#
    if ms == 'all':
        cat_sets = ['mid', 'min', 'max']
    else:
        cat_sets = [ms]

    print('Data sets: '  + str(data_sets) + ' : ' + 'Categoray: ' + str(cat_sets))
#
#--- clean out future estimate direcotry
#
    cmd = 'rm -rf ' + web_dir + 'Future/* 2>/dev/null'
    os.system(cmd)
#
#--- get a list of msids (and the group name)
#
    if msid_list == "":
        mfile = house_keeping + 'msid_list'
    else:
        mfile = house_keeping + msid_list

        if not os.path.isfile(mfile):
            mfile = house_keeping + 'msid_list'

    data  = mcf.read_data_file(mfile)

    msid_list  = []
    group_list = []
    gchk       = ''
    g_dict     = {}
    m_save     = []

    for out in data:
        try:
            [msid, group] = re.split('\s+',  out)
        except:
            atemp = re.split('\s+', out)
            msid  = atemp[0]
            group = atemp[1]

        if msid[0] == '#':
            continue

        msid_list.append(msid)
        group_list.append(group)

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

    for k in range(0, len(msid_list)):
#
#--- some msids have a different display name
#
        msid  = msid_list[k]

        mc    = re.search('#', msid)
        if mc is not None:
            continue

        msid2 = msid
        try:
            msid2 = alias[msid]
        except:
            pass

        group = group_list[k]
#
#--- check whether the output directries exist; p_dir is the directory to save png files
#
        #[p_dir, p_dir2]  = check_directories(msid2, group)
        [p_dir, p_dir2]  = check_directories(msid, group)

        print('Processing: ' + msid + ' of ' + group)
#
#--- open a file to save last period slope
#
        ofile = web_dir + group + '/' + msid.capitalize() + '/Plots/' + msid + '_fit_results'

        dfile = web_dir + group + '/' + msid.capitalize() + '/Plots/' + msid + '_dev_fit_results'
#
#--- try to find the unit of the msid
#
        try: 
            unit    = udict[msid]
            descrip = ddict[msid]
        except:
            unit    = ''
            descrip = ''
#
#--- there are three different types of datasets: 'week' (5 min), 'short' (1 hr), 'long' (1 day)
#
        pchk = 0
        for ltype in data_sets:
#
#--- pdata is  two dim array of data (see read_msid_data_full for details). 
#--- flist is sub category of each data set
#
            try:
                [pdata, byear, flist] = select_data_set(msid, group, ltype)
            except:
                print("No data for: " + msid + ' of ' + group + '(' + ltype + ')')
                continue

            for otype in flist:
                for mtype in cat_sets:
                    plotname  = p_dir   + msid + '_' + otype + '_' + mtype + '.png'
                    plotname2 = p_dir2  + msid + '_' + otype + '_' + mtype + '.png'

                    if pchk == 0 and  otype == 'short':
                        pchk = 1

                        try:
                            if pdata[0][-1] > 425:
                                byear +=1
                                for m in range(0, len(pdata[0])):
                                    pdata[0][m] -= 366
                        except:
                            continue
#
#--- create the plot
#
                    try:
                        [pout, xxout]   = chs.create_trend_plots(msid, group, pdata, byear,\
                                               unit, otype, mtype, plotname, ptype)
                        pchk = 1

                    except:
                        print("plot was not created")
                        cmd = 'cp ' + house_keeping + 'no_data.png ' + plotname
                        os.system(cmd)
                        pchk = 0
#
#--- create the derivative plot
#
                    if pchk == 1:
                        try:
                            out  = cdp.plot_deviatives(pdata, byear, msid, group, otype, mtype)
                        except:
                            devplot = plotname.replace('.png', '_dev.png')
                            cmd     = 'cp ' + house_keeping + 'no_data.png ' + devplot
                            os.system(cmd)
                            out  = ['0', '0', '0', '0']
                    else: 
                        devplot = plotname.replace('.png', '_dev.png')
                        cmd     = 'cp ' + house_keeping + 'no_data.png ' + devplot
                        os.system(cmd)
                        out  = ['0', '0', '0', '0']

                    line = otype + ':' + mtype + ':' + out[0] + ':' + out[1] 
                    line = line  + ':' + out[2] + ':' + out[3] + '\n'

                    update_fit_result_file(otype, mtype, dfile, line)
#
#--- create html page; g_dict contains a list of msids of that group

                    if ptype == 'inter':
                        create_plot_html_page(msid, g_dict[group], group, descrip,\
                                              pout, '', otype, mtype, ptype)

                    create_plot_html_page(msid, g_dict[group], group, descrip, '',\
                                          plotname2, otype, mtype, ptype)
#
#--- compute the slope for a given period (see compute_dy_dx for the period)
#
                    pos                 = chs.select_data_position(mtype)
                    try:
                        [a, b, d, avg, std] = chs.compute_dy_dx(pdata[0], pdata[pos], otype)
                    except:
                        [a, b, d, avg, std] = ['0.0', '0.0', '0.0', '0.0', '0.0']

                    outname = web_dir + group + '/' + msid.capitalize() + '/' + msid + '_' 
                    outname = outname + mtype + '_static_' + otype + '_plot.html'

                    line = otype + ':' + mtype + ':' + a + ':' + b + ':' + d + ':' 
                    line = line  + avg + ':' + std + ':' + outname + '\n'
                    
                    update_fit_result_file(otype, mtype, ofile, line)

#------------------------------------------------------------------------------------
#-- update_fit_result_file: update fitting line result file for the give type      --
#------------------------------------------------------------------------------------

def update_fit_result_file(otype, mtype, rfile, result):
    """
    update fitting line result file for the give type
    input:  otype   --- length of the data type (week, short, one, five, long)
            mtype   --- data type (mid, min, max)
            rfile   --- the result file name
            result  --- the new fitted result
    output: rfile   --- updated result file
    """
#
#--- read the saved results
#
    try:
        out  = mcf.read_data_file(rfile)    
        out  = list(set(out))
    except:
        out  = []
#
#--- find the line with the same type and replace it with the new result
#
    save = []
    chk  = 0
    for ent in out:
        test = otype + ':' + mtype
#
#--- remove the following few lines after cleaning finishes (Jan 17, 2018)
#
        mc = re.search(test, ent)
        if (ent.startswith('w:')) or  (ent.startswith('e:')) or (ent.startswith('k:')):
            continue

        if mc is not None:
            save.append(result)
            chk = 1
        else:
            if ent == "" or ent == '\s+':
                continue
            save.append(ent)

    if chk == 0:
        save.append(result)
#
#--- update the file
#
    sline = ''
    for ent in save:
        if ent == '':
            continue
        sline = sline + str(ent) + '\n'

    with open(rfile, 'w') as fo:
        fo.write(sline)

#------------------------------------------------------------------------------------
#-- select_data_set: read data and set sub-category                                --
#------------------------------------------------------------------------------------

def select_data_set(msid, group, ltype):
    """
    read data and set sub-category
    input:  msid    --- msid
            group   --- the group name to which msid belongs
            ltype   --- week, short, one, five, long
    output: pdata   --- a two dimensional array  of data (see read_out for more details)
            byear   --- the base year used for week and short data plot
            flist   --- sub categories of the data
    """

    dfile = data_dir + group.capitalize() + '/' + msid + '_data.fits'
#
#--- for short, we create 3 months and one year plots
#
    if ltype == 'short':
        dfile = dfile.replace('_data', '_short_data')
        flist = [str('short'), str('one')]
#
#--- with week data, only one week plot
#
    elif ltype == 'week':
        dfile = dfile.replace('_data', '_week_data')
        flist = [str('week')]
#
#--- long data is for 5 yrs and full range
#
    else:
        flist = [str('five'), str('long')]

    try:
        [pdata, byear]  = chs.read_msid_data_full(dfile, msid,  ltype)
        try:
            if pdata == [0]:
                pdata = []
                byear = 1999
        except:
            pass
    except:
        pdata = []
        byear = 1999

    return [pdata, byear, flist]

#------------------------------------------------------------------------------------
#-- check_directories: check the existances of directories. if not, create them   ---
#------------------------------------------------------------------------------------

def check_directories(msid, group):
    """
    check the existances of directories. if not, create them
    input:  msid    --- msid
            group   --- group name
    output: p_dir   --- directries created if there were not before
            p_dir2  --- wed address to the directory
            
    """
    p_dir  = web_dir + group + '/'
    p_dir2 = web_address + group + '/'
    chs.check_dir_exist(p_dir)

    p_dir  = p_dir  + msid.capitalize() + '/'
    p_dir2 = p_dir2 + msid.capitalize() + '/'
    chs.check_dir_exist(p_dir)

    p_dir  = p_dir  + 'Plots/'
    p_dir2 = p_dir2 + 'Plots/'
    chs.check_dir_exist(p_dir)

    return [p_dir, p_dir2]

#----------------------------------------------------------------------------------
#-- create_plot_html_page: create a html page to display the trend plot          --
#----------------------------------------------------------------------------------

def create_plot_html_page(msid, msid_list, group, descrip, pout, plotname, ltype, mtype, plink):
    """
    create a html page to display the trend plot
    input:  msid        --- msid
            msid_list   --- the list of msids in the group
            group       --- group name to which msid belongs
            descrip     --- description of the msid
            pout        --- plot in html format' it is <blank> if this is a static version
            plotname    --- the name of the png file; it is <blank> 
                            if this is an interacitve version
            ltype       --- data type, week, short, one, five, or long
            mtype       --- data type, mid, min, max
    output: plot <web_dir>/<msid>_plot.html
    """
    if plotname == "":
        ptype = 'inter'
    else:
        ptype = 'static'
#
#--- read javascript file
#
    jscript = chs.read_template('java_script_deposit')
#
#--- set web page names including link back pages
#
    [tweb, hname, other, other_list] = set_link_htmls(group, msid, ltype, mtype, ptype)
#
#--- pop up limit table web address
#
    file_name = web_address + group +  '/Limit_table/' + msid + '_limit_table.html'
#
#--- start creating html page
#
    repl = [["#MSID#",  msid.upper()], ["#JAVASCRIPT#", jscript], ["#STYLE#", '']]
    out = chs.read_template('html_head', repl )

    out = out + '<div style="float:right;padding-right:50px;">'
    out = out + '<a href="' + tweb + '" '
    out = out + 'style="text-align:right"><b>Back to ' + group + ' Page</b></a><br />\n'
    out = out + '<b><a href = "' + web_address + 'mta_trending_main.html">Back To Top</a><br />\n'
#
#--- interactive/static page link back
#
    out = out + '<a href="'  + other  + '" style="text-align:right">'
    if ptype == 'inter':
        out = out + '<b>Open Static Version</b>'
    else:
        if plink == 'inter':
            out = out + '<b>Open Interactive Version</b>'

    out = out + '</a><br />\n'
    out = out + '<b><a href="javascript:popitup(\'' + web_address 
    out = out + '/how_to_create_plots.html\')" style="text-align:right">'
    out = out + 'How the Plots Are Created</a></b><br />\n'
#
#--- prev and next msid
#
    out = out + make_msid_link(msid, msid_list, group,  ltype, mtype, ptype)

    out = out + '</div>\n'
#
#--- title of the page 
#
    out = out + set_title(msid, descrip, ltype, mtype, ptype)
#
#--- popup limit table link
#
    out = out + '<div style="paddng-top:10px"><h3>'
    out = out + 'Open <a href="javascript:popitup(\'' + file_name + '\')" '
    out = out + 'style="text-align:right">Limit Table</a>.'
    out = out + '</h3>\n'
    out = out + '</div>\n'
#
#--- link to the other type of length plots
#
    out = out + create_period_link(other_list)
#
#--- interactive page case
#
    if plotname == "":
        if (pout == False) or (str(pout) == 'na'):
            out = out + '<h3 style="padding-top:200px;padding-bottom:200px">No Data/No Plot</h3>'
        else:
            out = out +  '<div style="margin-left:-30px;">'
            out = out +  pout
            out = out + '</div>'

        out = out + chs.read_template('interact_descript')
#
#--- static page case
#
    else:
        out = out + '<img src="' + plotname + '" width=80%>'

    phpfile  = web_address + "Interactive/msid_data_interactive.php"
    int_note = web_address + 'interactive_note.html'

    out = out + '<div style="padding-bottom:10px;font-size:90%;">\n';
    if group.lower() in exclude_from_interactive:
        out = out + '<h3>This Data Set Cannot Produce an Interactive Plot</h3>\n'
    else:
        out = out + '<h3>Create an Interactive Plot ('
        out = out + '<a href="javascript:popitup(\'' + int_note + '\')" '
        out = out + 'style="text-align:right">Usage Note</a>'
        out = out + ')</h3>\n'
        out = out + '<form method="post" action=' + phpfile + '>\n'
        out = out + '<b>Starting Time:</b> <input type="text" name="tstart"  size=20>\n'
        out = out + '<b>Stopping Time:</b> <input type="text" name="tstop"  size=20>\n'
        out = out + '<b>Bin Size:</b>      <input type="text" name="binsize"  '
        out = out + 'value=300.0 size=10>\n '

        out = out + '<input type="hidden" name="ltype" value="' + ltype + '">\n'
        out = out + '<input type="hidden" name="mtype" value="' + mtype + '">\n'
        out = out + '<input type="hidden" name="msid"  value="' + msid  + '">\n'
        out = out + '<input type="hidden" name="group" value="' + group + '">\n'
    
        out = out + '</br><span style="text-align:right;"><input type=submit '
        out = out + 'name="submit" value="Submit"></span>\n'
        out = out + '<br />\n'
        out = out + '</form>\n'
    out = out + '</div>\n'
#
#--- add the derivative plot
#
    dplotname = web_address + group.capitalize() + '/' + msid.capitalize()
    dplotname = dplotname + '/Plots/' + msid + '_' + ltype + '_' + mtype + '_dev.png'

    out = out + '<h3>Derivative Plot</h3>\n'
    out = out + '<img src="' + dplotname + '" width=80%>'
#
#--- add the link to other plots in a table format
#
    [lout, gname] = get_group_names(msid, group,  ltype, mtype, ptype)
    if lout != '':
        out = out + '<h3>Other msids in this group: ' + gname + '</h3>'
        out = out + lout
#
#--- close html page
#
    out = out + chs.read_template('html_close')
#
#--- write out the html data
#
    with open(hname, 'w') as fo:
        fo.write(out)

#----------------------------------------------------------------------------------
#-- set_link_htmls: create the main html name and other link back html names     --
#----------------------------------------------------------------------------------

def set_link_htmls(group, msid, ltype, mtype, ptype):
    """
    create the main html name and other link back html names
    input:  group   --- group name
            msid    --- msid
            ltype   --- data type: week, short, one, five, long
            mtype   --- data type: mid, min, max
            ptype   --- static, int
    output: tweb    --- top web page link
            hname   --- main html name
            other   --- counter part of hname (static/interactive)
            other_list  --- a list of other html page links
    """
    if ptype == 'inter':
        insert1 = '_inter'
        insert2 = '_static'
    else:
        insert1 = '_static'
        insert2 = '_inter'
#
#--- check whether the directories exist
#
    odir   = web_dir + group
    o_dir  = odir  + '/' + msid.capitalize() + '/'
    chs.check_dir_exist(odir)
    chs.check_dir_exist(o_dir)

    odir2  = web_address + group
    o_dir2 = odir2  + '/' + msid.capitalize() + '/'
#
#--- top web page name to back to
#
    if group.lower() == 'ephkey_l1':
        tgroup = 'compephkey'
    else:
        tgroup = group.lower()

    tweb = web_address + group.capitalize() + '/' + tgroup.lower()  + '_' + mtype
    tweb = tweb + insert1 + '_' + ltype + '_main.html'
#
#--- other html pages
#
    hname  = o_dir  + msid + '_' + mtype + insert1 + '_' + ltype + '_plot.html'
    other  = o_dir  + msid + '_' + mtype + insert2 + '_' + ltype + '_plot.html'
    other_list = []

    for ctype in ['week', 'short', 'one', 'five', 'long']:

        if ctype != ltype:
            ohtml = o_dir2  + msid + '_' + mtype + insert1 + '_' + ctype + '_plot.html'
            other_list.append(ohtml)

    return [tweb, hname, other, other_list]

#----------------------------------------------------------------------------------
#-- set_title: create the title of the page                                      --
#----------------------------------------------------------------------------------

def set_title(msid, descrip, ltype, mtype, ptype):
    """
    create the title of the page
    input:  msid    --- msid
            descrip --- description of this msid
            ltype   --- week, short, one, five, long
            mtype   --- mid, min, max
            ptype   --- static, inter
    output: out     --- the title of the page
    """
    out = '<h2>'

    if descrip == '':
        out = out + msid.upper()
    else:
        out = out + msid.upper() + ' (' + descrip.upper() + ')' 

    if ptype == 'inter':
        out = out + '<br /> Interactive Version: '
    else:
        out = out + '<br /> Static Version: '

    if mtype == 'min':
        out = out + 'Min  ---'
    elif mtype == 'max':
        out = out + 'Max  ---'
    else:
        out = out + 'Mean ---'

    if ltype == 'week':
        out = out + 'One Week Plot\n'
    elif ltype == 'short':
        out = out + 'Last Three Month Plot\n'
    elif ltype == 'one':
        out = out + 'Last One Year Plot\n'
    elif ltype == 'five':
        out = out + 'Last Five Year Plot\n'
    else:
        out = out + 'Full Range Plot\n'

    out = out + '</h2>\n'

    return out

#----------------------------------------------------------------------------------
#-- make_msid_link: create links to the previous and the next msid               --
#----------------------------------------------------------------------------------

def make_msid_link(msid, msid_list, group,  ltype, mtype, ptype):
    """
    create links to the previous and the next msid
    input:  msid        --- msid
            msid_list   --- a list of msid in the group
            group       --- a group name
            ltype       --- week, short, one, five, long
            mytpe       --- mid, min, max
            ptype       --- static, inter
    output: line        --- links in html format
    """
    ltot = len(msid_list)
    if ltot == 0:
        return ''
#
#--- find the position of the msid in the list
#
    pos = 0
    for k in range(0, ltot):
        if msid_list[k] == msid:
            pos = k
            break

    main_msid = '<span style="color:green;">' + msid + '</span>\n'
#
#--- create the link to the previous msid
#
    try:
        if pos-1 < 0:
            pline = ''
        else:
            prev  = msid_list[pos-1]
            plink = web_address + group + '/' + prev.capitalize() + '/' + prev
            plink = plink + '_' + mtype + '_' + ptype + '_' + ltype + '_plot.html'
            pline = '<a href="' + plink + '">' + prev + '</a> &lt;&lt;  '
    except:
        pline = ''
#
#--- create the link to the next msid
#
    try:
        if pos+1 > ltot:
            nline = ''
        else:
            if pos == 0:
                next = msid_list[1]
            else:
                next = msid_list[pos+1]

            nlink = web_address + group + '/' + next.capitalize() + '/' + next 
            nlink = nlink + '_' + mtype + '_' + ptype + '_' + ltype + '_plot.html'
            nline = '  &gt;&gt; <a href="' + nlink + '">' + next + '</a>\n' 
    except:
        nline = ''
#
#--- now create the html code
#
    line = '<h3 style="float:right;text-align:right;font-size:90%;">\n'

    if pos == 0:
        line = line +  main_msid +  nline

    elif pos == ltot-1:
        line = line + pline + main_msid

    else:
        line = line + pline + main_msid +  nline

    line = line + '</h3>\n'

    return line

#----------------------------------------------------------------------------------
#-- create_period_link: create a table to list links to  different period length plots 
#----------------------------------------------------------------------------------

def create_period_link(other_list):
    """
    create a table to list links to  different period length plots
    input:  ohter_list  --- a list of path to the other html page
    output: out         --- html code of the table
    """
    #out = '<h3 style="padding-top:10px;">Other Period Length Plots</h3>\n'
    out = ''
    out = out + '<table border=1 cellspacing=2>\n'
    out = out + '<tr>\n'

    for ent in ['week', 'short', 'one', 'five', 'long']:
        chk = 0
        for elink in other_list:
            mc = re.search(ent, elink)
            if mc is not None:
                chk = 1
                break

        if ent == 'week':
            name = 'One Week Plot'
        elif ent == 'short':
            name = 'Three Month Plot'
        elif ent == 'one':
            name = 'One year Plot'
        elif ent == 'five':
            name = 'Five Year Plot'
        else:
            name = 'Full Range'

        if chk == 1:
            out = out + '<td style="text-align:center;width:20%;white-space:nowrap;">'
            out = out + '<a href="' + elink + '">' + name + '</a></td>\n'
        else:

            out = out + '<td style="text-align:center;width:20%;">'
            out = out + '<b style="color:green;white-space:nowrap;">' 
            out = out + name + '</b></td>\n'

    out = out + '</tr>\n'
    out = out + '</table>\n'
    out = out + '<div style="padding-bottom:15px;"></div>\n';

    return out

#----------------------------------------------------------------------------------
#-- get_group_names: create a table with links to other msids in the same group  --
#----------------------------------------------------------------------------------

def get_group_names(msid, group, ltype, mtype, ptype):
    """
    create a table with links to other msids in the same group
    input:  msid    --- msid
            group   --- group name
            ltype   --- week, short, one, five, long
            mtype   --- mid, min, max
            ptype   --- static or inter
    output: line    --- a link list in html table format
    """
#
#--- find which group this msid belongs to and then find all other msids in this group
#
    [group_id, group_list] = find_group_names(msid)
#
#--- create the table fo these msids with links to the plots
#
    nrow  = 0
    k     = 0
    if len(group) > 0:
        cname = group.capitalize()
        gname = '<a href="' + web_address + group.capitalize() + '/'  
        gname = gname + group.lower() + '_' + mtype + '_' + ptype 
        gname = gname + '_' + ltype   + '_main.html">' + group.upper() + '</a>'

        line = '<table border=1 cellpadding=3>\n'
        for ent in group_list:
#
#--- make the main msid not clickable
#
            tchk = 0
            ctemp = re.split('_plot.html', ent)
            if ctemp[0] == msid:
                tchk = 1

            ment  = ctemp[0]                #--- msid of the targeted link

            if k == 0:
                line = line + '<tr>'
#
#--- create link html address
#
            pname = ment + '_' + mtype + '_' + ptype + '_' + ltype + '_plot.html'

            line = line + '<td style="text-align:center">'
            if tchk == 1:
                line = line + '<b style="color:green;">' + msid + '</b></td>\n'
            else:
                line = line + '<a href="' + web_address  + cname + '/' 
                line = line + ment.capitalize() +  '/' + pname + '">' 
                line = line + ctemp[0] + '</a></td>\n'
#
#--- 10 entries per row
#
            if k >= 11:
                line = line + '</tr>\n'
                k    = 0
                nrow = 1
            else:
                k += 1
#
#--- filling up the empty cells
#
        chk = 0
        if (nrow > 0) and (k > 0):
            for m in range(k, 12):
                line = line + '<td>&#160;</td>\n'
                chk = 1
        else:
            chk = 1

        if chk == 1:
            line = line + '</tr>\n'
            line = line + '</table>\n'

    else:
        gname = ''
        line = ''

    return [line, gname]

#----------------------------------------------------------------------------------
#-- find_group_name: return a list of msids which belongs to the group with the given msid
#----------------------------------------------------------------------------------

def find_group_names(msid):
    """
    return a list of msids which belongs to the group with the given msid
    input:  msid        --- misd 
    output: group_id    --- a group name
            group_list  --- a list of msids belong to the group
    """
    group_id    = 'na'
    group_list = []
    try:
        msid      = alias[msid]
    except:
        pass

    test       = msid + '_plot.html'

    for ent in category_list:
        mc = re.search(test, ent)

        if mc is not None:
            atemp      = re.split('::', ent)
            group_id   = atemp[0].lower()
            group_list = re.split(':',  atemp[1])

            if test in group_list:
                break
            else:
                group_id   = 'na'
                group_list = []
                continue

    return [group_id, group_list]

#------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        mc = re.search('=', sys.argv[1])

        if mc is None:
            line = "create_html_page(qtype=<inter/static> msid_list=<list name> "
            line = line + "ds=<week/short/long/all> ms=<mid/min/max/all>"
            print(line)
            exit(1)
        else:
            out = chs.set_req(sys.argv)
            create_html_page(qtype=out['qtype'], msid_list=out['msid_list'],\
                             ds=out['ds'], ms=out['ms'])
    else:
        create_html_page(1)
