#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#   prep_for_test.py: prepare directories/files for test                                            #
#                                                                                                   #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                                   #
#                                                                                                   #
#       last update: Apr 11, 2013                                                                   #
#                                                                                                   #
#####################################################################################################

import sys
import os
import string
import re
import fnmatch

#
#--- reading directory list
#

path = '/data/mta/Script/Exposure/house_keeping/acis_dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def prep_for_test():

    cmd = 'mkdir ' + test_web_dir
    os.system(cmd)
    cmd = 'mkdir ' + test_data_out
    os.system(cmd)
    cmd = 'mkdir ' + test_plot_dir
    os.system(cmd)
    cmd = 'mkdir ' + test_img_dir
    os.system(cmd)
    cmd = 'mkdir ' + test_mon_dir
    os.system(cmd)
    cmd = 'mkdir ' + test_cum_dir
    os.system(cmd)
    cmd = 'cp  ' + cum_dir + 'ACIS_07_1999_12_2012*fits.gz ' + test_cum_dir
    os.system(cmd)

#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    prep_for_test()
