#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       acis_compute_stat: compute statistics for given month data                      #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Dec 03, 2014                                                      #
#                                                                                       #
#########################################################################################

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

path = '/data/mta/Script/Exposure/house_keeping/acis_dir_list'
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

sys.path.append(mta_dir)
sys.path.append(bin_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv
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

#-----------------------------------------------------------------------------------------------------------
#-- comp_stat: compute statistics and print them out                                                     ---
#-----------------------------------------------------------------------------------------------------------

def comp_stat(line, year, month, outfile, comp_test='NA'):

    """
    compute statistics and print them out
    input: command line, year, month, and output file name
           command line is used by dmcopy to extract a specific location 
           Example: ACIS_04_2012.fits.gz[1:1024,1:256]
    """

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmcopy ' + line + ' temp.fits clobber="yes"'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

#
#-- to avoid get min from outside of the edge of a CCD
#

###    try:
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimgthresh infile=temp.fits  outfile=zcut.fits  cut="0:1e10" value=0 clobber=yes'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#-- find avg, min, max and deviation
#
    [avg, minv, minp, maxv, maxp, dev] = extract_stat_result('zcut.fits')
#
#-- find the one sigma and two sigma count rate:
#
    [sigma1, sigma2, sigma3] = find_two_sigma_value('zcut.fits')

   
    print_stat(avg, minv, minp, maxv, maxp, dev, sigma1, sigma2, sigma3,  year, month, outfile, comp_test)

###    except:
###        pass

    os.system('rm temp.fits')


#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------

def find_two_sigma_value(fits_file):

    """
    """
#
#-- make histgram
#
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimghist infile=' + fits_file + '  outfile=outfile.fits hist=1::1 strict=yes clobber=yes'
    cmd  = cmd1 + cmd2 
    bash(cmd,  env=ascdsenv)

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmlist infile=outfile.fits outfile=' + zspace + ' opt=data'
    cmd  = cmd1 + cmd2 
    bash(cmd,  env=ascdsenv)

    f    = open(zspace, 'r')
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
###        try:
        atemp = re.split('\s+|\t+', ent)
        if mcf.chkNumeric(atemp[0]):
            hbin.append(float(atemp[1]))
            val = int(atemp[4])
            hcnt.append(val)
            vsum += val
###        except:
###            pass

#
#--- checking one sigma and two sigma counts
#

    if len(hbin) > 0:
        v68    = int(0.68 * vsum)
        v95    = int(0.95 * vsum)
        v99    = int(0.997 * vsum)
        sigma1 = -999
        sigma2 = -999
        sigma3 = -999
        acc    = 0
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


#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------

def extract_stat_result(file):

    """
    extract stat informaiton:
    Input:  file    --- image fits file 
    Output: avg
            minp
            maxp
            devp 
    """
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmstat infile=' + file + '  centroid=no >' + zspace
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    mcf.rm_file(zspace)

#
#--- extract mean, dev, min, and max
#
    for  ent in data:
        atemp = re.split('\s+|\t+', ent)

        m1 = re.search('mean', ent)
        m2 = re.search('min',  ent)
        m3 = re.search('max',  ent)
        m4 = re.search('sigma',ent)

        if m1 is not None:
            avg   = atemp[1]

        if m2 is not None:
            minv   = atemp[1]
            btemp = re.split('\(', ent)
            ctemp = re.split('\s+|\t+', btemp[1])
            minp  = '(' + ctemp[1] + ',' + ctemp[2] + ')'

        if m3 is not None:
            maxv   = atemp[1]
            btemp = re.split('\(', ent)
            ctemp = re.split('\s+|\t+', btemp[1])
            maxp  = '(' + ctemp[1] + ',' + ctemp[2] + ')'

        if m4 is not None:
            dev = atemp[1]

    return [avg, minv, minp, maxv,  maxp, dev]

#-----------------------------------------------------------------------------------------------------------
#-- print_stat: print out statistic                                                                      ---
#-----------------------------------------------------------------------------------------------------------

def print_stat(avg, minv, minp, maxv, maxp, dev, sigma1, sigma2, sigma3, year, month, outfile, comp_test ='NA'):

    """
    print out statistic
        input: result and result2 (output of dmstat)
               year, month
               outfile: the name of output file
    """

#
#--- print out data
#

    if comp_test == 'test':
        line = test_data_out + outfile
    else:
        line = data_out + outfile

    f    = open(line, 'a')

    line = '%i\t%i\t'       % (year, month)
    line = line + '%5.6f\t%5.6f\t' % (float(avg), float(dev))
    line = line + '%5.1f\t%s\t'    % (float(minv), minp)
    line = line + '%5.1f\t%s\t'    % (float(maxv), maxp)
    line = line + '%5.1f\t%5.1f\t%5.1f\n'    % (float(sigma1), float(sigma2), float(sigma3))
    f.write(line)
    f.close()


#-----------------------------------------------------------------------------------------------------------
#--- acis_dose_extract_stat_data_month: driving fuction to compute statistics                            ---
#-----------------------------------------------------------------------------------------------------------


def acis_dose_extract_stat_data_month(year='NA', month='NA', comp_test = 'NA'):

    """
    driving fuction to compute statistics
    input: year and month
    """
#
#--- set different output directories for test
#
    if comp_test == 'test':
        tmon_dir = test_mon_dir
        tcum_dir = test_cum_dir
    else:
        tmon_dir = mon_dir
        tcum_dir = cum_dir

    if year == 'NA' or month == 'NA':

        year  = raw_input("Year: ")
        year  = int(year)
        month = raw_input('Month: ')
        month = int(month)


    syear = str(year)
    smon  = str(month)
    if month < 10:
        smon = '0' + smon

#
#--- ACIS I2
#
    name1 = tcum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_i2.fits.gz'
    name2 = tmon_dir + 'ACIS_' + smon + '_' + syear + '_i2.fits.gz'

    line    = name1 + '[1:1024,1:256]'
    outfile = 'i_2_n_0_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:1024,1:256]'
    outfile = 'i_2_n_0_dff_out'
    comp_stat(line, year, month, outfile, comp_test)


    line    = name1 + '[1:1024,257:508]'            #--- the last few columns are dropped 
    outfile = 'i_2_n_1_acc_out'                     #--- to avoid bad pixles at the edge
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:1024,257:508]'
    outfile = 'i_2_n_1_dff_out'
    comp_stat(line, year, month, outfile, comp_test)


    line    = name1 + '[1:1024,513:768]'
    outfile = 'i_2_n_2_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:1024,513:768]'
    outfile = 'i_2_n_2_dff_out'
    comp_stat(line, year, month, outfile, comp_test)


    line    = name1 + '[1:1024,769:1020]'
    outfile = 'i_2_n_3_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:1024,769:1020]'
    outfile = 'i_2_n_3_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

