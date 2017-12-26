#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
search_keyword.py

Usage: search_keyword "keyword"

Search for keywords similar to the give one and print the results.
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
    print '  %s "keyword name"' % sys.argv[0]
    sys.exit(2)

name = sys.argv[1]


i = imdb.IMDb()

in_encoding = sys.stdin.encoding or sys.getdefaultencoding()
out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

name = unicode(name, in_encoding, 'replace')
try:
    # Do the search, and get the results (a list of keyword strings).
    results = i.search_keyword(name, results=20)
except imdb.IMDbError, e:
    print "Probably you're not connected to Internet.  Complete error report:"
    print e
    sys.exit(3)

# Print the results.
print '    %s result%s for "%s":' % (len(results),
                                    ('', 's')[len(results) != 1],
                                    name.encode(out_encoding, 'replace'))
print ' : keyword'

# Print every keyword.
for idx, keyword in enumerate(results):
    outp = u'%d: %s' % (idx+1, keyword)
    print outp.encode(out_encoding, 'replace')


