#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       acis_sci_run_functions.py: collection of functions used by acis sci run #
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

#
#--- pylab plotting routine related modules
#
from pylab import *
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines


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

#
#--- temp writing file name
#

rtail  = int(10000 * random())
zspace = '/tmp/zspace' + str(rtail)

http_dir = 'https://cxc.cfa.harvard.edu/mta_days/mta_acis_sci_run/'

#
#--- NOTE:
#--- because we need to run test, web_dir read from dir_list_py cannot be used. instead
#--- we are passing from the main script's web_dir to local html_dir variable. (Apr 26, 2013)
#

#-----------------------------------------------------------------------------------------------
#--- removeDuplicated: remove duplicated entries                                             ---
#-----------------------------------------------------------------------------------------------

def removeDuplicated(file):
    """
    remove duplicated rows from the file
    Input:      file --- a file name of the data

    Output:     file --- cleaned up data
    """

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    if len(data) > 0:
        first = data.pop(0)
        new   = [first]
    
        for ent in data:
            chk = 0
            for comp in new:
                if ent == comp:
                    chk = 1
                    break
            if chk == 0:
                new.append(ent)
    
#
#--- now print out the cleaned up data 
#
        f    = open(file, 'w')
        for ent in new:
            f.write(ent)
            f.write('\n')
        f.close()

#-----------------------------------------------------------------------------------------------
#--- acis_sci_run_print_html: update html pages                                               --
#-----------------------------------------------------------------------------------------------

def acis_sci_run_print_html(html_dir, pyear, pmonth, pday,  pchk):
    """
    update three html pages according for the year (pyear)
    Input: html_dir --- web directory path
           pyear  --- the year you want to update the html pages
           pmonth --- current month
           pday   --- current month date
           pchk   --- if it is "yes", it will also update the main html, otherwise, just update subs
    Output: science_run.html
            science_long_term.html
            science_run<year>.html

    """
    pyear = int(pyear)

    update = str(pyear) + '-' + str(pmonth) + '-' + str(pday)
    dom    = int(tcnv.findDOM(pyear, pmonth, pday, 0, 0, 0))
    ydate  = tcnv.findYearDate(pyear, pmonth, pday)
#
#---- update the main html page
#
    if pchk == 'yes':
        ylist = ''
        j    = 0
        for ryear in range(1999, pyear+1):
            ylist = ylist + '<td><a href=' + http_dir + '/Year' + str(ryear) + '/science_run' + str(ryear) + '.html>'
            ylist = ylist + '<strong>Year ' + str(ryear) + '</strong></a><br /><td />\n'
            if j == 5:
                j = 0
                ylist = ylist + '</tr><tr>\n'
            else:
                j += 1
    
    
        line  = house_keeping + 'science_run.html'
        f     = open(line, 'r')
        hfile = f.read()
        f.close()
        temp  = hfile.replace('#UPDATE#', update)
        temp1 = temp.replace('#DOY#',     str(ydate))
        temp2 = temp1.replace('#DOM#',    str(dom))
        temp3 = temp2.replace('#YEAR#',   str(pyear))
        temp4 = temp3.replace('#YLIST#',  str(ylist))
    
        line = html_dir + 'science_run.html'
        f    = open(line, 'w')
        f.write(temp4)
        f.close()

#
#--- update this year's sub directory html page
#

    line  = house_keeping + 'sub_year.html'
    f     = open(line, 'r')
    hfile = f.read()
    f.close()
    temp  = hfile.replace('#UPDATE#', update)
    temp1 = temp.replace('#DOY#',     str(ydate))
    temp2 = temp1.replace('#DOM#',    str(dom))
    temp3 = temp2.replace('#YEAR#',   str(pyear))

    line = html_dir + 'Year' + str(pyear) + '/science_run' + str(pyear) + '.html'
    f    = open(line, 'w')
    f.write(temp3)
    f.close()
#
#--- update long term html page
#
    line  = house_keeping + 'science_long_term.html'
    f     = open(line, 'r')
    hfile = f.read()
    f.close()
    temp  = hfile.replace('#UPDATE#', update)
    temp1 = temp.replace('#DOY#',     str(ydate))
    temp2 = temp1.replace('#DOM#',    str(dom))

    line = html_dir + 'Long_term/science_long_term.html'
    f    = open(line, 'w')
    f.write(temp2)
    f.close()


#-----------------------------------------------------------------------------------------------
#-- acis_sci_run_plot: sets up the parameters for the given file and create plots            ---
#-----------------------------------------------------------------------------------------------

