#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       acis_gain_update_html.py:  update the main html page and data tables                        #
#                                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                                   #
#               Last update: Apr 04, 2014                                                           #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string

#
#--- reading directory list
#
comp_test = 'live'
if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/Gain/house_keeping/dir_list_py_test'
else:
    path = '/data/mta/Script/ACIS/Gain/house_keeping/dir_list_py'

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

#---------------------------------------------------------------------------------------------------
#--  create_display_data_table: create a readable data table for html page                       ---
#---------------------------------------------------------------------------------------------------

def create_display_data_table():

    """
    create a readable data table for html page
    Input: none, but read from <data_dir>/ccd<ccd>_<node>
    Output: <web_dir>/ccd<ccd>_<node>
    """

    for ccd in range(0, 10):
        for node in range(0, 4):
            file    = 'ccd' + str(ccd) + '_' +  str(node)
            infile  = data_dir + file
            outfile = web_dir + 'Data/' + file

            f       = open(infile, 'r')
            data    = [line.strip() for line in f.readlines()]
            f.close()

            fo      = open(outfile, 'w')
#
#--- adding heading
#
            line    = "#\n#Date            Mn K alpha     Al K alpha     Ti K alpha       Slope   Sigma   Int     Sigma\n#\n"
            fo.write(line)
            for ent in data:
                atemp = re.split('\s+', ent)
                stime = int(atemp[0])
#
#--- converting the date into <mon> <year> form (e.g. May 2013)
#
                ltime = tcnv.axTimeMTA(stime)
                btemp = re.split(':', ltime)
                year  = btemp[0]
                [mon, mdate] = tcnv.changeYdateToMonDate(int(year), int(btemp[1]))
                lmon  = tcnv.changeMonthFormat(mon)
                line  = lmon + ' ' + year 
                for j in range(1, len(atemp)):
                    line = line + '\t' +  atemp[j]

                line = line + '\n'
                fo.write(line)
            fo.close()

#---------------------------------------------------------------------------------------------------
#--- update_main_page: update the main html page (replacing updated date)                        ---
#---------------------------------------------------------------------------------------------------

def update_main_page():

    """
    update the main html page (replacing updated date)
    Input: none, but read from <house_keeping>/acis_gain.html
    Output: <web_dir>/acis_gain.html
    """

    line = house_keeping + '/acis_gain.html'
    text = open(line, 'r').read()

    today = tcnv. currentTime('Display')

    text  = text.replace('#DATE#', today)

    file  = web_dir + '/acis_gain.html'
    fo    = open(file, 'w')
    fo.write(text)
    fo.close()

#-------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_display_data_table()
    update_main_page()

