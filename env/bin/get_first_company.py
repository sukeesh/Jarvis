#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
get_first_company.py

Usage: get_first_company "company name"

Search for the given name and print the best matching result.
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
    print '  %s "company name"' % sys.argv[0]
    sys.exit(2)

name = sys.argv[1]


i = imdb.IMDb()

in_encoding = sys.stdin.encoding or sys.getdefaultencoding()
out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

name = unicode(name, in_encoding, 'replace')
try:
    # Do the search, and get the results (a list of company objects).
    results = i.search_company(name)
except imdb.IMDbError, e:
    print "Probably you're not connected to Internet.  Complete error report:"
    print e
    sys.exit(3)

if not results:
    print 'No matches for "%s", sorry.' % name.encode(out_encoding, 'replace')
    sys.exit(0)

# Print only the first result.
print '    Best match for "%s"' % name.encode(out_encoding, 'replace')

# This is a company instance.
company = results[0]

# So far the company object only contains basic information like the
# name; retrieve main information:
i.update(company)

print company.summary().encode(out_encoding, 'replace')