#
#--- ACIS I3
#
    name1 = tcum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_i3.fits.gz'
    name2 = tmon_dir + 'ACIS_' + smon + '_' + syear + '_i3.fits.gz'

    line    = name1 + '[1:1024,769:1020]'
    outfile = 'i_3_n_0_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:1024,769:1020]'
    outfile = 'i_3_n_0_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[1:1024,513:768]'
    outfile = 'i_3_n_1_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:1024,513:768]'
    outfile = 'i_3_n_1_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[1:1024,257:508]'
    outfile = 'i_3_n_2_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:1024,257:508]'
    outfile = 'i_3_n_2_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[1:1024,1:256]'
    outfile = 'i_3_n_3_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:1024,1:256]'
    outfile = 'i_3_n_3_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

#
#--- ACIS S2
#
    name1 = tcum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_s2.fits.gz'
    name2 = tmon_dir + 'ACIS_' + smon + '_' + syear + '_s2.fits.gz'

    line    = name1 + '[1:256,1:1020]'
    outfile = 's_2_n_0_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:256,1:1020]'
    outfile = 's_2_n_0_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[257:508,1:1020]'
    outfile = 's_2_n_1_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[257:508,1:1020]'
    outfile = 's_2_n_1_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[513:768,1:1020]'
    outfile = 's_2_n_2_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[513:768,1:1020]'
    outfile = 's_2_n_2_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[769:1024,1:1020]'
    outfile = 's_2_n_3_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[769:1024,1:1020]'
    outfile = 's_2_n_3_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

#
#--- ACIS S3
#
    name1 = tcum_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_s3.fits.gz'
    name2 = tmon_dir + 'ACIS_' + smon + '_' + syear + '_s3.fits.gz'

    line    = name1 + '[1:256,1:1020]'
    outfile = 's_3_n_0_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[1:256,1:1020]'
    outfile = 's_3_n_0_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[257:508,1:1020]'
    outfile = 's_3_n_1_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[257:508,1:1020]'
    outfile = 's_3_n_1_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[513:768,1:1020]'
    outfile = 's_3_n_2_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[513:768,1:1020]'
    outfile = 's_3_n_2_dff_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name1 + '[769:1024,1:1020]'
    outfile = 's_3_n_3_acc_out'
    comp_stat(line, year, month, outfile, comp_test)

    line    = name2 + '[769:1024,1:1020]'
    outfile = 's_3_n_3_dff_out'
    comp_stat(line, year, month, outfile, comp_test)




#--------------------------------------------------------------------------------------------------------

if len(sys.argv) == 3:
    year = sys.argv[1] 
    year = int(year)
    mon  = sys.argv[2]
    mon  = int(mon)
else:
    year = 'na'
    mon  = 'na'

if __name__ == '__main__':
    
    acis_dose_extract_stat_data_month(year, mon)
