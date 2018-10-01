#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################################
#                                                                                                                       #
#           create_history_file.py: create count history file and the information file                                  #
#                                                                                                                       #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                                                           #
#                                                                                                                       #
#                   last update: May 13, 2014                                                                           #
#                                                                                                                       #
#########################################################################################################################

import os
import sys
import re
import string
import random
import operator
import math

path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat      as tcnv       #---- contains MTA time conversion routines
import mta_common_functions   as mcf        #---- contains other functions commonly used in MTA scripts

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------------------------------------------
#--- create_history_file: create count history file and the information file                                  ---
#----------------------------------------------------------------------------------------------------------------

def create_history_file(head):

    """
    create count history file and the information file containing current bad entry information
    Input:  head                --- ccd, hccd, or col to indicate which data to handle
    Output: <head>_ccd<ccd>_cnt --- count history data:<dom><><year:ydate><><cumlative cnt><><cnt for the day>
            <head>_ccd<ccd>_information --- current information of the bad entries. For example,  list warm pixels, 
                                            flickering pixels, totally new pixels, and all past and current warm pixels.

    """

    for ccd in range(0, 10):
#
#--- read data file head is either ccd, hccd, or col
#
        file = data_dir + 'Disp_dir/hist_' + head + str(ccd)
        data = mcf.readFile(file)

        bad_dat_list = []                       #--- save all bad data as elements
        bad_dat_save = []                       #--- save all bad data as a list for each day

        dom   = []
        ydate = []
        dcnt  = []                              #--- keep discreate count history
        ccnt  = []                              #--- keep cumulative count history
        new   = []                              #--- keep totally new bad entries in the last 5 days
        pcnt  = 0
        k     = 0
        tot   = len(data)

        for ent in data:
#
#--- read only data entries written in a correct format: <dom><><year>:<ydate><>:<bad_data>...
#
            atemp = re.split('<>', ent)
            chk1  = mcf.chkNumeric(atemp[0])
            btemp = re.split(':', atemp[1])
            chk2  = mcf.chkNumeric(btemp[1])

            if (chk1 == True) and (int(atemp[0]) > 0)  and (chk2 == True) and (int(btemp[1]) > 0):
                dom.append(atemp[0])
                ydate.append(atemp[1])
#
#--- check the bad data is recorded for the given day
#
                if head == 'ccd' or head == 'hccd':
                    m1 = re.search('\(', atemp[2])
                else:
                    btemp = re.split(':', atemp[2])                 #--- case for warm columns
                    if mcf.chkNumeric(btemp[len(btemp) -1]):
                        m1 = 'OK'
                    else:
                        m1 = None

                if m1 is not None:
                    btemp = re.split(':', atemp[2])
                    if btemp != '':
                        dcnt.append(len(btemp))
#
#--- for the last five days, check whether there are any totally new bad entries exists
#
                    if k > tot - 5:
                        for test in btemp:
                            chk = 0
                            for comp in bad_dat_list:
                                if test == comp:
                                    chk = 1
                                    continue
                            if chk == 0:
                                new.append(test)

                    bad_dat_list = bad_dat_list + btemp
                    out          = list(set(bad_dat_list))

                    pcnt         = len(out)
                    ccnt.append(pcnt)
                    bad_dat_save.append(btemp)
                else:
                    dcnt.append(0)
                    bad_dat_save.append([])
                    ccnt.append(pcnt)

            k += 1                                                  #--- k is inlimented to check the last 5 days
#
#--- find out which entries are warm/hot and flickering
#
        [warm, flick, b_list, p_list]=  find_warm_and_flickering(bad_dat_save)
#
#--- open output file to print current information
#
        line = data_dir + '/Disp_dir/'+ head + str(ccd) + '_information'
        fo   = open(line, 'w')

        fo.write("warm:\t")
        print_data(fo, warm)

        fo.write('flick:\t')
        print_data(fo, flick)

        fo.write('new:\t')
        out = list(set(new))
        print_data(fo, out)

        fo.write('past:\t')
        out = list(set(bad_dat_list))
        print_data(fo, out)

        fo.close()

#
#--- open output file to print out count history
#
        ofile = data_dir + 'Disp_dir/' + head + str(ccd) + '_cnt'
        fo    = open(ofile, 'w')

        for i in range(0, len(dom)):
            if i < 13:
                line = dom[i] + '<>' + ydate[i] + '<>' + str(ccnt[i]) + '<>'  + str(dcnt[i]) + '<>0<>0\n'
            else:
                line = dom[i] + '<>' + ydate[i] + '<>' + str(ccnt[i]) + '<>'  + str(dcnt[i]) + '<>'+ str(b_list[i-13]) + '<>' + str(p_list[i-13]) + '\n'

            fo.write(line)

        fo.close()

#-------------------------------------------------------------------------------------------------
#---  print_data: print out data                                                               ---
#-------------------------------------------------------------------------------------------------

