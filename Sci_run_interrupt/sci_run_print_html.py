#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       sci_run_print_html.py: print out html pagess                            #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Sep 13, 2017                                       #
#                                                                               #
#################################################################################

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
#--- append a path to a private folder to python directory
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

#---------------------------------------------------------------------------------------------
#---  printEachHtmlControl: html page printing control                                     ---
#---------------------------------------------------------------------------------------------

def printEachHtmlControl(file = 'NA'):

    """
    html page printing control function. 
    input:  file    --- the name of the file containing event information
    output: <main_dir>/rad_interrupt.html       if file == 'NA"
            <html_dir>/<evnet>.html
    """
    if file != 'NA':
        f = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
#
#--- first pint indivisula html pages
#
        for ent in data:
                atemp = re.split('\s+', ent)
        
                event = atemp[0]
                start = atemp[1]
                stop  = atemp[2]
                gap   = atemp[3]
                type  = atemp[4]
        
                printEachHtml(event, start, stop, gap, type)
    else:
#
#--- print top pages, auto, manual, hardness, and time ordered
#
        printSubHtml()
#
#---- change permission/owner group of pages
#
    cmd = 'chmod 775 '       + web_dir  + '/*'
    os.system(cmd)
    cmd = 'chgrp mtagroup  ' + web_dir  + '/*'
    os.system(cmd)

    cmd = 'chmod 775 '       + html_dir + '/*'
    os.system(cmd)
    cmd = 'chgrp mtagroup  ' + html_dir + '/*'
    os.system(cmd)

#---------------------------------------------------------------------------------------------
#--- printEachHtml: print out indivisual html page                                         ---
#---------------------------------------------------------------------------------------------

def printEachHtml(event, start, stop, gap, stopType):
    """
    create indivisual event html page. 
    input:  event       ---   event name
            start       --- start time
            stop        --- stop time
            gap         --- aount of interrution in sec
            stopType    --- auto/manual
    
    example: 20031202        2003:12:02:17:31        2003:12:04:14:27        139.8   auto
    output: html pages
    """
#
#--- modify date formats
#   
    begin = start + ':00'
    (year1, month1, date1, hours1, minutes1, seconds1, ydate1, dom1, sectime1) = tcnv.dateFormatConAll(begin)

    end   = stop  + ':00'
    (year2, month2, date2, hours2, minutes2, seconds2, ydate2, dom2, sectime2) = tcnv.dateFormatConAll(end)
#
#--- find plotting range
#
    (pYearStart, periodStart, pYearStop, periodStop, plotYearStart,\
     plotStart, plotYearStop, plotStop, pannelNum)  = itrf.findCollectingPeriod(year1, ydate1, year2, ydate2)
#
#--- check whether we need multiple pannels
#
    pannelNum  = int((plotStop - plotStart) / 5)
#
#--- choose a template
#
    atemp = re.split(':', start)
    year  = int(atemp[0])
    if year < 2011:
        file = house_keeping + 'sub_html_template'
    elif year < 2014:
        file = house_keeping + 'sub_html_template_2011'
    else:
        file = house_keeping + 'sub_html_template_2014'
#
#--- read the template and start substituting 
#
    data = open(file).read()

    data = re.sub('#header_title#',  event,    data)
    data = re.sub('#main_title#',    event,    data)
    data = re.sub('#sci_run_stop#',  start,    data)
    data = re.sub('#sci_run_start#', stop,     data)
    data = re.sub('#interruption#',  gap,      data)
    data = re.sub('#trigger#',       stopType, data)

    noteN = event + '.txt'
    data = re.sub('#note_name#',     noteN,  data)
