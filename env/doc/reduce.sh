#!/bin/bash
#
# reduce.sh: Bash script useful to create a "slimmed down" version of the
#            IMDb's plain text data files.
#
# Usage: copy this script in the directory with the plain text data files;
#        configure the options below and run it.
#
# Copyright: 2009-2010 Davide Alberani <da@erlug.linux.it>
#
# This program is released under the terms of the GNU GPL 2 or later license.
#

# Cygwin packages to install (Windows):
#  - util-unix for rev
#  - gzip for gzip, zcat, zgrep

# Directory with the plain text data file.
ORIG_DIR="."
# Directory where "reduced" files will be stored; it will be create if needed.
# Beware that this directory is relative to ORIG_DIR.
DEST_DIR="./partial/"
# How much percentage of the original file to keep.
KEEP_X_PERCENT="1"
# The compression ratio of the created files.
COMPRESSION="1"


# -
# Nothing to configure below.
# -


cd "$ORIG_DIR"
mkdir -p "$DEST_DIR"

DIV_BY="`expr 100 / $KEEP_X_PERCENT`"

for file in *.gz
do
	LINES="`zcat "$file" | wc -l`"
	CONSIDER="`expr $LINES / $DIV_BY`"
	FULL_CONS="$CONSIDER"
	CONSIDER="`expr $CONSIDER / 2`"
	NEWNAME="`echo "$file" | rev | cut -c 4- | rev `"

	# Tries to keep enough lines from the top of the file.
	MIN_TOP_LINES="`zgrep -a -n -m 1 "^-----------------------------------------" "$file" | cut -d : -f 1`"
	if test -z "$MIN_TOP_LINES" ; then
		MIN_TOP_LINES=0
	fi
	if test "$file" == "business.list.gz" -a $MIN_TOP_LINES -lt 260 ; then
		MIN_TOP_LINES=260
	elif test "$file" == "alternate-versions.list.gz" -a $MIN_TOP_LINES -lt 320 ; then
		MIN_TOP_LINES=320
	elif test "$file" == "cinematographers.list.gz" -a $MIN_TOP_LINES -lt 240 ; then
		MIN_TOP_LINES=240
	elif test "$file" == "complete-cast.list.gz" ; then
		MIN_TOP_LINES=140
	elif test "$file" == "complete-crew.list.gz" ; then
		MIN_TOP_LINES=150
	elif test "$file" == "composers.list.gz" -a $MIN_TOP_LINES -lt 160 ; then
		MIN_TOP_LINES=160
	elif test "$file" == "costume-designers.list.gz" -a $MIN_TOP_LINES -lt 240 ; then
		MIN_TOP_LINES=240
	elif test "$file" == "directors.list.gz" -a $MIN_TOP_LINES -lt 160 ; then
		MIN_TOP_LINES=160
	elif test "$file" == "genres.list.gz" -a $MIN_TOP_LINES -lt 400 ; then
		MIN_TOP_LINES=400
	elif test "$file" == "keywords.list.gz" -a $MIN_TOP_LINES -lt 36000 ; then
		MIN_TOP_LINES=36000
	elif test "$file" == "literature.list.gz" -a $MIN_TOP_LINES -lt 320 ; then
		MIN_TOP_LINES=320
	elif test "$file" == "mpaa-ratings-reasons.list.gz" -a $MIN_TOP_LINES -lt 400 ; then
		MIN_TOP_LINES=400
	elif test "$file" == "producers.list.gz" ; then
		MIN_TOP_LINES=220
	elif test "$file" == "production-companies.list.gz" -a $MIN_TOP_LINES -lt 270 ; then
		MIN_TOP_LINES=270
	elif test "$file" == "production-designers.list.gz" -a $MIN_TOP_LINES -lt 240 ; then
		MIN_TOP_LINES=240
	elif test "$file" == "ratings.list.gz" -a $MIN_TOP_LINES -lt 320 ; then
		MIN_TOP_LINES=320
	elif test "$file" == "special-effects-companies.list.gz" -a $MIN_TOP_LINES -lt 320 ; then
		MIN_TOP_LINES=320
	elif test "$file" == "sound-mix.list.gz" -a $MIN_TOP_LINES -lt 340 ; then
		MIN_TOP_LINES=340
	elif test "$file" == "writers.list.gz" ; then
		MIN_TOP_LINES=400
	else
		MIN_TOP_LINES="`expr $MIN_TOP_LINES + 60`"
	fi
	if test "$MIN_TOP_LINES" -gt "$CONSIDER" ; then
		TOP_CONSIDER=$MIN_TOP_LINES
	else
		TOP_CONSIDER=$CONSIDER
	fi
	
	HOW_MANY="`expr $TOP_CONSIDER + $CONSIDER`"
	echo "Processing $file [$KEEP_X_PERCENT%: $HOW_MANY lines]"
	zcat "$file" | head -$TOP_CONSIDER > "$DEST_DIR/$NEWNAME"
	zcat "$file" | tail -$CONSIDER >> "$DEST_DIR/$NEWNAME"
	gzip -f -$COMPRESSION "$DEST_DIR/$NEWNAME"
done

