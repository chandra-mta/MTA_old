#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#       plot_bias.py: create  various history plots of bias related data                                    #
#                                                                                                           #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                           #
#                   Last update: May 13, 2014                                                               #
#                                                                                                           #
#############################################################################################################

import os
import sys
import re
import string
import random
import operator
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

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
    path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/bias_dir_list_test_py'
else:
    path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/bias_dir_list_py'

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
import convertTimeFormat       as tcnv
import mta_common_functions    as mcf
import bad_pix_common_function as bcf
#
#--- temp writing file name
#

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#--- plot_bias_data: creates history plots of bias, overclock and bias - overclock               ---
#--------------------------------------------------------------------------------------------------- 

def plot_bias_data():

    """
    creates history plots of bias, overclock and bias - overclock
    Input:  None but read from:
                <data_dir>/Bias_save/CCD<ccd>/quad<quad>
    Output:     <web_dir>/Plots/Bias_bkg/ccd<ccd>.png'
                <web_dir>/Plots/Overclock/ccd<ccd>.png
                <web_dir>/Plots/Sub/ccd<ccd>.png
    """

    for ccd in range(0, 10):
#
#--- set arrays
#
        yMinSets1  = []
        yMaxSets1  = []
        xSets1     = []
        ySets1     = []
        entLabels1 = []

        yMinSets2  = []
        yMaxSets2  = []
        xSets2     = []
        ySets2     = []
        entLabels2 = []

        yMinSets3  = []
        yMaxSets3  = []
        xSets3     = []
        ySets3     = []
        entLabels3 = []

        for quad in range(0, 4):
#
#--- read data in
#
            file = data_dir + 'Bias_save/CCD' + str(ccd) + '/quad' + str(quad)
            f    = open(file, 'r')
            data = [line.strip() for line in f.readlines()]
            f.close()

            time      = []
            bias      = []
            overclock = []
            bdiff     = []
            scnt      = 0.0
            sum1      = 0.0
            sum2      = 0.0
            sum3      = 0.0

            for ent in data:
                try:
                    atemp = re.split('\s+|\t+', ent)
                    stime = (float(atemp[0]) - 48902399.0)/86400.0

                    bval = float(atemp[1])
                    oval = float(atemp[3])
                    bmo  = bval - oval 

                    time.append(stime)
                    bias.append(bval)
                    overclock.append(oval)
                    bdiff.append(bmo)

                    sum1 += bval
                    sum2 += oval
                    sum3 += bmo
                    scnt += 1.0
                except:
                    pass
#
#--- put x and y data list into  the main list
#
            xSets1.append(time)
            ySets1.append(bias)
            title = 'CCD' + str(ccd) + ' Quad' + str(quad)
            entLabels1.append(title)

            xSets2.append(time)
            ySets2.append(overclock)
            title = 'CCD' + str(ccd) + ' Quad' + str(quad)
            entLabels2.append(title)

            xSets3.append(time)
            ySets3.append(bdiff)
            title = 'CCD' + str(ccd) + ' Quad' + str(quad)
            entLabels3.append(title)
#
#--- set plotting range
#
            xmin = min(time)
            xmax = max(time)
            diff = xmax - xmin
            xmin = int(xmin - 0.05 * diff)
            if xmin < 0:
                xmin = 0

            xmax = int(xmax + 0.05 * diff)
#
#-- plotting range of bias
#
            avg  = float(sum1) / float(scnt)
            ymin = int(avg - 200.0)
            ymax = int(avg + 200.0)

            yMinSets1.append(ymin)
            yMaxSets1.append(ymax)
#
#-- plotting range of overclock
#
            avg  = float(sum2) / float(scnt)
            ymin = int(avg - 200.0)
            ymax = int(avg + 200.0)

            yMinSets2.append(ymin)
            yMaxSets2.append(ymax)

#
#-- plotting range of bias - overclock
#
            ymin = -1.0
            ymax = 2.5
            if ccd == 7:
                ymin = 2.5
                ymax = 6.0

            yMinSets3.append(ymin)
            yMaxSets3.append(ymax)

        xname = "Time (DOM)"
