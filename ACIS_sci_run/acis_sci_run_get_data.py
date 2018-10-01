#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       acis_sci_run_get_data.py:obtain data from MIT and plot acis science run #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Apr 30, 2014                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import operator

import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

#
#--- check whether this is a test case
#

if len(sys.argv) == 2:
    if sys.argv[1] == 'test':
        comp_test = 'test'
    elif sys.argv[1] == 'test2':
        comp_test = 'test2'
    else:
        comp_test = 'real'
else:
    comp_test = 'real'

#
#--- reading directory list
#
if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/Acis_sci_run/house_keeping/dir_list_py_test'
else:
    path = '/data/mta/Script/ACIS/Acis_sci_run/house_keeping/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
import acis_sci_run_functions as asrf

#
#--- temp writing file name
#

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)

#
#--- a list of columns to extract
#
col_names = bin_data_dir + '/col_list2004'


#
#--- today's date
#
if comp_test == 'test':             #---- for the test case, set the date to the last day of Phase 71
    year    =  2012
    month   =  4
    day     =  22
#
#--- create test directories
#
    asrf.prep_for_test(web_dir, comp_test)

elif comp_test == 'test2':          #---- this is another test case, but go over two years 2011 and 2012
    year    = 2012
    month   = 2
    day     = 2

    asrf.prep_for_test(web_dir, comp_test)
else:
    today   = tcnv.currentTime('local')
    year    = today[0]
    month   = today[1]
    day     = today[2]
#
#--- setting the current output directory
#
current_dir = 'Year' + str(year) + '/'

#-----------------------------------------------------------------------------------------------
#---acis_sci_run_get_data: extracts mit data and updates acis science run data and plots     ---
#-----------------------------------------------------------------------------------------------

def acis_sci_run_get_data():
    """
    this function is a driving fuction which extracts mit data and updates acis science run data and plots

    Input:  none but read the data from mit site

    Output: updated data tables and plots in web_dir/Year<this_year>
        data_<year> --- this contains all data
        sub data sets are:
            te1_3_out           te3_3_out
            te5_5_out           cc2_3_out
            drop_<year>         drop5x5_<year>
            high_error_<year>   high_error5x5_<year>
            high_event_<year>   high_event5x5_<year>

        there are a few other files, but they are mostly empty and ignored.

        plots: te3_3_out.png    te5_5_out.png   cc3_3_out.png

    """
#
#---check whether "Working_dir" exists
#
    chk = mcf.chkFile('./','Working_dir')
    if chk > 0:
        cmd = 'rm ./Working_dir/*'
    else:
        cmd = 'mkdir ./Working_dir'

    os.system(cmd)
#
#--- check current_dir exists; if this is the first of the year, analyze data in the last year's frame
#
    chk_new = mcf.chkFile(web_dir, current_dir)

#
#---- get data from MIT
#
    if chk_new ==  0:
        last_year = int(year) -1
        mit_data = get_mit_data(last_year)
    else:
        mit_data = get_mit_data(year)
#
#---- check whether mit_data goes over two years
#
    ychk = checkYearChange(mit_data)        #--- if ychk > 1, the mit_data contains year changes

#---------------
#---- for the case that there is year change during this data
#---------------

    if ychk > 0:
#---- previous year's data
#
        last_year = year -1
        name      = web_dir + 'Year' + str(last_year) + '/data' + str(last_year)
        addToPastData(mit_data, name)

        lastYear_dir = 'Year' + str(last_year) + '/'
        separate_data(name, lastYear_dir)
#
#---- print a html page
#
        asrf.acis_sci_run_print_html(web_dir, last_year, 12, 31, 'yes')
#
#---- make plots (only when the day this year's directory is created)
#
        if chk_new == 0:
            plot_events(lastYear_dir)
#
#--- check whether there are any high events
#
            chkHighEvent(last_year)
#
#---- now work on this year's data
#
    if chk_new == 0:
        cmd = 'mkdir ' + web_dir + current_dir + '/'
        os.system(cmd)

        name = web_dir + 'Year' + str(year) + '/data' + str(year)
        fout = open(name, 'w')
        for ent in mit_data:
            atemp = re.split('\t+|\s+', ent)
            btemp = re.split(':', atemp[1])
            val   = float(btemp[0])
            if val < 100:
                fout.write(ent)
                fout.write('\n')
        fout.close()

        asrf.removeDuplicated(name)
