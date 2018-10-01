#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#       create_interactive_page.py: create interactive html page for a given msid   #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 14, 2018                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time


#
#--- interactive plotting module
#
import mpld3
from mpld3 import plugins, utils
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat        as tcnv #---- contains MTA time conversion routines
import mta_common_functions     as mcf  #---- contains other functions commonly used in MTA scripts
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import update_database_suppl    as uds  #---- supplemental functions to get data
import create_html_suppl        as chs  #---- supplemental functions to crate html page
#import glimmon_sql_read         as gsr  #---- glimmon database reading
#import violation_estimate_data  as ved  #---- save violation estimated times in sqlite database v_table
#import find_moving_average      as fma  #---- moving average 
#import find_moving_average_bk   as fmab #---- moving average (backword fitting version)
#import robust_linear            as rfit #---- robust fit rountine
#import create_derivative_plots  as cdp  #---- create derivative plot
#
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- other settings
#
na     = 'na'
#
#--- read category data
#
cfile         = house_keeping + 'sub_html_list_all'
category_list = ecf.read_file_data(cfile)
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

web_address = 'https://' + web_address

#-------------------------------------------------------------------------------------------
#-- create_interactive_page: update all msid listed in msid_list                                 --
#-------------------------------------------------------------------------------------------

def create_interactive_page(msid, group, start, stop, step):
    """
    create an interactive html page for a given msid
    input:  msid    --- msid
            group   --- group name
            start   --- start time
            stop    --- stop time
            step    --- bin size in seconds
    """
    start = ecf.check_time_format(start)
    stop  = ecf.check_time_format(stop)
#
#--- create msid <---> unit dictionary
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read mta database
#
    mta_db = ecf.read_mta_database()
#
#--- read mta msid <---> sql msid conversion list
#
    mta_cross = ecf.read_cross_check_table()
#
#--- get limit data table for the msid
#
    try:
        tchk  = ecf.convert_unit_indicator(udict[msid])
    except:
        tchk  = 0

    glim  = ecf.get_limit(msid, tchk, mta_db, mta_cross)
#
#--- extract data from archive
#
    chk = 0
    try:
        out     = fetch.MSID(msid, start, stop)
        tdata   = out.vals
        ttime   = out.times
    except:
#
#--- if no data in archive, try mta local database
#
        try:
            [ttime, tdata] = uds.get_mta_fits_data(msid, start, stop)
#
#--- if it is also failed, return the empty data set
#
        except:
            chk = 1
#
#--- only short_p can change step size (by setting "step")
#
    if chk == 0:
        [week_p, short_p, long_p] = uds.process_day_data(msid, ttime, tdata, glim,  step=step)
#
#--- try to find data from ska or mta local data base
#
        try:
            fits_data = create_inter_fits(msid, short_p)
#
#--- for the case, the data is mta special cases
#
        except:
            fits_data = 'na'
    else:
        fits_data = 'na'
#
#--- create interactive html page
#
    create_html_page(msid, fits_data, step)
#
#--- remove fits file
#
    if fits_data != 'na':
        cmd = 'rm -rf ' + fits_data
        os.system(cmd)

#-------------------------------------------------------------------------------------------
#-- create_inter_fits: update/create fits data files of msid                              --
#-------------------------------------------------------------------------------------------

def create_inter_fits(msid, gdata):
    """
    update/create fits data files of msid
    input:  msid    --- msid
            gdata   --- a list of 15 lists related to the data (see col below)
    output: <data_dir>/Interactive/<msid>+inter_data.fits
    """

    cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower', 'yupper', 'rlower', 'rupper', 'dcount',\
             'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

    out_dir = data_dir + 'Interactive/'
#
#--- make sure that the sub directory exists
#
    if not os.path.isdir(out_dir):
        cmd = 'mkdir ' + out_dir
        os.system(cmd)

    ofits = out_dir + msid + '_inter_data.fits'
    ecf.create_fits_file(ofits, cols, gdata)

    return ofits

#--------------------------------------------------------------------------------------------------------
#-- plotting starts here                                                                               --
#--------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------
#-- create_html_page: create indivisual html pages for all msids in database                           --
#--------------------------------------------------------------------------------------------------------

def create_html_page(msid, fits_data, bin_size):
    """
    """
    group = find_group_name(msid)

    try: 
        unit    = udict[msid]
        descrip = ddict[msid]
    except:
        unit    = ''
        descrip = ''
#
#--- pdata is  two dim array of data (see read_data for details). flist is sub category of each data set
#
    if fits_data == 'na':
        pout  = '<h1 style="padding-top:40px;padding-bottom:40px;">NO DATA FOUND</h1>\n'

    else:
        [pdata, byear] = chs.read_data(fits_data, msid, ltype='week', ptype='inter')
#
#--- create the plot
#
        plotname = web_dir + 'Interactive/' + msid + '_inter_avg.png'
    
        pout  = chs.create_trend_plots(msid, group, pdata, byear, unit, 'week', 'mid', plotname, 'inter')
#
#--- create html page
#
    ltype = 'week'
    mtype = 'mid'

    create_plot_html_page(msid, group, ltype, mtype,  descrip, pout, bin_size)

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def find_group_name(msid):

    fname = house_keeping + 'msid_list_all'
    data  = ecf.read_file_data(fname)

    group = ''
    for ent in data:
        atemp = re.split('\s+', ent)
        if atemp[0] == msid:
            group = atemp[1]
            break

    return group



