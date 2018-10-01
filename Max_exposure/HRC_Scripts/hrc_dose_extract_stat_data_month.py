#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       hrc_dose_extract_stat_data_month.py: extract statistics from HRC S and I files          #
#                               output is avg, min, max,                                        #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Oct 13, 2015                                                               #
#                                                                                               #
#       commented out full image statistics     Jan 04, 2016                                    #
#                                                                                               #
#################################################################################################

import sys
import os
import string
import re
import random

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')

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

#
#--- append path to a private folder
#

sys.path.append(bin_dir)
sys.path.append(mta_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv

#
#--- mta common functions
#

import mta_common_functions as mcf

#
#--- Exposure related funcions shared
#

import exposureFunctions as expf
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)


#--------------------------------------------------------------------------------------------------------------
#--- comp_stat: compute statistics for the hrc image and print out the result                                --
#--------------------------------------------------------------------------------------------------------------

def comp_stat(file, year, month, out):

    """
    compute statistics for the hrc image and print out the result: input: hrc image file, year, month, output file name.
    """

    chk = mcf.chkFile(file)        #--- checking whether the file exists

    if chk > 0:
#
#--- to avoid getting min value from the outside of the frame edge of a CCD, set threshold
#
        try:
            cmd1 = "/usr/bin/env PERL5LIB="
            cmd2 = ' /bin/nice -n15 dmimgthresh infile=' + file + ' outfile=zcut.fits  cut="0:1.e10" value=0 clobber=yes'
            cmd  = cmd1 + cmd2
            bash(cmd,  env=ascdsenv)
            cmd1 = "/usr/bin/env PERL5LIB="
            cmd2 = ' dmstat  infile=zcut.fits  centroid=no >' + zspace
            cmd  = cmd1 + cmd2
            bash(cmd,  env=ascdsenv)

            mcf.rm_file('./zcut.fits')

            f    = open(zspace, 'r')
            data = [line.strip() for line in f.readlines()]
            f.close()
        except:
            data = []
        
        val = 'NA'
        for ent in data:
            ent.lstrip()
            m = re.search('mean', ent)
            if m is not None:
                atemp = re.split('\s+|\t', ent)
                val   = atemp[1]
                break

        if val != 'NA':
            (mean,  dev,  min,  max , min_pos_x,  min_pos_y,  max_pos_x,  max_pos_y)  = readStat(zspace)
            mcf.rm_file(zspace)

            (sig1, sig2, sig3) = find_two_sigma_value(file)

        else:
            (mean,  dev,  min,  max , min_pos_x,  min_pos_y,  max_pos_x,  max_pos_y)  = ('NA','NA','NA','NA','NA','NA','NA','NA')
            (sig1, sig2, sig3) = ('NA', 'NA', 'NA')

    else:
        (mean,  dev,  min,  max , min_pos_x,  min_pos_y,  max_pos_x,  max_pos_y)  = ('NA','NA','NA','NA','NA','NA','NA','NA')
        (sig1, sig2, sig3) = ('NA', 'NA', 'NA')


#
#--- print out the results
#

    chk = mcf.chkFile(out)        #--- checking whether the file exists

    if chk > 0:
        f = open(out, 'a')
    else:
        f = open(out, 'w')


    if mean == 'NA':
        line = '%d\t%d\t' % (year, month)
        f.write(line)
        f.write('NA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\n')
    else:
        line = '%d\t%d\t' % (year, month)
        line = line +  '%5.6f\t%5.6f\t%5.1f\t(%d,%d)\t' % (float(mean), float(dev), float(min), float(min_pos_x), float(min_pos_y))
        line = line +  '%5.1f\t(%d,%d)\t%5.1f\t%5.1f\t%5.1f\n' % (float(max), float(max_pos_x), float(max_pos_y), float(sig1), float(sig2), float(sig3))
        f.write(line)

    f.close()


#--------------------------------------------------------------------------------------------------------------
#--- readStat:  dmstat output file and extract data values.                                                 ---
#--------------------------------------------------------------------------------------------------------------

def readStat(file):

    """
    read dmstat output file and extract data values. 
        input: file. output: (mean, dev, min, max, min_pos_x, min_pos_y, max_pos_x, max_pos_y)
    """

    mean      = 'NA'
    dev       = 'NA'
    min       = 'NA'
    max       = 'NA'
    min_pos_x = 'NA'
    min_pos_y = 'NA'
    max_pos_x = 'NA'
    max_pos_y = 'NA'

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        ent.lstrip()
        atemp = re.split('\s+|\t+', ent)
        m1 = re.search('mean',  ent)
        m2 = re.search('sigma', ent)
        m3 = re.search('min',   ent)
        m4 = re.search('max',   ent)

        if m1 is not None:
            mean = float(atemp[1])
        elif m2 is not None:
            dev  = float(atemp[1])
        elif m3 is not None:
            min  = float(atemp[1])
            btemp = re.split('\(', ent)
            ctemp = re.split('\s+|\t+', btemp[1])
            min_pos_x = float(ctemp[1])
            min_pos_y = float(ctemp[2])
        elif m4 is not None:
            max  = float(atemp[1])
            btemp = re.split('\(', ent)
            ctemp = re.split('\s+|\t+', btemp[1])
            max_pos_x = float(ctemp[1])
            max_pos_y = float(ctemp[2])

    return (mean, dev, min, max, min_pos_x, min_pos_y, max_pos_x, max_pos_y)