#
#--- plotting bias 
#
        yname = 'Bias'
        pchk = plotPanel(xmin, xmax, yMinSets2, yMaxSets1, xSets1, ySets1, xname, yname, entLabels1,mksize=1.0, lwidth=0.0)
        if pchk > 0:
            cmd = 'mv out.png ' + web_dir + 'Plots/Bias_bkg/ccd' + str(ccd) +'.png'
            os.system(cmd)
#
#--- plotting overclock
#
        yname = 'Overclock Level'
        pchk = plotPanel(xmin, xmax, yMinSets2, yMaxSets2, xSets2, ySets2, xname, yname, entLabels2, mksize=1.0, lwidth=0.0)
        if pchk > 0:
            cmd = 'mv out.png ' + web_dir + 'Plots/Overclock/ccd' + str(ccd) +'.png'
            os.system(cmd)
#
#--- plotting bias - overclock
#
        yname = 'Bias'
        pchk = plotPanel(xmin, xmax, yMinSets3, yMaxSets3, xSets3, ySets3, xname, yname, entLabels3, mksize=1.0, lwidth=0.0)
        if pchk > 0:
            cmd = 'mv out.png ' + web_dir + 'Plots/Sub/ccd' + str(ccd) +'.png'
            os.system(cmd)

#-----------------------------------------------------------------------------------------------
#--- plot_bias_sub_info: creates history plots for overclock and bias devided by sub category --
#-----------------------------------------------------------------------------------------------

def plot_bias_sub_info():

    """
    creates history plots for overclock and bias devided by sub category 
    Input:  None but read from:
                <data_dir>/Info_dir/CCD<ccd>/quad<quad>
                <data_dir>/Bias_save/CCD<ccd>/quad<quad>
    Output:     <web_dir>/Plot/Param_diff/CCD<ccd>/CCD<ccd>_q<quad>/*
                <web_dir>/Plot/Param_diff/CCD<ccd>/CCD<ccd>_bias_q<quad>/*
                            obs_mode.png            --- categorized by FAINT / VERY FAINT / Others
                            partial_readout.png     --- categorized by Full Data / Partial Data
                            bias_arg1.png           --- categorized by biasarg1 = 9, 10, or others
                            no_ccds.png             --- categorized by # of CCD used: 5, 6, or others
    """

    for ccd in range(0, 10):
        for quad in range(0, 4):
#
#--- read data
#
            file     = data_dir + '/Info_dir/CCD' + str(ccd) + '/quad' + str(quad)
            dataSets = readBiasInfo(file)
            if dataSets == 0:
                continue
#
#--- overclock
#
            dir1   = web_dir + 'Plots/Param_diff/CCD' + str(ccd) + '/CCD' + str(ccd) +  '_q' + str(quad)
            col    = 1
            yname  = 'Overclock Level'
            lbound = 200
            ubound = 200
            plot_obs_mode(dir1, dataSets, col, yname, lbound, ubound)
            plot_partial_readout(dir1, dataSets, col, yname, lbound, ubound)
            plot_bias_arg1(dir1, dataSets, col, yname, lbound, ubound)
            plot_num_ccds(dir1, dataSets, col, yname, lbound, ubound)
#
#---  bias background
#
#
#--- since data size is different, adjust the data to the bais data sets
#
            biasSets = readBiasInfo2(ccd, quad, dataSets)

            dir2   = web_dir + 'Plots/Param_diff/CCD' + str(ccd) + '/CCD' + str(ccd) + '_bias_q' + str(quad)
            col    = 13
            yname  = 'Bias'
            lbound = 3.0
            ubound = 3.0
            plot_obs_mode(dir2, biasSets, col, yname, lbound, ubound)
            plot_partial_readout(dir2, biasSets, col, yname, lbound, ubound)
            plot_bias_arg1(dir2, biasSets, col, yname, lbound, ubound)
            plot_num_ccds(dir2, biasSets, col, yname, lbound, ubound)