#
#--- ACA (NOAA) radiation data
#
    aceData = event + '_dat.txt'
    data = re.sub('#ace_data#',     aceData, data)

    file = stat_dir + event + '_ace_stat'
    try:
        stat = open(file).read()
        data = re.sub('#ace_table#',    stat,    data)
    
        line =  event + '.png"'
        for i in range(2, pannelNum+1):
            padd = ' alt="main plot" style="width:100%">\n<br />\n<img src = "../Main_plot/' 
            padd = padd + event + '_pt' + str(i) + '.png '
            line = line + padd
    
        data = re.sub('#ace_plot#', line , data)
    except:
        pass
#
#---EPHIN data
#

    ephData = event + '_eph.txt'
    data = re.sub('#eph_data#', ephData, data)

    file = stat_dir + event + '_ephin_stat'
    try:
        stat = open(file).read()
        data = re.sub('#eph_table#',    stat,    data)
    
        line =  event + '_eph.png"'
        for i in range(2, pannelNum+1):
            padd = ' alt="eph plot" style="width:100%">\n<br />\n<img src = "../Ephin_plot/' 
            padd = padd + event + '_eph_pt' + str(i) + '.png '
            line = line + padd
    
        data = re.sub('#eph_plot#', line , data)
    except:
        pass
#
#---GOES data
#
    goesData = event + '_goes.txt'
    data = re.sub('#goes_data#', goesData, data)

    file = stat_dir + event + '_goes_stat'
    try:
        stat = open(file).read()
        data = re.sub('#goes_table#',    stat,    data)
    
        line =  event + '_goes.png"'
        for i in range(2, pannelNum+1):
            padd = ' alt="goes plot" style="width:100%"> \n<br />\n<img src = "../GOES_plot/' 
            padd = padd + event + '_goes_pt' + str(i) + '.png '
            line = line + padd
    
        data = re.sub('#goes_plot#', line , data)
    
        if year1 >= 2011:
            data = re.sub('GOES-11', 'GOES-15', data)
    except:
        pass
#
#---XMM data
#
    xmmData = event + '_xmm.txt'
    data = re.sub('#xmm_data#', xmmData, data)

    file = stat_dir + event + '_xmm_stat'
    try:
        stat = open(file).read()
        data = re.sub('#xmm_table#',    stat,    data)
    
        line =  event + '_xmm.png"'
        for i in range(2, pannelNum+1):
            padd = ' alt="xmm plot" style="width:100%"> \n<br />\n<img src = "../XMM_plot/' 
            padd = padd + event + '_xmm_pt' + str(i) + '.png '
            line = line + padd
    
        data = re.sub('#xmm_plot#', line , data)
    except:
        pass
#
#--- ACIS
#
    fin = open('./acis_list', 'r')
    alist = [line.strip() for line in fin.readlines()]
    fin.close()
    for ent in alist:
        mc = re.search(event, ent)
        if mc is not None:
            atemp = re.split('::', ent)
            blist = re.split(':', atemp[1])
            break
    k = 0
    aline = ''
    for ent in blist:
        aline = aline + "<img src='http://acis.mit.edu/asc/txgif/gifs/"
        aline = aline + ent + ".gif' style='width:45%; padding-bottom:30px;'>\n"
        k += 1
        if k % 2 == 0:
            aline = aline + '<br />\n'

    data = re.sub('#acis_plot#', aline, data)
#
#--- print the page
#
    file = web_dir + 'Html_dir/' + event + '.html'
    f    = open(file, 'w')
    f.write(data)
    f.close()

#----------------------------------------------------------------------------------------------------
#--- printEachPannel: create each event pannel for the top html pages                             ---
#----------------------------------------------------------------------------------------------------

