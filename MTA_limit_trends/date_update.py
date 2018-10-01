#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       date_update.py: update html page footer date to today                   #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Feb 07, 2018                                           #
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
f     = open(ifile, 'r')
text  = f.read()
f.close()

text  = text.replace('#TODAY#', today)

ofile = template_dir + 'html_close'
fo    = open(ofile, 'w')
fo.write(text)
fo.close()


