
import os
import csv
import sys



def usage():
    print 'Syntax: $ python csv2qif.py <TRANSACTIONS> <ACCOUNT> <BALANCE>'
    print 'Example: $ python csv2qif.py out_tra.csv out_acc.csv out_bal.csv'
    sys.exit(2)

if len(sys.argv) < 4:
    usage()

try:
    t=open(sys.argv[1],'r')
    a=open(sys.argv[2],'r')
    b=open(sys.argv[3],'r')
except IOError:
    print 'File ' + sys.argv[1] + ' not found'
    sys.exit(3)

data = csv.reader(a)
data.next() # jump header
print '!Account'    # begin account description
for e in data:
    print 'N'+e[0]
#    print 'L1000'  # credit
    print 'D'+e[4]

data = csv.reader(b)
data.next() # jump header
for e in data:
    print '/'+e[0]
    print '$'+e[1]

print '^'           # end account description


data = csv.reader(t)
data.next() # jump header
print '!Type:Memorized' # begin transactions
for e in data:
    memo = e[7].split(os.linesep)
    print 'D'+e[0]
    print 'T'+e[1]
    print 'P'+memo[2]
    print 'CR'      # status: reconciled transaction
    m = ' '.join(memo)
    #print m
    print 'M'+m[-75:]  # reference (trancated at 70 chars)
    #print 'E'+m[70:140]  # reference (trancated at 70 chars)

    #for m in memo:
    #    print 'M'+m
    if e[4]=='CREDIT':
        print 'KD'  # deposit transaction
    else:
        print 'KP'  # payment transaction
    print '^'