#-----------------------------------------------------------------------------------------------
#-- readBiasInfo: reads bias related data and make a list of 12 lists                        ---
#-----------------------------------------------------------------------------------------------

def readBiasInfo(file):

    """
    reads bias related data and make a list of 12 lists
    Input:      file    --- inputfile name
    Output:     a list of 12 lists which contains:
                    time, overclock, mode, ord_mode, 
                    outrow, num_row, sum2_2, deagain, 
                    biasalg, biasarg0, biasarg1, biasarg2, biasarg3
    """
    data = mcf.readFile(file)

    time      = []
    overclock = []
    mode      = []
    ord_mode  = []
    outrow    = []
    num_row   = []
    sum2_2    = []
    deagain   = []
    biasalg   = []
    biasarg0  = []
    biasarg1  = []
    biasarg2  = []
    biasarg3  = []
    bias      = []
    stest     = 0

    for ent in data:
        try:
            atemp = re.split('\s+|\t+', ent)
            dom   = (float(atemp[0]) -  48902399)/86400
            dom   = round(dom, 2)
            time.append(dom)
            overclock.append(float(atemp[1]))
            mode.append(atemp[2])
            ord_mode.append(atemp[3])
            outrow.append(int(atemp[4]))
            num_row.append(int(atemp[5]))
            sum2_2.append(int(atemp[6]))
            deagain.append(float(atemp[7]))
            biasalg.append(float(atemp[8]))
            biasarg0.append(float(atemp[9]))
            biasarg1.append(float(atemp[10]))
            biasarg2.append(float(atemp[11]))
            biasarg3.append(float(atemp[12]))
            stest += 1
        except:
            pass

    if stest > 0:
        return [time, overclock, mode, ord_mode, outrow, num_row, sum2_2, deagain, biasalg, biasarg0, biasarg1, biasarg2, biasarg3]
    else:
        return 0

#-----------------------------------------------------------------------------------------------
#--- readBiasInfo2: reads bias data and adds the list to category information                ---
#-----------------------------------------------------------------------------------------------

def readBiasInfo2(ccd, quad, dataSets):

    """
    reads bias data and adds the list to category information
    Input:      ccd   --- CCD #
                quad  --- Quad #
                dataSets --- a list of 12 data sets (lists) which contains category data
                also need:
                <data_dir>/Bias_save/CCD<ccd>/quad<quad>
    Output:     a list of 13 entiries; 12 above and one of category of 
                    <bias> - <overclock>
                at the 13th position
    """

    dlen  = len(dataSets)
#
#--- get a list of time stamp from the dataSets.
#
    ctime = dataSets[0]
#
#--- read the bias data
#
    line  = data_dir + '/Bias_save/CCD' + str(ccd) + '/quad' + str(quad)
    data  = mcf.readFile(line)

    biasSets = []
    biasdata = []
#
#--- initialize a list to read out each category from dataSets
#
    for i in range(0, 13):
        exec "elm%s = []" % (str(i))
#
#--- start checking bias data
#
    for ent in data:
       atemp = re.split('\s+|\t+', ent)
       try:
#
#--- convert time to DOM
#
            btime = float(atemp[0])
            dom   = (btime -  48902399.0)/86400.0
            dom   = round(dom, 2)

            diff  = float(atemp[1]) - float(atemp[3])
#
#--- there are some bad data; ignore them
#
            if abs(diff) > 5:
                continue
#
#--- match the time in two data sets
#
            for i in range(0, len(ctime)):
                if dom < int(ctime[i]):
                    break
                elif int(dom) == int(ctime[i]):
#
#--- if the time stamps match, save all category data 
#
                    biasdata.append(diff)
                    for j in range(0, dlen):
                        earray  = dataSets[j]
                        val     = earray[i]
                        if isinstance(val, (long, int)):
                            exec "elm%s.append(int(%s))"   % (str(j), str(val))
                        elif isinstance(val, float):
                            exec "elm%s.append(float(%s))" % (str(j), str(val))
                        else:
                            exec "elm%s.append(str(val))"   % (str(j))
                    break    
       except:
            pass
