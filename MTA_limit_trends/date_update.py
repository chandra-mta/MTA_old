#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#################################################################################
#                                                                               #
#       date_update.py: update html page footer date to today                   #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: May 17, 2019                                           #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import time

mon = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

template_dir = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/Templates/'

pmon  = int(float(time.strftime(" %m", time.gmtime())))

today =  mon[pmon-1] + time.strftime(" %d, %Y", time.gmtime())

ifile = template_dir + 'html_close_template'
with open(ifile, 'r') as f:
    text  = f.read()

text  = text.replace('#TODAY#', today)

ofile = template_dir + 'html_close'
with  open(ofile, 'w')as fo:
    fo.write(text)


