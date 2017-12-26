#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
get_first_movie.py

Usage: get_first_movie "movie title"

Search for the given title and print the best matching result.
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
    print '  %s "movie title"' % sys.argv[0]
    sys.exit(2)

title = sys.argv[1]


i = imdb.IMDb()

in_encoding = sys.stdin.encoding or sys.getdefaultencoding()
out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

title = unicode(title, in_encoding, 'replace')
try:
    # Do the search, and get the results (a list of Movie objects).
    results = i.search_movie(title)
except imdb.IMDbError, e:
    print "Probably you're not connected to Internet.  Complete error report:"
    print e
    sys.exit(3)

if not results:
    print 'No matches for "%s", sorry.' % title.encode(out_encoding, 'replace')
    sys.exit(0)

# Print only the first result.
print '    Best match for "%s"' % title.encode(out_encoding, 'replace')

# This is a Movie instance.
movie = results[0]

# So far the Movie object only contains basic information like the
# title and the year; retrieve main information:
i.update(movie)

print movie.summary().encode(out_encoding, 'replace')