def acis_sci_run_plot(file, outname):
    """
    this function sets up the parameters for the given file and create plots
    Input:   file --- data file name
             outname --- plot output file name

    Output:  <outname>.png
    """
#
#--- read input data
#
    f   = open(file, 'r')
    data =  [line.strip() for line in f.readlines()]
    f.close()

    col        = []
    date_list  = []
    count_list = []
    err_list   = []
    drop_list  = []

    xmakerInd  = 0                  #--- used to mark whether this is a plot for a long term (if so, 1)

    for ent in data:
        col   = re.split('\t+|\s+', ent)
        try:
            val = float(col[6])
            if val > 0:
                m = re.search(':', col[1])
#
#--- for each year, change date format to ydate (date format  in the data file is: 112:00975.727)
#
                if m is not None:
                    atemp = re.split(':', col[1])
                    date  = float(atemp[0]) + float(atemp[1])/86400.0
#
#---- for the case of long term: the date format is already in a  fractional year date
#
                else:
                    date      = float(col[1])
                    xmakerInd =  1
#
#--- convert event rate and error rate in an appropreate units
#
                evt   = float(col[7])/float(val)/1000.0
                err   = float(col[8])/float(val)
#
#--- save needed data
#
                date_list.append(date)
                count_list.append(evt)
                err_list.append(err)
                drop_list.append(float(col[9]))
        except:
            pass

    if len(date_list) > 0:
#
#--- set plotting range
#
        (xmin, xmax)   = set_min_max(date_list)

        if xmakerInd == 1:                  #--- if it is a long term, x axis in year (in interger)
            xmin = int(xmin)
            xmax = int(xmax) + 1

        (ymin1, ymax1) = set_min_max(count_list)
#
#--- if the data set is te_raw_out, set the y plotting range to fixed size: 0  - 10
#
        m1 = re.search(file, 'te_raw_out')
        if m1 is not None:
            ymin1 = 0
            ymax1 = 10

        (ymin2, ymax2) = set_min_max(err_list)
        (ymin3, ymax3) = set_min_max(drop_list)

        yminSet  = [ymin1, ymin2, ymin3]
        ymaxSet  = [ymax1, ymax2, ymax3]
        xSets    = [date_list,  date_list, date_list]
        ySets    = [count_list, err_list,  drop_list]

        if xmakerInd == 0:
            xname    = 'Time (Day of Year)'
        else:
            xname    = 'Time (Year)'

        yLabel   = ['Events/sec', 'Events/sec', 'Percent']
        entLabels= ['Events per Second (Science Run)','Errors (Science Run)','Percentage of Exposures Dropped (Science Run)']
#
#--- calling actual plotting routine
#
        plotPanel(xmin, xmax, yminSet, ymaxSet, xSets, ySets, xname, yLabel, entLabels)

        cmd = 'mv out.png ' + outname
        os.system(cmd)

#-----------------------------------------------------------------------------------------------
#--- set_min_max: set min and max of plotting range                                          ---
#-----------------------------------------------------------------------------------------------

def set_min_max(data):
    """
    set  min and max of the plotting range; 10% larger than actual min and max of the data set
    Input: data --- one dimentioinal data set

    Output (pmin, pmanx): min and max of plotting range
    """

    try:
        pmin = min(data)
        pmax = max(data)
        diff = pmax - pmin
        pmin = pmin - 0.1 * diff
        if pmin < 0:
            pmin = 0
        pmax = pmax + 0.1 * diff

        if pmin == pmax:
            pmax = pmin + 1
    
    except:
        pmin = 0
        pmax = 1

    return (pmin, pmax)


#-----------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                       ---
#-----------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yminSet, ymaxSet, xSets, ySets, xname, yLabel, entLabels):

    """
    This function plots multiple data in separate panels.
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            xname: a name of x-axis
            yname: a name of y-axis
            entLabels: a list of the names of each data

    Output: a png plot: out.png
    """
#
#--- set line color list
#
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
#
#--- clean up the plotting device
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    tot = len(entLabels)
#
#--- start plotting each data
#
    for i in range(0, tot):
        axNam = 'ax' + str(i)
