  IMDbPY package
  ==============

Here you can find information useful to use IMDbPY to write your
own scripts or programs.
These information are far from complete: the code is the final
documentation! ;-)

Sections in this file:
* GENERAL USAGE
* THE Movie CLASS
* THE Person CLASS
* THE Character CLASS
* THE Company CLASS
* INFORMATION SETS
* Person OBJECTS INSIDE A Movie CLASS AND Movie OBJECTS INSIDE A Person OBJECT
* Company OBJECTS INSIDE A Movie CLASS AND Movie OBJECTS INSIDE A Company OBJECT
* THE (NOT-SO-)"UNIVERSAL" '::' SEPARATOR
* MOVIE TITLES AND PERSON/CHARACTER NAMES REFERENCES
* EXCEPTIONS
* OTHER SOURCES OF INFO

  UNICODE NOTICE
  ==============

Since release 2.4, IMDbPY internally manages every information about
movies and people using unicode strings.  Please read the README.unicode file.


  GENERAL USAGE
  =============

To use the IMDbPY package, you've to import the imdb package and
call the IMDb function.
the basic invocation is:

  import imdb
  imdb_access = imdb.IMDb()

If you're accessing a sql installation of the IMDb's data,
you must do:
  imdb_access = imdb.IMDb('sql', uri='URI_TO_YOUR_DB')
where 'URI_TO_YOUR_DB' points to your SQL database (see README.sqldb
for more information).

Now you've the "imdb_access" object, instance of a subclass
of the imdb.IMDbBase class, which can be used to search for a given
title/name and to retrieve information about the referred movie,
person or character.

