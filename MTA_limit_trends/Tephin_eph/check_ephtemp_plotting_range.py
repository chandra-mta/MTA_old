#!/usr/bin/env /proj/sot/ska/bin/python

###########################################################################################################
#                                                                                                         #
#           check_ephtemp_plotting_range.py: check ephtemp plotting range                                 #
#                                                                                                         #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                     #
#                                                                                                         #
#           last update: Jan 31, 2018                                                                     #
#                                                                                                         #
###########################################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import numpy
import getopt
import os.path
import time
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- read argv
#
try:
    option, remainder = getopt.getopt(sys.argv[1:],'t',['test'])
except getopt.GetoptError as err:
     print str(err)
     sys.exit(2)

path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(mta_dir)
sys.path.append(bin_dir)

import convertTimeFormat        as tcnv #---- converTimeFormat contains MTA time conversion routines
import mta_common_functions     as mtac #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import glimmon_sql_read         as gsr  #---- glimmon database reading
import violation_estimate_data  as ved  #---- save violation estimated times in sqlite database v_table
import find_moving_average      as fma  #---- moving average 
import find_moving_average_bk   as fmab #---- moving average (backword fitting version)
import robust_linear            as rfit #---- robust fit rountine
import create_derivative_plots  as cdp  #---- create derivative plot
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

dir = '/data/mta4/Deriv/MTA_msid_trend/Data/Eleak/'
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------

def find_min_max():

    cmd = 'ls -d ' + dir + '* > ' + zspace
    os.system(cmd)
    d_list = ecf.read_file_data(zspace, remove=1)

    line = ''
    chk  = 0
    testmax = 8.4e6

    for ent in d_list:
        atemp = re.split('\/', ent)
        msid = atemp[-1]

        mc   = re.search('S', msid)
        if mc is not None:
            group = 'Ephkey'
        else:
            group = 'Ephtv'

        msid = msid.lower()

        cmd = 'ls  ' + ent + '/*.fits > ' + zspace
        os.system(cmd)
        f_list = ecf.read_file_data(zspace, remove=1)

        amin = 1.0e12
        amax = -1.0e12
        a97  = -1.0e12
        for fits in f_list:
            f    = pyfits.open(fits)
            data = f[1].data
            f.close()

            dout = data[msid]
            tmin = dout.min()
            tmax = dout.max()

            if tmin < amin:
                amin = tmin
            if tmax > amax:
                amax = tmax

            t97  = numpy.percentile(dout, 97)
            if t97 > a97:
                a97 = t97

        if group == 'Ephtv':

            cmin = str(float(int(round(amin, 1) -1)))
            cmax = str(float(int(round(amax, 1) -1)))

            if amin < 10 and amin > 0:
                line = line + msid + '\t' + group.capitalize() + '\t' + cmin + '\t\t' + cmax + '\t0.011\n'
            else:
                line = line + msid + '\t' + group.capitalize() + '\t' + cmin + '\t' + cmax + '\t0.011\n'

        else:
            if amax > testmax:
                chk = amax
            if a97 < 1000:
                cmax =  str(float(int(round(a97, 1) -1)))
                line = line + msid + group.capitalize() +  '\t-10.0\t' + cmax  + '\t0.011\n'
            else:
                cmax = str(float(int(round(a97, 1) -1)))
                line = line + msid + group.capitalize() +  '\t-100.0\t' + cmax  + '\t0.011\n'

    fo = open('./msid_list_eph_tephin', 'w')
    fo.write(line)
    fo.close()

    if chk > 0:
        print "Ephkey max increased: " + str(chk)





#------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    find_min_max()