#
#--- create a list of 13 lists
#
    for i in range(0, 13):
        exec "biasSets.append(elm%s)" % (str(i))

    biasSets.append(biasdata)

    return biasSets

#-----------------------------------------------------------------------------------------------
#--- plot_obs_mode: creates history plots categorized by observation modes                   ---
#-----------------------------------------------------------------------------------------------

def plot_obs_mode(mdir, dataSets, col, yname, lbound, ubound):

    """
    creates history plots categorized by observation modes
    Input:      mdir     --- Output directory
                dataSets --- a list of multiple lists. each list contains category data (except the first one is time)
                col      --- a position of data we want to use as a data
                lbound   --- a lower boundary interval from the mean value of the data
                ubound   --- a upper boundary interval from the mean value of the data
    Output:     <mdir>/obs_mode.png     
    """
    time      = dataSets[0]             #--- time in DOM
    dataset   = dataSets[col]
    mode      = dataSets[2]             #--- FAINT, VFAINT, etc

    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x3 = []
    y3 = []
#
#--- divide data into three categories
#
    try:
        for i in range(0, len(time)):
            if mode[i] == 'FAINT':
                x1.append(time[i])
                y1.append(dataset[i])
            elif mode[i] == 'VFAINT':
                x2.append(time[i])
                y2.append(dataset[i])
            else:
                x3.append(time[i])
                y3.append(dataset[i])
    except:
        pass
#
#--- create lists of lists to pass the data into plotting rouinte
#
    xSets     = []
    ySets     = []
    yMinSets  = []
    yMaxSets  = []
    entLabels = []

    xSets.append(x1)
    xSets.append(x2)
    xSets.append(x3)

    ySets.append(y1)
    ySets.append(y2)
    ySets.append(y3)

    entLabels.append('Faint Mode')
    entLabels.append('Very Faint Mode')
    entLabels.append('Others')
#
#--- set plotting range
#
    xmin = min(time)
    xmax = max(time)
    diff = xmax - xmin
    xmin = int(xmin - 0.05 * diff)
    if xmin < 0:
        xmin = 0
    xmax = int(xmax + 0.05 * diff)
#
#--- for y axis, the range is the mean of the data - lbound/ + ubound
#
    asum  = 0.0
    acnt  = 0.0
    for ent  in dataset:
        asum += float(ent)
        acnt += 1.0
    avg = asum / acnt

    if lbound > 10:
        ymin = int(avg - lbound)
        ymax = int(avg + ubound)
    else:
        ymin = avg - lbound
        ymin = round(ymin, 1)
        ymax = avg + ubound
        ymax = round(ymax, 1)

    for i in range(0, 3):
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    xname = 'Time (DOM)' 
#
#--- calling plotting routines; create 3 panels
#
    pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=1.0, lwidth=0.0)
    if pchk > 0:
        cmd = 'mv out.png ' + mdir + '/obs_mode.png'
        os.system(cmd)

#-----------------------------------------------------------------------------------------------
#--- plot_partial_readout: creates history plots categorized by full/partial readout         ---
#-----------------------------------------------------------------------------------------------

def plot_partial_readout(mdir, dataSets, col, yname, lbound, ubound):

    """
    creates history plots categorized by full/partial readout
    Input:      mdir     --- Output directory
                dataSets --- a list of multiple lists. each list contains category data (except the first one is time)
                col      --- a position of data we want to use as a data
                lbound   --- a lower boundary interval from the mean value of the data
                ubound   --- a upper boundary interval from the mean value of the data
    Output:     <mdir>/partial_readout.png
    """

    time      = dataSets[0]             #--- time in DOM
    dataset   = dataSets[col]
    num_row   = dataSets[5]             #--- partial or full readout (if full 1024)

    x1 = []
    y1 = []
    x2 = []
    y2 = []
