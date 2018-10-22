#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       hrc_dose_get_data_full_rage.py: obtain HRC Evt 1 data for a month and create    #
#                                cumulative data fits files in multiple image files     #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Oct 03, 2018                                                      #
#                                                                                       #
#       commented out full image part   Jan 04, 2016                                    #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release;source /home/mta/bin/reset_param', shell='tcsh')

#
#--- reading directory list
#

path = '/data/mta/Script/Exposure/house_keeping/hrc_dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append path to a private folder
#

sys.path.append(bin_dir)
sys.path.append(mta_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv

#
#---- mta common functions
#
import mta_common_functions as mtac

#
#--- Exposure related funcions shared
#

import exposureFunctions as expf

#
#--- setting sections for subdeviding image
#

xstart_s = (   0,    0,     0,     0,     0,     0,     0,     0,     0,     0)          #--- for HRC S
xend_s   = (4095, 4095,  4095,  4095,  4095,  4095,  4095,  4095,  4095,  4095)
ystart_s = (   1, 4916,  9832, 14748, 19664, 24580, 29496, 34412, 39328, 44244)         
yend_s   = (4915, 9831, 14747, 19663, 24579, 29495, 34411, 39327, 44243, 49159)

xstart_i  = (   1,    1,     1,  5462,  5462,  5462, 10924, 10924, 10924)                #--- for HRC I
xend_i    = (5461, 5461 , 5461, 10923, 10923, 10923, 16385, 16385, 16385)
ystart_i  = (   1, 5462, 10924,     1,  5462, 10924,     1,  5562, 10942)
yend_i    = (5461,10923, 16385,  5461, 10923, 16385,  5461, 10923, 16385)

xstart_i_c = []
xstart_i_c.append(6144)                                                                     #--- for HRC I center
xend_i_c  = []
xend_i_c.append(10239)
ystart_i_c = []
ystart_i_c.append(6144)
yend_i_c  = []
yend_i_c.append(10239)

xstart_s_c = []
xstart_s_c.append(0)                                                                        #--- for HRC S center
xend_s_c  = []
xend_s_c.append(4095)
ystart_s_c = []
ystart_s_c.append(22528)
yend_s_c  = []
yend_s_c.append(26623)

#
#--- a couple of things needed
#
dare   = mtac.get_val('.dare',   dir = bindata_dir, lst=1)
hakama = mtac.get_val('.hakama', dir = bindata_dir, lst=1)


#-----------------------------------------------------------------------------------------------------------
#--- hrc_dose_get_data: extract HRC evt1 data fro a month and create cumulative data fits file            --
#-----------------------------------------------------------------------------------------------------------

def hrc_dose_get_data(startYear = 'NA', startMonth = 'NA', stopYear = 'NA', stopMonth = 'NA', comp_test = 'NA'):

    """
    extract HRC evt1 data from a month and create cumulative data fits file. Input: start year, start month, stop year, stop month
    """


    if startYear == 'NA' or startMonth == 'NA' or stopYear == 'NA' or stopMonth == 'NA':
        startYear  = raw_input('Starting Year: ')
        startYear  = int(startYear)
        startMonth = raw_input('Starting Month: ')
        startMonth = int(startMonth)

        stopYear   = raw_input('Stopping Year: ')
        stopYear   = int(stopYear)
        stopMonth  = raw_input('Stopping Month: ')
        stopMonth  = int(stopMonth)

#
#--- start extracting the data for the year/month period
#
    for year in range(startYear, stopYear+1):

        lyear = str(year)
        syear = lyear[2] + lyear[3]

        month_list =  expf.make_month_list(year, startYear, stopYear, startMonth, stopMonth)  #---- create a list of month appropriate for the year

        for month in month_list:

            smonth = str(month)
            if month < 10:
                smonth = '0' + smonth
#
#--- output file name settings
#
            outfile_i_c = './HRCI_' + str(smonth) + '_' + str(lyear) + '.fits'
            outfile_s_c = './HRCS_' + str(smonth) + '_' + str(lyear) + '.fits'

            outfile_i = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
            for i in range(0, 9):
                outfile_i[i] = './HRCI_' + str(smonth) + '_' + str(lyear) + '_' + str(i) + '.fits'

            outfile_s = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
            for i in range(0, 10):
                outfile_s[i] = './HRCS_' + str(smonth) + '_' + str(lyear) + '_' + str(i) + '.fits'

#
#--- using ar5gl, get file names
#
            smonth = str(month)
            if month < 10:
                smonth = '0' + smonth

            syear = str(year)
            #start = smonth + '/01/' + syear[2] + syear[3] + ',00:00:00'
            start = syear + '-' + smonth + '-01T00:00:00'

            nextMonth = month + 1
            if nextMonth > 12:
                lyear     = year + 1
                nextMonth = 1
            else:
                lyear  = year                

            smonth = str(nextMonth)
            if nextMonth < 10:
                smonth = '0' + smonth

            syear = str(lyear)
            #stop  = smonth + '/01/' + syear[2] + syear[3] + ',00:00:00'
            stop  = str(lyear) + '-' + smonth + '-01T00:00:00'

            line = 'operation=browse\n'
            line = line + 'dataset=flight\n'
            line = line + 'detector=hrc\n'
            line = line + 'level=1\n'
            line = line + 'filetype=evt1\n'
            line = line + 'tstart=' + start + '\n'
            line = line + 'tstop=' +  stop  + '\n'
            line = line + 'go\n'
            f    = open('./zspace', 'w')
            f.write(line)
            f.close()
            cmd1 = "/usr/bin/env PERL5LIB="
            #cmd2 =  '  /proj/axaf/simul/bin/arc5gl -user isobe -script ./zspace > ./zout'
            cmd2 =  ' /proj/sot/ska/bin/arc5gl -user isobe -script ./zspace > ./zout'
            cmd  = cmd1 + cmd2
            #bash(cmd,  env=ascdsenv)
            os.system(cmd2)
            mtac.rm_file('./zspace')

            f    = open('./zout', 'r')
            fitsList = [line.strip() for line in f.readlines()]
            f.close()
            mtac.rm_file('./zout')

#
#--- extract each evt1 file, extract the central part, and combine them into a one file
#
            hrciCnt   = [0, 0, 0, 0, 0, 0, 0, 0, 0]                                 #--- counters for how many hrc-i and hrc-s are extracted
            hrcsCnt   = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  
            hrciCnt_c = 0
            hrcsCnt_c = 0

            chk = 0
            for line in fitsList:
                m = re.search('fits', line)
                if m is None:
                    continue
                chk = 1

                try:
#                    [fitsName] = mtac.useArc4gl('retrieve','flight', 'hrc', 1, 'evt1', filename=file)
                    atemp = re.split('\s+', line)
                    fitsName  = atemp[0]
                    line = 'operation=retrieve\n'
                    line = line + 'dataset=flight\n'
                    line = line + 'detector=hrc\n'
                    line = line + 'level=1\n'
                    line = line + 'filetype=evt1\n'
                    line = line + 'filename=' + fitsName + '\n'
                    line = line + 'go\n'
                    f    = open('./zspace', 'w')
                    f.write(line)
                    f.close()
                    cmd1 = "/usr/bin/env PERL5LIB="
                    #cmd2 =  ' /proj/axaf/simul/bin/arc5gl -user isobe -script  ./zspace'
                    cmd2 =  ' /proj/sot/ska/bin/arc5gl -user isobe -script ./zspace > ./zout'
                    cmd  = cmd1 + cmd2
                    #bash(cmd,  env=ascdsenv)
                    os.system(cmd2)
                    mtac.rm_file('./zspace')

                    cmd = 'gzip -d ' + fitsName + '.gz'
                    os.system(cmd)
                except:
                    continue

                detector = whichHRC(fitsName)                                                   #--- checking which HRC (S or I)
#
#--- creating the center part image ----------------------------------
#                
                line = set_cmd_line(fitsName, detector, 'center',  0)             #---- set command line

                ichk =  expf.create_image(line, 'ztemp.fits')               #---  create an image file
#
#--- for HRC S
#
                if detector == 'HRC-S' and ichk > 0:
                    expf.combine_image('ztemp.fits', 'total_s.fits')
                    hrcsCnt_c += 1
#
#--- for HRC I
#
                elif detector == 'HRC-I' and ichk > 0:
                    expf.combine_image('ztemp.fits', 'total_i.fits')
                    hrciCnt_c += 1

#
#---- now work on the full image ----------------------------------------
#

##                for i in range(0, 10):
##
##                    if detector == 'HRC-I' and i == 9:                  #---- HRC-I has only 9 sections HRC-S has 10 sections
##                        break
##
##                    line = set_cmd_line(fitsName, detector, 'full',  i)           #---- set command line
##
##                    ichk =  expf.create_image(line, 'ztemp.fits')           #---- create an image file
#
#--- for HRC S
#
##                    if detector == 'HRC-S' and ichk > 0:
##                        fits  = 'total_s' + str(i) + '.fits'
##                        expf.combine_image('ztemp.fits', fits)    #--- add ztemp.fits to fits, if there if no fits, mv ztempfits to fits
##                        hrcsCnt[i] += 1
#
#--- for HRC I
#
##                    elif detector == 'HRC-I' and ichk > 0:
##                        fits  = 'total_i' + str(i) + '.fits'
##                        expf.combine_image('ztemp.fits', fits)
##                        hrciCnt[i] += 1

                cmd = 'rm out.fits ' + fitsName
                os.system(cmd)
#
#--- move the file to a depository ; first the center image -----------------------------
#
            if comp_test == 'test':
                dp_web_dir = test_web_dir
            else:
                dp_web_dir = web_dir

            if chk > 0:
                if hrcsCnt_c > 0:
                    cmd = 'mv total_s.fits ' + dp_web_dir + 'Month_hrc/' +  outfile_s_c
                    os.system(cmd)
                    cmd = 'gzip ' + dp_web_dir + '/Month_hrc/*.fits'
                    os.system(cmd)
    
    
                if hrciCnt_c > 0:
                    cmd = 'mv total_i.fits ' + dp_web_dir + 'Month_hrc/' +  outfile_i_c
                    os.system(cmd)
                    cmd = 'gzip ' + dp_web_dir + '/Month_hrc/*.fits'
                    os.system(cmd)
            
            createCumulative(year, month, 'HRC-S', 'center', dp_web_dir, i=0)
            createCumulative(year, month, 'HRC-I', 'center', dp_web_dir, i=0)

#
#---full image
#
##            if comp_test == 'test':
##                    dp_hrc_full_data = test_hrc_full_data
##            else:
##                    dp_hrc_full_data = hrc_full_data
##
##            for i in range(0,10):    
##                if hrcsCnt[i] > 0:
##                    cmd = 'mv total_s' + str(i) + '.fits ' + dp_hrc_full_data + '/Month_hrc/' + outfile_s[i]
##                    os.system(cmd)
##                    cmd = 'gzip ' + dp_hrc_full_data + '/Month_hrc/*.fits'
##                    os.system(cmd)
##                
##                createCumulative(year, month, 'HRC-S', 'full', dp_hrc_full_data, i)
##
##            for i in range(0,9):    
##                if hrciCnt[i] > 0:
##                    cmd = 'mv total_i' + str(i) + '.fits ' + dp_hrc_full_data + '/Month_hrc/' + outfile_i[i]
##                    os.system(cmd)
##                    cmd = 'gzip ' + dp_hrc_full_data + '/Month_hrc/*.fits'
##                    os.system(cmd)
##                
##                createCumulative(year, month, 'HRC-I', 'full', dp_hrc_full_data, i)



#-------------------------------------------------------------------------------------------------------------------------
#-- set_cmd_line: generate image creating command line for dmcopy                                                      ---
#-------------------------------------------------------------------------------------------------------------------------

def set_cmd_line(fitsName, detector, type,  i):

    """
    generate image creating command line for dmcopy 
    input: fitsName, detector, type (center or otherwise),  i (for section #)
    """

    if type == 'center':
        if detector == 'HRC-S':
            xstart = str(xstart_s_c[i])
            xend   = str(xend_s_c[i])
            ystart = str(ystart_s_c[i])
            yend   = str(yend_s_c[i])
            mem    = str(80)
        if detector == 'HRC-I':
            xstart = str(xstart_i_c[i])
            xend   = str(xend_i_c[i])
            ystart = str(ystart_i_c[i])
            yend   = str(yend_i_c[i])
            mem    = str(80)
    else:
        if detector == 'HRC-S':
            xstart = str(xstart_s[i])
            xend   = str(xend_s[i])
            ystart = str(ystart_s[i])
            yend   = str(yend_s[i])
            mem    = str(200)
        if detector == 'HRC-I':
            xstart = str(xstart_i[i])
            xend   = str(xend_i[i])
            ystart = str(ystart_i[i])
            yend   = str(yend_i[i])
            mem    = str(200)


    line = fitsName + '[EVENTS][bin rawx='+ xstart + ':' + xend + ':1, rawy=' + ystart + ':' + yend + ':1]'
    line = line + '[status=xxxxxx00xxxxxxxxx000x000xx00xxxx][option type=i4,mem='+ mem + ']'

    return line

                

#-----------------------------------------------------------------------------------------------------
#--- createCumulative: create cumulative hrc data                                                   --
#-----------------------------------------------------------------------------------------------------

def createCumulative(year, month, detector,  type, arch_dir, i=0):

    'create cumulative hrc data for a given year and month'

#
#--- find the previous period
#
    pyear = year
    pmonth = month -1

    if pmonth < 1:
        pmonth = 12
        pyear -= 1

    syear  = str(year)
    smonth = str(month)

    if month < 10:
        smonth = '0' + smonth

    spyear  = str(pyear)
    spmonth = str(pmonth)

    if pmonth < 10:
        spmonth = '0' + spmonth

    if detector == 'HRC-I':
        inst = 'HRCI'
    else:
        inst = 'HRCS'

#
#--- set file names
#
    if type == 'center':
        hrc   = inst + '_'         + smonth  + '_' + syear  + '.fits.gz'
        chrc  = inst + '_08_1999_' + spmonth + '_' + spyear + '.fits.gz'
        chrc2 = inst + '_08_1999_' + smonth  + '_' + syear  + '.fits'
    else:
        hrc   = inst + '_'         + smonth  + '_' + syear  + '_' + str(i) + '.fits.gz'
        chrc  = inst + '_09_1999_' + spmonth + '_' + spyear + '_' + str(i) + '.fits.gz'
        chrc2 = inst + '_09_1999_' + smonth  + '_' + syear  + '_' + str(i) + '.fits'

#
#---- if the monthly file exists, reduce the size of the file before combine it into a cumulative data
#
    
    cdir = arch_dir + '/Month_hrc/'
    chk = mtac.chkFile(cdir, hrc)                   #---- checking hrc exisits or not

    if chk > 0: 
        line = arch_dir + '/Month_hrc/' + hrc + '[opt type=i2,null=-99]'
        cmd1 = "/usr/bin/env PERL5LIB="
        cmd2 = ' dmcopy infile="' + line + '"  outfile="./ztemp.fits"  clobber="yes"'
        cmd  = cmd1 + cmd2
        bash(cmd,  env=ascdsenv)

        cmd1 = "/usr/bin/env PERL5LIB="
        cmd2 = ' dmimgcalc infile=' + arch_dir + 'Cumulative_hrc/' + chrc + ' infile2=ztemp.fits outfile =' + chrc2 + ' operation=add clobber=yes'
        cmd  = cmd1 + cmd2
        bash(cmd,  env=ascdsenv)

        os.system('rm ./ztemp.fits')

        cmd  = 'gzip ' + chrc2
        os.system(cmd)

        cmd  = 'mv ' + chrc2 + '.gz ' + arch_dir + 'Cumulative_hrc/.'
        os.system(cmd)
#
#--- if the monthly fie does not exist, just copy the last month's cumulative data
#
    else:
        try:
            cmd = 'cp ' + arch_dir + 'Cumulative_hrc/' + chrc + ' '  + arch_dir + 'Cumulative_hrc/'  + chrc2 + '.gz'
            os.system(cmd)
        except:
            pass


#-----------------------------------------------------------------------------------------------------
#--- whichHRC: determine HRC I or HRC S observation from HRC event file                            ---
#-----------------------------------------------------------------------------------------------------

def whichHRC(file):

    'determine HRC I or HRC S observation from HRC event file; input: HRC event file'

    detector = findEntry(file, 'DETNAM')

    return detector

#-----------------------------------------------------------------------------------------------------
#---findEntry: find a value corresponding to a given marker                                         --
#-----------------------------------------------------------------------------------------------------

def findEntry(file, term):

    'find a value corresponding to a given marker in a fits file: input: file name, marker. the file must be an output of dmlist opt=data.'

    val = 'NA'
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmlist infile=' + file + ' opt=head >  zout '
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

    f    = open('zout', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    os.system('rm -rf  zout')

    for ent in data:
        m = re.search(term, ent)
        if m is not None:
            atemp = re.split('\s+|\t+', ent)
            val   = atemp[2]
            val.strip()
            break

    return val


#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    hrc_dose_get_data()