#
#--- setting the panel position
#
        j = i + 1
        if i == 0:
            line = str(tot) + '1' + str(j)
        else:
            line = str(tot) + '1' + str(j) + ', sharex=ax0'
            line = str(tot) + '1' + str(j)

        exec "%s = plt.subplot(%s)"       % (axNam, line)
        exec "%s.set_autoscale_on(False)" % (axNam)      #---- these three may not be needed for the new pylab, but 
        exec "%s.set_xbound(xmin,xmax)"   % (axNam)      #---- they are necessary for the older version to set

        exec "%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam)
        exec "%s.set_ylim(ymin=yminSet[i], ymax=ymaxSet[i], auto=False)" % (axNam)

        xdata  = xSets[i]
        ydata  = ySets[i]
  
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], lw =0,  markersize=4.0, marker='o')

#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec "%s.set_ylabel(yLabel[i], size=8)" % (axNam)

#
#--- add x ticks label only on the last panel
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        if i != tot-1: 
            exec "line = %s.get_xticklabels()" % (ax)
            for label in  line:
                label.set_visible(False)
        else:
            pass

    xlabel(xname)

#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=100)


#-----------------------------------------------------------------------------------------------
#-- plotPanel2: plotting multiple data in a single panel                                     ---
#-----------------------------------------------------------------------------------------------

def plotPanel2(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels):

    """
    This function plots multiple data in a single panel.
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            xname: a name of x-axis
            yname: a name of y-axis
            entLabels: a list of the names of each data

    Output: a png plot: out.png
    """

    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

#
#---- set a panel
#
    ax = plt.subplot(111)
    ax.set_autoscale_on(False)      #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)        #---- they are necessary for the older version to set

    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    tot = len(entLabels)
#
#--- start plotting each data set
#
    lnamList = []
    for i in range(0, tot):
        xdata  = xSets[i]
        ydata  = ySets[i]

        if tot > 1:
            lnam = 'p' + str(i)
            lnamList.append(lnam)
            exec "%s, = plt.plot(xdata, ydata, color=colorList[i], lw =1 , marker='.', markersize=0.5, label=entLabels[i])" % (lnam)
        else:
#
#--- if there is only one data set, ignore legend
#
            plt.plot(xdata, ydata, color=colorList[i], lw =1 , marker='.', markersize=0.5)

#
#--- add legend
#
    if tot > 1:
        line = '['
        for ent in lnamList:
            if line == '[':
                line = line + ent
            else:
                line = line +', ' +  ent
        line = line + ']'

        exec "leg = legend(%s,  entLabels, prop=props)" % (line)
        leg.get_frame().set_alpha(0.5)

    ax.set_xlabel(xname, size=8)
    ax.set_ylabel(yname, size=8)


#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=100)


#-----------------------------------------------------------------------------------------------
#--- checkEvent: check high event/error/drop cases, and send out a warning message if needed ---
#-----------------------------------------------------------------------------------------------

def checkEvent(html_dir, file, event, year, criteria, dname, comp_test):
    """
     check high event/error/drop cases, and send out a warning message if needed
     Input: html_dir --- web directory path
            file  --- data file name    e.g. drop_<year>
            event --- event name        e.g. Te3_3
            criteria --- cut off        e.g. 3.0 for Te3_3
            dname    --- table name     e.g. drop rate(%)
            comp_test --- test case indicator 

    Output: file --- updated with newly found violation
            email will be sent out if a new violation was found
    """

#
#----- read the past record of high error records
#
    old_data = readPastData(file)
#
#----- read the main table and file new entries
#
    current_data = readCurrentData(html_dir, year)

#
#----- now update the "event" table
#
    new_list = updateEventTable(html_dir, current_data, event, year, criteria, dname)
    
#
#---- check new high event and send out warning if there is a new  high event
#
    chkNewHigh(old_data, new_list, event, dname, comp_test)


#-----------------------------------------------------------------------------------------------
#-- readPastData: read the "past" data                                                      ----
#-----------------------------------------------------------------------------------------------

def readPastData(file):
    """
    read "past"data 
    Input: file --- the name of the file you want to read in

    Output: old_data

    """

    try:
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        old_data = []
        for ent in data:
            atemp = re.split('\t+|\s+', ent)
            try:
                val = float(atemp[0])
                old_data.append(ent)
            except:
                pass
    except:
        old_data = []

    return old_data

#-----------------------------------------------------------------------------------------------
#-- readCurrentData: read the "current" data                                                 ---
#-----------------------------------------------------------------------------------------------

def readCurrentData(html_dir, year):
    """
    read the "current" data
    Input: html_dir --- web directory path
           year  ---- the data file name is Year<year>/data<year> e.g., Year2013/data2013

    Output: data
    """

    file = html_dir + 'Year' + str(year) + '/data' + str(year)
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    return data


#-----------------------------------------------------------------------------------------------
#-- updateEventTable: extract violation data from the data and update the violation tables   ---
#-----------------------------------------------------------------------------------------------