The IMDb function can be called with a 'accessSystem' keyword argument,
that must be a string representing the type of data access you want
to use.  That's because different systems to access the IMDb data are
available: you can directly fetch data from the web server, you can
have a local copy of the database (see http://www.imdb.com/interfaces/),
you can access movie data through the e-mail interface, etc. etc.


  Supported access systems  |  Aliases  |  Description
 ---------------------------+-----------+------------------------------------
  (default) 'http'          |   'web',  | information are fetched through
                            |   'html'  | the http://akas.imdb.com web server.
 ---------------------------+-----------+------------------------------------
             'sql'          |   'db',   | information are fetched through
                            | 'database'| a SQL database (every database
                            |           | supported by SQLObject and SQLAlchemy
                            |           | is available).
 ---------------------------+-----------+------------------------------------
           'mobile'         |           | same as 'httpThin', but string
                            |           | methods are used for parsing.
                            |           | Ideal for small systems like PDA,
                            |           | smart phones, hand-held devices with
                            |           | limited bandwidth and CPU power.
 ---------------------------+-----------+------------------------------------
          'httpThin'        | 'webThin' | identical to 'http', but less
                            | 'htmlThin'| information are gathered; useful
                            |           | for systems with limited bandwidth.

NOTE ON THE 'DEFAULT' ACCESS SYSTEM: since release 3.4, the 'imdbpy.cfg'
configuration file is available, so that you can set a system-wide (or
user-wide) default.  The file is commented with indication of the location
where it can be put, and how to modify it.
Obviously, if no imdbpy.cfg file is found (or is not readable or it can't
be parsed), 'http' is still considered the default.


The imdb_access object has ten main methods: search_movie(title),
get_movie(movieID), search_person(name), get_person(personID),
search_character(name), get_character(characterID), search_company(name),
get_company(companyID), search_episode() and update(MovieOrPersonObject)

  Methods description:

search_movie(title) searches for the given title, and returns a
list of Movie objects containing only basic information like the
movie title and year, and with a "movieID" instance variable:
   - movieID is an identifier of some kind; for the sake of simplicity
     you can think of it as the ID used by the IMDb's web server used to
     univocally identify a movie (e.g.: '0094226' for Brian De Palma's
     "The Untouchables"), but keep in mind that it's not necessary the
     same ID!!!
     For some implementations of the "data access system" these two IDs can
     be the same (and this is the case of the 'http' data access system), but
     other "access systems" can use a totally different kind of movieID.
     The easier (I hope!) way to understand this is to think at the
     movieID of a Movie returned by the search_movie() method as the _thing_
     you've  to pass to the get_movie() method, so that it can retrieve info
     about the referred movie.
     So, movieID _can_ be the imdbID ('0094226') if you're accessing
     the web server, but with a sql installation of the IMDb database,
     movieID will be an integer, as read from the id columns in the database.

search_episode(title) is identical to search_movie(), except that its
tailored to search for episodes' titles; best results are expected
searching for just the title of the episode, _without_ the title of
the TV series.

get_movie(movieID) will fetch the needed data and return a Movie object
for the movie referenced by the given movieID; the Movie class can be
found in the Movie module; a Movie object presents basically the same
interface of a Python's dictionary, so you can access, for example, the
list of actors and actress using the syntax: movieObject['cast']

The search_person(name), get_person(personID) search_character(name)
get_character(characterID), search_company(name) and get_company(companyID)
methods work the same way as search_movie(title) and get_movie(movieID).

The search_keyword(string) method returns a list of unicode string that are
valid keywords, similar to the one given.
The get_keyword(keyword) method returns a list of Movie instances that
are tagged with the given keyword.
For more information see README.keywords.

The get_imdbMovieID(movieID), get_imdbPersonID(personID),
get_imdbCharacterID(characterID) and get_imdbCompanyID(companyID) take,
respectively, a movieID, a personID, a movieID and a companyID and return
the relative imdbID; it's safer to use the
get_imdbID(MovieOrPersonOrCharacterOrCompanyObject) method.

The title2imdbID(title), name2imdbID(name), character2imdbID(name) and
company2imdbID(name) take, respectively, a movie title (in the plain text
data files format), a person name, a character name and a company name, and
return the relative imdbID; when possibile it's safer to use the
get_imdbID(MovieOrPersonOrCharacterOrCompanyObject) method.
These functions _always_ need to connect to the IMDb's web site, if
you're not using 'http', 'httpThin' or 'mobile' data acess systems.

The get_imdbID(MovieOrPersonOrCharacterOrCompanyObject) method returns the
imdbID for the given Movie, Person, Character or Company object.

The get_imdbURL(MovieOrPersonOrCharacterOrCompanyObject) method returns a
string with the main IMDb URL for the given Movie, Person, Character or
Company object; it tries to do its best to retrieve the URL.

The update(MovieOrPersonOrCharacterOrCompanyObject) method takes an
instance of a Movie, Person, Character or Company class and retrieve
other available information.
Remember that the search_*(txt)  methods will return a list of Movie, Person,
Character or Company objects with only basic information, like the movie
title or the person/character name, so update() can be used to retrieve
every other information.
By default a "reasonable" set of information are retrieved ('main',
'filmography' and 'biography' for a Person/Character objects, 'main'
and 'plot' for a Movie object and 'main' for Company objects).

Example:
  i = IMDb()
  # movie_list is a list of Movie objects, with only attributes like 'title'
  # and 'year' defined.
  movie_list = i.search_movie('the passion')
  # the first movie in the list.
  first_match = movie_list[0]
  # only basic information like the title will be printed.
  print first_match.summary()
  # update the information for this movie.
  i.update(first_match)
  # a lot of information will be printed!
  print first_match.summary()
  # retrieve trivia information and print it.
  i.update(first_match, 'trivia')
  print m['trivia']
  # retrieve both 'quotes' and 'goofs' information (with a list or tuple)
  i.update(m, ['quotes', 'goofs'])
  print m['quotes']
  print m['goofs']
  # retrieve every available information.
  i.update(m, 'all')


  THE Movie CLASS
  ===============

The main use of a Movie object is to access to the info it contains
with a dictionary-like interface, like "movieObject[key]" where 'key'
is a string that identifies the information you want to get.

I've a really bad news for you: at this time, what 'key' is, is a
little unclear! <g>

In general, it's the name of the section as used by the IMDb web
server to show the data.
Where the information is a list of people with a role (an actor,
a stunt, a writer, etc.) the relative section in the HTML page
starts with a link to a "/Glossary/X#SectName" page; here "sectname"
is used as 'key'.
When the info regard companies (distributors, special effects, etc.)
or the movie itself (sound mix, certifications, etc.) the section
in the HTML page begins with a link to a "/List?SectName=" page, so
we use "sectname" as a 'key'.
The section name (the key) is always (with some minor exceptions)
lowercase; underscores and minus signs are replaced with spaces.
Some other keys aren't taken from the HTML page, but are defined
within the Movie class.
To get the complete list of keys available for a given Movie object,
you can use the movieObject.keys() method (obviously only keys that
refer to some existing information are defined, so a movie without an
art director will raise a KeyError exception is you try
movieObject['art director']); to avoid the exception, you can test
if a Movie object has a given key with the has_key(key) method, or
get the value with the get(key) method, which returns the value or
None if the key is not found (an optional paramenter can modify the
default value returned if the key isn't found).

Below, a list of the main keys you can encounter, the type of the value
returned by movieObject[key] and a short description/example:

title; string; the "usual" title of the movie, like "The Untouchables".
long imdb title; string; "Uncommon Valor (1983/II) (TV)"
canonical title; string; the title in the canonical format,
                         like "Untouchables, The".
long imdb canonical title; string; "Patriot, The (2000)".
year; string; the year of release or '????' if unknown.
kind; string; one in ('movie', 'tv series', 'tv mini series', 'video game',
                      'video movie', 'tv movie', 'episode')
imdbIndex; string; the roman number for movies with the same title/year.
director; Person list; a list of director's name (e.g.: ['Brian De Palma'])
cast; Person list; list of actor/actress, with the currentRole instance
                   variable set to a Character object which describe his
                   role/duty.
cover url; string; the link to the image of the poster.
writer; Person list; list of writers ['Oscar Fraley (novel)']
plot; list; list of plots and authors of the plot.
rating; string; user rating on IMDb from 1 to 10 (e.g. '7.8')
votes; string; number of votes (e.g. '24,101')
runtimes; string list; in minutes ['119'] or something like ['USA:118',
          'UK:116']
number of episodes; int; number or episodes for a series.
color info; string list; ["Color (Technicolor)"]
countries; string list; production's country ['USA', 'Italy']
genres; string list; one or more in (Action, Adventure, Adult, Animation,
		Comedy, Crime, Documentary, Drama, Family, Fantasy, Film-Noir,
		Horror, Musical, Mystery, Romance, Sci-Fi, Short, Thriller,
		War, Western) and other genres defined by IMDb.
akas; string list; list of aka for this movie
languages; string list; list of languages
certificates; string list; ['UK:15', 'USA:R']
mpaa; string; the mpaa rating
episodes (series only); dictionary of dictionary; one key for every season,
                        one key for every episode in the season.
number of episodes (series only); int; total number of episodes.
number of seasons (series only); int; total number of seasons.
series years (series only); string; range of years when the series was produced.
episode of (episode only); Movie object; the parent series for an episode.
season (episode only); int; the season number.
episode (episode only); int; the number of the episode in the season.
long imdb episode title (episode only); string; episode and series title.
series title; string.
canonical series title; string.


Other keys that contain a list of Person objects are: costume designer,
sound crew, crewmembers, editor, production manager, visual effects,
assistant director, art department, composer, art director,
cinematographer, make up, stunt performer, producer, set decorator,
production designer.

Other keys that contain list of companies are: production companies, special
effects, sound mix, special effects companies, miscellaneous companies,
distributors.

Converting a title to its 'Title, The' canonical format, IMDbPY does
some assumptions about what is an article and what not, and this could
lead to some wrong canonical titles.
For more information on this subject, see the "ARTICLES IN TITLES"
section of the README.locale file.


  THE Person CLASS
  ================

It works mostly like the Movie class. :-)

The Movie class defines a __contains__() method, which is used to
check if a given person has worked in a given movie with the syntax:
  if personObject in movieObject:
      print '%s worked in %s' % (personObject['name'], movieObject['title'])

The Person class defines a isSamePerson(otherPersonObject) method, useful
to compare two person if you're not sure that both objects have retrieved
complete information (e.g.: a Person object returned by a query);
th syntax is:
   if personObject.isSamePerson(otherPersonObject):
       print 'they are the same person!'

An analogous method is defined for the Movie class, and it's
called isSameTitle(otherMovieObject)


  THE Character CLASS
  ===================

It works mostly like the Person class. :-)
For more information about the "currentRole" attribute, see the
README.currentRole file.


  THE Company CLASS
  ================

