#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_monthly_report.py: create monthly report tables                       #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Nov 04, 2014                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re

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
#--- Exposure related funcions shared
#

import exposureFunctions as expf

data_out = '/data/mta/www/mta_max_exp/Data/'

#--------------------------------------------------------------------------------------------------------
#-- acis_dose_monthly_report: create monthly report tables                                            ---
#--------------------------------------------------------------------------------------------------------

def acis_dose_monthly_report(year='NA', month='NA'):

    """
     create monthly report tables 
     input: year and month, if they are not given, the latest stat will be used
    """


#
#--- if year and/or month is not given, find the latest year month entry
#
    if year == 'NA' or month == 'NA':
        file = data_out + 'i_2_n_0_acc_out'
        f    = open(file, 'r')
        data  = [line.strip() for line in f.readlines()]
        f.close()

        line = data[len(data)-1]
        atemp = re.split('\s+|\t+', line)
        year = int(atemp[0])
        month= int(atemp[1])

    syear = str(year)
    smon  = str(month)
    if month < 10:
        smon = '0' + smon


    line = './monthly_diff_' + smon + '_' + syear
    f1 = open(line, 'w')

    line = './monthly_acc_'  + smon + '_' + syear
    f2 = open(line,  'w')

#
#--- convert month in digit to month in letter
#
    lmon = tcnv.changeMonthFormat(month)
    lmon = lmon.lower()
#
#--- find monthly stat
#
    diff = mon_dir + 'ACIS_' + smon + '_' + syear + '.fits.gz'
    (mean, std, min, max) = getstat(diff)
    line = 'ACIS_' + lmon + syear[2] + syear[3] + ' 6004901       '
    f1.write(line)
    line = '%3.3f         %3.3f           %3.1f     %4d\n\n' % (mean, std, min, max)
    f1.write(line)

#
#--- find cumulative stat
#
    acc  = cum_dir + 'ACIS_07_1999_'  + smon + '_' + syear + '.fits.gz'
    (mean, std, min, max) = getstat(acc)
    line = 'ACIS_total   6004901       '
    f2.write(line)
    line = '%3.3f         %3.3f           %3.1f   %6d\n\n' % (mean, std, min, max)
    f2.write(line)

#
#--- now print stat for each section
#

    for inst in ('i', 's'):
        for ccd in (2, 3):
            f1.write('\n')
            f2.write('\n')
            for node in (0, 1, 2, 3):
                file1 = data_out + inst + '_' + str(ccd) +  '_n_' + str(node) + '_dff_out'
                file2 = data_out + inst + '_' + str(ccd) +  '_n_' + str(node) + '_acc_out'
            
                f     = open(file1, 'r')
                data  = [line.strip() for line in f.readlines()]
                f.close()

                if year == 'NA' or month == 'NA':
                    line  = data[len(data)-1]
                    atemp = re.split('\s+|\t+', line)
                else:
                    for ent in data:
                        atemp = re.split('\s+|\t+', ent)
                        if int(atemp[0]) == year and int(atemp[1]) == month:
                            break


                line  = inst.upper() + str(ccd) + ' node ' + str(node) + '  262654\t'
                f1.write(line)
                line  = '%3.6f\t%3.6f\t%3.1f\t%5.1f\n' % (float(atemp[2]), float(atemp[3]), float(atemp[4]), float(atemp[6]))
                f1.write(line)

            
                f     = open(file2, 'r')
                data  = [line.strip() for line in f.readlines()]
                f.close()

                if year == 'NA' or month == 'NA':
                    line  = data[len(data)-1]
                    atemp = re.split('\s+|\t+', line)
                else:
                    for ent in data:
                        atemp = re.split('\s+|\t+', ent)
                        if int(atemp[0]) == year and int(atemp[1]) == month:
                            break

                line  = inst.upper() + str(ccd) + ' node ' + str(node) + '  262654\t'
                f2.write(line)
                line  = '%3.6f\t%3.6f\t%3.1f\t%5.1f\n' % (float(atemp[2]), float(atemp[3]), float(atemp[4]), float(atemp[6]))
                f2.write(line)

    f1.close()
    f2.close()

#--------------------------------------------------------------------------------------------------------
#-- getstat: compute stat for fits image                                                               --
#--------------------------------------------------------------------------------------------------------

def getstat(fits):

    """
    compute stat for fits image
    input: fits name
    output: (mean, std, min, max)
    """

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmstat ' + fits + ' centroid=no > ./ztemp'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    f    = open('./ztemp', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        m1 = re.search('min',   ent)
        m2 = re.search('max',   ent)
        m3 = re.search('mean',  ent)
        m4 = re.search('sigma', ent)

        if m1 is not None:
            atemp = re.split('\s+|\t+', ent)
            min   = float(atemp[1])

        if m2 is not None:
            atemp = re.split('\s+|\t+', ent)
            atemp = re.split('\s+|\t+', ent)
            max   = int(atemp[1])

        if m3 is not None:
            atemp = re.split('\s+|\t+', ent)
            mean  = float(atemp[1])

        if m4 is not None:
            atemp = re.split('\s+|\t+', ent)
            std   = float(atemp[1])

    return (mean, std, min, max)


#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    acis_dose_monthly_report(year='NA', month='NA')
