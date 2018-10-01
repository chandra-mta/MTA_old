#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
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
#
#--- set directory path
#
d_dir  = '/data/mta4/www/DAILY/mta_deriv/'

#---------------------------------------------------------------------------------

def set_trend_data_input(tdate):

    title = find_input_title(tdate)
#
#--- msid lists
#
    title  = title.replace(' ', '_')
    ltitle = title.lower()

    file = '/data/mta/Script/Weekly/Templates/Headers/Dsave/' +  str(ltitle)
    f= open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- read header file
#
    file = '/data/mta/Script/Weekly/Templates/Headers/' +  str(title)
    f= open(file, 'r')
    hdata = [line.strip() for line in f.readlines()]
    f.close()

    chk = 0
    hdict = {}
    for ent in hdata:
        if chk == 0:
            atemp = re.split('.html', ent)
            fname = atemp[0]
            line = ''
            chk = 1
        else:
            if ent == "":
                hdict[fname] = line + '\n\n'
                chk = 0
                continue
            else:
                line = line + ent + '\n'



    out = '' 
    for ent in data:
        atemp     = re.split('<>', ent)
        msid_list = re.split(':', atemp[1])

        infile    = d_dir + atemp[0]
        f         = open(infile, 'r')
        tdata     = [line.strip() for line in f.readlines()]
        f.close()

        btemp     = re.split('.html', atemp[0])

        save = hdict[btemp[0]]
        for msid in msid_list:
            chk = 0
            for line in tdata:
                if chk == 0:
                    mc  = re.search(msid, line)
                    if mc is not None:
                        save = save +  line + '\n'
                        chk += 1
                else:
                    save = save + line + '\n'
                    chk += 1
                    if chk >= 7:
                        break
        out = out + save
        out = out + '</table>\n</ul >\n<br />\n\n\n'

    fo = open('./out', 'w')
    fo.write(out)
    fo.close()

#---------------------------------------------------------------------------------

def find_input_title(tdate):

#
#--- find trending dates/title
#
    f= open('/data/mta/Script/Weekly/Templates/trending_order', 'r')
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

    return title


#---------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        tdate = sys.argv[1]

    set_trend_data_input(tdate)