#
#--- categorize the data
#
    try:
        for i in range(0, len(time)):
            if int(num_row[i]) == 1024:
                x1.append(time[i])
                y1.append(dataset[i])
            else:
                x2.append(time[i])
                y2.append(dataset[i])
    except:
        pass

    xSets     = []
    ySets     = []
    yMinSets  = []
    yMaxSets  = []
    entLabels = []

    xSets.append(x1)
    xSets.append(x2)

    ySets.append(y1)
    ySets.append(y2)

    entLabels.append('Full Readout')
    entLabels.append('Partial Readout')
#
#--- set plotting range
#
    xmin = min(time)
    xmax = max(time)
    diff = xmax - xmin
    xmin = int(xmin - 0.05 * diff)
    if xmin < 0:
        xmin = 0
    xmax = int(xmax + 0.05 * diff)
#
#--- for y axis, the range is the mean of the data - lbound/ + ubound
#
    asum  = 0.0
    for ent  in dataset:
        asum += float(ent)
    avg = asum / float(len(dataset))

    if lbound > 10:
        ymin = int(avg - lbound)
        ymax = int(avg + ubound)
    else:
        ymin = avg - lbound
        ymin = round(ymin, 1)
        ymax = avg + ubound
        ymax = round(ymax, 1)

    for i in range(0, 2):
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    xname = 'Time (DOM)' 
#
#--- call plotting routine
#
    pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=1.0, lwidth=0.0)
    if pchk > 0:
        cmd = 'mv out.png ' + mdir + '/partial_readout.png'
        os.system(cmd)

#-----------------------------------------------------------------------------------------------
#--- plot_bias_arg1: creates history plots categorized by biasarg1 value                    ----
#-----------------------------------------------------------------------------------------------

def plot_bias_arg1(mdir, dataSets, col, yname, lbound, ubound):

    """
    creates history plots categorized by biasarg1 value
    Input:      mdir     --- Output directory
                dataSets --- a list of multiple lists. each list contains category data (except the first one is time)
                col      --- a position of data we want to use as a data
                lbound   --- a lower boundary interval from the mean value of the data
                ubound   --- a upper boundary interval from the mean value of the data
    Output:     <mdir>/bias_arg1.png
    """

    time      = dataSets[0]
    dataset = dataSets[col]
    biasarg1  = dataSets[10]

    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x3 = []
    y3 = []
#
#--- categorize data biasarg = 9, 10, or others
#
    try:
        for i in range(0, len(time)):
            if biasarg1[i] == 9:
                x1.append(time[i])
                y1.append(dataset[i])
            elif biasarg1[i] == 10:
                x2.append(time[i])
                y2.append(dataset[i])
            else:
                x3.append(time[i])
                y3.append(dataset[i])
    except:
        pass

    xSets     = []
    ySets     = []
    yMinSets  = []
    yMaxSets  = []
    entLabels = []

    xSets.append(x1)
    xSets.append(x2)
    xSets.append(x3)

    ySets.append(y1)
    ySets.append(y2)
    ySets.append(y3)

    entLabels.append('Bias Arg 1 = 9')
    entLabels.append('Bias Arg 1 = 10')
    entLabels.append('Bias Arg 1 : Others')
#
#--- set plotting range
#
    xmin = min(time)
    xmax = max(time)
    diff = xmax - xmin
    xmin = int(xmin - 0.05 * diff)
    if xmin < 0:
        xmin = 0
    xmax = int(xmax + 0.05 * diff)
#
#--- for y axis, the range is the mean of the data - lbound/ + ubound
#
    asum  = 0.0
    for ent  in dataset:
        asum += float(ent)
    avg = asum / float(len(dataset))

    if lbound > 10:
        ymin = int(avg - lbound)
        ymax = int(avg + ubound)
    else:
        ymin = avg - lbound
        ymin = round(ymin, 1)
        ymax = avg + ubound
        ymax = round(ymax, 1)


    for i in range(0, 3):
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    xname = 'Time (DOM)' 
#
#--- call plotting routine
#
    pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=1.0, lwidth=0.0)
    if pchk > 0:
        cmd = 'mv out.png ' + mdir + '/bias_arg1.png'
        os.system(cmd)


