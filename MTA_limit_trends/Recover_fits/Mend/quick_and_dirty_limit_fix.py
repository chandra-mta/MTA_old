#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       quick_and_dirty_limit_fix.py: quick and dirty limit fix on an exsiting data fits    #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Feb 16, 2018                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time

#------------------------------------------------------------------------------------------
#-- quick_and_dirty_limit_fix: quick and dirty limit fix on an exsiting data fits       ---
#------------------------------------------------------------------------------------------

def quick_and_dirty_limit_fix(fits, yl, yu, rl, ru, start, stop):
    """
    quick and dirty limit fix on an exsiting data fits
    input:  fits    --- fits file name
            yl      --- yellow lower limit
            yu      --- yellow upper limit
            rl      --- red lower limit
            ru      --- red upper limit
            start   --- starting time of change in seconds from 1998.1.1
            stop    --- stopping time of change in seconds from 1998.1.1
    output: updated_data.fits   --- updated fits file
    """

    f       = pyfits.open(fits)
    data    = f[1].data
    cols_in = f[1].columns
    cols    = cols_in.names
    f.close()


    time  = data['time']
    pchk  = [(time>start) & (time<stop)]

    for k in range(0, len(pchk[0])):

        if pchk[0][k] == True:
            data['ylimlower'][k] = yl
            data['ylimupper'][k] = yu
            data['rlimlower'][k] = rl
            data['rlimupper'][k] = ru

            data['ylower'][k]    = 0
            data['yupper'][k]    = 0
            data['rlower'][k]    = 0
            data['rupper'][k]    = 0


    dlist = []
    for col in cols:
        
        dcol = pyfits.Column(name=col, format='F', array=data[col])
        dlist.append(dcol)

    dcols = pyfits.ColDefs(dlist)
    tbhdu = pyfits.BinTableHDU.from_columns(dcols)
    tbhdu.writeto('updated_data.fits')

#------------------------------------------------------------------------------------------

if __name__ == '__main__':

    fits = sys.argv[1]
    yl   = float(sys.argv[2])
    yu   = float(sys.argv[3])
    rl   = float(sys.argv[4])
    ru   = float(sys.argv[5])
    start= float(sys.argv[6])
    stop = float(sys.argv[7])

    quick_and_dirty_limit_fix(fits, yl, yu, rl, ru, start, stop)