def updateEventTable(html_dir, data, event, year, criteria, dname):
    """
    extract violation data (eg. high drop rate/high event rate/high error rate) from the data<year>
    and update violation tables

    Input: html_dir --- web directory path 
           data --- data<year>     full data for the year
           event -- event name     e.g. drop (for te3_3) 
           year  -- year of the data
           criteria -- violation criteria
           dname   --- name of the column e.g. "drop rate (%)"
    Output: 
            updated table such as Year<year>/drop_<year>
            new_lst --- the same information passed back to a calling function

    """
#
#--- start writing the table (over write the past table)
#
    new_list = []
    file = html_dir + 'Year' + str(year) + '/' + event + '_' + str(year)
    f    = open(file, 'w')
    line = 'obsid   target                  start time  int time        inst    ccd     grat    ' + dname + '\n'
    f.write(line)
    f.write('-----------------------------------------------------------------------------------------------------------\n')

    m = re.search('Te', event)

    for ent in data:
        atemp = re.split('\t+|\s+', ent)
        if m is not None:
#
#--- if the case is "drop" rate, the pass the data as it is
#
            cval = float(atemp[9])
        else:
#
#--- otherwise normalize the data
#
            cval = 0
            try:
                val6  = float(atemp[6])
                if val6 > 0:
                    cval = float(atemp[7])/val6
                    cval = round(cval, 3)
            except:
                pass
#
#--- here is the selection criteria
#
        if atemp[2] == 'ACIS' and atemp[4] == event and cval > criteria:
            ratio = round(ratio, 6)
#
#--- limit length of description to 20 letters
#
            alen  = len(atemp[11])
            if alen < 20:
                dline = atemp[11]
                for i in range(alen, 20):
                    dline = dline + ''
            else:
                dline = '' 
                for i in range(0, 20):
                    dline = dline + atemp[11][i]

            line = atemp[0] + '\t' + dline + '\t' + atemp[1] + '\t' + atemp[6] + '\t' +atemp[2] + '\t' + atemp[3] + '\t'
            line = line + '\t' + atemp[10] + '\t' + str(cval) + '\n'
            f.write(line)
            new_list.append(line)

    f.close()                    

    return new_list

#-----------------------------------------------------------------------------------------------
#-- updateLongTermTable: update a long term violation tables                                 ---
#-----------------------------------------------------------------------------------------------

def updateLongTermTable(html_dir, event, this_year, dname):
    """
    updates long term violation tables
    Input:   html_dir --- web directory path
             events  --- name of events such as drop (te3_3)
             this_year --- the latest year
             dname     --- column name to use

    Output:
            violation table file named "event"
    """

    oname = html_dir + 'Long_term/' + event.lower()
    fout  = open(oname, 'w')
    line  = 'obsid   target                  start time  int time        inst    ccd     grat    ' + dname + '\n'
    fout.write(line)
    fout.write('-----------------------------------------------------------------------------------------------------------\n')

    for  year in range(1999, this_year+1):
        line = '\nYear' + str(year) + '\n'
        fout.write(line)

        fname = html_dir + 'Year' + str(year) + '/' + event.lower() + '_' + str(year)
        f     = open(fname, 'r')

        data  = [line.strip() for line in f.readlines()]
        f.close()
        for ent in data:
            atemp = re.split('\t+|\s+', ent)
            try:
                val = float(atemp[0])
                fout.write(ent)
                fout.write('\n')
            except:
                pass
    fout.close()


#-----------------------------------------------------------------------------------------------
#-- updateLongTermTable2: update long term sud data tables                                   ---
#-----------------------------------------------------------------------------------------------

def updateLongTermTable2(html_dir, event, this_year):
    """
    update long term sub data tables
    Input:   html_dir    web directory path
             event    name of the event  such as te3_3
             this_year    the latest year
    Output:  sub data file suchas te3_3_out
    """

    oname = html_dir + 'Long_term/' + event.lower() + '_out'
    fout  = open(oname, 'w')

    for  year in range(1999, this_year+1):
#
#--- check leap year
#
        chk   =  4.0 * int(0.25 * float(year))
        if chk == float(year):
            base = 366.0
        else:
            base = 365.0
#
#--- read each year's data
#
        fname = html_dir + 'Year' + str(year) + '/' + event.lower() + '_out'
        f     = open(fname, 'r')
        data  = [line.strip() for line in f.readlines()]
        f.close()

        for ent in data:
            atemp = re.split('\t+|\s+', ent)
            try:
                val = float(atemp[0])
                btemp = re.split(':', atemp[1])
