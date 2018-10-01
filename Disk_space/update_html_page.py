#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       update_html_page.py: update disk space html page                        #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Jul 31, 2014                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string

#
#--- reading directory list
#
path = '/data/mta/Script/Disk_check/house_keeping/dir_list_py'
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
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def update_html_page():
#
#--- today's date
#
    today   = tcnv.currentTime('local')
    year    = today[0]
    month   = today[1]
    day     = today[2]

    update  = 'Last Update: ' + str(month) + '/' + str(day) + '/' + str(year)


#    line = house_keeping + 'disk_space_backup.html'
    line = house_keeping + 'disk_space_backup_py.html'
    f    = open(line, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    line = web_dir + 'disk_space.html'
    f    = open(line, 'w')
    for ent in data:
        m = re.search('Last Update', ent)
        if m is not None:
            f.write(update)
        else:
            f.write(ent)

        f.write('\n')
    f.close()


#--------------------------------------------------------------------

if __name__ == '__main__':

    update_html_page()
