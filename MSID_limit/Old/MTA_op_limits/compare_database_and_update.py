#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       compare_database_and_update.py: compare the current mta limit data base                     #
#                                       to glimmon and update the former                            #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Mar 01, 2016                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import math
import sqlite3
import unittest
import time
from time import gmtime, strftime, localtime

mta_op_limit = '/data/mta4/MTA/data/op_limits/op_limits.db'
glimmon      = './glimmondb.sqlite3'

#-----------------------------------------------------------------------------------
#-- compare_database_and_update: compare the current mta limit data base to glimmon and update the former
#-----------------------------------------------------------------------------------

def compare_database_and_update():
    """
    compare the current mta limit data base to glimmon and update the former
    input: none, but read from  /data/mta4/MTA/data/op_limits/op_limits.db
           and glimmondb.sqlite3. you may need to download this from the web
    output: updated op_limits.db (locally saved)
    """
#
#--- get time stamps
#
    today   = strftime("%Y_%m_%d", localtime())                     #--- e.g.2015_03_13
    Epoch   = float(time.mktime(localtime()))
    Ebase_t = float(time.mktime((1998, 1, 1, 0, 0, 0, 5, 1, 0)))
    stime   = str(Epoch - Ebase_t)                                  #--- seconds from 1998.1.1
#
#-- read the current op_limit.db
#
    [msids, y_min, y_max, r_min, r_max, fline, tind, org_data] = read_mta_database()
#
#--- save updated line in a msid based dictionary
#
    updates      = {}

    for msid in msids:
#
#--- there are temperature related msids based on K and C. update both
#
        ind = tind[msid]
        name = msid
#
#--- temp msid with C ends "TC"
#
        tail = name[-2] + name[-1]
        if tail == 'TC':
            name = msid[:-1]
            ind = 0
#
#--- get data out from glimmon sqlite database
#
        out = read_glimmon(name, ind)

        if len(out) == 0:
            continue

        else:
#
#--- compare two database and save only updated data line
#
            [gy_min, gy_max, gr_min, gr_max] = out

            if (y_min[msid] == gy_min) and (y_max[msid] == gy_min)  \
                and (r_min[msid] == gr_min) and (r_max[msid] == gr_min):
                continue
            else:

                line = fline[msid]
                temp = re.split('\s+', line)

                org  = str(y_min[msid])
                new  = str(gy_min.strip())
                line = line.replace(org, new)

                org  = str(y_max[msid])
                new  = str(gy_max.strip())
                line = line.replace(org, new)

                org  = str(r_min[msid])
                new  = str(gr_min.strip())
                line = line.replace(org, new)

                org  = str(r_max[msid])
                new  = str(gr_max.strip())
                line = line.replace(org, new)
#
#--- time stamp 
#
                org = temp[5].strip()
                line = line.replace(org, stime)
#
#--- new data entry indicator
#
                org  = temp[-1].strip()
                line = line.replace(org, today)

                line = line  + '\n'

                updates[msid] = line

#
#--- now update the original data. append the updated line to the end of each msid entry
#
    fo = open('op_limits.db', 'w')

    prev = ''
    for ent in org_data:
        if prev == "":
            atemp = re.split('\s+', ent)
            prev  = atemp[0]
            fo.write(ent)
            fo.write('\n')
        else:
#
#--- for the case msid is the same as the previous; do nothing
#
            atemp = re.split('\s+', ent)
            if prev == atemp[0]:
                fo.write(ent)
                fo.write('\n')
                continue
            else:
#
#--- if the msid changed from the last entry line, check there is an update for the previous msid
#--- if so, add the line before printing the current line
#
                try:
                    line = updates[prev] 
                    line = line + ent
                except:
                    line = ent

                fo.write(line)
                fo.write('\n')

                atemp = re.split('\s+', ent)
                prev  = atemp[0]


    fo.close()


