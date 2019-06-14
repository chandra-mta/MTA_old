#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#           find_new_dump.py: find unprocessed dmup files                           #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 20, 2019                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re

dea_dir = '/data/mta/Script/MTA_limit_trends/Scripts/DEA/'

infile  = dea_dir + 'past_dump_list'
infile2 = dea_dir + 'past_dump_list~'
ofile   = dea_dir + 'today_dump_files'
#
#--- read the list of the data already processed
#

with open(infile, 'r') as f:
    plist   = [line.strip() for line in f.readlines()]
#
#--- find the last entry
#
last_entry = plist[-1]

cmd = ' mv ' +  infile + ' ' + infile2
os.system(cmd)
#
#--- create the current data list
#
cmd = 'ls -rt /dsops/GOT/input/*Dump_EM*.gz > ' + infile
os.system(cmd)

with open(infile, 'r') as f:
    data    = [line.strip() for line in f.readlines()]

#
#---- find the data which are not processed yet and print out
#
chk   = 0
line  = ''
for ent in data:
    if chk == 0:
        if ent == last_entry:
            chk = 1
            continue
    else:
        line = line +  ent + '\n'

with open(ofile, 'w') as fo:
    fo.write(line)



