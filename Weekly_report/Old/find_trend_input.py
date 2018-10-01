#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           set_up.py:  setting up weekly report template for the week                                      #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Sep 15, 2015                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import copy
import math
import Cookie
import unittest
import time
import random

#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folders
#
#sys.path.append(base_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)


#---------------------------------------------------------------------------------

def set_trend_data_input(tdate):

#
#--- find trending dates/title
#
    f= open('/data/mta/Script/Weekly/Temprate/trending_order', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    
    data.reverse()
    chk = 0
    for ent in data:
        if ent == '\s+' or ent == '':
            continue
    
        atemp = re.split(' : ', ent)
        adate = atemp[0].strip()
        adate = adate.replace('/', '')
        aname = atemp[1].strip()
    
        if chk == 0:
            if adate == tdate:
                title = aname
                chk   = 1
                break
#
#--- read trend input information
#
    f= open('/data/mta/Script/Weekly/Temprate/trend_input', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    
    title = title.replace(' ', '_')
    for ent in data:
        atemp = re.split('<>', ent)
        if atemp[0] == title:
            outname_list = re.split(':', atemp[1])
            name_list    = re.split(':', atemp[2])
            html_list    = re.split(':', atemp[3])
            if atemp[4] != '':
                note = '/data/mta/Script/Weekly/Temprate/Headers/' + atemp[4]
            else:
                note = ''
            break

#
#--- prep trend_input_file
#
    if note == '':
        line = ''
        for i in range(0, len(html_list)):
            line = line + outname_list[i] + '\n\n'
            line = line + name_list[i] + '\n'
            line = line + 'https://cxc.cfa.harvard.edu/mta/DAILY/mta_deriv/' + html_list[i] + '\n\n'
        fo = open('./trend_input_file', 'w')
        fo.write(line)
        fo.close()
    else:
        line = outname_list[0] + '\n\n'
        fo = open('./trend_input_file', 'w')
        fo.write(line)
        fo.close()
        cmd = 'cat ' + note + '>> ./trend_input_file'
        os.system(cmd)

#---------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        tdate = sys.argv[1]

    set_trend_data_input(tdate)

