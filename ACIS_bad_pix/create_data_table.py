#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#   create_data_table.py: create a data display html sub pages                                      #
#                                                                                                   #
#               author: t. isobe (tisobe@head.cfa.harvard.edu)                                      #
#                                                                                                   #
#               Last upated: Jan 09, 2017                                                           #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
#
#--- check whether this is a test case
#
comp_test = 'live'
if len(sys.argv) == 2:
    if sys.argv[1] == 'test':                   #---- test case
        comp_test = 'test'
    elif sys.argv[1] == 'live':                 #---- automated read in
        comp_test = 'live'
    else:
        comp_test = sys.argv[1].strip()         #---- input data name
#
#--- reading directory list
#
if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py_test'
else:
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
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
#
#--- temp writing file name
#

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#--- create_data_table: create a data display html sub pages                                     ---
#---------------------------------------------------------------------------------------------------

def create_data_table():

    """
    create a data display html sub pages
    Input:  None, but read from <data_dir>/Disp_dir/*

    Output: <web_dir>/Html_dir/ccd_data<ccd>.html
    """
#
#--- sub page part ------------------------------------------------------
#
    main_update_chk  = []
    new_bad_pix_list = []
    new_hot_pix_list = []
    new_col_pix_list = []
    past_bad_list    = []
    past_hot_list    = []
    past_col_list    = []

    for ccd in range(0, 10):
#
#--- open output file
#
        outfile = web_dir + 'Html_dir/ccd_data' + str(ccd) + '.html'
        fo      = open(outfile, 'w')
        chk = 0
#
#--- print header of html page and a part of table
#
        printHtmlHead(fo, ccd)
#
#--- warm pixel cases
#
        (warm, flick, new, past) = readData(ccd, 'ccd')
        printTableContent(fo, warm) 
        printTableContent(fo, flick) 
        printTableContent(fo, past) 

        if warm[0] != '':
            chk += 1
        past_bad_list.append(len(past))
        new_bad_pix_list.append(new)
#
#--- hot pixel cases
#
        (warm, flick, new, past) = readData(ccd, 'hccd')
        printTableContent(fo, warm) 
        printTableContent(fo, flick) 
        printTableContent(fo, past) 

        if warm[0] != '':
            chk += 1
        past_hot_list.append(len(past))
        new_hot_pix_list.append(new)
#
#--- bad column cases
#
        (warm, flick, new, past) = readData(ccd, 'col')
        printTableContent(fo, warm) 
        printTableContent(fo, flick) 
        printTableContent(fo, past) 

        if warm[0] != '':
            chk += 1
        past_col_list.append(len(past))
        new_col_pix_list.append(new)
#
#--- close table and then html page
#
        printHtmlEnd(fo)

        main_update_chk.append(chk)

        fo.close()