#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def read_mta_database():
    """
    read mta limit database
    input: none but read data from database: <mta_op_limit>
    ouput:  msids   --- a list of msids
            y_min   --- a msid based dictionary of yellow lower limit
            y_max   --- a msid based dictionary of yellow upper limit
            r_min   --- a msid based dictionary of red lower limit
            r_max   --- a msid based dictionary of red upper limit
            fline   --- a msid based dictionary of the entire line belong to the msid (the last entry)
            tind    --- a msid based dictionary of an indicator 
                        that whether this is a temperature related msid and in K. 0: no, 1: yes
            data    --- a list of all lines read from the database
    """
#
#--- read the database
#
    f     = open(mta_op_limit, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    prev  = ''
    ymin  = ''
    ymax  = ''
    rmin  = ''
    rmax  = ''

    y_min = {}
    y_max = {}
    r_min = {}
    r_max = {}
    tind  = {}
    fline = {}
    msids = []
    for ent in data:
#
#--- skip the line which is commented out
#
        test = re.split('\s+', ent)
        mc   = re.search('#', test[0])

        if mc is not None:
            continue
#
#--- go through the data and fill each dictionary. if there are
#--- multiple entries for the particular msid, only data from the last entry is kept
#
        atemp = re.split('\s+', ent)
        if (prev != '') and (atemp[0] != prev):
            msids.append(prev)
            y_min[prev] = ymin
            y_max[prev] = ymax
            r_min[prev] = rmin
            r_max[prev] = rmax
            tind[prev]  = temp
            fline[prev] = line

        if len(atemp) > 4:
            line = ent
            prev = atemp[0]
            ymin = atemp[1]
            ymax = atemp[2]
            rmin = atemp[3]
            rmax = atemp[4]
#
#--- check whether this is a temperature related msid and it is in K
#
            temp = 0
            if atemp[-1] == 'K' or atemp[-2] == 'K':
                temp = 1


    return [msids, y_min, y_max, r_min, r_max, fline,  tind, data]


#-----------------------------------------------------------------------------------
#-- read_glimmon: read glimmondb.sqlite3 and return yellow and red lower and upper limits 
#-----------------------------------------------------------------------------------

def read_glimmon(msid, tind):
    """
    read glimmondb.sqlite3 and return yellow and red lower and upper limits
    input:  msid    --- msid
            tind    --- whether this is a temperature related msid and in K. O; no, 1: yes
    output: y_min   --- lower yellow limit
            y_max   --- upper yellow limit
            r_min   --- lower red limit
            r_max   --- upper red limit
    """

    msid = msid.lower()
#
#--- glimmon keeps the temperature related quantities in C. convert it into K.
#
    if tind == 0:
        add = 0
    else:
        add = 273.15

    db = sqlite3.connect(glimmon)
    cursor = db.cursor()

    cursor.execute("SELECT * FROM limits WHERE msid='%s'" %msid)
    allrows = cursor.fetchall()

    if len(allrows) == 0:
        return []

    tup   = allrows[0]
    y_min = str(float(tup[11] + add))
    y_max = str(float(tup[10] + add))
    r_min = str(float(tup[13] + add))
    r_max = str(float(tup[12] + add))

    return [y_min, y_max, r_min, r_max]

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#------------------------------------------------------------

    def test_read_mta_database(self):

        [msids, y_min, y_max, r_min, r_max, tind] = read_mta_database()

        print str(msids[:10])

        print str(y_min['OHRTHR44'])
        print str(y_max['OHRTHR44'])
        print str(r_min['OHRTHR44'])
        print str(r_max['OHRTHR44'])

        print str(tind['OHRTHR44'])


#------------------------------------------------------------

    def test_read_glimmon(self):
    
        msid = 'OHRTHR44'
        msid = '1CBAT'
        tind = 1
        out = read_glimmon(msid, tind)
        print str(out)

        msid  = '1DAHBVO'
        tind = 1
        out = read_glimmon(msid, tind)
        print str(out)
        
#-----------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- if you want to test the script, add "test" after
#--- compare_database_and_update.py
#
    test = 0
    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':
            test = 1
            del sys.argv[1:]

    if test == 0:
        compare_database_and_update()
    else:
        unittest.main()

