#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       sci_run_get_rad_zone_info.py: find expected radiation zone timing               #
#                                                                                       #
#           this script must be run on rhodes to see the radiation zone information     #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Apr 11, 2013                                               #
#                                                                                       #
#########################################################################################

import os
import sys
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
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf

#------------------------------------------------------------------------------------------------------------------------
#--- cleanEntry: Clean up Radiation zone Entry/Exist information                                                       --
#------------------------------------------------------------------------------------------------------------------------

def cleanEntry(line):

    "Clean up Radiation zone Entry/Exist information suitable for use.  See extractRadZoneInfo "


    temp1 = re.split('\s+', str(line))
    temp2 = re.split('=',   temp1[0])
    ctime = temp2[1]
    dtime = re.split(':',   temp2[1])

    dom   = tcnv.findDOM(float(dtime[0]), float(dtime[1]), float(dtime[2]), float(dtime[3]), float(dtime[4]))   #--- get Day of Mission

    m = re.search('RADENTRY', line)
    if m is not None: 
        act = 'ENTRY'
    else:
        act = 'EXIT'

    line = act + '\t' + str(dom) + '\t' + str(ctime)

    return line


#------------------------------------------------------------------------------------------------------------------------
#--- extractRadZoneInfo: extract radiation zone information from MP data                                              ---
#------------------------------------------------------------------------------------------------------------------------

def extractRadZoneInfo(year, month, type):

    "extract radiation zone information from MP data. input: year, month "

    if type == 'ENTRY':
        etype = 'RADENTRY'
    else:
        etype = 'RADEXIT'
#
#--- find the next month
#

    year2  = year
    month2 = month + 1

    if month2 == 13:
        year2 += 1
        month2 = 1

#
#--- extract this month and the next month radiation zone information
#

    name = str.upper(tcnv.changeMonthFormat(month)) + '*'
    if comp_test == 'test':
        line = 'cat ' + house_keeping + 'Test_prep/mp_data/*|grep ' + etype + ' >  ./zout'
    else:
#>        line = 'cat ' + ' /data/mpcrit1/mplogs/'+ str(year) + '/' +  name + '/ofls/*dot|grep ' + etype + '  >  /tmp/mta/zout'
        line = 'cat ' + ' /data/mpcrit1/mplogs/'+ str(year) + '/' +  name + '/ofls/*dot|grep ' + etype + ' >  ./zout'

    os.system(line)

    name = str.upper(tcnv.changeMonthFormat(month2)) + '*'
    if comp_test == 'test':
        line = 'cat ' + house_keeping + 'Test_prep/mp_data/' + str(year2) + '/' +  name + '/ofls/*dot|grep ' + etype + ' >>  ./zout'
    else:
#>        line = 'cat ' + ' /data/mpcrit1/mplogs/' + str(year2) + '/' +  name + '/ofls/*dot|grep ' + etype + '  >>  /tmp/mta/zout'
        line = 'cat ' + ' /data/mpcrit1/mplogs/' + str(year2) + '/' +  name + '/ofls/*dot|grep ' + etype + ' >>  ./zout'

    os.system(line)

#
#--- read the tmp files and clean up the the radiation zone entry / exit information
#

#>    f = open('/tmp/mta/zout', 'r')
    f = open('./zout', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

#>    os.system('rm /tmp/mta/zout')
    os.system('rm ./zout')

    outList = []
    for ent in data:
        line = cleanEntry(ent)
#        outList.list.append(line)
        outList.append(line)

    return outList

#------------------------------------------------------------------------------------------------------------------------
#--- getRadZoneInfo: update rad_zone_info                                                                            ----
#------------------------------------------------------------------------------------------------------------------------

def getRadZoneInfo():

    "update rad_zone_info (a list of radiation zone entry/exit). it will check this month and the next month. "

#
#--- read the past radiation zone information
#

    if comp_test == 'test':
        file = test_web_dir + 'rad_zone_info'
    else:
        file = house_keeping + 'rad_zone_info'


    f    = open(file, 'r')
    radZone = [line.strip() for line in f.readlines()]

#
#--- find out today's date in Local time frame
#

    if comp_test == 'test':
        year  = 2012
        month = 10
    else:
        today = tcnv.currentTime('local')
        year  = today[0];
        month = today[1];
   
#
#--- extract radiation zone information of "ENTRY" and "EXIT"
#

    entryList = extractRadZoneInfo(year, month, 'ENTRY')
    exitList  = extractRadZoneInfo(year, month, 'EXIT')

#
#--- combined all three lists
#

    combList = radZone + entryList + exitList

#
#--- to sort the list, first separate each entory to three elements
#

    temp0 = []
    temp1 = []
    temp2 = []

    for ent in combList:
        atemp = re.split('\s+|\t+', ent)
        temp0.append(atemp[0])
        temp1.append(atemp[1])
        temp2.append(atemp[2])

#
#--- the second elemet (temp1) is DOM; use that to sort the list in time order
#

    ztemp = sorted(zip(temp1, temp0))
    ent1, ent0 = zip(*ztemp)

    ztemp = sorted(zip(temp1, temp2))
    dummy, ent2 = zip(*ztemp)

#
#--- recombine three element into one and make a time ordered list
#

    orderedList = []
    for i in range(1,len(ent1)):
        line = ent0[i] + '\t' + ent1[i] + '\t' + ent2[i]
        orderedList.append(line)

#
#--- eliminate duplicated lines
#

    chk = orderedList.pop(0)
    cleanedList = [chk]

    for ent in orderedList:
        if(ent != chk):
            cleanedList.append(ent)
            chk = ent

#
#--- move the old file
#

    if comp_test == 'test':
        crtFile = test_web_dir + 'rad_zone_info'
    else:
        oldFile = house_keeping + 'rad_zone_info~'
        crtFile = house_keeping + 'rad_zone_info'

        cmd     = 'chmod 775 ' + crtFile + ' ' +  oldFile
        os.system(cmd)

        cmd     = 'mv ' + crtFile + ' ' + oldFile
        os.system(cmd)
    
        cmd     = 'chmod 644 ' +  oldFile
        os.system(cmd)


    f = open(crtFile, 'w')

#
#--- before pinting out the data, make sure that no two consequtive 
#--- entries have the same type (ENTRY/EXIT)
#

    ind = ''
    for eachLine in cleanedList:
        test = re.split('\s+|\t+', eachLine)
        if(test[0] != ind):
            line = eachLine + '\n'
            f.write(line)
            ind = test[0]

    f.close()

#------------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':               #---- this is a test case
            comp_test = 'test'
        else:
            comp_test = 'real'
    else:
            comp_test = 'real'
#
#--- if this is a test case, check whether output file exists. If not, creaete it
#
    if comp_test == 'test':
        chk = mcf.chkFile(test_web_dir)
        if chk == 0:
            cmd = 'mkdir ' + test_web_dir
            os.system(cmd)
#
#--- prepare for test
#
        cmd = 'cp ' + house_keeping + 'Test_prep/rad_zone_info '  + test_web_dir + '/.'
        os.system(cmd)
#
#--- now call the main function
#

    getRadZoneInfo()





