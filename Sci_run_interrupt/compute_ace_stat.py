#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       compute_ace_stat.py: find hradness and other statistics of the radiation curves         #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Sep 12, 2017                                                       #
#                                                                                               #
#################################################################################################

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




#-----------------------------------------------------------------------------------------------
#--- computeACEStat: compute ACE radiation data statistics                                   ---
#-----------------------------------------------------------------------------------------------

def computeACEStat(event, start, stop, comp_test = 'NA'):

    'for a gien event, start and stop data, compute ACE statistics. format: 20110804        2011:08:04:07:03        2011:08:07:10:25'

#
#--- change time format to year and ydate (float)
#
    begin = start + ':00'                #---- need to add "seconds" part to dateFormtCon to work correctly
    end   = stop  + ':00'

    (year1, month1, day1, hours1, minutes1, seconds1, ydate1) = tcnv.dateFormatCon(begin)
    (year2, month2, day2, hours2, minutes2, seconds2, ydate2) = tcnv.dateFormatCon(end)

#
#--- find plotting range
#
    (pYearStart, periodStart, pYearStop, periodStop, plotYearStart, plotStart, plotYearStop, plotStop, pannelNum) \
                 = itrf.findCollectingPeriod(year1, ydate1, year2, ydate2)

#
#--- read ACE data
#

    if comp_test == 'test':
        line = test_data_dir + event + '_dat.txt'
    else:
        line = data_dir + event + '_dat.txt'

    f    = open(line, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- initialization
#
    cnt1            = 0
    cnt2            = 0
    cnt3            = 0
    cnt4            = 0
    cnt5            = 0
    cnt6            = 0
    cnt7            = 0
    cnt8            = 0
    cnt9            = 0
    cnt10           = 0
    cnt11           = 0
    cnt12           = 0
    cnt13           = 0
    e38_a           = 0
    e38_a2          = 0
    e175_a          = 0
    e175_a2         = 0
    p47_a           = 0
    p47_a2          = 0
    p112_a          = 0
    p112_a2         = 0
    p310_a          = 0
    p310_a2         = 0
    p761_a          = 0
    p761_a2         = 0
    p1060_a         = 0
    p1060_a2        = 0
    aniso_a         = 0
    aniso_a2        = 0
    r38_175_a       = 0
    r38_175_a2      = 0
    r47_1060_a      = 0
    r47_1060_a2     = 0
    r112_1060_a     = 0
    r112_1060_a2    = 0
    r310_1060_a     = 0
    r310_1060_a2    = 0
    r761_1060_a     = 0
    r761_1060_a2    = 0

    e38_max         = 0
    e38_min         = 1.0e10
    e175_max        = 0
    e175_min        = 1.0e10
    p47_max         = 0
    p47_min         = 1.0e10
    p112_max        = 0
    p112_min        = 1.0e10
    p310_max        = 0
    p310_min        = 1.0e10
    p761_max        = 0
    p761_min        = 1.0e10
    p1060_max       = 0
    p1060_min       = 1.0e10
    aniso_max       = 0
    aniso_min       = 1.0e10
    r38_175_max     = 0
    r38_175_min     = 1.0e10
    r47_1060_max    = 0
    r47_1060_min    = 1.0e10
    r112_1060_max   = 0
    r112_1060_min   = 1.0e10
    r310_1060_max   = 0
    r310_1060_min   = 1.0e10
    r761_1060_max   = 0
    r761_1060_min   = 1.0e10

    e38_max_t       = 0
    e38_min_t       = 0
    e175_max_t      = 0
    e175_min_t      = 0
    p47_max_t       = 0
    p47_min_t       = 0
    p112_max_t      = 0
    p112_min_t      = 0
    p310_max_t      = 0
    p310_min_t      = 0
    p761_max_t      = 0
    p761_min_t      = 0
    p1060_max_t     = 0
    p1060_min_t     = 0
    aniso_max_t     = 0
    aniso_min_t     = 0
    r38_175_max_t   = 0
    r38_175_min_t   = 0
    r47_1060_max_t  = 0
    r47_1060_min_t  = 0
    r112_1060_max_t = 0
    r112_1060_min_t = 0
    r310_1060_max_t = 0
    r310_1060_min_t = 0
    r761_1060_max_t = 0
    r761_1060_min_t = 0

    e38_int         = 0
    e175_int        = 0
    p47_int         = 0
    p112_int        = 0
    p310_int        = 0
    p761_int        = 0
    p1060_int       = 0
    aniso_int       = 0
    r38_175_int     = 0
    r47_1060_int    = 0
    r112_1060_int   = 0
    r310_1060_int   = 0
    r761_1060_int   = 0

#
#--- start accumulating the values
#
    for ent in data:    
        atemp = re.split('\s+|\t+', ent)
        btemp = re.split('\.', atemp[0])

        if atemp[0]  and btemp[0].isdigit():

            time = float(atemp[0])

            e38  = float(atemp[1])
            if e38 > 0: 
                cnt1 += 1
                if e38 > e38_max:
                    e38_max = e38
                    e38_max_t = time
                 
                if e38 < e38_min:
                    e38_min = e38
                    e38_min_t = time
                
                e38_a    += e38
                e38_a2   += e38*e38
            

            e175 = float(atemp[2])
            if e175 > 0:
                cnt2 += 1
                if e175 > e175_max:
                    e175_max = e175
                    e175_max_t = time
                 
                if e175 < e175_min:
                    e175_min = e175
                    e175_min_t = time
                 
                e175_a   += e175
                e175_a2  += e175*e175
             

            p47  = float(atemp[3])
            if p47 > 0:
                cnt3 += 1
                if p47 > p47_max:
                    p47_max = p47
                    p47_max_t = time
                 
                if p47 < p47_min:
                    p47_min = p47
                    p47_min_t = time
                
                p47_a    += p47
                p47_a2   += p47*p47
             

            p112 = float(atemp[4])
            if p112 > 0:
                cnt4 += 1
                if p112 > p112_max:
                    p112_max = p112
                    p112_max_t = time
                 
                if p112 < p112_min:
                    p112_min = p112
                    p112_min_t = time
                 
                p112_a   += p112
                p112_a2  += p112*p112
             
            p310 = float(atemp[5])
            if p310 > 0:
                cnt5 += 1
                if p310 > p310_max:
                    p310_max = p310
                    p310_max_t = time
                 
                if p310 < p310_min:
                    p310_min = p310
                    p310_min_t = time

                p310_a   += p310
                p310_a2  += p310*p310
             
            p761 = float(atemp[6])
            if p761 > 0:
                cnt6 += 1
                if p761 > p761_max:
                    p761_max = p761
                    p761_max_t = time
                 
                if p761 < p761_min:
                    p761_min = p761
                    p761_min_t = time
                 
                p761_a   += p761
                p761_a2  += p761*p761
             
            p1060= float(atemp[7])
            if p1060 > 0:
                cnt7 += 1
                if p1060 > p1060_max:
                    p1060_max = p1060
                    p1060_max_t = time

                if p1060 < p1060_min:
                    p1060_min = p1060
                    p1060_min_t = time
                 
                p1060_a  += p1060
                p1060_a2 += p1060*p1060
             
            aniso = float(atemp[8])
            if aniso > 0:
                cnt8 += 1
                if aniso > aniso_max:
                    aniso_max = aniso
                    aniso_max_t = time
                 
                if aniso < aniso_min:
                    aniso_min = aniso
                    aniso_min_t = time
                 
                aniso_a  += aniso
                aniso_a2 += aniso*aniso

            if e175 > 0:
                r38_175   = e38/e175
                if r38_175 > 0:
                    cnt9 += 1
                    if r38_175 > r38_175_max:
                        r38_175_max = r38_175
                        r38_175_max_t = time
                     
                    if r38_175 < r38_175_min:
                        r38_175_min = r38_175
                        r38_175_min_t = time
                     
                    r38_175_a    += r38_175
                    r38_175_a2   += r38_175*r38_175
                 

            if p1060 > 0:
                r47_1060  = p47/p1060
                if r47_1060 > 0:
                    cnt10 += 1
                    if r47_1060 > r47_1060_max:
                        r47_1060_max = r47_1060
                        r47_1060_max_t = time
                     
                    if r47_1060 < r47_1060_min:
                        r47_1060_min = r47_1060
                        r47_1060_min_t = time
                     
                    r47_1060_a   += r47_1060
                    r47_1060_a2  += r47_1060*r47_1060
                 

                r112_1060 = p112/p1060
                if r112_1060 > 0:
                    cnt11 += 1
                    if r112_1060 > r112_1060_max:
                        r112_1060_max = r112_1060
                        r112_1060_max_t = time
                     
                    if r112_1060 < r112_1060_min:
                        r112_1060_min = r112_1060
                        r112_1060_min_t = time
                     
                    r112_1060_a  += r112_1060
                    r112_1060_a2 += r112_1060*r112_1060
                 

                r310_1060 = p310/p1060
                if r310_1060 > 0:
                    cnt12 += 1
                    if r310_1060 > r310_1060_max:
                        r310_1060_max = r310_1060
                        r310_1060_max_t = time
                     
                    if r310_1060 < r310_1060_min:
                        r310_1060_min = r310_1060
                        r310_1060_min_t = time
                     
                    r310_1060_a  += r310_1060
                    r310_1060_a2 += r310_1060*r310_1060

                r761_1060 = p761/p1060
                if r761_1060 > 0:
                    cnt13 += 1
                    if r761_1060 > r761_1060_max:
                        r761_1060_max = r761_1060
                        r761_1060_max_t = time
                     
                    if r761_1060 < r761_1060_min:
                        r761_1060_min = r761_1060
                        r761_1060_min_t = time
                     
                    r761_1060_a  += r761_1060
                    r761_1060_a2 += r761_1060*r761_1060
                 

                e38_int       = e38
                e175_int      = e175
                p47_int       = p47
                p112_int      = p112
                p310_int      = p310
                p761_int      = p761
                p1060_int     = p1060
                aniso_int     = aniso
                r38_175_int   = r38_175
                r47_1060_int  = r47_1060
                r112_1060_int = r112_1060
                r310_1060_int = r310_1060
                r761_1060_int = r761_1060

#
#----a big loop ends here; now compute avg and std
#
     
    if cnt1 == 0:
        e38_avg   =    0
        e38_var   =    0
    else:
        e38_avg   =    e38_a/cnt1
        e38_var   =    math.sqrt(e38_a2/cnt1  - e38_avg * e38_avg)
     
    if cnt2 == 0:
        e175_avg  =    0
        e175_var  =    0
    else:
        e175_avg  =    e175_a/cnt2
        e175_var  =    math.sqrt(e175_a2/cnt2 - e175_avg*e175_avg)
     

    if cnt3 == 0:
        p47_avg   =    0
        p47_var   =    0
    else:
        p47_avg   =    p47_a/cnt3
        p47_var   =    math.sqrt(p47_a2/cnt3  - p47_avg * p47_avg)
     

    if cnt4 == 0:
        p112_avg  =    0
        p112_var  =    0
    else:
        p112_avg  =    p112_a/cnt4
        p112_var  =    math.sqrt(p112_a2/cnt4 - p112_avg * p112_avg)
     

    if cnt5 == 0:
        p310_avg  =    0
        p310_var  =    0
    else:
        p310_avg  =    p310_a/cnt5
        p310_var  =    math.sqrt(p310_a2/cnt5 - p310_avg * p310_avg)
     

    if cnt6 == 0:
        p761_avg  =    0
        p761_var  =    0
    else:
        p761_avg  =    p761_a/cnt6
        p761_var  =    math.sqrt(p761_a2/cnt6 - p761_avg * p761_avg)
     

    if cnt7 == 0:
        p1060_avg =    0
        p1060_var =    0
    else:
        p1060_avg =    p1060_a/cnt7
        p1060_var =    math.sqrt(p1060_a2/cnt7 - p1060_avg * p1060_avg)
     

    if cnt8 == 0:
        aniso_avg =    0
        aniso_var =    0
    else:
        aniso_avg =    aniso_a/cnt8
        aniso_var =    math.sqrt(aniso_a2/cnt8 - aniso_avg * aniso_avg)
     

    if cnt9 == 0:
        r38_175_avg   =  0
        r38_175_var   =  0
    else:
        r38_175_avg   =  r38_175_a/cnt9
        r38_175_var   =  math.sqrt(r38_175_a2/cnt9 - r38_175_avg * r38_175_avg)
     

    if cnt10 == 0:
        r47_1060_avg  =  0
        r47_1060_var  =  0
    else:
        r47_1060_avg  =  r47_1060_a/cnt10
        r47_1060_var  =  math.sqrt(r47_1060_a2/cnt10 - r47_1060_avg * r47_1060_avg)
    

    if cnt11 == 0:
        r112_1060_avg =  0
        r112_1060_var =  0
    else:
        r112_1060_avg =  r112_1060_a/cnt11
        r112_1060_var =  math.sqrt(r112_1060_a2/cnt11 - r112_1060_avg * r112_1060_avg)
     

    if cnt12 == 0:
        r310_1060_avg =  0
        r310_1060_var =  0
    else:
        r310_1060_avg =  r310_1060_a/cnt12
        r310_1060_var =  math.sqrt(r310_1060_a2/cnt12 - r310_1060_avg * r310_1060_avg)
     

    if cnt13 == 0:
        r761_1060_avg =  0
        r761_1060_var =  0
    else:
        r761_1060_avg =  r761_1060_a/cnt13
        r761_1060_var =  math.sqrt(r761_1060_a2/cnt13 - r761_1060_avg * r761_1060_avg)

#
#--- create stat table
#

    line = 'Data Period  (dom): %6.4f - %6.4f\n' % (plotStart, plotStop)
    line = line + 'Interruption (dom): %6.4f - %6.4f\n\n' % (ydate1,    ydate2)

    line = line + '\t\t\tAvg\t\t Max\t\tTime\tMin\t\tTime\t\tValue at Interruption Started\n'
    line = line + '-' * 95 + '\n'

    line = line + 'e38 \t\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'\
                        % (e38_avg,e38_var,e38_max,e38_max_t,e38_min,e38_min_t,e38_int)

    line = line + 'e175\t\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'\
                        % (e175_avg,e175_var,e175_max,e175_max_t,e175_min,e175_min_t,e175_int)

    line = line + 'p47 \t\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'\
                        % (p47_avg,p47_var,p47_max,p47_max_t,p47_min,p47_min_t,p47_int)

    line = line + 'p112\t\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'\
                        % (p112_avg,p112_var,p112_max,p112_max_t,p112_min,p112_min_t,p112_int)

    line = line + 'p310\t\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'\
                        % (p310_avg,p310_var,p310_max,p310_max_t,p310_min,p310_min_t,p310_int)

    line = line + 'p761\t\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'\
                        % (p761_avg,p761_var,p761_max,p761_max_t,p761_min,p761_min_t,p761_int)

    line = line + 'p1060\t\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'\
                        % (p1060_avg,p1060_var,p1060_max,p1060_max_t,p1060_min,p1060_min_t,p1060_int)

    if year1 < 2014:
        line = line + 'anisotropy\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'\
                        % (aniso_avg,aniso_var,aniso_max,aniso_max_t,aniso_min,aniso_min_t,aniso_int)

    line = line + '\nHardness:\n'

    line = line + 'e38/e175\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n'  \
                % (r38_175_avg,r38_175_var,r38_175_max,r38_175_max_t,r38_175_min,\
                   r38_175_min_t,r38_175_int)

    line = line + 'p47/p1060\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n' \
                % (r47_1060_avg,r47_1060_var,r47_1060_max,r47_1060_max_t,r47_1060_min,\
                   r47_1060_min_t,r47_1060_int)

    line = line + 'p112/p1060\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n' \
                % (r112_1060_avg,r112_1060_var,r112_1060_max,r112_1060_max_t,r112_1060_min,\
                   r112_1060_min_t,r112_1060_int)

    line = line + 'p310/p1060\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n' \
                % (r310_1060_avg,r310_1060_var,r310_1060_max,r310_1060_max_t,r310_1060_min,\
                   r310_1060_min_t,r310_1060_int)

    line = line + 'p761/p1060\t%4.3e+/-%4.3e\t%4.3e\t%4.3f \t%4.3e\t%4.3f\t\t%4.3e\n' \
                % (r761_1060_avg,r761_1060_var,r761_1060_max,r761_1060_max_t,r761_1060_min,\
                   r761_1060_min_t,r761_1060_int)
#
#---- find gradient and chooes the steepest rising point
#
    time = []
    e1   = []
    e2   = []
    p1   = []
    p2   = []
    p3   = []
    p4   = []
    p5   = []
    ans  = []

    for ent in data:    
        atemp = re.split('\s+|\t+', ent)
        btemp = re.split('\.', atemp[0])

        if atemp[0]  and btemp[0].isdigit():

            time.append(float(atemp[0]))
            for j in range(1, 9):
                if float(atemp[j]) <= 0:
                    atemp[j] = 1.0e-5

            e1.append(float(atemp[1]))
            e2.append(float(atemp[2]))
            p1.append(float(atemp[3]))
            p2.append(float(atemp[4]))
            p3.append(float(atemp[5]))
            p4.append(float(atemp[6]))
            p5.append(float(atemp[7]))

    line = line + '\nSteepest Rise\n'
    line = line + '------------\n'
    line = line + '\tTime\t\tSlope(in log per hr)\n'
    line = line + '----------------------------------------\n'

    (max_pos, max_slope) = find_jump(e1, time)
    line = line + 'e1  \t'
    if max_pos == -999:
        line = line + 'na\t\tna\n'
    else:
        line = line + '%5.4f\t\t%3.4f\n' % (time[max_pos], max_slope)


    (max_pos, max_slope) = find_jump(e2, time)
    line = line + 'e175\t'
    if max_pos == -999:
        line = line + 'na\t\tna\n'
    else:
        line = line + '%5.4f\t\t%3.4f\n' % (time[max_pos], max_slope)

    (max_pos, max_slope) = find_jump(p1, time)
    line = line + 'p47 \t'
    if max_pos == -999:
        line = line + 'na\t\tna\n'
    else:
        line = line + '%5.4f\t\t%3.4f\n' % (time[max_pos], max_slope)

    (max_pos, max_slope) = find_jump(p2, time)
    line = line + 'p112\t'
    if max_pos == -999:
        line = line + 'na\t\tna\n'
    else:
        line = line +  '%5.4f\t\t%3.4f\n' % (time[max_pos], max_slope)

    (max_pos, max_slope) = find_jump(p3, time)
    line = line + 'p310\t'
    if max_pos == -999:
        line = line + 'na\t\tna\n'
    else:
        line = line + '%5.4f\t\t%3.4f\n' % (time[max_pos], max_slope)

    (max_pos, max_slope) = find_jump(p4, time)
    line = line + 'p761\t'
    if max_pos == -999:
        line = line + 'na\t\tna\n'
    else:
        line = line + '%5.4f\t\t%3.4f\n' % (time[max_pos], max_slope)

    (max_pos, max_slope) = find_jump(p5, time)
    line = line + 'p1060\t'
    if max_pos == -999:
        line = line + 'na\t\tna\n'
    else:
        line = line + '%5.4f\t\t%3.4f\n' % (time[max_pos], max_slope)



    if comp_test == 'test':
        out = test_stat_dir + event + '_ace_stat'
    else:
        out = stat_dir + event + '_ace_stat'

    f = open(out, 'w')
    f.write(line)

    f.close()


#---------------------------------------------------------------------------------------------
#--- fin_jump: find a steepest jump from a given list                                      ---
#---------------------------------------------------------------------------------------------

def find_jump(list, time):

    'find the steepest jump from a given line: input: a list. output: (max position, max slope)'

    if len(list) < 10:
        temp = [0 for x in range(100)]
        return (-999, temp[0])
    else:
        last      = len(list) - 10
        diff      = 24.0 * (time[last] - time[10])/(last -10)
        max_slope = 0;
        max_pos   = 0;
    
        if diff > 0:
            for k in range(10, last):
                start = k
                end   = k + 1
                sum   = 0
    
                for m in range(0, 10):
                    sum += list[end] - list[start]
                    start += 1
                    end   += 1
    
                slope = 0.1 * sum / diff
                if slope > max_slope:
                    max_slope = slope
                    max_pos   = k + 5
    
        return (max_pos, max_slope)