It works mostly like the Person class. :-)
The "currentRole" attribute is always None.


  INFORMATION SETS
  ================

Since release 1.2, it's possibile to retrieve almost every piece of
information about a given movie or person; this can be a problem, because
(at least for the 'http' data access system) it means that a lot of
web pages must be fetched and parsed, and this can be time and
bandwidth consuming, especially if you're interested only in a small set
of information.

Now the get_person, get_movie, get_character, get_company and update
methods have an optional 'info' argument, which can be set to a list
of strings, each one representing an "information set".
Movie/Person/Character/Company objects have, respectively, their own list
of available "information sets".
E.g.: the Movie class have a set called 'taglines' for the taglines
of the movie, a set called 'vote details' for the number of votes for
rating [1-10], demographic breakdowns and top 250 rank; the Person
class have a set called 'other works' for miscellaneous works of
this person an so on.

By default only important information are retrieved/updated (i.e.:
for a Movie object, only the 'main' and 'plot' information sets;
for a Person/Character object only 'main', 'filmography', 'biography'.

Example:
  i = imdb.IMDb(accessSystem='http')
  m = i.get_movie('0133093') # only default info set are retrieved.
  m.has_key('demographic') # returns false, since no demographic breakdowns
                           # aren't available by default.
  i.update(m, info=('vote details',)) # retrieve the vote details info set.
  print m['demographic'] # print the demographic breakdowns.

Another example:
  i = imdb.IMDb(accessSystem='http')
  # retrieve only the biography and the "other works" page:
  p = i.get_person('0000154', info=['biography', 'other works'])
  print p['salary']
  print p['other works']

To see which information sets are available and what are the defaults,
see the all_info and default_info instance variable of Movie, Person
and Character classes.  Each object instance of Movie, Person or Character,
also have a current_info instance variable, to remember the information sets
already retrieved.

Beware that the information sets vary from an access system to another:
locally not every data is accessible, while - for example for sql -
accessing one set of data automatically means automatic access to a number
of other unrelated information (without major performace drawbacks).
You can get the list of available info set with the methods:
i.get_movie_infoset(), i.get_person_infoset(), i.get_character_infoset()
and i.get_company_infoset().


  TOP250 / BOTTOM100 LISTS
  ========================

Since IMDbPY 4.0, it's possible to retrieve the list of top250
and bottom100 movies.
Use the get_top250_movies() and get_bottom100_movies() methods.
Beware that, for 'sql', the bottom100 list i limited to the first 10 results.


  Person OBJECTS INSIDE A Movie CLASS AND Movie OBJECTS INSIDE A Person OBJECT
  ============================================================================

Parsing the information about a movie, you'll encounter a lot of references
to the people who worked on it, like the cast, the director, the stunts,
and so on.
For people in the cast (actors/actresses), the "currentRole" instance
variable is set to the name of the character they played (e.g.: "Roy Neary"
for the role played by Richard Dreyfuss in Close Encounters of the Third Kind).
In fact, in this case currentRole will be a Character instance.

Another instance variable of a Person object is "notes", used to store
miscellaneous information (like an aka name for the actor, an "uncredited"
notice and so on).
It's also used, for non-cast people, to describe the specific task of
the person (e.g.: "assistant dialogue staff" for a person of the sound
departement).

It's possible to test, with the Python "in" statement, if a person worked
in a given movie, or vice-versa; the following are all valid tests:
  movie in person
  movie in character
  person in movie
  person in character
  character in movie
  character in person

Considerations similar to the above ones, can be done for Character
instances: please read the README.currentRole file for more information.

E.g.:
    # retrieve data for Steven Spielberg's "Close Encounters of the Third Kind"
    import imdb
    i =  imdb.IMDb(accessSystem='http')
    movie = i.get_movie('0075860')

    # Get the 7th Person object in the cast list
    cast = movie['cast'][6]
    # Will print "Warren J. Kemmerling"
    print cast['name']
    # Will print "Wild Bill"
    print cast.currentRole
    # Will print "(as Warren Kemmerling)"
    print cast.notes

    # Get the 5th Person object in the list of writers
    writer = movie['writer'][4]
    # Will print "Steven Spielberg"
    print writer['name']
    # Will print "written by", because that was duty of Steven Spielberg,
    # as a writer for the movie.
    print writer.notes

Obviously these Person objects contain only information directly
available parsing the movie pages (e.g.: the name, an imdbID, the role/duty),
so if now you:
    print writer['actor']
to get a list of movies acted by Mel Gibson, you'll get a KeyError
exception, because the Person object doesn't contain this kind of
information.

To gather every available information, you've to use the update()
method of the IMDb class:
    i.update(writer)
    # Now it will print a list of Movie objects.
    print writer['actor']

The same is true parsing a person data: you'll find a list of movie
he/she worked on and, for every movie, the currentRole instance variable
is set to a string describing the role/duty of the considered person.
E.g.:
    # Julia Roberts
    julia = i.get_person('0000210')
    # Print a list of movies she acted in and the played role, separated
    # by '::'
    print [movie['title'] + '::' + movie.currentRole
           for movie in julia['actress']]

Here the various Movie objects only contain minimal information, like
the title and the year; the latest movie with Julia Roberts:
    last = julia['actress'][0]
    # Retrieve full information
    i.update(last)
    # Print the name of the first director
    print last['director'][0]['name']


  Company OBJECTS INSIDE A Movie CLASS AND Movie OBJECTS INSIDE A Company OBJECT
  ==============================================================================

As for Person/Character and Movie objects, you can test - using the "in"
operator - if a Company has worked on a given Movie.


  THE (NOT-SO-)"UNIVERSAL" '::' SEPARATOR
  =======================================

Sometimes I've used '::' to separate a set of different information
inside a string, like the name of a company and what it has done for the
movie, the information in the "Also Known As" section, and so on.
It's easier to understand if you look at it; look at the output of:
  import imdb
  i = imdb.IMDb()
  m = i.get_movie('0094226')
  print m['akas']

As a rule, there's as much as one '::' separator inside a string,
splitting it two logical pieces: "TEXT::NOTE".
In the helpers module there's the makeTextNotes function, that can
be used to create a custom function to pretty-print this kind of
information.  See its documentation for more info.


  MOVIE TITLES AND PERSON/CHARACTER NAMES REFERENCES
  ==================================================

Sometimes in Movie, Person and Character attributes, there're strings
with references to other movies or persons (e.g.: in the plot, in
the biography, etc.).
These references are stored in the Movie, Person and Character
instances; in the strings you'll find values like _A Movie (2003)_ (qv)
or 'A Person' (qv) or '#A Character# (qv)'; accessing these
string (like movie['plot'] or person['biography']), these strings are
modified using a provided function, which must take, as arguments, the
string and two dictionary with titles and names references;
by default the (qv) strings are converted in the "normal"
format ("A Movie (2003)", "A Person" and "A Character").
You can find some examples of these functions in the
imdb.utils module.
The function used to modify the strings can be set with
the defaultModFunct parameter of the IMDb class or
with the modFunct parameter of the get_movie, get_person
and get_character methods.
E.g.:
  import imdb
  i = imdb.IMDb(defaultModFunct=imdb.utils.modHtmlLinks)

Or:
  import imdb
  i = imdb.IMDb()
  i.get_person('0000154', modFunct=imdb.utils.modHtmlLinks)


  EXCEPTIONS
  ==========

The imdb._exceptions module contains the exceptions raised by the
imdb package.  Every exception is a subsclass of IMDbError, which is
available from the imdb package.

You can catch any type of errors raised by the IMDbPY package with
something like:
  from imdb import IMDb, IMDbError

  try:
      i = IMDb()
  except IMDbError, err:
      print err

  try:
      results = i.search_person('Mel Gibson')
  except IMDbError, err:
      print err

  try:
      movie = i.get_movie('0335345')
  except IMDbError, err:
      print err


  OTHER SOURCES OF INFO
  =====================

Once the IMDbPY package is installed, you can read the docstring for
packages, modules, functions, classes, objects, methods using the
pydoc program; e.g.: "pydoc imdb.IMDb" will show the documentation
about the imdb.IMDb class.

The code contains a lot of comments, try reading it, if you can
understand my English!


