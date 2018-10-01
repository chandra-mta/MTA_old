#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       sci_run_compute_gap.py: compute science time lost                               #
#                               (interuption total - radiation zone)                    #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Sep 12, 2017                                               #
#                                                                                       #
#########################################################################################

import sys
import os
import re
import string

#
#--- reading directory list
#

path = '/data/mta/Script/Interrupt/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a privte folder to python directory
#

sys.path.append(bin_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#

import convertTimeFormat as tcnv   

#----------------------------------------------------------------------------------------------------
#--- sci_run_compute_gap: for given data, recompute the science run lost time excluding rad zones ---
#----------------------------------------------------------------------------------------------------

def sci_run_compute_gap(file):
    """
    for a given file name which contains a list, recompute the lost science time (excluding radiation zone) 
    input:  file    --- the file containing information, e.g.:
        20120313        2012:03:13:22:41        2012:03:14:13:57         53.3   auto" 
    output: file    --- updated file
    """
#
#--- if file is not given (if it is NA), ask the file input
#
    test = exc_dir + file
    if not os.path.isfile(test):
        file = raw_input('Please put the intrrupt timing list: ')

    f = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()
#
#--- a starting date of the interruption in yyyy:mm:dd:hh:mm (e.g., 2006:03:20:10:30)
#--- there could be multiple lines of date; in that is the case, the scripts add the rad zone list
#--- to each date
#

    update = []

    for ent in data:

        if not ent:                         #--- if it is a blank line end the operation
            break

        etemp = re.split('\s+', ent)
        atemp = re.split(':', etemp[1])
        year  = atemp[0]
        month = atemp[1]
        date  = atemp[2]
        hour  = atemp[3]
        mins  = atemp[4]
#
#--- convert to dom/sec1998
#
        ydate = tcnv.findYearDate(int(year), int(month), int(date))
        dom   = tcnv.findDOM(int(year), int(ydate), int(hour), int(mins), 0)
        line  = year + ':' + str(ydate) + ':' + hour + ':' + mins + ':00'
        csec  = tcnv.axTimeMTA(line)                                       
#
#--- end date
#

        atemp  = re.split(':', etemp[2])
        eyear  = atemp[0]
        emonth = atemp[1]
        edate  = atemp[2]
        ehour  = atemp[3]
        emins  = atemp[4]

        ydate = tcnv.findYearDate(int(eyear), int(emonth), int(edate))
        dom2  = tcnv.findDOM(int(eyear), int(ydate), int(ehour), int(emins), 0)
        line  = eyear + ':' + str(ydate) + ':' + ehour + ':' + emins + ':00'
        csec2 = tcnv.axTimeMTA(line)
#
#--- date stamp for the list
#
        list_date = str(year) + str(month) + str(date)

#
#--- read radiation zone information from "rad_zone_list" and add up the time overlap with 
#--- radiatio zones with the interruption time period
#

        line  = house_keeping + '/rad_zone_list'
        f     = open(line, 'r')
        rlist = [line.strip() for line in f.readlines()]
        f.close()

        sum = 0
        for record in rlist:
            atemp = re.split('\s+', record)
            if list_date == atemp[0]:
                btemp = re.split(':', atemp[1])
                for period in btemp:

                    t1 = re.split('\(', period)
                    t2 = re.split('\)', t1[1])
                    t3 = re.split('\,', t2[0])
                    pstart = float(t3[0])
                    pend   = float(t3[1])

                    if pstart >= dom and  pstart < dom2:
                        if pend <= dom2:
                            diff = pend - pstart
                            sum += diff
                        else:
                            diff = dom2 - pstart
                            sum += diff
                    elif pstart < dom2 and pend > dom:
                        if pend <= dom2:
                            diff = pend - dom
                            sum += diff
                        else:
                            diff = dom2 - dom
                            sum += diff

                break
                
        sum *= 86400                            #--- change unit from day to sec

        sciLost = (csec2 - csec - sum) / 1000   #--- total science time lost excluding radiation zone passes

        line = etemp[0] + '\t' + etemp[1] + '\t' + etemp[2] + '\t' + "%.1f" %  sciLost  + '\t' + etemp[4]

        update.append(line)


    fo = open(file, 'w')
    for line in update:
        fo.write(line)
        fo.write('\n')
    fo.close()

    return update


#--------------------------------------------------------------------

if __name__ == '__main__':


    if len(sys.argv) == 2:
        input_file = sys.argv[1]
    else:
        input_file = 'interruption_time_list'

    out = sci_run_compute_gap(input_file)

    for ent in out:
        print ent

