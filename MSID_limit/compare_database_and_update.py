#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       compare_database_and_update.py: compare the current mta limit data base                     #
#                                       to glimmon and update the former                            #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Feb 15, 2018                                                               #
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
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a few names etc
#
mta_op_limit = '/data/mta4/MTA/data/op_limits/op_limits.db'
glimmon      = './glimmondb.sqlite3'
admin        = 'tisobe@cfa.harvard.edu'

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
#--- read the special_msid_list
#
    ifile = './special_msid_list'
    f     = open(ifile, 'r')
    special_msid_list = [line.strip() for line in f.readlines()]
    f.close()
#
#--- get time stamps
#
    today   = strftime("%Y_%m_%d", localtime())                     #--- e.g.2015_03_13
    Epoch   = float(time.mktime(localtime()))
    Ebase_t = float(time.mktime((1998, 1, 1, 0, 0, 0, 5, 1, 0)))
    stime   = str(Epoch - Ebase_t)                                  #--- seconds from 1998.1.1
#
#--- download the current glimmon sql data base
#
    download_glimmon()
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
#--- if the msid is in the special_msid_list, skip --- they are manually defined by mta
#
        if msid.lower() in special_msid_list:
            continue
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
#--- read data out from glimmon sqlite database
#
        out = read_glimmon(name, ind)

        if len(out) == 0:
            continue

        else:
#
#--- compare two database and save only updated data line
#
            [gy_min, gy_max, gr_min, gr_max] = out

            try:
                chk = 0
                ty_min = y_min[msid]
                ty_max = y_max[msid]
                tr_min = r_min[msid]
                tr_max = r_max[msid]
            except:
                chk = 1

            if (chk == 0) and ((ty_min == gy_min) and (ty_max == gy_max)  \
                and (tr_min == gr_min) and (tr_max == gr_max)):
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
    exit(1)
    fo = open('./op_limits.db', 'w')

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
                    if not (prev in special_msid_list):
                        line = updates[prev] 
                        line = line + ent
                except:
                    line = ent

                fo.write(line)
                fo.write('\n')

                atemp = re.split('\s+', ent)
                prev  = atemp[0]


    fo.close()
#
#--- check whether there are any changes and if so, save/update databases
#
    test_and_save()

#-----------------------------------------------------------------------------------
#-- read_mta_database: read mta limit database                                    --
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
#-- download_glimmon: downloading glimmon data from the website                         --
#-----------------------------------------------------------------------------------------

def download_glimmon():
    """
    downloading glimmon data from the website
    input: none but read from:
            https://occweb.cfa.harvard.edu/occweb/FOT/engineering/thermal/AXAFAUTO_RSYNC/G_LIMMON_Archive/glimmondb.sqlite3
    output: './glimmondb.sqlite3'
    """
#
#--- save the last one
#
    cmd = 'mv -f  ' + glimmon + ' ' + glimmon + '~'
    os.system(cmd)

    f   = open('/home/isobe/.occpass')
    out = f.read()
    f.close()
    out = out.replace('\n', '')
#
#--- download the database
#
    cmd = 'curl -u tisobe:' + out + ' https://occweb.cfa.harvard.edu/occweb/FOT/engineering/thermal/AXAFAUTO_RSYNC/G_LIMMON_Archive/glimmondb.sqlite3 > ' +  glimmon

    os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- test_and_save: save a copy of op_limit.db and glimon to Past_data directory         --
#-----------------------------------------------------------------------------------------

def test_and_save():
    """
     save a copy of op_limit.db and glimon to Past_data directory and also update the main mta limit database
     input: none but read from op_limits.db and the current mta limit database
     output: ./Past_data/op_limits.db_<time stamp>
             ./Past_data/glimmondb.sqlite3_<time stamp>
             /data/mta4/MTA/data/op_limits/op_limits.db
    """
#
#--- check whether the local file exist before start checking
#
    if not os.path.isfile('./op_limits.db'):
        return  False 
#
#--- check whether there are any differences from the current mta limit database
#
    cmd  = 'diff ' + mta_op_limit + ' ./op_limits.db > ' + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    cmd = 'rm ' + zspace
    os.system(cmd)
#
#--- if so, save a copy of op_limit.db and glimon to Past_data directory and also 
#--- update the main mta limit database
#
    if len(data) > 0:
        tail = strftime("%m%d%y", localtime())

        cmd = 'cp ./op_limits.db ./Past_data/op_limits.db_' + tail
        os.system(cmd)

        cmd = 'cp -f ./op_limits.db  ' + mta_op_limit
        os.system(cmd)

        cmd = 'cp ' +  glimmon + ' ./Past_data/' + glimmon + '_' + tail
        os.system(cmd)
#
#--- notify the changes to admin person
#
        fo = open(zspace, 'w')
        line = 'There are some changes in mta limit database; check /data/mta/Script/MSID_limit/* '
        line = line + 'and /data/mta4/MTA/data/op_limits/op_limits.db.\n'
        fo.write(line)
        fo.close()

        cmd = 'cat ' + zspace + '| mailx -s "Subject: MTA limit database updated  " ' + admin
        os.system(cmd)

        cmd = 'rm ' + zspace
        os.system(cmd)

        cmd = 'chgroup mtagroup ./*'
        os.system(cmd)
        cmd = 'chgroup mtagroup ./Past_data/*'
        os.system(cmd)
        cmd = 'chgroup mtagroup ' + mta_op_limit
        os.system(cmd)

    return True 

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#------------------------------------------------------------

    def test_read_mta_database(self):

        [msids, y_min, y_max, r_min, r_max, fline, tind, org_data] = read_mta_database()

        print str(msids[:10])

        print str(y_min['OHRTHR44'])
        print str(y_max['OHRTHR44'])
        print str(r_min['OHRTHR44'])
        print str(r_max['OHRTHR44'])

        print str(tind['OHRTHR44'])


#------------------------------------------------------------

    def test_read_glimmon(self):
    
        msid = 'OHRTHR44'
        #msid = '1CBAT'
        tind = 1
        out = read_glimmon(msid, tind)
        print str(out)

        msid  = '1DAHBVO'
        tind = 1
        out = read_glimmon(msid, tind)
        print str(out)

#------------------------------------------------------------

    def test_read_glimmon(self):

        download_glimmon()

        cmd =  'ls -lrt ' + glimmon + '> zzz'
        os.system(cmd)

        f   = open('zzz', 'r')
        test = f.read()
        print test
        cmd =  'rm zzz'
        os.system(cmd)


        
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

