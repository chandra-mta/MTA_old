#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#   hrc_prep_test.py: prepare directories/files for test                                            #
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

path = '/data/mta/Script/Exposure/house_keeping/hrc_dir_list'
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
    cmd = 'mkdir ' + test_web_dir + 'HRC/'
    os.system(cmd)
    cmd = 'mkdir ' + test_web_dir + 'mays/'
    os.system(cmd)
    cmd = 'mkdir ' + test_data_out
    os.system(cmd)
    cmd = 'mkdir ' + test_plot_dir
    os.system(cmd)
    cmd = 'mkdir ' + test_img_dir
    os.system(cmd)
    cmd = 'mkdir ' + test_data_out_hrc
    os.system(cmd)
    cmd = 'mkdir ' + test_mon_dir_hrc
    os.system(cmd)
    cmd = 'mkdir ' + test_cum_dir_hrc
    os.system(cmd)
    cmd = 'mkdir ' + test_hrc_full_data
    os.system(cmd)
    cmd = 'mkdir ' + test_mon_dir_hrc_full
    os.system(cmd)
    cmd = 'mkdir ' + test_cum_dir_hrc_full
    os.system(cmd)
    cmd = 'mkdir ' + test_mays_dir
    os.system(cmd)
    cmd = 'mkdir ' + test_mays_dir + 'Cumulative_hrc/'
    os.system(cmd)
    cmd = 'mkdir ' + test_mays_dir + 'Month_hrc/'
    os.system(cmd)
    cmd = 'mkdir ' + test_mays_dir + 'Data/'
    os.system(cmd)
    cmd = 'mkdir ' + test_mays_dir + 'Plots/'
    os.system(cmd)

    cmd = 'cp  ' + cum_dir_hrc + 'HRC*_08_1999_11_2012*fits.gz ' + test_cum_dir_hrc
    os.system(cmd)
    cmd = 'cp  ' + cum_dir_hrc_full + 'HRC*_09_1999_11_2012*fits.gz ' + test_cum_dir_hrc_full
    os.system(cmd)

#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    prep_for_test()