#----------------------------------------------------------------------------------
#-- create_plot_html_page: create a html page to display the trend plot          --
#----------------------------------------------------------------------------------

def create_plot_html_page(msid, group, ltype, mtype, descrip, pout, bin_size):
    """
    create a html page to display the trend plot
    input:  msid        --- msid
            group       --- group name to which msid belongs
            ltype       --- week, short etc, but usually week for the interactive
            mtype       --- mid, max, min, but usually mid
            descrip     --- description of the msid
            pout        --- plot in html format' it is <blank> if this is a static version
    output: plot <web_dir>/Interactive/<msid>_tmin_avg.html
    """
#
#--- copy an empty page to the position so that the user won't get an error message
#
    hname = web_dir + 'Interactive/' + msid + '_inter_avg.html'

    cmd = 'cp ' + house_keeping + '/Templates/no_page_yet ' + hname
    os.system(cmd)
    cmd = 'chmod 777 ' + hname
    os.system(cmd)
#
#--- read javascript file
#
    jscript = chs.read_template('java_script_deposit')
#
#--- pop up limit table web address
#
    file_name = web_address + group +  '/Limit_table/' + msid + '_limit_table.html'
#
#--- start creating html page
#
    repl = [["#MSID#",  msid.upper()], ["#JAVASCRIPT#", jscript], ["#STYLE#", '']]
    out = chs.read_template('html_head', repl )
#
#--- title of the page 
#
    if bin_size == 0.0:
        out = out + '<h2>' + msid + ' <span style="font-size:90%;">(Full Resolution)</span></h2>'
    else:
        out = out + '<h2>' + msid + ' <span style="font-size:90%;">(Bin Size: ' +str(bin_size) +' sec)</span></h2>'
#
#--- popup limit table link
#
    out = out + '<div style="paddng-top:10px"><h3>'
    out = out + 'Open <a href="javascript:popitup(\'' + file_name + '\')" style="text-align:right">Limit Table</a>.'
    out = out + '</h3>\n'
    out = out + '</div>\n'
#
#--- interactive page case
#
    if (pout == False) or (str(pout) == 'na'):
        out = out + '<h3 style="padding-top:200px;padding-bottom:200px">No Data/No Plot</h3>'
    else:
        out = out +  '<div style="text-align:center;">'
        out = out +  pout
        out = out + '</div>'
#
#---- changing the time span, step etc again
#
    phpfile  = web_address + "Interactive/msid_data_interactive.php"
    int_note = web_address + 'interactive_note.html'

    out = out + '<div style="padding-bottom:10px;font-size:90%;">\n';
    out = out + '<h3>Change the Interactive Plot Parameters ('
    out = out + '<a href="javascript:popitup(\'' + int_note + '\')" style="text-align:right">Usage Note</a>'
    out = out + ')</h3>\n'
    out = out + '<form method="post" action=' + phpfile + '>\n'
    out = out + '<b>Starting Time:</b> <input type="text" name="tstart"  size=20>\n'
    out = out + '<b>Stopping Time:</b> <input type="text" name="tstop"  size=20>\n'
    out = out + '<b>Bin Size:</b>      <input type="text" name="binsize"  value=300.0 size=10>\n '

    out = out + '<input type="hidden" name="ltype" value="' + ltype + '">\n'
    out = out + '<input type="hidden" name="mtype" value="' + mtype + '">\n'
    out = out + '<input type="hidden" name="msid"  value="' + msid  + '">\n'
    out = out + '<input type="hidden" name="group" value="' + group + '">\n'
    out = out + '</br><span style="text-align:right;"><input type=submit name="submit" value="Submit"></span>\n'
    out = out + '<br />\n'
    out = out + '</form>\n'
    out = out + '</div>\n'


    out = out + chs.read_template('interact_descript')

#
#--- add the derivative plot
#
###    dplotname = web_dir + 'Interactive/' + msid + '_inters_avg_dev.png'
###
###    out = out + '<h3>Derivative Plot</h3>\n'
###    out = out + '<img src="' + dplotname + '" width=80%>'
#
#--- close html page
#
    out = out + chs.read_template('html_close')
#
#--- write out the html data
#
    mcf.rm_file(hname)
    fo = open(hname, 'w')
    fo.write(out)
    fo.close()

    cmd = 'chmod 777 ' + hname
    os.system(cmd)



#--------------------------------------------------------------------------------------------------------

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines


if __name__ == "__main__":

    if len(sys.argv) ==  5:
        msid   = sys.argv[1]
        group  = sys.argv[2]
        tstart = sys.argv[3]
        tstop  = sys.argv[4]
        step   = 300.0

        create_interactive_page(msid, group, tstart, tstop, step)

    elif len(sys.argv) == 6:
        msid   = sys.argv[1]
        group  = sys.argv[2]
        tstart = sys.argv[3]
        tstop  = sys.argv[4]
        step   = int(float(sys.argv[5]))

        create_interactive_page(msid, group, tstart, tstop, step)
    
    else:
        print "Usage: create_interactive_page.py <msid> <group> <start> <stop> <bin size> "

