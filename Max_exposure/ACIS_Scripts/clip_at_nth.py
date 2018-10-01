#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       clip_at_nth: set upper limit at nth brightest and chop the image at that value#
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
import fnmatch

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
import mta_common_functions as mtac

#
#--- Exposure related funcions shared
#

import exposureFunctions as expf


#-----------------------------------------------------------------------------------------------------------
#-- clip_at_nth: set upper limit at n th brightest and chop the image at that value                    ----
#-----------------------------------------------------------------------------------------------------------

def clip_at_nth(infits, cut=10):

    """
    set upper limit at nth brightest and chop the image at that value
    input: fits file, cut: n th brightest, default is 10th
    """

#
#--- trim the extreme values
#
    upper = find_nth(infits, cut)

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimgthresh infile=' + infits+ ' outfile=zout.fits cut="0:' + str(upper) + '" value=0 clobber=yes'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    outfile = infits.replace('.fits','_full.fits')
    cmd     = 'mv ' + infits + ' ' + outfile
    os.system(cmd)
    
    m = re.search('gz', infits)
    if m is not None:
        os.system('gzip zout.fits')
        cmd = 'mv zout.fits.gz ' + infits
        os.system(cmd)
    else:
        cmd = 'mv zout.fits ' + infits
        os.system(cmd)
            


#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------

def find_nth(fits_file = 'NA', cut= 10):

    """
    find nth brightest value    input: fits file/ cut = upper limit
    """

    if fits_file == 'NA':
        fits_file = raw_input('Fits file name: ')
        cut       = raw_input('Where to Cut?: ')
#
#-- make histgram
#
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmimghist infile=' + fits_file + '  outfile=outfile.fits hist=1::1 strict=yes clobber=yes'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 =' dmlist infile=outfile.fits outfile=./zout opt=data'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    f    = open('./zout', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    os.system('rm outfile.fits ./zout')
#
#--- read bin # and its count rate
#
    hbin = []
    hcnt = []

    for ent in data:
        try:
            atemp = re.split('\s+|\t+', ent)
            if (len(atemp) > 3) and mtac.chkNumeric(atemp[1])  and mtac.chkNumeric(atemp[2])  and (int(atemp[4]) > 0):
                hbin.append(float(atemp[1]))
                hcnt.append(int(atemp[4]))
        except:
            pass

#
#--- checking 10 th bright position
#
    limit = cut -1
    try:
        j = 0
        for i in  range(len(hbin)-1, 0, -1):
            if j == limit:
                val = i
                break
            else:
                if hcnt[i] > 0:                 #---- only when the value is larger than 0, record as count
                    j += 1

        return hbin[val]
    except:
        return 'I/INDEF'




#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    clip_at_nth()
    

