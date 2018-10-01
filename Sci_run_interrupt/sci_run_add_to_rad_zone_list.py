#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       sci_run_add_to_rad_zone_list.py: add radiation zone list around a given date            #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvarad.edu)                                      #
#                                                                                               #
#               last update: Apr 11, 2013                                                       #
#                                                                                               #
#################################################################################################

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


#------------------------------------------------------------------------------------------------------------------
#--- sci_run_add_to_rad_zone_list: adding radiation zone list to rad_zone_list                                  ---
#------------------------------------------------------------------------------------------------------------------

def sci_run_add_to_rad_zone_list(file='NA'):

    'adding radiation zone list to rad_zone_list. input: file name containing: e.g. 20120313        2012:03:13:22:41        2012:03:14:13:57         53.3   auto'
    
#
#--- if file is not given (if it is NA), ask the file input
#

    if file == 'NA':
        file = raw_input('Please put the intrrupt timing list: ')

    f    = open(file, 'r')
    data  = [line.strip() for line in f.readlines()]
    data.reverse()
    f.close()

    for ent in data:

#
#--- a starting date of the interruption in yyyy:mm:dd:hh:mm (e.g., 2006:03:20:10:30)
#--- there could be multiple lines of date; in that is the case, the scripts add the rad zone list
#--- to each date
#

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
        dom   = tcnv.findDOM(int(year), int(ydate))
        line  = year + ':' + str(int(ydate)) + ':' + hour + ':' + mins + ':00'
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
        dom2  = tcnv.findDOM(int(eyear), int(ydate))
        line  = eyear + ':' + str(int(ydate)) + ':' + ehour + ':' + emins + ':00'
        csec2 = tcnv.axTimeMTA(line)

#
#--- date stamp for the list
#
        list_date = str(year) + str(month) + str(date)

#
#--- check radiation zones for 3 days before to 5 days after from the interruptiondate
#

        begin = dom - 3
        end   = dom2 + 5

#
#--- read radiation zone infornation
#

        infile = house_keeping + '/rad_zone_info'
        f      = open(infile, 'r')
        rdata  = [line.strip() for line in f.readlines()]
        f.close()
    
        status = []
        rdate  = []
        chk    = 0
        last_st= ''
        cnt    = 0
    
        for line in rdata:
            atemp = re.split('\s+', line)
    
            dtime = float(atemp[1])                 #--- dom of the entry or exit
    
            if chk  == 0 and atemp[0] == 'ENTRY' and dtime >= begin:
                status.append(atemp[0])
                rdate.append(dtime)
                chk += 1
                last_st = atemp[0]
                cnt += 1
            elif chk > 0 and dtime >= begin and dtime <= end:
                status.append(atemp[0])
                rdate.append(dtime)
                last_st = atemp[0]
                cnt += 1
            elif atemp[1] > end and last_st == 'EXIT':
                break
            elif atemp[1] > end and last_st == 'ENTRY':
                status.append(atemp[0])
                rdate.append(dtime)
                cnt += 1
                break
            
        f = open('./temp_zone', 'w')

#
#--- a format of the output is, e.g.: '20120313    (4614.2141112963,4614.67081268519):...'
#

        line = list_date + '\t'
        f.write(line)
    
        i = 0
        while i < cnt:
            line = '(' + str(rdate[i]) + ','
            f.write(line)
            i += 1
            if i < cnt-1:
                line = str(rdate[i]) + '):'
                f.write(line)
            else:
                line = str(rdate[i]) + ')\n'
                f.write(line)
            i += 1
    
        f.close()

#
#--- append the past rad zone list 
#

        oldFile = house_keeping + '/rad_zone_list~'
        crtFile = house_keeping + '/rad_zone_list'

#>        cmd = 'cat ' './temp_zone ' + crtFile + ' > /tmp/mta/temp_comb'
        cmd = 'cat '+ './temp_zone ' + crtFile +  ' > ./temp_comb'
        os.system(cmd)

#>        os.systm('rm /tmp/mta/temp_zone')
        os.system('rm ./temp_zone')

#
#--- save the old file and move the update file to rad_zone_list
#

        cmd     = 'chmod 775 ' + crtFile + ' ' +  oldFile
        os.system(cmd)
    
        cmd     = 'mv ' + crtFile + ' ' + oldFile
        os.system(cmd)
    
        cmd     = 'chmod 644 ' +  oldFile
        os.system(cmd)
    
#>        cmd     = 'mv  ' + '/tmp/mta/temp_comb ' + crtFile
        cmd     = 'mv  ' + './temp_comb ' + crtFile
        os.system(cmd)


#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------

if __name__ == '__main__':

    sci_run_add_to_rad_zone_list(file='NA')