def printEachPannel(event, start, stop, gap, stopType):
    """
    create each event pannel for the top html pages. 
    input:  event       ---   event name
            start       --- start time
            stop        --- stop time
            gap         --- aount of interrution in sec
            stopType    --- auto/manual
            out         --- the name of the output file
    output: line        --- part crated
    """
    line = '<li style="text-align:left;font-weight:bold;padding-bottom:20px">\n'
    line = line + '<table style="border-width:0px"><tr>\n'
    line = line + '<td>Science Run Stop: </td><td> ' + start + '</td><td>Start:  </td><td>' + stop + '</td>'
    line = line + '<td>Interruption: </td><td> %4.1f ks</td><td>%s</td>\n' %(float(gap), stopType)
    line = line + '</tr></table>\n'

    address = html_dir.replace('/data/mta_www/', '/mta_days/')
    line = line + '<a href="' + address + event + '.html"><img src="./Intro_plot/' 
    line = line + event + '_intro.png" alt="intro plot" style="width:100%;height:20%"></a>\n'

    address = data_dir.replace('/data/mta_www/', '/mta_days/')
    line = line + '<a href="' + address + event + '_dat.txt">ACE RTSW EPAM Data</a>\n'
    line = line + '<a href="' + address + event + '_eph.txt">Ephin Data</a>\n'
    line = line + '<a href="' + address + event + '_goes.txt">GOES Data</a>\n'

    address = note_dir.replace('/data/mta_www/', '/mta_days/')
    line = line + '<a href="' + address + event + '.txt">Note</a>\n'

    address = html_dir.replace('/data/mta_www/', '/mta_days/')
    line = line + '<a href="' + address + event + '.html">Plots</a>\n'

    line = line + '<br />\n'
    line = line + '<div style="padding-bottom:10px">\n</div>\n'
    line = line + '</li>\n'

    return line


#----------------------------------------------------------------------------------------------------
#--- printSubHtml: create auto/manual/hardness/time ordered html pages                            ---
#----------------------------------------------------------------------------------------------------

def printSubHtml():

    """
    create auto/manual/hardness/time ordered html page. 
    input: none, but data are read from house_keeping and stat_dir 
    output: auto_shut.html etc
    """
#
#--- read the list of the interruptions
#

    file        = house_keeping+ 'all_data'
    fin         = open(file, 'r')
    timeOrdered = [line.strip() for line in fin.readlines()]
    fin.close()

    auto_list      = []
    manual_list    = []
    hardness_list  = []
#
#--- create list of auto, manual, and hardness ordered list. time ordered list is the same as the original one
#
    [auto_list, manual_list, hardness_list] = createOrderList(timeOrdered)
#
#--- print out each html page
#
    for type in ('auto_shut', 'manual_shut', 'hardness_order', 'time_order'):
#
#--- read the template for the top part of the html page
#
        line = house_keeping + 'main_html_page_header_template'
        data = open(line).read()
#
#---- find today's date so that we can put "updated time in the web page
#
        [dyear, dmon, dday, dhours, dmin, dsec, dweekday, dyday, dst] = tcnv.currentTime('UTC')
        today = str(dyear) + '-' + str(dmon) + '-' + str(dday)
        data  = re.sub("#DATE#", today, data)
        oline = data

        oline = oline + '<table style="border-width:0px">\n'
        oline = oline + '<tr><td>\n'

        if type == 'auto_shut':
            oline = oline + autoHtml()
            inList = auto_list

        elif type == 'manual_shut':
            oline = oline + manualHtml()
            inList = manual_list

        elif type == 'hardness_order':
            oline = oline + hardnessHtml()
            inList = hardness_list

        else:
            oline = oline + timeOrderHtml()
            inList = timeOrdered

        oline = oline + '</table>\n'
        oline = oline + '<ul>\n'
#
#--- now create each event pannel
#
        for ent in inList:
            atemp    = re.split('\s+|\t+', ent)
            event    = atemp[0]
            start    = atemp[1]
            stop     = atemp[2]
            gap      = atemp[3]
            stopType = atemp[4]

            oline = oline + printEachPannel(event, start, stop, gap, stopType)

        oline = oline + '</ul>\n'
        oline = oline + '</body>'
        oline = oline + '</html>'

        fout = web_dir + type +'.html'
        out  = open(fout, 'w')
        out.write(oline)
        out.close()

