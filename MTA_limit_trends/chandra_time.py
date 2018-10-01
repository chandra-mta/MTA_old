#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#           chandra_time.py: compute Chandra time                               #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update Feb 21, 2018                                        #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import time
import numpy
import Chandra.Time

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

def chandra_time(stime):

    if stime == '':
        print "Input: <yyyy>:<ddd>:<hh>:<mm>:<ss> or seconds from 1998.1.1"
        exist(1)

    mc = re.search(':', stime)

    if mc is not None:
        date = Chandra.Time.DateTime(stime).secs
    else:
        temp   = Chandra.Time.DateTime(float(stime))
        year   = str(temp.year)
        ydate  = temp.yday
        cydate = str(ydate)

        if ydate < 10:
            cydate = '00' + cydate
        elif ydate < 100:
            cydate = '0'  + cydate
        
        chh  = adjust_digit(temp.hour)
        cmm  = adjust_digit(temp.min)
        css  = adjust_digit(temp.sec)

        date = year + ':' + cydate + ':' + chh + ':' + cmm + ':' + css


    print date
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

def adjust_digit(val):

    cval = str(val)
    if val < 10:
        cval = '0' + cval

    return cval

#---------------------------------------------------------------------------------

if __name__ == "__main__":

        stime = sys.argv[1]

        chandra_time(stime)