def print_data(fo, data):

    """
    print out data
    Input:  fo      --- file hander
            data    --- data
    Output: data writting in the given format in the output file
    """

    tlen  = len(data)
    tlen1 = len(data) -1
    for i in range(tlen):
        if data[i] != '':
            fo.write(data[i])
            if i < tlen1:
                fo.write(' : ')
    fo.write('\n')



#-------------------------------------------------------------------------------------------------
#--- find_warm_and_flickering: determine which entries are bad or flickering                  ----
#-------------------------------------------------------------------------------------------------

def find_warm_and_flickering(rlist):

    """
    check the last two week amounts of data and determine which entries are bad or flickering
    if the data exit more than 70% of thetime, it is "warm" and if it exists more than 30% but less 
    than 70% of the time, it is flickering

    Input:      rlist   --- a list of list of bad entries separated by each dom
    Output:     warm    --- a list of warm entries
                flick   --- a list of flickering entries
    """
    tlen  = len(rlist)
    tlen1 = len(rlist)

    bad_cnt_hist           = []
    potential_bad_cnt_hist = []
    for j in range(13, tlen1):
        start = j - 13
        stop  = j + 1

        pix_list = []
        for k in range(start, stop):
            if len(rlist[k]) > 0:
                pix_list = pix_list + rlist[k]
#
#--- select out unique entries
#
        oset = list(set(pix_list))
        olen = len(oset)

        if olen > 0:
            mlist = [0 for x in range(0, olen)]
            for i in range(0, olen):
#
#--- count how many times the same entry appears in the data set
#
                for ent in pix_list:

                    if oset[i] == ent:
                        mlist[i] += 1
#
#--- if the data appears more than 70% of the time, it is warm, 
#--- if it appears more than 30% but less than 70% of the time, it is flickering
#
        warm  = []
        flick = []
        for i in range(0, olen):
            if oset[i] != '':
                rate = float(mlist[i]) / 14.0
    
                if rate > 0.7:
                    warm.append(oset[i])
                elif rate > 0.3:
                    flick.append(oset[i])
#
#--- add to real and potential bad point count history
#
        bad_cnt_hist.append(len(warm))
        potential_bad_cnt_hist.append(len(flick))
#
#--- return only the latest warm pix (col), flickering pix( col) data and history data
#
    return (warm, flick, bad_cnt_hist, potential_bad_cnt_hist)


#-------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------

def combing_front_sides(head):

    for ccd in (0, 1, 2, 3, 4, 6, 8, 9):
        file = data_dir + '/Disp_dir/' + head + str(ccd) + '_cnt'
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        if ccd == 0:
            tlen  = len(data) 
            atemp = re.split('<>', data[tlen-1])
            tmax  = int(atemp[0]) + 1

            time = [ 0 for x in range(0, tmax)]
            cdat = [ 0 for x in range(0, tmax)]
            ddat = [ 0 for x in range(0, tmax)]
            bdat = [ 0 for x in range(0, tmax)]
            pdat = [ 0 for x in range(0, tmax)]

            for k in range(0, len(data)):
                atemp = re.split('<>', data[k])
                dom   = int(atemp[0])
                day   = atemp[0] + '<>' + atemp[1]
                time[dom] = day
                cdat[dom] = int(atemp[2])
                ddat[dom] = int(atemp[3])
                bdat[dom] = int(atemp[4])
                pdat[dom] = int(atemp[5])

        else:
            tlen =len(data)
            for k in range(0, tlen):
                atemp = re.split('<>', data[k])
                dom   = int(atemp[0])
                day   = atemp[0] + '<>' + atemp[1]
                if dom > tmax:
                    break

                time[dom] = day
                cdat[dom] += int(atemp[2])
                ddat[dom] += int(atemp[3])
                bdat[dom] += int(atemp[4])
                pdat[dom] += int(atemp[5])

    line = data_dir + './Disp_dir/fornt_side_' + head + '_cnt'
    fo   = open(line, 'w')

    prev = cdat[0]
    for i in range(0, tmax):
        if time[i] != 0:
            if cdat[i] > prev:
                cval = str(cdat[i])
                prev = cdat[i]
            else:
                cval = str(prev)
            line = str(time[i]) + '<>' + cval + '<>' + str(ddat[i]) + '<>' + str(bdat[i]) + '<>' + str(pdat[i]) + '\n'
            fo.write(line)

    fo.close()



#-------------------------------------------------------------

if __name__ == "__main__":

#
#--- warm pixel case
#
    head = 'ccd'
    create_history_file(head)
    combing_front_sides(head)
#
#--- hot pixel case
#
    head = 'hccd'
    create_history_file(head)
    combing_front_sides(head)
#
#--- warm column case
#
    head = 'col'
    create_history_file(head)
    combing_front_sides(head)

