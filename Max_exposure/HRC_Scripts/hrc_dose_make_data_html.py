#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       hrc_dose_make_data_html.py:   create  html data pages for a report              #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Jun 22, 2018                                                       #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re

#
#--- reading directory list
#

path = '/data/mta/Script/Exposure/house_keeping/hrc_dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append path to a privte folder
#

sys.path.append(bin_dir)
sys.path.append(mta_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv

#
#--- Exposure related funcions shared
#

import exposureFunctions as expf

#------------------------------------------------------------------------------------------------------------------------
#--- hrc_dose_plot_exposure_stat: read hrc database, and plot history of exposure                                     ---
#------------------------------------------------------------------------------------------------------------------------

def hrc_dose_make_data_html(indir = 'NA', outdir = 'NA', indir2 = 'NA', outdir2 = 'NA', comp_test = 'NA'):

    'read hrc database, and create html page: input: indir (data directory)'

#
#--- setting indir and outdir if not given
#
    if comp_test == 'test':
        indir   = test_data_out
        outdir  = test_data_out
        indir2  = test_data_out_hrc
        outdir2 = test_data_out_hrc
    else:
        if indir   == 'NA':
            indir   = data_out
    
        if outdir  == 'NA':
            outdir  = data_out
    
        if indir2  == 'NA':
            indir2  = data_out_hrc
    
        if outdir2 == 'NA':
            outdir2 = data_out_hrc

    for hrc in ('hrci', 'hrcs'):

#
#--- center exposure map --------
#

#
#--- just in a case, clear up the files before reading them
#
        expf.clean_data(indir)

#
#--- read HRC histrical data
#
        [date,year,month,mean_acc,std_acc,min_acc,min_apos, max_acc,max_apos,asig1, asig2, asig3, mean_dff,std_dff, \
                      min_dff, min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3] = expf.readExpData(indir,hrc)
        
#
#--- create a HTML page to display histrical data
#
        printHtml(indir, outdir,  hrc, date, year,month,mean_acc,std_acc,min_acc,min_apos,max_acc,max_apos, asig1, asig2, asig3, \
                           mean_dff,std_dff,min_dff,min_dpos,max_dff,max_dpos, dsig1, dsig2, dsig3)

#
#--- full exposure map --------
#

#
#--- just in a case, clear up the files before reading them
#
#        expf.clean_data(indir2)


        for i in range(0,10):
            if hrc == 'hrci' and i == 9:
                break

            hrc2 = hrc + '_' + str(i)           #--- naming is slightly different from the center exposure maps
#
#--- read HRC histrical data --- sec='full' indicating reading full exposure maps
#
            [date,year,month,mean_acc,std_acc,min_acc,min_apos, max_acc,max_apos,asig1, asig2, asig3, mean_dff,std_dff, \
                      min_dff, min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3] = expf.readExpData(indir2, hrc2)
#
#--- create a HTML page to display histrical data
#
            printHtml(indir2, outdir2, hrc2, date, year,month,mean_acc,std_acc,min_acc,min_apos,max_acc,max_apos, asig1, asig2, asig3, \
                           mean_dff,std_dff,min_dff,min_dpos,max_dff,max_dpos, dsig1, dsig2, dsig3)


#--------------------------------------------------------------------------------------------------------
#--  printHtml: create HTML page to display HRC historical data                                      ----
#--------------------------------------------------------------------------------------------------------

def printHtml(indir,outdir,  hrc, date, year,month,mean_acc,std_acc,min_acc,min_apos,max_acc,max_apos, asig1, asig2, asig3,mean_dff,  \
                std_dff,min_dff,min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3):

    'create HTML page to display HRC historical data.'


    [tyear, mon, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime("Local")

    smon = str(mon)
    if mon < 10:
        smon = '0' + smon

    sday = str(day)
    if day < 10:
        sday = '0' + sday

    outdir = outdir + '/' + hrc + '.html'

    f = open(outdir, 'w')
#
#--- this is a html 5 document
#
    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')

    f.write("<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />\n")

    f.write("<style  type='text/css'>\n")
    f.write("table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}\n")
    f.write("a:link {color:#00CCFF;}\n")
    f.write("a:visited {color:yellow;}\n")
    f.write("td{text-align:center;padding:8px}\n")
    f.write("</style>\n")


    if hrc == 'hrci':
        hname = 'HRC I'
        wname = 'HRCI'
    else:
        hname = 'HRC S'
        wname = 'HRCS'

    line = '<title>' + hname + ' History Data</title>\n'
    f.write(line)
    f.write("</head>\n")

    f.write('<body style="color:white;background-color:black">\n')
    line = '<h2 style="text-align:center">Data: ' + hname + '</h2>\n'
    f.write(line)

    f.write("<div style='padding-bottom:30px'>\n")
    f.write('<table border=1>\n')
    f.write('<tr><th>&#160;</th><th>&#160;</th><th colspan=11>Monlthy</th><th colspan=11>Cumulative</th></tr>\n')
    f.write('<tr style="color:yellow"><th>Year</th><th>Month</th>\n')
    f.write('<th>Mean</th><th>SD</th><th>Min</th><th>Min Position</th><th>Max</th><th>Max Position</th><th>68% Level</th><th>95% Level</th><th>99.7% Level</th><th>Data</th><th>Map</th>\n')
    f.write('<th>Mean</th><th>SD</th><th>Min</th><th>Min Position</th><th>Max</th><th>Max Position</th><th>68% Level</th><th>95% Level</th><th>99.7% Level</th><th>Data</th><th>Map</th></tr>\n')

    for i in range(0, len(date)):

        smonth = str(month[i])
        if month[i] < 10:
            smonth = '0' + smonth

        cmonth = tcnv.changeMonthFormat(month[i])        #---- converting digit to letters, i.e. 1 to Jan

#
#--- monthly HRC dose data
#

        if mean_dff[i] == 0 and std_dff[i] == 0:

            line = '<tr><td>%d</td><td>%d</td><td>NA</td><td>NA</td><td>NA</td><td>NA</td><td>NA</td><td>NA</td>\n' % (year[i], month[i])
            f.write(line)
            f.write('<td>NA</td><td>NA</td><td>NA</td><td>No Data</td><td>No Image</td>\n')
        else:
            line = '<tr><td>%d</td><td>%d</td><td>%4.4f</td><td>%4.4f</td><td>%4.1f</td><td>%s</td><td>%4.1f</td><td>%s</td><td>%4.1f</td><td>%s</td><td>%4.1f</td>\n' \
                    % (year[i], month[i], mean_dff[i], std_dff[i], min_dff[i],min_dpos[i], max_dff[i], max_dpos[i],dsig1[i], dsig2[i], dsig3[i])
            f.write(line)

            fname = wname + '_' + smonth + '_' + str(year[i]) + '.fits.gz'
            line  = '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Month_hrc/' + fname +'">fits</a></td>\n'
            f.write(line)
            fname = wname + '_' + smonth + '_' + str(year[i]) + '.png'
            line  = '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Images/' + fname + '">map</a></td>\n'
            f.write(line)

#
#---- cumulative HRC dose data
#
        line = '<td>%4.4f</td><td>%4.4f</td><td>%4.1f</td><td>%s</td><td>%4.1f</td><td>%s</td><td>%4.1f</td><td>%s</td><td>%4.1f</td>\n' \
                    % (mean_acc[i], std_acc[i], min_acc[i], min_apos[i], max_acc[i], max_apos[i], asig1[i], asig2[i], asig3[i])

        f.write(line)
        fname = wname + '_08_1999_' + smonth + '_' + str(year[i]) + '.fits.gz'
        line  = '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Cumulative_hrc/' + fname +'">fits</a></td>\n'
        f.write(line)
        fname = wname + '_08_1999_' + smonth + '_' + str(year[i]) + '.png'
        line  = '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Images/' + fname + '">map</a></td>\n\n'
        f.write(line)

#
#--- put header every new year so that we can read data easier
#
        if month[i] % 12 == 0 and i != (len(date)-1):
            f.write('\n<tr style="color:yellow"><th>Year</th><th>Month</th><th>Mean</th><th>SD</th><th>Min</th><th>Min Position</th><th>Max</th><th>Max Position</th><th>68% Level</th><th>95% Level</th><th>99.7% Level</th><th>Data</th><th>Map</th>\n')
            f.write('<th>Mean</th><th>SD</th><th>Min</th><th>Min Position</th><th>Max</th><th>Max Position</th><th>68% Level</th><th>95% Level</th><th>99.7% Level</th><th>Data</th><th>Map</th></tr>\n\n')

    f.write('</table>\n\n')
    f.write("</div>\n")
    f.write('<hr />\n')

    line = '<p style="padding-top:10px;padding-bottom:10px"><strong style="font-size:105%;float:right">Last Update: ' + smon + '/' + sday + '/' + str(tyear) + '</strong></p>\n'
    f.write(line)

    line = '<p>If you have any questions about this page, contact <a href="mailto:isobe@haed.cfa.harvad.edu">isobe@haed.cfa.harvad.edu.</a></p>\n'
    f.write(line)
    f.write('</body>\n')
    f.write('</html>\n')

    f.close()    


#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def update_main_html():

    [tyear, mon, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime("Local")
    
    today = str(mon) + '/' + str(day) + '/ ' +str(tyear)

    syear = tyear
    smon  = mon -1
    if smon < 1:
        smon  = 12
        syear = tyear -1

    lyear = str(syear)

    lmon  = str(smon)
    if smon < 10:
        lmon = '0' + lmon

    line = lmon + '_' + lyear

    file = hosue_keeping + 'template'
    data = open(file, 'r').read()
    data = data.replace('#LATEST#', line)
    data = data.replace('#DATE#',   today)

    file = web_dir + 'exposure.html'
    fo   = open(file, 'w')
    fo.write(data)
    fo.close()


#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    hrc_dose_make_data_html()
    update_main_html()