#
#--- main page part ---------------------------------------------------------------
#

    ofile = web_dir + '/mta_bad_pixel_list.html'
    fo = open(ofile, 'w')

    print_main_head_part(fo, new_bad_pix_list, new_hot_pix_list, new_col_pix_list)

    prit_main_mid_part(fo, main_update_chk, past_bad_list, past_hot_list, past_col_list)

    print_main_tail_part(fo)

    fo.close()

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def  print_main_head_part(fo, new_bad_pix_list, new_hot_pix_list, new_col_pix_list):

    localt = tcnv.currentTime('UTC')
    tyear  = int(localt[0])
    tyday  = int(localt[7])
    dom    = tcnv.YdateToDOM(tyear, tyday)

    dispt  = tcnv.currentTime('Display')
    atemp  = re.split('\s+', dispt)
    dtime  = atemp[0] + ' ' +  atemp[1] + ' ' + atemp[2] +', ' + atemp[4]

    hfile  = house_keeping + 'head'
    head_part = open(hfile, 'r').read()
    head_part = head_part.replace('#DISPLAY# ', dtime)
    head_part = head_part.replace('#YDATE#', str(tyday))
    head_part = head_part.replace('#DOM#', str(dom))

    line = ''
    chk  = 0
    for i in range(0, 10):
        if new_bad_pix_list[i][0] != '':
            chk += 1
            line = line + 'CCD' + str(i) + ': '
            for ent in new_bad_pix_list[i]:
                line = line + ent
            line = line + '<br />\n'
    if chk == 0:
            line = 'No New Warm Pixel'

    head_part = head_part.replace('#WARMPIX#', line)


    line = ''
    chk  = 0
    for i in range(0, 10):
        if new_hot_pix_list[i][0] != '':
            chk += 1
            line = line + 'CCD' + str(i) + ': '
            for ent in new_hot_pix_list[i]:
                line = line + ent
            line = line + '<br />\n'
    if chk == 0:
            line = 'No New Hot Pixel'

    head_part = head_part.replace('#HOTPIX#', line)


    line = ''
    chk  = 0
    for i in range(0, 10):
        if new_col_pix_list[i][0] != '':
            chk += 1
            line = line + 'CCD' + str(i) + ': '
            for ent in new_col_pix_list[i]:
                line = line + ent
            line = line + '<br />\n'
    if chk == 0:
            line = 'No New Warm Column'

    head_part = head_part.replace('#WARMCOL#', line)

    fo.write(head_part)


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def prit_main_mid_part(fo, main_update_chk,  past_bad_list, past_hot_list, past_col_list):


    line = ''
    for ccd in range(0, 10):

        line = line + '<tr><td>CCD' + str(ccd) + '</td>\n'
        aline = print_current_codition(ccd,'ccd')
        line = line + aline
        aline = print_current_codition(ccd,'hccd')
        line = line + aline
        aline = print_current_codition(ccd,'col')
        line = line + aline



        if past_bad_list[ccd] <= 1:
            line = line + '<td>No History</td>\n'
        else:
            line = line + '<td><a href="./Disp_dir/hist_ccd' + str(ccd) + '">Data</a> \n'
            line = line + '<a href="javascript:WindowOpener(\'hist_plot_ccd'+str(ccd)+'.png\')">Plot</a><br /> \n'
            line = line + '<a href="./Html_dir/past_ccd' + str(ccd) + '">Past Warm Pixels</a></td>'

        if past_hot_list[ccd] <= 1:
            line = line + '<td>No History</td>\n'
        else:
            line = line + '<td><a href="./Disp_dir/hist_hccd' + str(ccd) + '">Data</a>\n'
            line = line + '<a href="javascript:WindowOpener(\'hist_plot_hccd'+str(ccd)+'.png\')">Plot</a><br />\n'
            line = line + '<a href="./Html_dir/past_hccd' + str(ccd) + '">Past Hot Pixels</a></td>'

        if past_col_list[ccd] <= 1:
            line = line + '<td>No History</td>\n'
        else:
            line = line + '<td><a href="./Disp_dir/hist_col' + str(ccd) + '">Data</a>\n'
            line = line + '<a href="javascript:WindowOpener(\'hist_plot_col'+str(ccd)+'.png\')">Plot</a><br />\n'
            line = line + '<a href="./Html_dir/past_col' + str(ccd) + '">Past Warm Columns</a></td>'

        line = line + '</tr>\n'

    line = line + '</table>\n'

    fo.write(line)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def print_current_codition(ccd, head):

    (warm, flick, new, past) = readData(ccd, head)

    line = '<td>'
    for ent in warm:
        if ent != '':
            line = line + ent + '<br />'
    line = line + '</td>'

    line = line + '<td>'
    for ent in flick:
        if ent != '':
            line = line + ent + '<br />'
    line = line + '</td>'

    file = web_dir +  'Html_dir/past_'+ head + str(ccd)
    fo   = open(file, 'w')
    for ent in past:
        fo.write(ent)
        fo.write('\n')
    fo.close()

    return line


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def print_main_tail_part(fo):

    tfile     = house_keeping + 'tail'
    tail_part = open(tfile, 'r').read()

    fo.write(tail_part)


#---------------------------------------------------------------------------------------------------
#--- readData: read data from three files and return three list of data                          ---
#---------------------------------------------------------------------------------------------------

