#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
get_character.py

Usage: get_character "characterID"

Show some info about the character with the given characterID (e.g. '0000001'
for "Jesse James", using 'http' or 'mobile').
Notice that characterID, using 'sql', are not the same IDs used on the web.
"""

import sys

# Import the IMDbPY package.
try:
    import imdb
except ImportError:
    print 'You bad boy!  You need to install the IMDbPY package!'
    sys.exit(1)


if len(sys.argv) != 2:
    print 'Only one argument is required:'
    print '  %s "characterID"' % sys.argv[0]
    sys.exit(2)

characterID = sys.argv[1]

i = imdb.IMDb()

out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

try:
    # Get a character object with the data about the character identified by
    # the given characterID.
    character = i.get_character(characterID)
except imdb.IMDbError, e:
    print "Probably you're not connected to Internet.  Complete error report:"
    print e
    sys.exit(3)


if not character:
    print 'It seems that there\'s no character with characterID "%s"' % characterID
    sys.exit(4)

# XXX: this is the easier way to print the main info about a character;
# calling the summary() method of a character object will returns a string
# with the main information about the character.
# Obviously it's not really meaningful if you want to know how
# to access the data stored in a character object, so look below; the
# commented lines show some ways to retrieve information from a
# character object.
print character.summary().encode(out_encoding, 'replace')


