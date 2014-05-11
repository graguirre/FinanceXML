#!/bin/sh

# check dependences (xml2)
if [ ! -e /usr/bin/xml2 ];
then
	echo "ERROR: xml2 command not found."
	echo "Generation cannot continue."
	exit 3
fi

# check dependences (python2)
if [ ! -e /usr/bin/python2 ];
then
	echo "ERROR: python command not found."
	echo "Generation cannot continue."
	exit 3
fi


if [ ! -f $2 ]; then
	echo "File not found"
	echo "syntax: sh generate.sh input-file.xml"
	exit 1
fi

dir=$(echo out`date +%Y%m%d-%H%M`)
echo "Generated files will be move to $dir, do you want to continue? [y/n]:"
read prompt

if [[ $prompt == y ]]; then
	echo "Starting..."
else
	echo "Exiting..."
	exit 2
fi

echo "Generating input XML ---> TXT"
xml2 < $1 > input.txt

echo "Converting TXT ---> CSV"
python2 xml2csv.py input.txt

echo "Reordering columns on CSV files"
python2 order_csv.py out_entries.csv

echo "Generating transactions QIF"
python2 csv2qif.py out_tra.csv out_acc.csv out_bal.csv > out_tra.qif

echo "Generating direct debit QIF"
python2 csv2qif.py out_dir.csv out_acc.csv out_bal.csv > out_dir.qif

# append direct transactions to transactions
tail -n +8 out_dir.qif >> out_tra.qif

echo "Convertion has been successfully completed."

echo "creating new directory"
mkdir $dir

echo "Moving file to "$dir
mv *.csv *.txt *.qif $dir

