#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           update_rejected_event_data.py: update rejected event data sets                                  #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           last update: Mar 04, 2019                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import numpy
import os.path
import time
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- read directory list
#
path = '/data/mta/Script/ACIS/Rej_events/Scripts/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(bin_dir)
#
#--- set a temporary file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------------------------------
#-- update_rejected_event_data: update rejected event data sets                                        --
#--------------------------------------------------------------------------------------------------------

def update_rejected_event_data():
    """
    update rejected event data sets
    input:  none but read from /dsops/ap/sdp/cache/*/acis/acis*stat1.fits
    output: <data_dir>/CCD<ccd>_rej.dat
    """
#
#--- find current data fits files available
#
    cmd    = 'ls /dsops/ap/sdp/cache/*/acis/acis*stat1.fits > ' + zspace
    os.system(cmd)
    f_list = read_data_file(zspace, remove=1)
#
#--- create a dictionary of obsid <---> fits file name
#
    s_dict = {}
    o_list = []
    for ent in f_list:
        atemp = re.split('acisf', ent)
        btemp = re.split('_', atemp[1])
        o_list.append(btemp[0])
        s_dict[btemp[0]] = ent
#
#--- a list of obsids already analyzied
#
    p_list = past_obsid_list()
#
#--- a list of obsids which are not analyzied
#
    n_list = numpy.setdiff1d(o_list, p_list)
#
#--- read the data from the new fits files and update the database
#
    for obsid in n_list:
        ifile = s_dict[obsid]
        extract_data(ifile, obsid)

#--------------------------------------------------------------------------------------------------------
#-- past_obsid_list: create a list of obsids which are already analyzed                                --
#--------------------------------------------------------------------------------------------------------

def past_obsid_list():
    """
    create a list of obsids which are already analyzed
    input: none but read from <data_dir>/CCD<ccd>_rej.dat
    output: o_list  --- a list of obsids
    """

    o_list = []
    for ccd in range(0, 10):
        ifile  = data_dir + 'CCD' + str(ccd) + '_rej.dat'
        out    = read_data_file(ifile)
#
#--- read only the last 20 obsids added
#
        for ent in out[-20:]:
            atemp = re.split('\s+', ent)
            o_list.append(atemp[-2])
#
#--- remove duplicate
#
    o_list = list(set(o_list))

    return o_list

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def extract_data(dfits, obsid):
    """
    update database
    input   dfits   --- fits file name
            obsid   --- obsid of the data
    output: <data_dir>/CCD<ccd>_rej.dat; new data are just appended to the existing database
    """
#
#--- open fits file and read out needed data sets
#
    f     = pyfits.open(dfits)
    data  = f[1].data
    f.close()

    evtsent   = data['evtsent']
    drop_amp  = data['drop_amp']
    drop_pos  = data['drop_pos']
    drop_grd  = data['drop_grd']
    thr_pix   = data['thr_pix']
    berr_sum  = data['berr_sum']
    ccd_id    = data['ccd_id']
    time      = data['time']
#
#--- separate the data into each ccds; not all ccds have the data
#
    s_evtsent   = []
    s_drop_amp  = []
    s_drop_pos  = []
    s_drop_grd  = []
    s_thr_pix   = []
    s_berr_sum  = []
    s_navg      = []
    for k in range(0, 10):
        s_evtsent.append([])
        s_drop_amp.append([])
        s_drop_pos.append([])
        s_drop_grd.append([])
        s_thr_pix.append([])
        s_berr_sum.append([])
        s_navg.append(0)

    for k in range(0, len(ccd_id)):
        s_evtsent[ccd_id[k]].append(evtsent[k])
        s_drop_amp[ccd_id[k]].append(drop_amp[k])
        s_drop_pos[ccd_id[k]].append(drop_pos[k])
        s_drop_grd[ccd_id[k]].append(drop_grd[k])
        s_thr_pix[ccd_id[k]].append(thr_pix[k])
        s_berr_sum[ccd_id[k]].append(berr_sum[k])
        s_navg[ccd_id[k]] += 1

    a_time = numpy.mean(time)
#
#--- if there are data,  take average and std of each data set for each ccd
#
    for k in range(0, 10):
        if len(s_evtsent[k]) == 0:
            #break 
            continue                                #----- 03/04/19 TI

        a_evtsent   = numpy.mean(s_evtsent[k])
        d_evtsent   = numpy.std(s_evtsent[k])
        a_drop_amp  = numpy.mean(s_drop_amp[k])
        d_drop_amp  = numpy.std(s_drop_amp[k])
        a_drop_pos  = numpy.mean(s_drop_pos[k])
        d_drop_pos  = numpy.std(s_drop_pos[k])
        a_drop_grd  = numpy.mean(s_drop_grd[k])
        d_drop_grd  = numpy.std(s_drop_grd[k])
        a_thr_pix   = numpy.mean(s_thr_pix[k])
        d_thr_pix   = numpy.std(s_thr_pix[k])
        a_berr_sum  = numpy.mean(s_berr_sum[k])
        d_berr_sum  = numpy.std(s_berr_sum[k])

        line = "%1.9e\t" % (a_time)
        line = line + "%5.2f\t" % (a_evtsent)
        line = line + "%5.2f\t" % (d_evtsent)
        line = line + "%5.2f\t" % (a_drop_amp)
        line = line + "%5.2f\t" % (d_drop_amp)
        line = line + "%5.2f\t" % (a_drop_pos)
        line = line + "%5.2f\t" % (d_drop_pos)
        line = line + "%5.2f\t" % (a_drop_grd)
        line = line + "%5.2f\t" % (d_drop_grd)
        line = line + "%5.2f\t" % (a_thr_pix)
        line = line + "%5.2f\t" % (d_thr_pix)
        line = line + "%5.2f\t" % (a_berr_sum)
        line = line + "%5.2f\t" % (d_berr_sum)
        line = line + "%8d\t"   % (s_navg[k])
        line = line + "%8d\t"   % (int(obsid)) + '\t'
        line = line + str(k)     + '\n'
#
#--- append the new data line to the database
#
        out  = data_dir + 'CCD' + str(k) + '_rej.dat'
        fo   = open(out, 'a')
        fo.write(line)
        fo.close()
    
#--------------------------------------------------------------------------------------------------------
#-- read_data_file: read data file and return a list of data                                           --
#--------------------------------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):
    """
    read data file and return a list of data
    input:  ifile   --- file name
            remove  --- if 1, remove the file after reading it
    output: data    --- a list of data
    """

    try:
        f    = open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        if remove == 1:
            cmd = 'rm ' + ifile
            os.system(cmd)
    except:
        data = []

    return data

#---------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_rejected_event_data()
