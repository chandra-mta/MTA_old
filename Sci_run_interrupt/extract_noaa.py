#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       extract_noaa.py: extract noaa data                                              #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Apr 28, 2014                                               #
#                                                                                       #
#########################################################################################

import math
import re
import sys
import os
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

#
#--- Science Run Interrupt related funcions shared
#

import interruptFunctions as itrf 


#-----------------------------------------------------------------------------------
#---startACEExtract:  the main script to extracct ACE data                       ---
#-----------------------------------------------------------------------------------

def startACEExtract(event, start, stop, comp_test = 'NA'):


    'for a gien event, start and stop data, initiate ACE plottings.'

#
#--- change time format to year and ydate (float)
#
    begin = start + ':00'                #---- need to add "seconds" part to dateFormtCon to work correctly
    end   = stop  + ':00'

    (year1, month1, day1, hours1, minutes1, seconds1, ydate1) = tcnv.dateFormatCon(begin)
    (year2, month2, day2, hours2, minutes2, seconds2, ydate2) = tcnv.dateFormatCon(end)

#
#--- extract ACE Data: put interruption starting/ending time in year, ydate format
#
    createRadDataTable(event, year1, ydate1, year2, ydate2, comp_test) 



#--------------------------------------------------------------------
#--- createRadDataTable: create NOAA radiation data table          --
#--------------------------------------------------------------------

def createRadDataTable(event, startYear, startYday, stopYear, stopYday, comp_test = 'NA'):


    "for a given event, interruption startYear, startYday, stopYear, stopYday, create a radiation data table <event>_dat.txt in data directory."

    if comp_test == 'test':
        out_name = test_data_dir + event + '_dat.txt'
    else:
        out_name = data_dir + event + '_dat.txt'

    out = open(out_name, 'w')

#
#--- set data collecting period
#

    (pYearStart, periodStart, pYearStop, periodStop, plotYearStart, plotStart, plotYearStop, plotStop, pannelNum) \
                = itrf.findCollectingPeriod(startYear, startYday, stopYear, stopYday)
#
#--- start printing out the database
#

    out.write('Science Run Interruption: $time\n\n')
    out.write('dofy\telectron38\telectron175\tprotont47\tproton112\tproton310\tproton761\tproton1060\taniso\n')
    out.write('---------------------------------------------------------------------------------------------------------------------------\n')
    out.write('\n')

    if pYearStart == pYearStop:
        printACEData(pYearStart, periodStart, periodStop, out)

    else:
#
#--- for the case, the data collectiing period goes over two years
#
        printACEData(pYearStart, periodStart, base,       out)
        printACEData(pYearStop,  1,           periodStop, out)

    out.close()


#--------------------------------------------------------------------
#--- printACEData: printing out NOAA data into a table            ---
#--------------------------------------------------------------------

def printACEData(byear, start, stop, out):

    "extract ACE data from rad_data<yyyy> then print it out. Input: year, start ydate, stop ydate, out (file destination) "

    file = house_keeping + 'rad_data' + str(byear)

    if byear <= 2000:
            file = house_keeping + 'rad_data_pre2001'

    f = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        m = re.search('#', ent)
        if ent and (m is None):
            atemp = re.split('\s+|\t+', ent)
            if atemp[0].isdigit() and int(atemp[0]) == byear:
                year  = int(atemp[0])
                month = int(atemp[1])
                day   = int(atemp[2])
                ydate = tcnv.findYearDate(year, month, day)
    
                btemp = atemp[3]
                shr   = btemp[0] + btemp[1]
                hours = float(shr)
                smin  = btemp[2] + btemp[3]
                mins  = float(smin)
                ydate += (hours/24 + mins/1440)
    
                if ydate >= start and ydate <= stop:
                    if atemp[7] and atemp[8] and atemp[10] and  atemp[11] and atemp[12] and atemp[13] and atemp[14] and atemp[15]:
                        line = '%6.4f\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
                            % (ydate, atemp[7], atemp[8], atemp[10], atemp[11], atemp[12], atemp[13], atemp[14], atemp[15])
                        out.write(line)