#---------------------------------------------------------------------------------------------------
#--- autoHtml: print a header line for auto shutdown case                                        ---
#---------------------------------------------------------------------------------------------------

def autoHtml():

    line = '<a href="time_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Time Ordered List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<em class="lime" style="font-weight:bold;font-size:120%">\n'
#    line = line + '<a href="auto_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Auto Shutdown List</em>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="manual_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Manually Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="hardness_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Hardness Ordered List</a>\n'
    line = line + '</td><td>\n'

    return line

#---------------------------------------------------------------------------------------------------
#--- manualHtml: print a header line for manual shotdown case                                    ---
#---------------------------------------------------------------------------------------------------

def manualHtml():

    line = '<a href="time_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Time Ordered List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="auto_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Auto Shutdown List</em>\n'
    line = line + '</td><td>\n'
    line = line + '<em class="lime" style="font-weight:bold;font-size:120%">\n'
#    line = line + '<a href="manual_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Manually Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="hardness_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Hardness Ordered List</a>\n'
    line = line + '</td><td>\n'

    return line

#---------------------------------------------------------------------------------------------------
#--- hardnessHtml: print a header line for hardness ordered case                                 ---
#---------------------------------------------------------------------------------------------------

def hardnessHtml():

    line = '<a href="time_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Time Ordered List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="auto_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Auto Shutdown List</em>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="manual_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Manually Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<em class="lime" style="font-weight:bold;font-size:120%">\n'
#    line = line + '<a href="hardness_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Hardness Ordered List</a>\n'
    line = line + '</td><td>\n'

    return line

#---------------------------------------------------------------------------------------------------
#--- timeOrderHtml: print a header line for time ordered case                                    ---
#---------------------------------------------------------------------------------------------------

def timeOrderHtml():

    line = '<em class="lime" style="font-weight:bold;font-size:120%">\n'
#    line = line + '<a href="time_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Time Ordered List</em>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="auto_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Auto Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="manual_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Manually Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="hardness_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Hardness Ordered List</a>\n'
    line = line + '</td><td>\n'

    return line

#---------------------------------------------------------------------------------------------------
#--- createOrderList: create lists of auto/manual shut down and harness ordered list             ---
#---------------------------------------------------------------------------------------------------

def createOrderList(data):

    """
    create lists of auto, manual, and hardness ordered events. 
    input:  data    ---e.g.: 20031202        2003:12:02:17:31        2003:12:04:14:27        139.8   auto
    output: auto_list   --- a list of auto shutdown
            manual_list --- a list of manual shutdown
            hardness_list   --- a list of events sorted by hardness
    """
    auto_list     = []
    manual_list   = []
    hardness_list = []

    hardList      = []

    for ent in data:
#
#--- extract auto and manual entries
#
        m = re.search('auto',   ent)
        n = re.search('manual', ent)
        if m is not None:
            auto_list.append(ent)
        elif n is not None:
            manual_list.append(ent)
#
#--- hardness list bit more effort. find p47/p1060 value from stat file
#

        atemp    = re.split('\s+|\t+', ent)
        statData = stat_dir + atemp[0] + '_ace_stat'

        try:
            sin      = open(statData, 'r')
        except:
            continue

        input    = [line.strip() for line in sin.readlines()]

        for line in input:
            m = re.search('p47/p1060', line)
            if m is not None:
                btemp = re.split('\s+|\t+', line)
                hardList.append(btemp[2])
#
#--- zip the hardness list and the original list so that we can sort them by hardness
#
    tempList = zip(hardList, data)
    tempList.sort()
#
#--- extract original data sorted by the hardness
#
    for ent in tempList:
        hardness_list.append(ent[1])

    return [auto_list, manual_list, hardness_list]

#---------------------------------------------------------------------------------------------

if __name__ == '__main__':
#
#---- plotting the data and create html pages
#
    file = raw_input('Please put the intrrupt timing list (if "NA", print all top level html pages: ')
    printEachHtmlControl(file)