#
#--- separate data into each category
#
        separate_data(name, current_dir)

        asrf.acis_sci_run_print_html(web_dir, year, month, day,  'no')
#
#--- plot data
#
        plot_events(current_dir)
#
#--- check whether there are any high events
#
        chkHighEvent(year)
#
#--- update long term data tables
#
        longTermTable(year)
#
#--- plot long term trends
#
        plot_events('Long_term/')
#
#--- update all_data file
#
        update_all_data(mit_data, year)

#---------
#--- no year change... business as usual
#---------
    else:
        name = web_dir + 'Year' + str(year) + '/data' + str(year)
        chk = mcf.chkFile('name')
        if chk == 0:
            fout = open(name, 'w')
        else:
            fout = open(name, 'a')

        for ent in mit_data:
            fout.write(ent)
            fout.write('\n')
        fout.close()
#
#--- remove duplicated lines
#
        asrf.removeDuplicated(name)
#
#--- separate data into each category
#
        separate_data(name, current_dir)
#
#--- update html pages
#
        asrf.acis_sci_run_print_html(web_dir, year, month, day,  'yes')
#
#--- plot trends
#
        plot_events(current_dir)
#
#--- check whether there are any high events
#
        chkHighEvent(year)
#
#--- update long term data tables
#
        longTermTable(year)
#
#--- plot long term trends
#
        plot_events('Long_term/')
#
#--- update all_data file
#
        update_all_data(mit_data, year)


#-----------------------------------------------------------------------------------------------
#--- addToPastData: adding new data to the saved data set                                    ---
#-----------------------------------------------------------------------------------------------

def addToPastData(mit_data, pdata_name):
        """
        adding the current data to the past data set
        Input: mit_data ---- data set extreacted mit site
               pdata_name--- the name of the past data
        Output: updated "pdata_name"
        """
#
#---- here is the previous year's data
#
        fout = open('./Working_dir/adding_data', 'w')
        for ent in mit_data:
            atemp = re.split('\t+|\s+', ent)
            if atemp[1] > 300:
                fout.write(ent)
                fout.write('\n')
        fout.close()

        cmd  = 'cat ./Working_dir/adding_data >> ' + pdata_name
        os.system(cmd)
        cmd  = 'rm ./Working_dir/adding_data'
        os.system(cmd)
#
#--- remove duplicated lines
#
        asrf.removeDuplicated(pdata_name)


#-----------------------------------------------------------------------------------------------
#--- get_mit_data: extract data from mit sites                                                --
#-----------------------------------------------------------------------------------------------

def get_mit_data(tyear):

    """
    this function extracts data from the MIT web site and select out the newest part by comparing the
    data to the current data saved locally.

    Input: tyear --- year of the last save data,  
            data will read the data from MIT web site and a locat data (data_<tyear>)
    
    Output: mit_data
    """

#
#--- first find out the latest version of phase by reading main html page 
#--- here is the lnyx script to obtain web page data
#
    if comp_test == 'test':
        last_phase  = 71
        first_phase = 71
    elif comp_test == 'test2':
        last_phase  = 70
        first_phase = 70

    else:
        phase_list  = createPhaseList()
        plen        = len(phase_list)
        if plen > 3:
            last_phase  = phase_list[plen -1]
            first_phase = last_phase - 3
        else:
            exit(1)

#
#--- extract data needed
#
    new_data = getNewData(first_phase, last_phase)
#
#--- if there is no new data, stop the entire operation
#
    if len(new_data) == 0:
        exit(1)
#
#--- read column names --- this is the name of columns we need to save
#
    f        = open(col_names, 'r')
    col_list = [line.strip() for line in f.readlines()]
    f.close()
#
#---extract specified column data
#
    new_data_save = extractElements(new_data, col_list)

#
#---- read the past data
#
    pname    = web_dir + 'Year' + str(tyear) + '/data' + str(tyear)

    chk = mcf.chkFile(pname)
