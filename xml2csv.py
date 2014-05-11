#
# xml2csv -- convert XML (Post Finance) to CSV
#
# (C) 2014 by Gonzalo Aguirre <graguirre@gmail.com>, licensed under the terms 
# of the GNU General Public License as published by the Free Software
# Foundation; either version 2 or later.
# 
# 

# Tested with python version 2.7.6, under Archlinux

# The input is line-oriented format processed by XML/Unix processing tool.
# http://www.ofb.net/~egnor/xml2/
# $ xml2 < acc_200*.xml > input.txt

# Script syntax, the script will read from input.txt file
# $ python xml2csv.py  

# The script will create two files containing balance and transactions entries.
# output: balance.csv, transaction.csv

import getopt,sys
import re
import csv
import os

def getValue(strn):  # get value fromelement pattern
    a = strn.split('=')
    if len(a) > 1:
        v = a[1].replace(os.linesep,'')
        return v
    else:
        return ''

def getMemo(strn):  # get memo, dont trim linesep
    a = strn.split('=')
    if len(a) > 1:
        return a[1]
    else:
        return ''

def setMemo():
    global item
    global memo
    #memo = memo.replace(os.linesep,'')
    item.append(memo)
    memo=''


def SG2(strn):
    global account
    global acc
    if strn.count('Desc'):               # discard desc
        pass
    elif strn.count('FII/C078'):         # account id / IBAN / BIC / currency
        account.append( getValue(strn) )  
    elif strn.count('FII/PF:D_5388'):    # description
        account.append( getValue(strn) ) 
        acc.writerow(account)             # save record
    else:
        print 'ERR SG2 entry: ' + strn



def SG4(tra): # records
    #print '--------------'
    global item
    setMemo()
    #print entry
    tra.writerow(item)
    item = []   # reset item (entry)

def SG4_SG6():
    setMemo()
 
def IC_TRAILER(tra): # last record
    global item
    setMemo()
    if len(memo):
        tra.writerow(item)
 

def SG4_LIN(strn): # type of entry
    global entry
    item.append( getValue(strn) )
    e = getValue(strn).replace(os.linesep,'') # get entry
    if e=='LST' or e=='LNE' or e=='LNS' or e=='LTI' or e=='LEN' : 
        entry=e
    else:
        print 'ERR SG4/LIN entry ' + strn



def SG5_MOA(strn):
    if strn.count('Value=315'):
        pass # print 'opening balance'
    elif line.count('Value=15'):
        pass # print 'balance update'
    elif line.count('Value=343'):
        pass # print 'balance close';
    elif strn.count('C516/D_5004'):
        global amount
        amount = getValue( strn )
    elif strn.count('PF:D_5003'):
        sign = getValue( strn )
        item.append(sign + amount)
    else:
        print 'ERR SG5/MOA entry: ' + strn



def SG6_MOA(strn):
    global sign
    if line.count('Value=210'):
        item.append('CREDIT')
        sign = '+'
    elif line.count('Value=211'):
        item.append('DEBIT')
        sign = '-'
    elif line.count('C516/D_5004'):
        global amount
        amount = getValue( strn )
    elif line.count('PF:D_5003'):
        #sign = getValue( strn )
        item.append(sign + amount)
    else:
        print 'ERR SG6/MOA entry: ' + strn

def SG6_RFF(strn):
    if strn.count('C506/D_1153'):
        pass
    elif strn.count('C506/D_1154'):
        red = getValue( strn )
        item.append( red )
    else:
        print 'ERR SG6/RFF entry: ' + strn



def SG5_DTM(strn):      # date
    if strn.count('C507/D_2005'):
        pass
    elif strn.count('C507/D_2380'):
        date = getValue( strn )
        item.append( date[6:8]+'/'+date[4:6]+'/'+date[0:4] )
    else:
        print 'ERR SG5/DTM'

def SG6_DTM(strn):
    SG5_DTM( strn )



def SG6_TGT(strn): 
    if strn.count('PF:D_4752'):
        pass    # TGT
    elif strn.count('PF:D_4753'):
        pass
    elif strn.count('PF:D_4754'):
        data = getValue( strn )
        item.append( data )
    else:
        pass

def SG6_EPC(strn):
    if strn.count('PF:D_4752'):
        pass    # EPC
    elif strn.count('PF:D_4753'):
        data = getValue( strn )
        item.append( data )
        
def usage():
    print 'Syntax: $ python xml2csv.py <INPUT>'
    sys.exit(2)

#### main program ####

if len(sys.argv) < 2:
    usage()

try:
    f = open(sys.argv[1],'r')
except IOError:
    print 'File ' + sys.argv[1] + ' not found.'
    sys.exit(3)


acc = csv.writer(open('out_acc.csv','w'),delimiter=',',quoting=csv.QUOTE_ALL)
acc_title=['Account Id','IBAN','BIC','Currency','Description']
acc.writerow(acc_title)

tra = csv.writer(open('out_entries.csv','w'),delimiter=',',quoting=csv.QUOTE_ALL)
title =['entry','balance','date balance','Reference','TGT','Date','type','Amount','EPC','Description']
tra.writerow(title)

l=[]
item=[]
account=[]
memo=''
entry=''
prefix='/IC/KONAUS/'


for line in f:
#    regex = re.search('SG4',line,0)

    if line.count('IC_HEADER'): # header
        pass

    elif line.count(prefix+'SG2'):   # account info
        SG2( line )

    elif line.count(prefix+'SG3'):    # company info
        pass

    elif line.count(prefix+'BGM'):  # entry (?)
        pass

    elif line.count(prefix+'DTM'):  # balance date (?)
        pass

    elif line.count(prefix+'PF:FTX'): # header free text
        pass

    elif line.count('SG4/LIN'): # type of entry
        SG4_LIN( line )

    elif line.count('SG4\n'): # new item
        SG4( tra )

    elif line.count('SG4/SG6\n'): # new item
        SG4_SG6( )

    elif line.count('SG5/MOA'): # current balance
        SG5_MOA( line )

    elif line.count('SG6/MOA'): # transaction/movement amount
        SG6_MOA( line )

    elif line.count('SG6/FTX') \
            + line.count('SG5/FTX') \
            + line.count('SG4/FTX'): # free text
        memo += getMemo(line)

    elif line.count('SG6/RFF'): # red payment slips
        SG6_RFF( line ) 

    elif line.count('SG6/DTM'): # date transaction
        SG6_DTM( line )

    elif line.count('SG5/DTM'): # date balance
        SG5_DTM( line )

    elif line.count('SG6/PF:TGT'): # new element
        SG6_TGT( line )

    elif line.count('SG6/PF:EPC'): # new element
        SG6_EPC( line )

    elif line.count('IC_TRAILER'):
        IC_TRAILER( tra )
    
    else:
        print 'not recognised ' + line

f.close()
