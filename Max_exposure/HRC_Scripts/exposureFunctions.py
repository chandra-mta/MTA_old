#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#   exposureFunctions.py: collection of Max exposure related functions                  #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Mar 03, 2016                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')

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
import convertTimeFormat    as tcnv
import mta_common_functions as mtac

#
#--- check whose account, and set a path to temp location
#

user = getpass.getuser()
user = user.strip()

#
#--- set temp directory/file
#
tempdir = '/tmp/' + user + '/'
tempout = tempdir + 'ztemp'



#------------------------------------------------------------------------------------------------------------------------
#-- readExpData: read data from acis/hrc history data files                                                                ---
#------------------------------------------------------------------------------------------------------------------------

def readExpData_old(indir, inst, date , year ,month ,mean_acc ,std_acc ,min_acc ,min_apos , max_acc ,max_apos ,m10_acc ,
			m10_apos ,mean_dff ,std_dff ,min_dff ,min_dpos ,max_dff ,max_dpos ,m10_dff ,m10_dpos,sec='NA'):

    """
    read data from acis/hrc history data files
            input: indir: directory where the data locate
                   inst:  instruments hrci, hrcs, or acis data such as i_2_n_1 (for i_2_n_1_dff_out)
    """

    for set in ('dff', 'acc'):

        m = re.search('hrc', inst)
#
#--- HRC data
#
        if m is not None:
            if sec == 'NA':
                file = indir +  inst + '_' + set + '_out'
            else:
                file = indir +  inst + '_' + set

#
#--- ACIS data
#
        else:
            file = indir +  inst + '_' + set + '_out'



        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        for ent in data:
            ent.lstrip()
            m = re.search('NA', ent)
            if m is not None:
                ent = ent.replace('NA', '0')

            atemp = re.split('\s+|\t+', ent)
            if set == 'dff':
		time = float(atemp[0]) + (float(atemp[1]) - 0.5) / 12
		date.append(time)
                year.append(int(atemp[0]))
                month.append(int(atemp[1]))
                mean_dff.append(float(atemp[2]))
                std_dff.append(float(atemp[3]))
                min_dff.append(float(atemp[4]))
                min_dpos.append(atemp[5])
                max_dff.append(float(atemp[6]))
                max_dpos.append(atemp[7])
                m10_dff.append(float(atemp[8]))
                m10_dpos.append(atemp[9])
            else:
                mean_acc.append(float(atemp[2]))
                std_acc.append(float(atemp[3]))
                min_acc.append(float(atemp[4]))
                min_apos.append(atemp[5])
                max_acc.append(float(atemp[6]))
                max_apos.append(atemp[7])
                m10_acc.append(float(atemp[8]))
                m10_apos.append(atemp[9])


#------------------------------------------------------------------------------------------------------------------------
#-- readExpData: read data from acis/hrc history data files                                                                ---
#------------------------------------------------------------------------------------------------------------------------

def readExpData(indir, inst, sec='NA'):

    """
    read data from acis/hrc history data files
            input: indir: directory where the data locate
                   inst:  instruments hrci, hrcs, or acis data such as i_2_n_1 (for i_2_n_1_dff_out)
                   sec:   indicator of input file form
    """
    date     = []
    year     = []
    month    = []
    mean_acc = []
    std_acc  = []
    min_acc  = []
    min_apos = []
    max_acc  = []
    max_apos = []
    asig1    = []
    asig2    = []
    asig3    = []
    mean_dff = []
    std_dff  = []
    min_dff  = []
    min_dpos = []
    max_dff  = []
    max_dpos = []
    dsig1    = []
    dsig2    = []
    dsig3    = []

    for set in ('dff', 'acc'):

        m = re.search('hrc', inst)
#
#--- HRC data
#
        if m is not None:
            if sec == 'NA':
                file = indir +  inst + '_' + set + '_out'
            else:
                file = indir +  inst + '_' + set

#
#--- ACIS data
#
        else:
            file = indir +  inst + '_' + set + '_out'

        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        for ent in data:
            ent.lstrip()
            m = re.search('NA', ent)
            if m is not None:
                ent = ent.replace('NA', '0')

            atemp = re.split('\s+|\t+', ent)
            if set == 'dff':
		time = float(atemp[0]) + (float(atemp[1]) - 0.5) / 12
		date.append(time)
                year.append(int(atemp[0]))
                month.append(int(atemp[1]))
                mean_dff.append(float(atemp[2]))
                std_dff.append(float(atemp[3]))
                min_dff.append(float(atemp[4]))
                min_dpos.append(atemp[5])
                max_dff.append(float(atemp[6]))
                max_dpos.append(atemp[7])
                dsig1.append(float(atemp[8]))
                dsig2.append(float(atemp[9]))
                dsig3.append(float(atemp[10]))
            else:
                mean_acc.append(float(atemp[2]))
                std_acc.append(float(atemp[3]))
                min_acc.append(float(atemp[4]))
                min_apos.append(atemp[5])
                max_acc.append(float(atemp[6]))
                max_apos.append(atemp[7])
                asig1.append(float(atemp[8]))
                asig2.append(float(atemp[9]))
                asig3.append(float(atemp[10]))

    return [date,year,month,mean_acc,std_acc,min_acc,min_apos, max_acc,max_apos,asig1, asig2, asig3, mean_dff,std_dff,min_dff, min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3]

#---------------------------------------------------------------------------------------------------------------------
#--   clean_data: clean up and correct ACIS/HRC data.                                                               --
#---------------------------------------------------------------------------------------------------------------------

def clean_data(dir, startYear = 'NA', startMonth = 'NA' , stopYear= 'NA', stopMonth = 'NA'):

    """
    clean up and correct ACIS/HRC data. if there is duplicated line, remove it. if there are missing line add one (with NA)
    input dir, startYear = 1999, startMonth = 9, stopYear, stopMonth
     
    """
