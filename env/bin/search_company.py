#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
search_company.py

Usage: search_company "company name"

Search for the given name and print the results.
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

# Print the results.
print '    %s result%s for "%s":' % (len(results),
                                    ('', 's')[len(results) != 1],
                                    name.encode(out_encoding, 'replace'))
print 'companyID\t: imdbID : name'

# Print the long imdb name for every company.
for company in results:
    outp = u'%s\t\t: %s : %s' % (company.companyID, i.get_imdbID(company),
                                company['long imdb name'])
    print outp.encode(out_encoding, 'replace')