def readData(ccd, head):

    """
    read data from three files and return three list of data
    Input:  infile1, infile2, infile3 --- three input file names
    Output: file1,   file2,   file3   --- three list of data
    """
    file  = data_dir + 'Disp_dir/' + head + str(ccd) + '_information'

    data = mcf.readFile(file)

    warm  = get_elm(data[0])
    flick = get_elm(data[1])
    new   = get_elm(data[2])
    past  = get_elm(data[3])


    return [warm, flick, new, past]

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def get_elm(line):
    dlist = []
    line  = line.replace(' ', '')
    atemp = re.split(':', line)
    if len(atemp) > 1:
        for k in range(1, len(atemp)):
            ent = atemp[k].strip()
            dlist.append(ent)

    return dlist

#---------------------------------------------------------------------------------------------------
#-- printHtmlHead: print head of HTML page and a beginning of a table                            ---
#---------------------------------------------------------------------------------------------------

def printHtmlHead(fo, ccd):

    """
    print head of HTML page and a beginning of a table
    Input:  fo  --- file hnadle
            ccd --- ccd #
    """

    line = "<!DOCTYPE html>\n"
    line = line + "<html>\n"
    line = line + "<head>\n"
    line = line + "<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />\n"
    line = line + "<style  type='text/css'>\n"
    line = line + "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}\n"
    line = line + "td{text-align:center;padding:8px}\n"
    line = line + "a:link {color:#00CCFF;}\n"
    line = line + "a:visited {color:yellow;}\n"
    line = line + "span.nobr {white-space:nowrap;}\n"
    line = line + "</style>\n"
    line = line + "<title> ACIS Bad Pixel List: CCD" + str(ccd) + "</title>\n"
    line = line + "</head>\n"

    #line = line + "<body style='color:#FFFFFF;background-color:#000000;'>\n"
    line = line + "<body>\n"

    line = line + "<h3>CCD" + str(ccd) + "</h3>\n"
    line = line + "<br /><br /><a href ='./mta_bad_pixel_list.html'>Back to the main page</a>\n"
    line = line + "<br /><br />\n"

    line = line + "<table border=1 style='border-width:2px;text-align:top'>\n"
    line = line + "<tr>\n"
    line = line + "<th>Current Warm Pixels</th>"
    line = line + "<th>Flickering Warm Pixels</th>"
    line = line + "<th>Past Warm Pixels</th>\n"
    line = line + "<th>Current Hot Pixels</th>"
    line = line + "<th>Flickering Hot Pixels</th>"
    line = line + "<th>Past Hot Pixels</th>\n"
    line = line + "<th>Current Warm Columns</th>"
    line = line + "<th>Flickering Warm Columns</th>"
    line = line + "<th>Past Warm Columns</th>\n"
    line = line + "</tr><tr>\n"

    fo.write(line)


#---------------------------------------------------------------------------------------------------
#-- printTableContent: print table contents                                                      ---
#---------------------------------------------------------------------------------------------------

def printTableContent(fo, list):

    """
    print table contents 
    Input: fo   --- file handle
           list --- a list of data to be printed
    """
    fo.write("<td style='vertical-align:text-top;'>\n")
    if len(list) == 0:
        fo.write("&#160;\n")
    else:
        for i in range(0, len(list)):
            line = "<span class='nobr'>" + str(list[i]) + "</span> <br />\n"
            fo.write(line)
    fo.write("</td>\n")

#---------------------------------------------------------------------------------------------------
#-- printHtmlEnd: print closing part of HTML page (including the end of the table)               ---
#---------------------------------------------------------------------------------------------------

def printHtmlEnd(fo):

    """
    print closing part of HTML page (including the end of the table)
    Input: fo --- file handle

    """
    
    line = "</tr>\n"
    line = line + "</table>\n"
    line = line + "</body>\n"
    line = line + "</html>\n"
    fo.write(line)

#--------------------------------------------------------------------

if __name__ == '__main__':

    create_data_table()