#-----------------------------------------------------------------------------------------------
#--- plot_num_ccds: creates history plots categorized by numbers of ccd used                 ---
#-----------------------------------------------------------------------------------------------

def plot_num_ccds(mdir, dataSets, col, yname, lbound, ubound):

    """
    creates history plots categorized by numbers of ccd used 
    Input:      mdir     --- Output directory
                dataSets --- a list of multiple lists. each list contains category data (except the first one is time)
                lbound   --- a lower boundary interval from the mean value of the data
                ubound   --- a upper boundary interval from the mean value of the data
                col      --- a position of data we want to use as a data
                also need:
                <data_dir>/Info_dir/list_of_ccd_no

    Output:     <mdir>/no_ccds.png
    """
    time    = dataSets[0]
    dataset = dataSets[col]
#
#---- read ccd information --- ccd information coming from a different file
#
    line = data_dir + 'Info_dir/list_of_ccd_no'
    data = mcf.readFile(line)

    ttime  = []
    ccd_no = []
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        dom   = (float(atemp[0]) -  48902399.0)/86400.0
        dom   = round(dom, 2)
        ttime.append(dom)
        ccd_no.append(int(atemp[1]))

    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x3 = []
    y3 = []
#
#--- compare time stamps and if they are same, catogorize the data
#
    for i in range(0, len(time)):
        chk = 0
        for j in range(0, len(ttime)):
            if time[i] == ttime[j]:
                if ccd_no[j] == 6:
                    x1.append(time[i])
                    y1.append(dataset[i])
                elif ccd_no[j] == 5:
                    x2.append(time[i])
                    y2.append(dataset[i])
                else:
                    x3.append(time[i])
                    y3.append(dataset[i])
                chk = 1
                continue
        if chk > 0:
            continue

    xSets     = []
    ySets     = []
    yMinSets  = []
    yMaxSets  = []
    entLabels = []

    xSets.append(x1)
    xSets.append(x2)
    xSets.append(x3)

    ySets.append(y1)
    ySets.append(y2)
    ySets.append(y3)

    entLabels.append('# of CCDs = 6')
    entLabels.append('# of CCDs = 5')
    entLabels.append('# of CCDs : Others')
#
#--- set plotting range
#
    xmin = min(time)
    xmax = max(time)
    diff = xmax - xmin
    xmin = int(xmin - 0.05 * diff)
    if xmin < 0:
        xmin = 0
    xmax = int(xmax + 0.05 * diff)
#
#--- for y axis, the range is the mean of the data - lbound/ + ubound
#
    asum  = 0.0
    for ent  in dataset:
        asum += float(ent)
    avg = asum / float(len(dataset))

    if lbound > 10:
        ymin = int(avg - lbound)
        ymax = int(avg + ubound)
    else:
        ymin = avg - lbound
        ymin = round(ymin, 1)
        ymax = avg + ubound
        ymax = round(ymax, 1)


    for i in range(0, 3):
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    xname = 'Time (DOM)' 
#
#--- calling plotting rouinte
#
    pchk = plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=1.0, lwidth=0.0)
    if pchk > 0:
        cmd = 'mv out.png ' + mdir + '/no_ccds.png'
        os.system(cmd)


#---------------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                           ---
#---------------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, mksize=1.0, lwidth=1.5):

    """
    This function plots multiple data in separate panels
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            yMinSets: a list of ymin 
            yMaxSets: a list of ymax
            entLabels: a list of the names of each data
            mksize:     a size of maker
            lwidth:     a line width

    Output: a png plot: out.png
            return 1 if the plot is crated, if not 0
    """
#
#--- set line color list
#
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
#
#--- close all opened plot
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
    for i in range(0, len(entLabels)):
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
        exec "%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (axNam)

        xdata  = xSets[i]
        ydata  = ySets[i]
  
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], marker='.', markersize=mksize, lw = lwidth)

#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec "%s.set_ylabel(yname, size=8)" % (axNam)

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

    return mcf.chkFile('./out.png')

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


#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':
    
    plot_bias_data()

    plot_bias_sub_info()


