  What's IMDbPY?
  ==============

NOTE: see also the recommendations in the "DISCLAIMER.txt" file.


IMDbPY is a Python package useful to retrieve and manage the data of
the IMDb movie database.

IMDbPY is mainly a tool intended for programmers and developers, but
some example scripts are included.

If you're a poor, simple, clueless user, read the "README.users" file. :-)
Seriously: take a look at the provided example scripts even if you're
a Really Mighty Programmer(tm), they should clearly show how to use IMDbPY.
Other IMDbPY-based programs can be downloaded from:
  http://imdbpy.sourceforge.net/?page=programs

If you want to develop a program/script/package/framework using the
IMDbPY package, see the "README.package" file, for instructions about
how to use this package.

If you're installing IMDbPY in a smart phone, PDA or hand-held system,
read the "README.mobile" file.

If you're crazy enough and/or you've realized that your higher
inspiration in life is to help the development of IMDbPY, begin reading
the "README.devel" file. ;-)


  INSTALLATION
  ============

Everything you need to do is to run, as the root user, the command:
    # python setup.py install

IMDbPY itself can be installed through easy_install and pip,
with - respectively - these commands (as root):
  easy_install IMDbPY
  pip install IMDbPY

Using easy_install and pip, the dependencies will be automatically
satisfied.  Third-party packages may be downloaded, and if not
otherwise specified (see below), C extensions compiled (this means
that you need the python-dev package installed).

If, for some reason, it doesn't work, you can copy the "./imdb"
directory in the local site-packages directory of the python
major version you're using, but remember that you'll not satisfy
the required dependencies and neither compile the optional C module,
so use this as your very last resort.
To know what major version of python you've installed, run:
    $ python -V
It should return a string like "Python 2.6.1"; in this example
the major version is "2.6".
Now copy the "./imdb" directory:
    # cp -r ./imdb /usr/local/lib/python{MAJORVERSION}/site-packages/

The setup.py contains some configuration options that could
be useful if you're installing IMDbPY in a system with very
little hard disk space (like an handheld device) or where
you've not a complete development environment available;
read the "README.mobile" file.

If you want to insert the content of the plain text data files
into a SQL database, read the "README.sqldb" file.

The whole list of command line options of the setup.py script is:
  --without-lxml	exclude lxml (speeds up "http" considerably,
					so try to fix it).
  --without-cutils	don't compile the C module (speeds up 'sql')
  --without-sqlobject	exclude SQLObject
  --without-sqlalchemy	exclude SQLAlchemy

By default, setup.py tries to install BOTH SQLObject
and SQLAlchemy.  In fact, having one of them will be enough:
you can exclude the unwanted one.


  Mercurial VERSION
  =================

The best thing is always to use a package for your distribution,
or use easy_install or pip to install the latest release, but it
goes without saying that sometimes you need the very latest version
(keep in mind that the IMDb site is a moving target...).
In this case, you can always use the Mercurial version, available here:
  http://imdbpy.sourceforge.net/?page=download#hg


  HELP
  ====

Refer to the web site http://imdbpy.sf.net/ and subscribe to the
mailing list:  http://imdbpy.sf.net/?page=help#ml


  NOTES FOR PACKAGERS
  ===================

If you plan to package IMDbPY for your distribution/operating system,
keep in mind that, while IMDbPY can works out-of-the-box, some external
package may be required for certain functionality:
  - python-lxml: the 'http' data access system will be much faster, if
    it's installed.
  - SQLObject or SQLAlchemy: one of these is REQUIRED if you want to use
    the 'sql' data access system.

All of them should probably be "recommended" (or at least "suggested")
dependencies.
To compile the C module, you also need the python-dev package.

As of IMDbPY 4.0, the installer is based on setuptools.


  RECENT IMPORTANT CHANGES
  ========================

Since release 2.4, IMDbPY internally manages every information about
movies and people using unicode strings.  Please read the README.unicode file.

Since release 3.3, IMDbPY supports IMDb's character pages; see the
README.currentRole file for more information.

Since release 3.6, IMDbPY supports IMDb's company pages; see the
README.companies file for more information.

Since release 3.7, IMDbPY has moved its main parsers from a SAX-based
approach to a DOM/XPath-based one; see the README.newparsers file
for more information.

Since release 3.8, IMDbPY supports both SQLObject and SQLAlchemy; see
README.sqldb for more information.

Since release 3.9 support dumping the plain text data files in CSV files;
see README.sqldb for more information.

Since release 4.0 it's possible to search for keywords (get keywords
similar to a given one and get a list of movies for a specified keyword).
See README.keywords for more information.
Moreover, it's possible to get information out of Movie, Person, Character
and Company instances as XML (getting a single keys or the representation
of a whole object).
See README.info2xml for more information.
Another new feature, is the ability to get top250 and bottom100 lists;
see the "TOP250 / BOTTOM100 LISTS" section of the README.package file
for more information.

Since release 4.1 a DTD for the XML output is available (see
imdbpyXY.dtd).  Other important features are locale (i18n) support (see
README.locale) and support for the new style of movie titles used by IMDb
(now in the "The Title" style, and no more as "Title, The").


  FEATURES
  ========

So far you can search for a movie with a given title, a person
with a given name, a character you've seen in a movie or a company, and retrieve
information for a given movie, person, character or company; the supported data
access systems are 'http' (i.e.: the data are fetched through the IMDb's
web server http://akas.imdb.com) and 'sql', meaning that the data are
taken from a SQL database, populated (using the imdbpy2sql.py script) with
data taken from the plain text data files; see
http://www.imdb.com/interfaces/ for more information.
For mobile systems there's the 'mobile' data access system, useful
for PDA, hand-held devices and smart phones.
Another data access system is 'httpThin', which is equal to 'http'
but fetch less data and so it is (or at least it tries to be)
suitable for systems with limited bandwidth but normal CPU power.


  FEATURES OF THE HTTP DATA ACCESS SYSTEM
  =======================================

* Returns almost every available information about a movie, person or
  character.
* The use of the "akas" server will provide access to a lot of
  AKA titles in many languages, so it's really useful if English is
  not your native language.
* By default includes adult titles (and people who have worked
  only/mostly in adult movies) in the results of a title/name search; this
  behavior can be changed with the do_adult_search() method; please
  read the "README.adult" file.
* You can set/use a proxy to access the web; if set, the HTTP_PROXY
  environment variable will be automatically used, otherwise you can set a
  proxy with the set_proxy() method of the class returned by the
  imdb.IMDb function; obviously this method is available only for the http
  data access system, since it's defined in the IMDbHTTPAccessSystem class
  of the parser.http package.
  Example:
      from imdb import IMDb
      i = IMDb(accessSystem='http') # the accessSystem argument is not really
                            # needed, since "http" is the default.
      i.set_proxy('http://localhost:8080/')

  You can force a direct connection to the net setting the proxy
  to a null value (i.e.: i.set_proxy('')).


  FEATURES OF THE SQL DATA ACCESS SYSTEM
  ======================================

* Returns every information available in the plain text data files.
* Every database supported by SQLObject and SQLAlchemy is available.


  FEATURES OF THE MOBILE DATA ACCESS SYSTEM
  =========================================

* Very lightweight, returns almost every needed information.
* Accessories data sets (like 'goofs', 'trivia' and so on) are always
  available (being a subclass of the 'http' data access system).