#
#--- if there is no data_<tyear> existed, create an empty file for convenience. 
#
    if chk == 0:
        fo = open(pname, 'w')
        fo.close()
        old_data = []
    else:
        f        = open(pname, 'r')
        old_data = [line.strip() for line in f.readlines()]
        f.close()
#
#--- adjust the last few entries of the old_data as they might be modified while new data come in
#
    adjstPastData(old_data, new_data_save)
#
#--- clean up old and new data files just created (removing duplicate and sorting)
#
    cleanup('./Working_dir/old_data',  1)
    cleanup('./Working_dir/zdata_out', 1)

    name2 = pname + '~'
    cmd   = 'mv ./Working_dir/old_data ' + name2
    os.system(cmd)
#
#--- read cleaned current mit data
#
    f        = open('./Working_dir/zdata_out', 'r')
    mit_data = [line.strip() for line in f.readlines()]
    f.close()

    return mit_data

#-----------------------------------------------------------------------------------------------
#-- checkYearChange: check whether in the given phase, mit data change year                   --
#-----------------------------------------------------------------------------------------------

def checkYearChange(mit_data):
    """
    this function check whether the current mit_data contains data from two consequtive years.
    Input : mit_data
    Output: chk   0 for no, 1 for yes
    """

    chk = 0
    for ent in mit_data:
        atemp = re.split('\t+|\s+', ent)
        btemp = re.split(':',       atemp[1])
#
#--- if it is 1, which means that Jan 1, and hence we think the year changed during the period
#
        if float(btemp[0]) == 1:
            chk = 1
            break

    return chk

#-----------------------------------------------------------------------------------------------
#--- createPhaseList: create a list of phase from the mit web site                            --
#-----------------------------------------------------------------------------------------------

def createPhaseList():
    """
    extract the phase numbers from mit site and creates a list

    Input: noe but read from MIT site

    Output: phase_list: a list of the phase numbers
    """
#
#--- using lynx, read the mit web page where shows phase list
#
    cmd = 'lynx -source http://acis.mit.edu/asc/ >' + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    cmd = 'rm ' + zspace
    os.system(cmd)

    phase_list = []
    for ent in data:
        try:
            atemp = re.split('Phase', ent)
            btemp = re.split('\<',    atemp[1])
            val = float(btemp[0])
            phase_list.append(int(val))
        except:
            pass

    phase_list.sort()

    return phase_list

#-----------------------------------------------------------------------------------------------
#-- getNewData: for given time periods, extract data from mit site using their xs3 files    ----
#-----------------------------------------------------------------------------------------------

def getNewData(first_phase, last_phase):
    """
    using the given phase interval, extreact science run data from mit site
    Input: first_phase/last_phase: the phase interval which you want to extract data
           the data will be read from mit site (XS format)

    Output: new_data ---  extracted data table
    """

    for version in range(first_phase, last_phase+1):
        file = 'http://acis.mit.edu/asc/acisproc' + str(version) + '/acis' + str(version) + '.xs3'
        cmd  = 'lynx -source ' + file + '> ./Working_dir/input_data'
        os.system(cmd)
        cmd  = 'cp ./Working_dir/input_data ' + web_dir + current_dir + '/.'
        os.system(cmd)