#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
        
def find_two_sigma_value(fits):
#
#-- make histgram
#
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimghist infile=' + fits + '  outfile=outfile.fits hist=1::1 strict=yes clobber=yes'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmlist infile=outfile.fits outfile=' + zspace + ' opt=data'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    
    f= open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)
#
#--- read bin # and its count rate
#
    hbin = []
    hcnt = []
    vsum = 0

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        if mcf.chkNumeric(atemp[0]):
            hbin.append(float(atemp[1]))
            val = int(atemp[4])
            hcnt.append(val)
            vsum += val

#
#--- checking one sigma and two sigma counts
#

    if len(hbin) > 0:
        v68= int(0.68 * vsum)
        v95= int(0.95 * vsum)
        v99= int(0.997 * vsum)
        sigma1 = -999
        sigma2 = -999
        sigma3 = -999
        acc= 0
        for i in range(0, len(hbin)):
            acc += hcnt[i]
            if acc > v68 and sigma1 < 0:
                sigma1 = hbin[i]
            elif acc > v95 and sigma2 < 0:
                sigma2 = hbin[i]
            elif acc > v99 and sigma3 < 0:
                sigma3 = hbin[i]
                break
    
        return (sigma1, sigma2, sigma3)
    
    else:
        return(0, 0, 0)

#--------------------------------------------------------------------------------------------------------------
#--- hrc_dose_extract_stat_data_month: compute HRC statistics                                               ---
#--------------------------------------------------------------------------------------------------------------

def hrc_dose_extract_stat_data_month(year='NA', month='NA', comp_test = 'NA'):

    """
    compute HRC statistics: input year, month
    """

    if year == 'NA' or month == 'NA':
        year  = raw_input('Year: ')
        month = raw_input('Month: ')
    
    year  = int(year)
    month = int(month)

    syear  = str(year)
    smonth = str(month)
    if month < 10:
        smonth = '0' + smonth
#
#---- test?
#
    if comp_test == 'test':
        dp_mon_dir_hrc      = test_mon_dir_hrc
        dp_cum_dir_hrc      = test_cum_dir_hrc
        dp_mon_dir_hrc_full = test_mon_dir_hrc_full
        dp_cum_dir_hrc_full = test_cum_dir_hrc_full
        dp_data_out         = test_data_out
        dp_data_out_hrc     = test_data_out_hrc
    else:
        dp_mon_dir_hrc      = mon_dir_hrc
        dp_cum_dir_hrc      = cum_dir_hrc
        dp_mon_dir_hrc_full = mon_dir_hrc_full
        dp_cum_dir_hrc_full = cum_dir_hrc_full
        dp_data_out         = data_out
        dp_data_out_hrc     = data_out_hrc
#
#--- center exposure map stat
#
    file = dp_cum_dir_hrc  + '/HRCS_08_1999_' + smonth + '_' + syear + '.fits.gz'
    out  = dp_data_out + '/hrcs_acc_out'
    comp_stat(file, year, month, out)

    file = dp_mon_dir_hrc + '/HRCS_'         + smonth + '_' + syear + '.fits.gz'
    out  = dp_data_out + '/hrcs_dff_out'
    comp_stat(file, year, month, out)

    file = dp_cum_dir_hrc  + '/HRCI_08_1999_' + smonth + '_' + syear + '.fits.gz'
    out  = dp_data_out + '/hrci_acc_out'
    comp_stat(file, year, month, out)

    file = dp_mon_dir_hrc + '/HRCI_'         + smonth + '_' + syear + '.fits.gz'
    out  = dp_data_out + '/hrci_dff_out'
    comp_stat(file, year, month, out)

#
#--- full exposure map stat
#

##    for i in range(0,10):
##        file = dp_cum_dir_hrc_full +  '/HRCS_09_1999_' + smonth + '_' + syear + '_'+ str(i) +  '.fits.gz'
##        out  = dp_data_out_hrc + '/hrcs_' + str(i) + '_acc_out'
##        comp_stat(file, year, month, out)
##
##        file = dp_mon_dir_hrc_full +  '/HRCS_' + smonth + '_' + syear + '_'+ str(i) +  '.fits.gz'
##        out  = dp_data_out_hrc + '/hrcs_' + str(i) + '_dff_out'
##        comp_stat(file, year, month, out)
##
##
##    for i in range(0,9):
##        file = dp_cum_dir_hrc_full +  '/HRCI_09_1999_' + smonth + '_' + syear + '_'+ str(i) +  '.fits.gz'
##        out  = dp_data_out_hrc + '/hrci_' + str(i) + '_acc_out'
##        comp_stat(file, year, month, out)
##
##        file = dp_mon_dir_hrc_full +  '/HRCI_' + smonth + '_' + syear + '_'+ str(i) +  '.fits.gz'
##        out  = dp_data_out_hrc + '/hrci_' + str(i) + '_dff_out'
##        comp_stat(file, year, month, out)


#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    year  = int(sys.argv[1])
    month = int(sys.argv[2])

    hrc_dose_extract_stat_data_month(year, month)
