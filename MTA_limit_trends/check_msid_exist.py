#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time


if len(sys.argv) > 1:
    msid = sys.argv[1]

else:
    print("msid??")

try:
    #out = fetch.MSID(msid, '2017:001:00:00:00', '2017:002')
    out = fetch.MSID(msid, '2000:060:00:00:00', '2000:062:00:00:00')
    tdata  = out.vals
    print("I AM HERE: " + str(tdata))
except:
    print("msid is not in the database")