#
#--- extract a new part of the data
#
        f    = open('./Working_dir/input_data', 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        new_data = []
        for ent in data:
            m1 = re.search('Multiple Choices',  ent)
            if m1 is not None:
                break
            m2 = re.search('not found',         ent)
            if m2 is not None:
                break
            m3 = re.search('Object not found!', ent)
            if m3 is not None:
                break
            m4 = re.search('was not found',     ent)
            if m4 is not None:
                break

            new_data.append(ent)

    return new_data

#-----------------------------------------------------------------------------------------------
#-- extractElements: extract needed data from mit dataset                                   ----
#-----------------------------------------------------------------------------------------------

def extractElements(new_data, col_list):
    """
    extract only data needed from the data extracted from mit site.
    Input:   new_data --- data extreacted from MIT site
             col_list --- a list of column names which we want to extract from new_data
             new_data contains data in the following format (example)
            ......
             Cn@A2:f2,0|j3|F1:=1
             Cn@B2:f2,0|F1:=53956
             Cl@C2:F1:"HRC-S"
             Cl@D2:j3|F1:"NONE"
             Cl@E2:c5,0|j3|F1:"FEB0413a"
             Cl@F2:c5,0|F1:"Faint_Mode_I"
             Cn@G2:c5,0|f2,0|j3|F1:=0
             Cl@H2:j2|F1:"18028:032"
             Cl@I2:j3|F1:"41:08149.053"
             Cl@J2:j3|F1:"41:16442.880"
             Cn@K2:f2,1|F1:=8.3
             Cn@L2:f2,1|F1:=100.0
             Cl@M2:j3|F1:"I6"
            ......

    Output:  new_data_save: data table only contains needed data in more usable format
    """
#
#--- initialized arrays
#
    for colnam in col_list:
        cname = 'data_' + colnam
        exec "%s = []" % (cname)
#
#---- since the last data entry of the table is usually incomplate, we need to drop it
#
    max_read = len(new_data) -1
    ichk     = 0
#
#---- read data
#
    for ent in new_data:

        if ichk == max_read:                    #---- check the entry until reaching the last entry
            break
        ichk += 1

        if ent[0] == 'C':
            btemp = re.split('\@', ent)
            ctemp = re.split('\:', btemp[1])
            dtemp = ctemp[0]
            seq    = ''
            pos_id = ''
            value  = 'NA'
            for letter in dtemp:
                try:
                    val = float(letter)
                    seq = seq + letter
                except:
#
#--- pos_id: entry position id: A.... BA
#
                    pos_id = pos_id + letter

#
#--- save data for only columns we need
#
            for comp in col_list:
                if pos_id.lower() == comp:
#
#---- time entries need a special care
#
                    if pos_id == 'I' or pos_id == 'J' or pos_id == 'i' or pos_id == 'j' :
                        gtemp =  re.split('\"', ent)
                        val   = gtemp[1]
                    else:
#
#---- none time element entries
#
                        m = re.search('=', ctemp[2])
                        if m is not None:
                            etemp = re.split('=', ctemp[2])
                            val   = etemp[1]
                        else:
                            ftemp = re.split('\"', ctemp[2])
                            val   = ftemp[1]
     
                    vname = 'data_' + pos_id.lower()
                    exec "%s.append(val)" % (vname)
                    break
#
#---- rearrange data
#
    colnam = 'data_' + col_list[0]
    exec "tlen = len(%s) " % (colnam)
    new_data_save = []
    for i in range(0, tlen):
        line = ''
        for colnam in col_list:
            try:
                cdat = 'data_' + colnam
                exec 'add = %s[i]' % (cdat) 
            except:
                add = ''

            if line == '':
                line = add +'\t'
            else:
                line = line + str(add) + '\t'

        new_data_save.append(line)

    return new_data_save

#-----------------------------------------------------------------------------------------------
#-- adjstPastData: update the last few entries of the last data set                          ---
#-----------------------------------------------------------------------------------------------

def adjstPastData(old_data, new_data_save):
    """
    the past data could be modified as an analysis progress; therefore, compare
    new data, and cut off the modified part and save as "old_data". the modified
    part and new part will be saved in zdata_out for the farther processes.

    Input: old_data      --- previously save data
           new_data_save --- newly extracted data

    Output: ./Working_dir/old_data  --- adjusted previous data
            ./Working_dir/zdata_out --- new data part
    """

    f1 = open('./Working_dir/old_data',  'w')
    f2 = open('./Working_dir/zdata_out', 'w')

    lchk = len(new_data_save)
    olen = len(old_data)
#
#--- check whether there are data in the arrays
#
    if lchk > 1 and olen > 0:

        chk_ent  = new_data_save[1]
        save_old = []
        old_pos  = 0
#
#--- find the overlap spot, and stop writing the old data before the spot
#
        for ent in old_data:
            if ent == chk_ent:
                break
            f1.write(ent)
            f1.write('\n')
            save_old.append(ent)
            old_pos += 1
    
    
        for ent in new_data_save:
            chk = 0
#
#--- add new data to old list from the new data list. 
#
            for j in range(old_pos, olen):
                comp  = old_data[j]
                atemp = re.split('\s+', ent)
                btemp = re.split('\s=', comp)
                if atemp[0] == btemp[0]:
                    if ent == conmp:
                        f1.write(ent)
                        f1.write('\n')
                    else:
#
#--- rest go to a new file
#
                        f2.write(ent)
                        f2.write('\n')
                    chk =1
            if(chk == 0):
                f2.write(ent)
                f2.write('\n')

    elif lchk <= 1 and  olen > 0:
        for ent in old_data:
            f1.write(ent)
            f1.write('\n')
    elif olen == 0 and lchk > 1:
        for ent in new_data_save:
            f2.write(ent)
            f2.write('\n')

    f1.close()
    f2.close()

#-----------------------------------------------------------------------------------------------
#--- cleanup: clean up the data file                                                         ---
#-----------------------------------------------------------------------------------------------

def cleanup(file_name, pos = 1):
    """
    this function sort the data at given column, and remove duplicated entries
    Input:  file_name  --- data file name
            pos        --- column # of the entry which you want to use for sorting
                           pos = 1 is date in this case

    Output: file_name  --- cleaned up data        
    """

    pos  = int(pos)
    f    = open(file_name, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    if len(data) > 0:
#
#---- sort the list by date
#
        ndata = []
        for ent in data:
            atemp = re.split('\t+|\s+', ent)
            if len(atemp) == 12:
                try:
#
#--- create a time stamp in float number, and create an array entry.
#--- them create an array of arries so that we can sort the entry with the 
#--- time entry
#
                    float(atemp[0])
                    btemp = re.split(':', atemp[pos])
                    ctime = float(btemp[0]) + float(btemp[1]) / 86400
                    tarry = [ctime, ent]                                #--- array with time stamp and data
                    ndata.append(tarry)                                 #--- array of arrays
                except:
                    pass
#
#--- sort the array by the first entry
#
        tdata = sorted(ndata, key=lambda a_entry: a_entry[0]) 
#
#--- remove the time stamp for the data
#
        data = []
        for ent in tdata:
            data.append(ent[1])

#
#---- remove duplicated raws if column<pos> values are identical
#
        fout = open(zspace, 'w')
        first = data.pop(0)
        fout.write(first)
        fout.write('\n')
        new   = [first]
        for ent in data:
            chk = 0
            atemp = re.split('\t+|\s+', ent)
            for comp in new:
                btemp = re.split('\t+|\s+', comp)
                if atemp[pos] == btemp[pos]:
                    chk = 1
                    break
            if chk == 0:
                new.append(ent)
                fout.write(ent)
                fout.write('\n')
        fout.close()
        cmd = 'mv ' + zspace + ' ' + file_name 
        os.system(cmd)


#-----------------------------------------------------------------------------------------------
#-- separate_data: separate data into sub groups and save them in the separate files         ---
#-----------------------------------------------------------------------------------------------

def separate_data(file, current_dir):
    """
    this function separate the data into sub data sets
    Input: file        --- input file e.g. data_2013
           current_dir --- the name of the directory containing the "file"

    Output: sub data files (see below... <>_out, the data will be saved in current_dir
    """

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- open files
#
    line = web_dir + current_dir + '/te1_3_out'
    f1   = open(line, 'w')
    line = web_dir + current_dir + '/te3_3_out'
    f2   = open(line, 'w')
    line = web_dir + current_dir + '/te5_5_out'
    f3   = open(line, 'w')
    line = web_dir + current_dir + '/te_raw_out'
    f4   = open(line, 'w')
    line = web_dir + current_dir + '/te_hist_out'
    f5   = open(line, 'w')
    line = web_dir + current_dir + '/cc1_3_out'
    f6   = open(line, 'w')
    line = web_dir + current_dir + '/cc3_3_out'
    f7   = open(line, 'w')
    line = web_dir + current_dir + '/cc5_5_out'
    f8   = open(line, 'w')
    line = web_dir + current_dir + '/cc_raw_out'
    f9   = open(line, 'w')
    line = web_dir + current_dir + '/cc_hist_out'
    f10  = open(line, 'w')

    for ent in data:
        col = re.split('\t+|\s+', ent)
#
#--- only ACIS data will be extracted
#
        if col[2] == 'ACIS-I' or col[2] == 'ACIS-S':
            line = ent + '\n'
            if col[4] == 'Te1x3':
                f1.write(line)
            elif col[4] == 'Te3x3':
                f2.write(line)
            elif col[4] == 'Te5x5':
                f3.write(line)
            elif col[4] == 'TeRaw':
                f4.write(line)
            elif col[4] == 'TeHist':
                f5.write(line)
            elif col[4] == 'Cc1x3':
                f6.write(line)
            elif col[4] == 'Cc3x3':
                f7.write(line)
            elif col[4] == 'Cc5x5':
                f8.write(line)
            elif col[4] == 'CcRaw':
                f9.write(line)
            elif col[4] == 'CcHist':
                f10.write(line)

    f1.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()
    f6.close()
    f7.close()
    f8.close()
    f9.close()
    f10.close()


#-----------------------------------------------------------------------------------------------
#--- plot_events: control sub for plotting each data group                                   ---
#-----------------------------------------------------------------------------------------------

def plot_events(data_dir):
    """
    control function to create plots for each sub data set
    Input: data_dir --- the directory name where the data located (e.g. Year2013/)

    Output: png plot file such as te3_3_out.png
    """

    file    = web_dir + data_dir + 'cc3_3_out'
    outname = file + '.png'
    asrf.acis_sci_run_plot(file, outname)

    file    = web_dir + data_dir + 'te3_3_out'
    outname = file + '.png'
    asrf.acis_sci_run_plot(file, outname)

    file    = web_dir + data_dir + 'te5_5_out'
    outname = file + '.png'
    asrf.acis_sci_run_plot(file, outname)

    file    = web_dir + data_dir + 'te_raw_out'
    outname = file + '.png'
    asrf.acis_sci_run_plot(file, outname)

#-----------------------------------------------------------------------------------------------
#--- chkHighEvent: control function to check high count/drop rate events                     ---
#-----------------------------------------------------------------------------------------------

def chkHighEvent(year):
    """
    check high error rates / count rates /drop rates comparing to the given criteria and update 
    the files
    Input: year --- current year.  data are read from the directory Year<year>

    Output: drop_<year>         drop5x5_<year>
            high_error_<year>   high_error5x5_<year>
            high_events_<year>  high_events5x5_<year>

    """

#
#--- te3x3 high drop rate
#
    file    = web_dir + 'Year' + str(year) + '/drop_' + str(year)
#    event   = 'Te3_3'
    event   = 'drop'
    criteria = 3.0 
    dname   = 'drop rate(%)'
    asrf.checkEvent(web_dir, file, event, year,  criteria, dname, comp_test)

#
#--- te5x5 high drop rate
#
    file    = web_dir + 'Year' + str(year) + '/drop5x5_' + str(year)
#    event   = 'Te5_5'
    event   = 'drop5x5'
    criteria = 3.0
    dname   = 'drop rate(%)'
    asrf.checkEvent(web_dir, file, event, year, criteria, dname, comp_test)

#
#--- te3x3 high error rate
#
    file    = web_dir + 'Year' + str(year) + '/high_error_' + str(year)
#    event   = 'Te3_3'
    event   = 'high_error'
    criteria = 1.0 
    dname   = 'err/ksec    '
    asrf.checkEvent(web_dir, file, event, year, criteria, dname, comp_test)

#
#--- te5x5 high error rate
#
    file    = web_dir + 'Year' + str(year) + '/high_error5x5_' + str(year)
#    event   = 'Te5_5'
    event   = 'high_error5x5'
    criteria = 1.0 
    dname   = 'err/ksec    '
    asrf.checkEvent(web_dir, file, event, year, criteria, dname, comp_test)

#
#--- te3x3 high event rate
#
    file    = web_dir + 'Year' + str(year) + '/high_event_' + str(year)
#    event   = 'Te3_3'
    event   = 'high_event'
    criteria = 180.0 
    dname   = 'avg # of events/sec'
    asrf.checkEvent(web_dir, file, event, year, criteria, dname, comp_test)

#
#--- te5x5 high event rate
#
    file    = web_dir + 'Year' + str(year) + '/high_event5x5_' + str(year)
#    event   = 'Te5_5'
    event   = 'high_event5x5'
    criteria = 180.0 
    dname   = 'avg # of events/sec'
    asrf.checkEvent(web_dir, file, event, year, criteria, dname, comp_test)


#-----------------------------------------------------------------------------------------------
#-- longTermTable: control function to update long term data tables                          ---
#-----------------------------------------------------------------------------------------------

def longTermTable(year):
    """
    control function to update each data table file save in Year<year> directory
    Input: year ---- the year you want to update 

    Ouptput data file in Year<year> directory e.g. high_errr_<year> or te3_3_out
    """

#
#--- acis_sci_run_te3x3 drop rate
#
    event   = 'drop'
    dname   = 'drop rate(%)'
    asrf.updateLongTermTable(web_dir, event, year, dname)

#
#--- acis_sci_run_te5x5 drop rate
#
    event   = 'drop5x5'
    dname   = 'drop rate(%)'
    asrf.updateLongTermTable(web_dir, event, year, dname)

#
#--- acis_sci_run_err3x3
#
    event   = 'high_error'
    dname   = 'err/ksec    '
    asrf.updateLongTermTable(web_dir, event, year, dname)

#
#--- acis_sci_run_err5x5
#
    event   = 'high_error5x5'
    dname   = 'err/ksec    '
    asrf.updateLongTermTable(web_dir, event, year, dname)

#
#--- acis_sci_run_high_evnt3x3
#
    event   = 'high_event'
    dname   = 'avg # of events/sec'
    asrf.updateLongTermTable(web_dir, event, year, dname)

#
#--- acis_sci_run_high_evnt5x5
#
    event   = 'high_event5x5'
    dname   = 'avg # of events/sec'
    asrf.updateLongTermTable(web_dir, event, year, dname)

#
#--- te1x3
#
    event = 'Te1_3'
    asrf.updateLongTermTable2(web_dir, event, year)

#
#--- te3x3
#
    event = 'Te3_3'
    asrf.updateLongTermTable2(web_dir, event, year)

#
#--- te5x5
#
    event = 'Te5_5'
    asrf.updateLongTermTable2(web_dir, event, year)

#
#--- te_raw
#
    event = 'Te_raw'
    asrf.updateLongTermTable2(web_dir, event, year)

#
#--- cc3x3
#
    event = 'cc3_3'
    asrf.updateLongTermTable2(web_dir, event, year)


#-----------------------------------------------------------------------------------------------
#-- update_all_data: update a file "all_data" to current                                     ---
#-----------------------------------------------------------------------------------------------

def update_all_data(mit_data, year):
    """
    this function updates a file "all_data" which contains all past data.
    Input: mit_data: a current data table extracted from mit site
           year:     the year of the mit_data

    Output:    web_dir/all_data
    """
#
#--- save the last data 
#
    cmd = 'mv ' + web_dir + 'all_data ' + web_dir + 'all_data~'
    os.system(cmd)
#
#--- add year to time column which is in ydate format
#
    fout = open(zspace, 'w')
    for ent in mit_data:
        atemp = re.split('\t+|\s+', ent)
        for j in range(0, 12):
            if j == 1:
                line = str(year) + ':' + atemp[j] + '\t'
                fout.write(line)
            elif j == 11:
                line = atemp[j] + '\n'
                fout.write(line)
            else:
                line = atemp[j] + '\t'
                fout.write(line)

    fout.close()

#
#--- append the most recent data to all_data
#
    cmd = 'cat ' + zspace + ' ' + web_dir + 'all_data~ >> ' + web_dir + 'all_data'
    os.system(cmd)

    cmd = 'rm ' + zspace
    os.system(cmd)
#
#--- remove duplicated lines
#
    name = web_dir + 'all_data'

    asrf.removeDuplicated(name)

#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':
    acis_sci_run_get_data()

