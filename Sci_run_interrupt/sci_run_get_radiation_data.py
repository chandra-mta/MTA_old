#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       sci_run_get_radiation_data.py: get NOAA data for radiaiton plots                #
#                                                                                       #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: apr 12, 2013                                               #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string

#
#--- reading directory list
#
path = '/data/mta/Script/Interrupt/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf

#-----------------------------------------------------------------------------------------------
#--- sci_run_get_radiation_data: extract radiation data                                      ---
#-----------------------------------------------------------------------------------------------

def sci_run_get_radiation_data():

    'extract needed radiation data from /data/mta4/www/DAILY/mta_rad/ACE/, and put in rada_data<YYYYY>, where YYYY is the year'
#
#--- find out today's date in Local time frame
#

    if comp_test == 'test':
        year  = 2012
        month = 1
        day   = 2
    else:
        today = tcnv.currentTime('local')
        year  = today[0]
        month = today[1]
        day   = today[2]

    if month ==1 and day == 1:
#
#--- this is a new year... complete the last year
#
        year -= 1

#
#--- extract data form ACE data files
#

    line = '/data/mta4/www/DAILY/mta_rad/ACE/' + str(year) + '*_ace_epam_5m.txt'
    cmd  = 'cat ' + line + ' > /tmp/mta/ztemp'
    cmd  = 'cat ' + line + ' > ./ztemp'
    os.system(cmd)

    f = open('./ztemp', 'r');
    data  = [line.strip() for line in f.readlines()]
    f.close()

    os.system('rm ./ztemp')

#
#--- move the old file to "~" to prepare for the new data
#

    name    = 'rad_data' + str(year)

    if comp_test == 'test':
        crtFile = test_web_dir + name 
    else:
        oldFile = house_keeping + name + '~'
        crtFile = house_keeping + name 

        cmd     = 'chmod 775 ' + crtFile + ' ' +  oldFile
        os.system(cmd)

        cmd     = 'mv ' + crtFile + ' ' + oldFile
        os.system(cmd)
    
        cmd     = 'chmod 644 ' +  oldFile
        os.system(cmd)
    
    f = open(crtFile, 'w')   

    for ent in data:
#
#--- remove comments and headers
#
        m = re.search('^#', str(ent))
        n = re.search('^:', str(ent))
        if (m is  None) and (n is  None):
            line = ent + '\n'
            f.write(line)

    f.close()
            
#--------------------------------------------------------------------

if __name__ == '__main__':

#
#--- check whether this is a test case
#
    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':               #---- this is a test case
            comp_test = 'test'
        else:
            comp_test = 'real'
    else:
        comp_test = 'real'

#
#--- if this is a test case, check whether output file exists. If not, creaete it
#
    if comp_test == 'test':
        chk = mcf.chkFile(test_web_dir)
        if chk == 0:
            cmd = 'mkdir ' + test_web_dir
            os.system(cmd)

#
#--- now call the main function
#
    sci_run_get_radiation_data()


