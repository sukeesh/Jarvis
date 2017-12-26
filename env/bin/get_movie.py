#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
get_movie.py

Usage: get_movie "movieID"

Show some info about the movie with the given movieID (e.g. '0133093'
for "The Matrix", using 'http' or 'mobile').
Notice that movieID, using 'sql', are not the same IDs used on the web.
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
    print '  %s "movieID"' % sys.argv[0]
    sys.exit(2)

movieID = sys.argv[1]

i = imdb.IMDb()

out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

try:
    # Get a Movie object with the data about the movie identified by
    # the given movieID.
    movie = i.get_movie(movieID)
except imdb.IMDbError, e:
    print "Probably you're not connected to Internet.  Complete error report:"
    print e
    sys.exit(3)


if not movie:
    print 'It seems that there\'s no movie with movieID "%s"' % movieID
    sys.exit(4)

# XXX: this is the easier way to print the main info about a movie;
# calling the summary() method of a Movie object will returns a string
# with the main information about the movie.
# Obviously it's not really meaningful if you want to know how
# to access the data stored in a Movie object, so look below; the
# commented lines show some ways to retrieve information from a
# Movie object.
print movie.summary().encode(out_encoding, 'replace')

# Show some info about the movie.
# This is only a short example; you can get a longer summary using
# 'print movie.summary()' and the complete set of information looking for
# the output of the movie.keys() method.
#print '==== "%s" / movieID: %s ====' % (movie['title'], movieID)
# XXX: use the IMDb instance to get the IMDb web URL for the movie.
#imdbURL = i.get_imdbURL(movie)
#if imdbURL:
#    print 'IMDb URL: %s' % imdbURL
#
# XXX: many keys return a list of values, like "genres".
#genres = movie.get('genres')
#if genres:
#    print 'Genres: %s' % ' '.join(genres)
#
# XXX: even when only one value is present (e.g.: movie with only one
#      director), fields that can be multiple are ALWAYS a list.
#      Note that the 'name' variable is a Person object, but since its
#      __str__() method returns a string with the name, we can use it
#      directly, instead of name['name']
#director = movie.get('director')
#if director:
#    print 'Director(s): ',
#    for name in director:
#        sys.stdout.write('%s ' % name)
#    print ''
#
# XXX: notice that every name in the cast is a Person object, with a
#      currentRole instance variable, which is a string for the played role.
#cast = movie.get('cast')
#if cast:
#    print 'Cast: '
#    cast = cast[:5]
#    for name in cast:
#        print '      %s (%s)' % (name['name'], name.currentRole)
# XXX: some information are not lists of strings or Person objects, but simple
#      strings, like 'rating'.
#rating = movie.get('rating')
#if rating:
#    print 'Rating: %s' % rating
# XXX: an example of how to use information sets; retrieve the "trivia"
#      info set; check if it contains some data, select and print a
#      random entry.
#import random
#i.update(movie, info=['trivia'])
#trivia = movie.get('trivia')
#if trivia:
#    rand_trivia = trivia[random.randrange(len(trivia))]
#    print 'Random trivia: %s' % rand_trivia


