#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#################################################################################################
#                                                                                               #
#   read_mta_limits_db.py: read mta_limit_db  and return yellow and red lower and upper limits  #
#               ---- copied from mta envelope page                                              #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: May 16, 2019                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import random
import math
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf      #---- mta common functions
import envelope_common_function as ecf
#
#--- general end time
#
etime = 3218831995      #---- 2100:001:00:00:00

#-----------------------------------------------------------------------------------
#-- read_mta_limits_db: read mta_limit_databse  and return yellow and red lower and upper limits 
#-----------------------------------------------------------------------------------

def read_mta_limits_db():
    """
    read mta_limit_databse  and return yellow and red lower and upper limits
    input:  msid        --- msid
    output: ldict       --- a dictionary of msid <---> a list of lists of:
                                stime   --- starting time in seconds from 1998.1.1
                                ntime   --- ending time in seconds from 1998.1.1
                                y_min   --- lower yellow limit
                                y_max   --- upper yellow limit
                                r_min   --- lower red limit
                                r_max   --- upper red limit
    """
    efile = mlim_dir  + 'op_limits.db'
    data  = mcf.read_data_file(efile)

    ldict  = {}
    s_list = []
    prev   = ''
    for ent in data:
        if ent == '':
            continue

        line = str(ent)
        if line[0] == '#':
            continue

        atemp = re.split('\s+', ent)
        for m in range(0, len(atemp)):
            atemp[m] = atemp[m].replace('.0.0', '.0')

        msid  = atemp[0].lower()
        stime = int(float(atemp[5]))

        yl    = float(atemp[1])
        yl    =  round_up(yl)

        yu    = float(atemp[2])
        yu    =  round_up(yu)

        rl    = float(atemp[3])
        rl    =  round_up(rl)

        ru    = float(atemp[4])
        ru    =  round_up(ru)
#
#--- the current msid is the same as the previous one; so replace the end time in the last data
#--- and save it in the list
#
        if msid == prev:
            tlist[1] = stime
            s_list.append(tlist)

            tlist = [stime, etime, yl, yu, rl, ru]
        else:
#
#--- the first time, just set up the prev and tlist
#
            if prev == '':
                prev = msid
#
#--- msid changed; so save the previous msid limit data in the dictionary
#
            else:
                s_list.append(tlist)
                ldict[prev] = s_list
                prev   = msid
                s_list = []

            tlist = [stime, etime, yl, yu, rl, ru]

    return ldict

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

def round_up(val):
    """
    round out the value in two digit
    input:  val --- value
    output: val --- rounded value
    Note: this is same as that of in envelope_common_function, but it also call a function
          in this set of scripts and cannot use round_up function there.
    """
    try:
        dist = int(math.log10(abs(val)))
        if dist < -2:
            val *= 10 ** abs(dist)
    except:
        dist = 0
    
    val = "%3.2f" % (round(val, 2))
    val = float(val)
    
    if dist < -2:
        val *= 10**(dist)
    
    return val

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#------------------------------------------------------------

    def test_read_mta_limits_db(self):

        mdict  = read_mta_limits_db()

        comp =  [84585599, 118627199, 141.0, 168.0, 131.0, 183.06]
        msid = '1crbt'
        out  = mdict[msid]
        self.assertEquals(out[1], comp)

        msid = 'oobthr07'
        comp = [573227507, 3218831995, 321.15, 333.15, 264.15, 368.15]
        out  = mdict[msid]
        self.assertEquals(out[3], comp)

        msid = 'airu1g2t'
        out  = mdict[msid]
        print(str(out))

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    unittest.main()
