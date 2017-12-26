#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
get_person.py

Usage: get_person "personID"

Show some info about the person with the given personID (e.g. '0000210'
for "Julia Roberts".
Notice that personID, using 'sql', are not the same IDs used on the web.
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
    print '  %s "personID"' % sys.argv[0]
    sys.exit(2)

personID = sys.argv[1]

i = imdb.IMDb()

out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

try:
    # Get a Person object with the data about the person identified by
    # the given personID.
    person = i.get_person(personID)
except imdb.IMDbError, e:
    print "Probably you're not connected to Internet.  Complete error report:"
    print e
    sys.exit(3)


if not person:
    print 'It seems that there\'s no person with personID "%s"' % personID
    sys.exit(4)

# XXX: this is the easier way to print the main info about a person;
# calling the summary() method of a Person object will returns a string
# with the main information about the person.
# Obviously it's not really meaningful if you want to know how
# to access the data stored in a Person object, so look below; the
# commented lines show some ways to retrieve information from a
# Person object.
print person.summary().encode(out_encoding, 'replace')

# Show some info about the person.
# This is only a short example; you can get a longer summary using
# 'print person.summary()' and the complete set of information looking for
# the output of the person.keys() method.
#print '==== "%s" / personID: %s ====' % (person['name'], personID)
# XXX: use the IMDb instance to get the IMDb web URL for the person.
#imdbURL = i.get_imdbURL(person)
#if imdbURL:
#    print 'IMDb URL: %s' % imdbURL
# XXX: print the birth date and birth notes.
#d_date = person.get('birth date')
#if d_date:
#    print 'Birth date: %s' % d_date
#    b_notes = person.get('birth notes')
#    if b_notes:
#        print 'Birth notes: %s' % b_notes
# XXX: print the last five movies he/she acted in, and the played role.
#movies_acted = person.get('actor') or person.get('actress')
#if movies_acted:
#    print 'Last roles played: '
#    for movie in movies_acted[:5]:
#        print '    %s (in "%s")' % (movie.currentRole, movie['title'])
# XXX: example of the use of information sets.
#import random
#i.update(person, info=['awards'])
#awards = person.get('awards')
#if awards:
#    rand_award = awards[random.randrange(len(awards))]
#    s = 'Random award: in year '
#    s += rand_award.get('year', '')
#    s += ' %s "%s"' % (rand_award.get('result', '').lower(),
#                        rand_award.get('award', ''))
#    print s