#
#--- if range is not defined, give them
#
    if startYear == 'NA':
        startYear = 1999
    if startMonth == 'NA':
        startMonth = 9

    (cyear, cmon, day, hours, min, sec, weekday, yday, dst) = tcnv.currentTime('Local')
    if stopYear == 'NA':
        stopYear = cyear
    if stopMonth == 'NA':
        stopMonth = cmon -1
        if stopMonth < 1:
            stopMonth = 12
            stopYear -= 1

    for type in ('*_acc*', '*_dff*'):

#
#--- find file names
#
        for fout in os.listdir(dir):
            if fnmatch.fnmatch(fout , type):
                ent = dir + fout
                
                f    = open(ent, 'r')
                data = [line.strip() for line in f.readlines()]
                f.close()
                f    = open('zout', 'w')

                cyear  = startYear
                cmonth = startMonth
                pyear  = 0
                pmonth = 0
    
                for aent in data:
    
                    atemp = re.split('\s+|\t+', aent)
                    year  = int(atemp[0])
                    month = int(atemp[1])
#
#--- if entry is duplicated, remove
#
                    if year == pyear and month == pmonth:
                        pass
                    elif year == cyear and month == cmonth:
                        f.write(aent)
                        f.write('\n')
                        pyear = year
                        pmonth = month
                        cmonth += 1
                        if cmonth > 12:
                            cmonth = 1
                            cyear += 1
                            if cyear == stopYear and cmonth > stopMonth:
                                break
#
#--- if entries are missing, add "NA" 
#
                    elif year == cyear and month > cmonth:
                        for i in range (cmonth, month):
                            smon = str(i)
                            if i < 10:
                                smon = '0' + smon
                            line = str(year) + '\t' + smon + '\tNA      NA      NA      NA      NA      NA      NA      NA\n'
                            f.write(line)
                        f.write(aent)
                        f.write('\n')
     
                        pyear = year
                        pmonth = month
                        cmonth += 1
                        if cmonth > 12:
                            cmonth = 1
                            cyear += 1
                            if cyear == stopYear and cmonth > stopMonth:
                                break
     
                f.close()

                cmd = 'mv zout ' + ent
                os.system(cmd)



#-----------------------------------------------------------------------------------------------------
#--- combine_image: combine two fits image files. combined fits file is renamed to the second fits ---
#-----------------------------------------------------------------------------------------------------

def combine_image(fits1, fits2):

    """
    combine two fits image files. input :fits1 fits2. a combined fits file is moved to fits2.
    """

    chk = mtac.chkFile('./', fits2)         #--- check the second fits file exist
    if chk == 0:
        cmd =  'mv ' + fits1 + ' ' + fits2
        os.system(cmd)
    else:
        try:
            cmd1 = "/usr/bin/env PERL5LIB="
            cmd2 = ' dmimgcalc infile=' + fits1 + ' infile2=' + fits2 + ' outfile=mtemp.fits operation=add  clobber=yes'
            cmd  = cmd1 + cmd2
            bash(cmd,  env=ascdsenv)

            cmd = 'rm ' + fits1
            os.system(cmd)
#
#--- rename the combined fits image to "fits2"
#

            cmd = 'mv mtemp.fits ' + fits2
            os.system(cmd)
        except:
            cmd = 'rm ' + fits1
            os.system(cmd)


#-----------------------------------------------------------------------------------------------------
#--- create_image: create image file according to instruction                                      ---
#-----------------------------------------------------------------------------------------------------

def create_image(line, outfile):

    """
    create image file according to instruction "line".
    input line: instruction,, outfile: output file name
    """

#    try:
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' dmcopy "' + line + '" out.fits option=image clobber=yes'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#    except:
#        pass

    try:
        cmd1 = "/usr/bin/env PERL5LIB="
        cmd2 = ' dmstat out.fits centroid=no > stest'
        cmd  = cmd1 + cmd2
        bash(cmd,  env=ascdsenv)
    except:
        pass
#
#--- if there is actually data, condense the iamge so that it won't take too much space
#
    f = open('stest', 'r')
    sdata = [line.strip() for line in f.readlines()]
    f.close()
    os.system('rm stest')

    val = 'NA'
    for lent in sdata:
        m = re.search('mean', lent)
        if m is not None:
            atemp = re.split('\s+|\t+', lent)
            val = atemp[1]
            break

         
    if val != 'NA' and float(val) > 0:
#        line = 'out.fits[opt type=i2,null=-99,mem=80]'
#        cmd  = 'dmcopy infile="' +line + '" outfile=' + outfile + ' clobber=yes'
#        os.system(cmd)
        cmd = 'mv out.fits ' + outfile
        os.system(cmd)

        return 1                        #--- the image file was created
    else:
        return 0                        #--- the image file was not created


#-----------------------------------------------------------------------------------------------------
#-- make_month_list: create an appropriate month list for a given conditions                      ----
#-----------------------------------------------------------------------------------------------------

def make_month_list(year, startYear, stopYear, startMonth, stopMonth):

    """
    create an appropriate month list for a given conditions
    input: year, startYear, stopYear, startMonth, stopMonth
    """
#
#--- fill up the month list
#
    month_list = []

    if startYear == stopYear:
#
#--- the period is in the same year
#

        month_list = range(startMonth, stopMonth+1)

    else:
#
#--- if the period is over two or more years, we need to set three sets of month list
#
        if year == startYear:
            month_list = range(startMonth, 13)
        elif year == stopYear:
            month_list = range(1,stopMonth+1)
        else:
            month_list = range(1,13)

    return month_list


