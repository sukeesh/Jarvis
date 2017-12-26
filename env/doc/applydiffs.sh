#!/bin/sh
#
# applydiffs.sh: Bash script useful apply patches to a set of
#            IMDb's plain text data files.
#
# Usage: copy this script in the directory with the plain text
#        data files and run it passing a list of diffs-file(s) as
#        arguments.
#        It's possible that the plain text data files will be left
#        in an inconsistent state, so a backup is probably a good idea.
#
# Copyright: 2009-2010 Davide Alberani <da@erlug.linux.it>
#
# This program is released under the terms of the GNU GPL 2 or later license.
#

if [ $# -lt 1 ] ; then
	echo "USAGE: $0 diffs-file [diffs-file...]"
	echo "       Beware that diffs-file must be sorted from the older to the newer!"
	exit 1
fi

COMPRESSION="1"

ALL_DIFFS="$@"

for DIFFS in $@
do
	rm -rf diffs

	echo -n "Unpacking $DIFFS..."
	tar xfz "$DIFFS"
	echo " done!"

	for DF in diffs/*.list
	do
		fname="`basename $DF`"
		if [ -f "$fname" ] ; then
			wasUnpacked=1
			applyTo="$fname"
		elif [ -f "$fname.gz" ] ; then
			wasUnpacked=0
			applyTo="$fname.gz"
		else
			echo "NOT applying: $fname doesn't exists."
			continue
		fi
		if [ $wasUnpacked -eq 0 ] ; then
			echo -n "unzipping $applyTo..."
			gunzip "$applyTo"
			echo "done!"
		fi
		echo -n "patching $fname with $DF..."
		patch -s "$fname" "$DF"
		if [ $? -ne 0 ] ; then
			echo "FAILED!"
			continue
		fi
		echo "done!"
	done
	echo "finished with $DIFFS"
	echo ""
done

rm -rf diffs

for lfile in *.list
do
	echo -n "gzipping $lfile..."
	gzip -$COMPRESSION "$lfile"
	echo "done!"
done

