#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################    
#                                                                                   #
#           find_new_dump.py: find unprocessed dmup files                           #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Nov 13, 2017                                               #
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
f       = open(infile, 'r')
plist   = [line.strip() for line in f.readlines()]
f.close()
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

f       = open(infile, 'r')
data    = [line.strip() for line in f.readlines()]
f.close()

fo      = open(ofile, 'w')
#
#---- find the data which are not processed yet and print out
#
chk   = 0
for ent in data:
    if chk == 0:
        if ent == last_entry:
            chk = 1
            continue
    else:
        line = ent + '\n'
        fo.write(line)

fo.close()



