
import os
import csv
import sys



def usage():
    print >> sys.stderr, 'Syntax: $ python csv2qif.py INPUT'
    print >> sys.stderr, 'Example: $ python csv2qif.py out_entries.csv'
    sys.exit(2)

if len(sys.argv) < 2:
    usage()

try:
    f=open(sys.argv[1],'r')
except IOError:
    print 'File '+sys.argv[1]+' not found'
    sys.exit(3)

entries = csv.reader(f)

balance=[]
transact=[]
direct=[]
totals=[]

for e in entries:
    if e[0]=='LST':
        balance.append([e[2],e[1],e[3]])
    elif e[0]=='LNE':
        p = e[9].split(os.linesep)
        if len(p) > 1:
            transact.append([e[5],e[7],p[3],e[3],e[6],e[4],e[8],e[9]])
        else: # red slip case
            p = e[10].split(os.linesep)
            transact.append([e[6],e[8],p[2],e[3],e[7],e[4],e[9],e[10]])
    elif e[0]=='LNS':
        p = e[9].split(os.linesep)
        direct.append([e[5],e[7],p[3],e[3],e[6],e[4],e[8],e[9]])
    elif e[0]=='LTI':
        totals.append([e[1],e[2],e[3],e[4],e[5],e[6]])
    else:
        print >> sys.stderr, 'ERR uknown entry. '
        print >> sys.stderr, e
        
f.close()

# uncomment while debugging
#print balance
#print transact
#print direct
#print totals

bal = csv.writer(open('out_bal.csv','w'),quoting=csv.QUOTE_ALL)
bal.writerow(["date","amount","description"])
bal.writerows(balance)

tra = csv.writer(open('out_tra.csv','w'),quoting=csv.QUOTE_ALL)
tra.writerow(["date","amount","payee","reference","type","TGT","EPC","description"])
tra.writerows(transact)

drc = csv.writer(open('out_dir.csv','w'),quoting=csv.QUOTE_ALL)
drc.writerow(["date","amount","payee","reference","type","TGT","EPC","description"])
drc.writerows(direct)

tot = csv.writer(open('out_tot.csv','w'),quoting=csv.QUOTE_ALL)
tot.writerow(["credit","amount 1","description 1","debit","amount 2","description 2"])
tot.writerows(totals)