#
#--- convert time to year date to fractional year
#
                time = float(year) + (float(btemp[0]) + float(btemp[1])/ 86400.0 ) / base
                time = round(time, 3)
                dlen = len(atemp)
                dlst = dlen -1

                for j in range(0, dlen):
                    if j == 1:
                        fout.write(str(time))
                        fout.write('\t')
                    elif j == dlst:
                        fout.write(atemp[j])
                        fout.write('\n')
                    else:
                        fout.write(atemp[j])
                        fout.write('\t')
            except:
                pass
    fout.close()

#-----------------------------------------------------------------------------------------------
#-- chkNewHigh: sending out email to warn that there are value violatioins                  ----
#-----------------------------------------------------------------------------------------------

def chkNewHigh(old_list, new_list, event, dname, comp_test):
    """
    sending out email to warn that there are value violatioins 
    Input: old_list:   old violation table
           new_list:   new violation table
           event:      event name
           dname:      column name to be used
           comp_test:  test indicator
    """

    wchk = 0
#
#--- compare old and new list and if there are new entries, save them in "alart"
#
    alart = []
    for ent in new_list:
        chk = 0
        ntemp  = re.split('\t+|\s+', ent)
        for comp in old_list:
            otemp = re.split('\t+|\s+', comp)
            if(ent == comp) or (ntemp[0] == otemp[0]):
                chk = 1
                break
        if chk == 0:
            alart.append(ent)
            wchk += 1
#
#--- if there is violations, send out email
#
    if wchk > 0:
        f = open(zspace, 'w')
        f.write('ACIS Science Run issued the following warning(s)\n\n')
        line = "The following observation has a " + event + "Rate in today's science run\n\n"
        f.write(line)
        line = 'obsid   target                  start time  int time        inst    ccd     grat    ' + dname + '\n'
        f.write(line)
        f.write('-------------------------------------------------------------------------------------------------------\n')
        for ent in alart:
            f.write(ent)
            f.write('\n')

        f.write('\nPlese check: https://cxc.cfa.harvard.edu/mta_days/mta_acis_sci_run/science_run.html\n')
        f.write('\n or MIT ACIS Site: http://acis.mit.edu/asc/\n')
        f.close()

        if comp_test == 'test' or comp_test == 'test2':
            cmd = 'cat ' + zspace + '|mailx -s \"Subject: ACIS Science Run Alert<>' + event + 'Rate \n" isobe\@head.cfa.harvard.edu'
        else:
            cmd = 'cat ' + zspace + '|mailx -s \"Subject: ACIS Science Run Alert<>' + event + 'Rate \n" isobe\@head.cfa.harvard.edu'
#            cmd = 'cat ' + zspace + '|mailx -s \"Subject: ACIS Science Run Alert<>' + event + 'Rate \n" isobe\@head.cfa.harvard.edu  swolk\@head.cfa.harvard.edu brad\@head.cfa.harvard.edu acisdude\@head.cfa.harvard.edu"'

        os.system(cmd)

        cmd = 'rm ' + zspace
        os.system(cmd)

#-----------------------------------------------------------------------------------------------
#-- prep_for_test: creating test output directories/fies                                     ---
#-----------------------------------------------------------------------------------------------

def prep_for_test(html_dir, comp_test):
    """
    this function creates test out put directories and files
    Input: html_dir --- web directory path
    Output: Test output directories, such as "Test_out"
    """
    
    cmd = 'mkdir ' + html_dir
    os.system(cmd)
    
    cmd = 'mkdir ' + html_dir + 'Long_term'
    os.system(cmd)

    end_year = 2012
    if comp_test == 'test2':
        end_year = 2011

    for tyear in range(1999, end_year):
        cmd = 'ln -s /data/mta/www/mta_acis_sci_run/Year' + str(tyear) + ' ' + html_dir + 'Year' + str(tyear)
        os.system(cmd)

    if comp_test == 'test':
        cmd = 'mkdir ' + html_dir + 'Year2012'
        os.system(cmd)

        line = html_dir + 'Year2012/data2012'
        f    = open(line, 'w')
        f.close()

        cmd = 'cp ' + house_keeping + 'Test_prep/data2012 ' + html_dir + 'Year2012/.'
        os.system(cmd)
    elif comp_test == 'test2':
        cmd = ' cp -r /data/mta/www/mta_acis_sci_run/Year2011 ' + html_dir + '/.'
        os.system(cmd)

