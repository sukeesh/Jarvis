#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
get_keyword.py

Usage: get_keyword "keyword"

search for movies tagged with the given keyword and print the results.
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
    print '  %s "keyword"' % sys.argv[0]
    sys.exit(2)

name = sys.argv[1]


i = imdb.IMDb()

in_encoding = sys.stdin.encoding or sys.getdefaultencoding()
out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

name = unicode(name, in_encoding, 'replace')
try:
    # Do the search, and get the results (a list of movies).
    results = i.get_keyword(name, results=20)
except imdb.IMDbError, e:
    print "Probably you're not connected to Internet.  Complete error report:"
    print e
    sys.exit(3)

# Print the results.
print '    %s result%s for "%s":' % (len(results),
                                    ('', 's')[len(results) != 1],
                                    name.encode(out_encoding, 'replace'))
print ' : movie title'

# Print the long imdb title for every movie.
for idx, movie in enumerate(results):
    outp = u'%d: %s' % (idx+1, movie['long imdb title'])
    print outp.encode(out_encoding, 'replace')


