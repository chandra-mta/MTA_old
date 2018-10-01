#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################################
#                                                                                                                       #
#       create_fornt_history_files.py: create combined front side ccds history files                                    #
#                                                                                                                       #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                                                           #
#                                                                                                                       #
#                   last update: May 11, 2016                                                                           #
#                                                                                                                       #
#########################################################################################################################

import os
import sys
import re
import string
import random
import operator
import math

path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'

f    = open(path, 'r')
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
import convertTimeFormat      as tcnv       #---- contains MTA time conversion routines
import mta_common_functions   as mcf        #---- contains other functions commonly used in MTA scripts

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------------------------------------------
#-- create_fornt_history_files: create combined front side ccds history files                                 ---
#----------------------------------------------------------------------------------------------------------------

def create_fornt_history_files():
    """
    create combined front side ccds history files
    input:  none but read from indivisual ccd history files
    output: front_side_<part><ccd#>
    """

    for part in ('ccd', 'col', 'hccd'):
        for ccd in (0, 1, 2, 3, 4, 6, 8, 9):
            infile = '/data/mta/Script/ACIS/Bad_pixels/Data/Disp_dir/' + part + str(ccd) + '_cnt'
            f      = open(infile, 'r')
            data   = [line.strip() for line in f.readlines()]
            f.close()
            adict = {}
            date  = []
            for ent in data:
                atemp = re.split('<>', ent)
                date.append(int(atemp[0]))
                dlist = [atemp[1], int(atemp[2]), int(atemp[3]), int(atemp[4]), int(atemp[5])]
                adict[atemp[0]] = dlist
    
    
            exec 'dict_%s = adict' % (str(ccd))
    
        line = ''
        for ent in date:
            a1 = 0
            a2 = 0
            a3 = 0
            a4 = 0
            for ccd in (0, 1, 2, 3, 4, 6, 8, 9):
                exec 'tdict = dict_%s' % (str(ccd))
                out = tdict[str(ent)]
                a1 += int(out[1])
                a2 += int(out[2])
                a3 += int(out[3])
                a4 += int(out[4])
    
                date = out[0]
    
    
            line = line +  str(ent) +'<>' + date + '<>' + str(a1) + '<>' + str(a2)+ '<>' + str(a3)+ '<>' + str(a4) + '\n'
    
        name = '/data/mta/Script/ACIS/Bad_pixels/Data/Disp_dir/front_side_' + part + '_cnt'
        fo = open(name, 'w')
        fo.write(line)
        fo.close()


#----------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_fornt_history_files()


