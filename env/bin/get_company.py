#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
get_company.py

Usage: get_company "companyID"

Show some info about the company with the given companyID (e.g. '0071509'
for "Columbia Pictures [us]", using 'http' or 'mobile').
Notice that companyID, using 'sql', are not the same IDs used on the web.
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
    print '  %s "companyID"' % sys.argv[0]
    sys.exit(2)

companyID = sys.argv[1]

i = imdb.IMDb()

out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

try:
    # Get a company object with the data about the company identified by
    # the given companyID.
    company = i.get_company(companyID)
except imdb.IMDbError, e:
    print "Probably you're not connected to Internet.  Complete error report:"
    print e
    sys.exit(3)


if not company:
    print 'It seems that there\'s no company with companyID "%s"' % companyID
    sys.exit(4)

# XXX: this is the easier way to print the main info about a company;
# calling the summary() method of a company object will returns a string
# with the main information about the company.
# Obviously it's not really meaningful if you want to know how
# to access the data stored in a company object, so look below; the
# commented lines show some ways to retrieve information from a
# company object.
print company.summary().encode(out_encoding, 'replace')


