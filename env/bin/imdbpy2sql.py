#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7
"""
imdbpy2sql.py script.

This script puts the data of the plain text data files into a
SQL database.

Copyright 2005-2016 Davide Alberani <da@erlug.linux.it>
               2006 Giuseppe "Cowo" Corbelli <cowo --> lugbs.linux.it>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import os
import sys
import getopt
import time
import re
import warnings
import anydbm
from itertools import islice, chain
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
from gzip import GzipFile
from types import UnicodeType

#from imdb.parser.sql.dbschema import *
from imdb.parser.sql.dbschema import DB_SCHEMA, dropTables, createTables, \
    createIndexes, createForeignKeys
from imdb.parser.sql import soundex
from imdb.utils import analyze_title, analyze_name, date_and_notes, \
        build_name, build_title, normalizeName, normalizeTitle, _articles, \
        build_company_name, analyze_company_name, canonicalTitle
from imdb._exceptions import IMDbParserError, IMDbError


HELP = """imdbpy2sql.py usage:
    %s -d /directory/with/PlainTextDataFiles/ -u URI [-c /directory/for/CSV_files] [-o sqlobject,sqlalchemy] [-i table,dbm] [--CSV-OPTIONS] [--COMPATIBILITY-OPTIONS]

        # NOTE: URI is something along the line:
                scheme://[user[:password]@]host[:port]/database[?parameters]

                Examples:
                mysql://user:password@host/database
                postgres://user:password@host/database
                sqlite:/tmp/imdb.db
                sqlite:/C|/full/path/to/database

        # NOTE: CSV mode (-c path):
                A directory is used to store CSV files; on supported
                database servers it should be really fast.

        # NOTE: ORMs (-o orm):
                Valid options are 'sqlobject', 'sqlalchemy' or the
                preferred order separating the voices with a comma.

        # NOTE: imdbIDs store/restore (-i method):
                Valid options are 'table' (imdbIDs stored in a temporary
                table of the database) or 'dbm' (imdbIDs stored on a dbm
                file - this is the default if CSV is used).

        # NOTE: --CSV-OPTIONS can be:
            --csv-ext STRING        files extension (.csv)
            --csv-only-write        exit after the CSV files are written.
            --csv-only-load         load an existing set of CSV files.

        # NOTE: --COMPATIBILITY-OPTIONS can be one of:
            --mysql-innodb          insert data into a MySQL MyISAM db,
                                    and then convert it to InnoDB.
            --mysql-force-myisam    force the creation of MyISAM tables.
            --ms-sqlserver          compatibility mode for Microsoft SQL Server
                                    and SQL Express.
            --sqlite-transactions   uses transactions, to speed-up SQLite.


                See README.sqldb for more information.
""" % sys.argv[0]

# Directory containing the IMDb's Plain Text Data Files.
IMDB_PTDF_DIR = None
# URI used to connect to the database.
URI = None
# ORM to use (list of options) and actually used (string).
USE_ORM = None
USED_ORM = None
# List of tables of the database.
DB_TABLES = []
# Max allowed recursion, inserting data.
MAX_RECURSION = 10
# Method used to (re)store imdbIDs.
IMDBIDS_METHOD = None
# If set, this directory is used to output CSV files.
CSV_DIR = None
CSV_CURS = None
CSV_ONLY_WRITE = False
CSV_ONLY_LOAD = False
CSV_EXT = '.csv'
CSV_EOL = '\n'
CSV_DELIMITER = ','
CSV_QUOTE = '"'
CSV_ESCAPE = '"'
CSV_NULL = 'NULL'
CSV_QUOTEINT = False
CSV_LOAD_SQL = None
CSV_MYSQL = "LOAD DATA LOCAL INFILE '%(file)s' INTO TABLE `%(table)s` FIELDS TERMINATED BY '%(delimiter)s' ENCLOSED BY '%(quote)s' ESCAPED BY '%(escape)s' LINES TERMINATED BY '%(eol)s'"
CSV_PGSQL = "COPY %(table)s FROM '%(file)s' WITH DELIMITER AS '%(delimiter)s' NULL AS '%(null)s' QUOTE AS '%(quote)s' ESCAPE AS '%(escape)s' CSV"
CSV_DB2 = "CALL SYSPROC.ADMIN_CMD('LOAD FROM %(file)s OF del MODIFIED BY lobsinfile INSERT INTO %(table)s')"

# Temporary fix for old style titles.
#FIX_OLD_STYLE_TITLES = True

# Store custom queries specified on the command line.
CUSTOM_QUERIES = {}
# Allowed time specification, for custom queries.
ALLOWED_TIMES = ('BEGIN', 'BEFORE_DROP', 'BEFORE_CREATE', 'AFTER_CREATE',
                'BEFORE_MOVIES', 'BEFORE_COMPANIES', 'BEFORE_CAST',
                'BEFORE_RESTORE', 'BEFORE_INDEXES', 'END', 'BEFORE_MOVIES_TODB',
                'AFTER_MOVIES_TODB', 'BEFORE_PERSONS_TODB',
                'AFTER_PERSONS_TODB','BEFORE_SQLDATA_TODB',
                'AFTER_SQLDATA_TODB', 'BEFORE_AKAMOVIES_TODB',
                'AFTER_AKAMOVIES_TODB', 'BEFORE_CHARACTERS_TODB',
                'AFTER_CHARACTERS_TODB', 'BEFORE_COMPANIES_TODB',
                'AFTER_COMPANIES_TODB', 'BEFORE_EVERY_TODB',
                'AFTER_EVERY_TODB', 'BEFORE_CSV_LOAD', 'BEFORE_CSV_TODB',
                'AFTER_CSV_TODB')

# Shortcuts for some compatibility options.
MYSQLFORCEMYISAM_OPTS = ['-e',
        'AFTER_CREATE:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=MyISAM;']
MYSQLINNODB_OPTS = ['-e',
        'AFTER_CREATE:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=MyISAM;',
        '-e',
        'BEFORE_INDEXES:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=InnoDB;']
SQLSERVER_OPTS =  ['-e', 'BEFORE_MOVIES_TODB:SET IDENTITY_INSERT %(table)s ON;',
        '-e', 'AFTER_MOVIES_TODB:SET IDENTITY_INSERT %(table)s OFF;',
        '-e', 'BEFORE_PERSONS_TODB:SET IDENTITY_INSERT %(table)s ON;',
        '-e', 'AFTER_PERSONS_TODB:SET IDENTITY_INSERT %(table)s OFF;',
        '-e', 'BEFORE_COMPANIES_TODB:SET IDENTITY_INSERT %(table)s ON;',
        '-e', 'AFTER_COMPANIES_TODB:SET IDENTITY_INSERT %(table)s OFF;',
        '-e', 'BEFORE_CHARACTERS_TODB:SET IDENTITY_INSERT %(table)s ON;',
        '-e', 'AFTER_CHARACTERS_TODB:SET IDENTITY_INSERT %(table)s OFF;',
        '-e', 'BEFORE_AKAMOVIES_TODB:SET IDENTITY_INSERT %(table)s ON;',
        '-e', 'AFTER_AKAMOVIES_TODB:SET IDENTITY_INSERT %(table)s OFF;']
SQLITE_OPTS = ['-e', 'BEGIN:PRAGMA synchronous = OFF;',
        '-e', 'BEFORE_EVERY_TODB:BEGIN TRANSACTION;',
        '-e', 'AFTER_EVERY_TODB:COMMIT;',
        '-e', 'BEFORE_INDEXES:BEGIN TRANSACTION;',
        'e', 'END:COMMIT;']

if '--mysql-innodb' in sys.argv[1:]:
    sys.argv += MYSQLINNODB_OPTS
if '--mysql-force-myisam' in sys.argv[1:]:
    sys.argv += MYSQLFORCEMYISAM_OPTS
if '--ms-sqlserver' in sys.argv[1:]:
    sys.argv += SQLSERVER_OPTS
if '--sqlite-transactions' in sys.argv[1:]:
    sys.argv += SQLITE_OPTS

# Manage arguments list.
try:
    optlist, args = getopt.getopt(sys.argv[1:], 'u:d:e:o:c:i:h',
                                                ['uri=', 'data=', 'execute=',
                                                'mysql-innodb', 'ms-sqlserver',
                                                'sqlite-transactions',
                                                'fix-old-style-titles',
                                                'mysql-force-myisam', 'orm',
                                                'csv-only-write',
                                                'csv-only-load',
                                                'csv=', 'csv-ext=',
                                                'imdbids=', 'help'])
except getopt.error, e:
    print 'Troubles with arguments.'
    print HELP
    sys.exit(2)

for opt in optlist:
    if opt[0] in ('-d', '--data'):
        IMDB_PTDF_DIR = opt[1]
    elif opt[0] in ('-u', '--uri'):
        URI = opt[1]
    elif opt[0] in ('-c', '--csv'):
        CSV_DIR = opt[1]
    elif opt[0] == '--csv-ext':
        CSV_EXT = opt[1]
    elif opt[0] in ('-i', '--imdbids'):
        IMDBIDS_METHOD = opt[1]
    elif opt[0] in ('-e', '--execute'):
        if opt[1].find(':') == -1:
            print 'WARNING: wrong command syntax: "%s"' % opt[1]
            continue
        when, cmd = opt[1].split(':', 1)
        if when not in ALLOWED_TIMES:
            print 'WARNING: unknown time: "%s"' % when
            continue
        if when == 'BEFORE_EVERY_TODB':
            for nw in ('BEFORE_MOVIES_TODB', 'BEFORE_PERSONS_TODB',
                        'BEFORE_SQLDATA_TODB', 'BEFORE_AKAMOVIES_TODB',
                        'BEFORE_CHARACTERS_TODB', 'BEFORE_COMPANIES_TODB'):
                CUSTOM_QUERIES.setdefault(nw, []).append(cmd)
        elif when == 'AFTER_EVERY_TODB':
            for nw in ('AFTER_MOVIES_TODB', 'AFTER_PERSONS_TODB',
                        'AFTER_SQLDATA_TODB', 'AFTER_AKAMOVIES_TODB',
                        'AFTER_CHARACTERS_TODB', 'AFTER_COMPANIES_TODB'):
                CUSTOM_QUERIES.setdefault(nw, []).append(cmd)
        else:
            CUSTOM_QUERIES.setdefault(when, []).append(cmd)
    elif opt[0] in ('-o', '--orm'):
        USE_ORM = opt[1].split(',')
    elif opt[0] == '--fix-old-style-titles':
        warnings.warn('The --fix-old-style-titles argument is obsolete.')
    elif opt[0] == '--csv-only-write':
        CSV_ONLY_WRITE = True
    elif opt[0] == '--csv-only-load':
        CSV_ONLY_LOAD = True
    elif opt[0] in ('-h', '--help'):
        print HELP
        sys.exit(0)

if IMDB_PTDF_DIR is None:
    print 'You must supply the directory with the plain text data files'
    print HELP
    sys.exit(2)

if URI is None:
    print 'You must supply the URI for the database connection'
    print HELP
    sys.exit(2)

if IMDBIDS_METHOD not in (None, 'dbm', 'table'):
    print 'the method to (re)store imdbIDs must be one of "dbm" or "table"'
    print HELP
    sys.exit(2)

if (CSV_ONLY_WRITE or CSV_ONLY_LOAD) and not CSV_DIR:
    print 'You must specify the CSV directory with the -c argument'
    print HELP
    sys.exit(3)


# Some warnings and notices.
URIlower = URI.lower()

if URIlower.startswith('mysql'):
    if '--mysql-force-myisam' in sys.argv[1:] and \
            '--mysql-innodb' in sys.argv[1:]:
        print '\nWARNING: there is no sense in mixing the --mysql-innodb and\n'\
                '--mysql-force-myisam command line options!\n'
    elif '--mysql-innodb' in sys.argv[1:]:
        print "\nNOTICE: you've specified the --mysql-innodb command line\n"\
                "option; you should do this ONLY IF your system uses InnoDB\n"\
                "tables or you really want to use InnoDB; if you're running\n"\
                "a MyISAM-based database, please omit any option; if you\n"\
                "want to force MyISAM usage on a InnoDB-based database,\n"\
                "try the --mysql-force-myisam command line option, instead.\n"
    elif '--mysql-force-myisam' in sys.argv[1:]:
        print "\nNOTICE: you've specified the --mysql-force-myisam command\n"\
                "line option; you should do this ONLY IF your system uses\n"\
                "InnoDB tables and you want to use MyISAM tables, instead.\n"
    else:
        print "\nNOTICE: IF you're using InnoDB tables, data insertion can\n"\
                "be very slow; you can switch to MyISAM tables - forcing it\n"\
                "with the --mysql-force-myisam option - OR use the\n"\
                "--mysql-innodb command line option, but DON'T USE these if\n"\
                "you're already working on MyISAM tables, because it will\n"\
                "force MySQL to use InnoDB, and performances will be poor.\n"
elif URIlower.startswith('mssql') and \
        '--ms-sqlserver' not in sys.argv[1:]:
    print "\nWARNING: you're using MS SQLServer without the --ms-sqlserver\n"\
            "command line option: if something goes wrong, try using it.\n"
elif URIlower.startswith('sqlite') and \
        '--sqlite-transactions' not in sys.argv[1:]:
    print "\nWARNING: you're using SQLite without the --sqlite-transactions\n"\
            "command line option: you'll have very poor performances!  Try\n"\
            "using it.\n"
if ('--mysql-force-myisam' in sys.argv[1:] and
        not URIlower.startswith('mysql')) or ('--mysql-innodb' in
        sys.argv[1:] and not URIlower.startswith('mysql')) or ('--ms-sqlserver'
        in sys.argv[1:] and not URIlower.startswith('mssql')) or \
        ('--sqlite-transactions' in sys.argv[1:] and
        not URIlower.startswith('sqlite')):
    print "\nWARNING: you've specified command line options that don't\n"\
            "belong to the database server you're using: proceed at your\n"\
            "own risk!\n"


if CSV_DIR:
    if URIlower.startswith('mysql'):
        CSV_LOAD_SQL = CSV_MYSQL
    elif URIlower.startswith('postgres'):
        CSV_LOAD_SQL = CSV_PGSQL
    elif URIlower.startswith('ibm'):
        CSV_LOAD_SQL = CSV_DB2
        CSV_NULL = ''
    else:
        print "\nERROR: importing CSV files is not supported for this database"
        sys.exit(3)


if USE_ORM is None:
    USE_ORM = ('sqlobject', 'sqlalchemy')
if not isinstance(USE_ORM, (tuple, list)):
    USE_ORM = [USE_ORM]
nrMods = len(USE_ORM)
_gotError = False
for idx, mod in enumerate(USE_ORM):
    mod = mod.lower()
    try:
        if mod == 'sqlalchemy':
            from imdb.parser.sql.alchemyadapter import getDBTables, setConnection
        elif mod == 'sqlobject':
            from imdb.parser.sql.objectadapter import getDBTables, setConnection
        else:
            warnings.warn('unknown module "%s".' % mod)
            continue
        DB_TABLES = getDBTables(URI)
        for t in DB_TABLES:
            globals()[t._imdbpyName] = t
        if _gotError:
            warnings.warn('falling back to "%s".' % mod)
        USED_ORM = mod
        break
    except ImportError, e:
        if idx+1 >= nrMods:
            raise IMDbError('unable to use any ORM in %s: %s' % (
                                            str(USE_ORM), str(e)))
        else:
            warnings.warn('unable to use "%s": %s' % (mod, str(e)))
            _gotError = True
        continue
else:
    raise IMDbError('unable to use any ORM in %s' % str(USE_ORM))


#-----------------------
# CSV Handling.


class CSVCursor(object):
    """Emulate a cursor object, but instead it writes data to a set
    of CSV files."""
    def __init__(self, csvDir, csvExt=CSV_EXT, csvEOL=CSV_EOL,
            delimeter=CSV_DELIMITER, quote=CSV_QUOTE, escape=CSV_ESCAPE,
            null=CSV_NULL, quoteInteger=CSV_QUOTEINT):
        """Initialize a CSVCursor object; csvDir is the directory where the
        CSV files will be stored."""
        self.csvDir = csvDir
        self.csvExt = csvExt
        self.csvEOL = csvEOL
        self.delimeter = delimeter
        self.quote = quote
        self.escape = escape
        self.escaped = '%s%s' % (escape, quote)
        self.null = null
        self.quoteInteger = quoteInteger
        self._fdPool = {}
        self._lobFDPool = {}
        self._counters = {}

    def buildLine(self, items, tableToAddID=False, rawValues=(),
                    lobFD=None, lobFN=None):
        """Build a single text line for a set of information."""
        # FIXME: there are too many special cases to handle, and that
        #        affects performances: management of LOB files, at least,
        #        must be moved away from here.
        quote = self.quote
        null = self.null
        escaped = self.escaped
        quoteInteger = self.quoteInteger
        if not tableToAddID:
            r = []
        else:
            _counters = self._counters
            r = [_counters[tableToAddID]]
            _counters[tableToAddID] += 1
        r += list(items)
        for idx, val in enumerate(r):
            if val is None:
                r[idx] = null
                continue
            if (not quoteInteger) and isinstance(val, (int, long)):
                r[idx] = str(val)
                continue
            if lobFD and idx == 3:
                continue
            val = str(val)
            if quote:
                val = '%s%s%s' % (quote, val.replace(quote, escaped), quote)
            r[idx] = val
        # Add RawValue(s), if present.
        rinsert = r.insert
        if tableToAddID:
            shift = 1
        else:
            shift = 0
        for idx, item in rawValues:
            rinsert(idx + shift, item)
        if lobFD:
            # XXX: totally tailored to suit person_info.info column!
            val3 = r[3]
            val3len = len(val3 or '') or -1
            if val3len == -1:
                val3off = 0
            else:
                val3off = lobFD.tell()
            r[3] = '%s.%d.%d/' % (lobFN, val3off, val3len)
            lobFD.write(val3)
        # Build the line and add the end-of-line.
        return '%s%s' % (self.delimeter.join(r), self.csvEOL)

    def executemany(self, sqlstr, items):
        """Emulate the executemany method of a cursor, but writes the
        data in a set of CSV files."""
        # XXX: find a safer way to get the table/file name!
        tName = sqlstr.split()[2]
        lobFD = None
        lobFN = None
        doLOB = False
        # XXX: ugly special case, to create the LOB file.
        if URIlower.startswith('ibm') and tName == 'person_info':
            doLOB = True
        # Open the file descriptor or get it from the pool.
        if tName in self._fdPool:
            tFD = self._fdPool[tName]
            lobFD = self._lobFDPool.get(tName)
            lobFN = getattr(lobFD, 'name', None)
            if lobFN:
                lobFN = os.path.basename(lobFN)
        else:
            tFD = open(os.path.join(CSV_DIR, tName + self.csvExt), 'wb')
            self._fdPool[tName] = tFD
            if doLOB:
                lobFN = '%s.lob' % tName
                lobFD = open(os.path.join(CSV_DIR, lobFN), 'wb')
                self._lobFDPool[tName] = lobFD
        buildLine = self.buildLine
        tableToAddID = False
        if tName in ('cast_info', 'movie_info', 'person_info',
                    'movie_companies', 'movie_link', 'aka_name',
                    'complete_cast', 'movie_info_idx', 'movie_keyword'):
            tableToAddID = tName
            if tName not in self._counters:
                self._counters[tName] = 1
        # Identify if there are RawValue in the VALUES (...) portion of
        # the query.
        parIdx = sqlstr.rfind('(')
        rawValues = []
        vals = sqlstr[parIdx+1:-1]
        if parIdx != 0:
            vals = sqlstr[parIdx+1:-1]
            for idx, item in enumerate(vals.split(', ')):
                if item[0] in ('%', '?', ':'):
                    continue
                rawValues.append((idx, item))
        # Write these lines.
        tFD.writelines(buildLine(i, tableToAddID=tableToAddID,
                        rawValues=rawValues, lobFD=lobFD, lobFN=lobFN)
                        for i in items)
        # Flush to disk, so that no truncaded entries are ever left.
        # XXX: is this a good idea?
        tFD.flush()

    def fileNames(self):
        """Return the list of file names."""
        return [fd.name for fd in self._fdPool.values()]

    def buildFakeFileNames(self):
        """Populate the self._fdPool dictionary with fake objects
        taking file names from the content of the self.csvDir directory."""
        class _FakeFD(object): pass
        for fname in os.listdir(self.csvDir):
            if not fname.endswith(CSV_EXT):
                continue
            fpath = os.path.join(self.csvDir, fname)
            if not os.path.isfile(fpath):
                continue
            fd = _FakeFD()
            fd.name = fname
            self._fdPool[fname[:-len(CSV_EXT)]] = fd

    def close(self, tName):
        """Close a given table/file."""
        if tName in self._fdPool:
            self._fdPool[tName].close()

    def closeAll(self):
        """Close all open file descriptors."""
        for fd in self._fdPool.values():
            fd.close()
        for fd in self._lobFDPool.values():
            fd.close()


def loadCSVFiles():
    """Load every CSV file into the database."""
    CSV_REPL = {'quote': CSV_QUOTE, 'delimiter': CSV_DELIMITER,
                'escape': CSV_ESCAPE, 'null': CSV_NULL, 'eol': CSV_EOL}
    for fName in CSV_CURS.fileNames():
        connectObject.commit()
        tName = os.path.basename(fName[:-len(CSV_EXT)])
        cfName = os.path.join(CSV_DIR, fName)
        CSV_REPL['file'] = cfName
        CSV_REPL['table'] = tName
        sqlStr = CSV_LOAD_SQL % CSV_REPL
        print ' * LOADING CSV FILE %s...' % cfName
        sys.stdout.flush()
        executeCustomQueries('BEFORE_CSV_TODB')
        try:
            CURS.execute(sqlStr)
            try:
                res = CURS.fetchall()
                if res:
                    print 'LOADING OUTPUT:', res
            except:
                pass
        except Exception, e:
            print 'ERROR: unable to import CSV file %s: %s' % (cfName, str(e))
            continue
        connectObject.commit()
        executeCustomQueries('AFTER_CSV_TODB')

#-----------------------


conn = setConnection(URI, DB_TABLES)
if CSV_DIR:
    # Go for a CSV ride...
    CSV_CURS = CSVCursor(CSV_DIR)

# Extract exceptions to trap.
try:
    OperationalError = conn.module.OperationalError
except AttributeError, e:
    warnings.warn('Unable to import OperationalError; report this as a bug, ' \
            'since it will mask important exceptions: %s' % e)
    OperationalError = Exception
try:
    IntegrityError = conn.module.IntegrityError
except AttributeError, e:
    warnings.warn('Unable to import IntegrityError')
    IntegrityError = Exception

connectObject = conn.getConnection()
# XXX: fix for a problem that should be fixed in objectadapter.py (see it).
if URI and URI.startswith('sqlite') and USED_ORM == 'sqlobject':
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if major > 2 or (major == 2 and minor > 5):
        connectObject.text_factory = str

# Cursor object.
CURS = connectObject.cursor()

# Name of the database and style of the parameters.
DB_NAME = conn.dbName
PARAM_STYLE = conn.paramstyle


def _get_imdbids_method():
    """Return the method to be used to (re)store
    imdbIDs (one of 'dbm' or 'table')."""
    if IMDBIDS_METHOD:
        return IMDBIDS_METHOD
    if CSV_DIR:
        return 'dbm'
    return 'table'


def tableName(table):
    """Return a string with the name of the table in the current db."""
    return table.sqlmeta.table

def colName(table, column):
    """Return a string with the name of the column in the current db."""
    if column == 'id':
        return table.sqlmeta.idName
    return table.sqlmeta.columns[column].dbName


class RawValue(object):
    """String-like objects to store raw SQL parameters, that are not
    intended to be replaced with positional parameters, in the query."""
    def __init__(self, s, v):
        self.string = s
        self.value = v
    def __str__(self):
        return self.string


def _makeConvNamed(cols):
    """Return a function to be used to convert a list of parameters
    from positional style to named style (convert from a list of
    tuples to a list of dictionaries."""
    nrCols = len(cols)
    def _converter(params):
        for paramIndex, paramSet in enumerate(params):
            d = {}
            for i in xrange(nrCols):
                d[cols[i]] = paramSet[i]
            params[paramIndex] = d
        return params
    return _converter

def createSQLstr(table, cols, command='INSERT'):
    """Given a table and a list of columns returns a sql statement
    useful to insert a set of data in the database.
    Along with the string, also a function useful to convert parameters
    from positional to named style is returned."""
    sqlstr = '%s INTO %s ' % (command, tableName(table))
    colNames = []
    values = []
    convCols = []
    count = 1
    def _valStr(s, index):
        if DB_NAME in ('mysql', 'postgres'): return '%s'
        elif PARAM_STYLE == 'format': return '%s'
        elif PARAM_STYLE == 'qmark': return '?'
        elif PARAM_STYLE == 'numeric': return ':%s' % index
        elif PARAM_STYLE == 'named': return ':%s' % s
        elif PARAM_STYLE == 'pyformat': return '%(' + s + ')s'
        return '%s'
    for col in cols:
        if isinstance(col, RawValue):
            colNames.append(colName(table, col.string))
            values.append(str(col.value))
        elif col == 'id':
            colNames.append(table.sqlmeta.idName)
            values.append(_valStr('id', count))
            convCols.append(col)
            count += 1
        else:
            colNames.append(colName(table, col))
            values.append(_valStr(col, count))
            convCols.append(col)
            count += 1
    sqlstr += '(%s) ' % ', '.join(colNames)
    sqlstr += 'VALUES (%s)' % ', '.join(values)
    if DB_NAME not in ('mysql', 'postgres') and \
            PARAM_STYLE in ('named', 'pyformat'):
        converter = _makeConvNamed(convCols)
    else:
        # Return the list itself.
        converter = lambda x: x
    return sqlstr, converter

def _(s, truncateAt=None):
    """Nicely print a string to sys.stdout, optionally
    truncating it a the given char."""
    if not isinstance(s, UnicodeType):
        s = unicode(s, 'utf_8')
    if truncateAt is not None:
        s = s[:truncateAt]
    s = s.encode(sys.stdout.encoding or 'utf_8', 'replace')
    return s

if not hasattr(os, 'times'):
    def times():
        """Fake times() function."""
        return (0.0, 0.0, 0.0, 0.0, 0.0)
    os.times = times

# Show time consumed by the single function call.
CTIME = int(time.time())
BEGIN_TIME = CTIME
CTIMES = os.times()
BEGIN_TIMES = CTIMES

def _minSec(*t):
    """Return a tuple of (mins, secs, ...) - two for every item passed."""
    l = []
    for i in t:
        l.extend(divmod(int(i), 60))
    return tuple(l)

def t(s, sinceBegin=False):
    """Pretty-print timing information."""
    global CTIME, CTIMES
    nt = int(time.time())
    ntimes = os.times()
    if not sinceBegin:
        ct = CTIME
        cts = CTIMES
    else:
        ct = BEGIN_TIME
        cts = BEGIN_TIMES
    print '# TIME', s, \
            ': %dmin, %dsec (wall) %dmin, %dsec (user) %dmin, %dsec (system)' \
            % _minSec(nt-ct, ntimes[0]-cts[0], ntimes[1]-cts[1])
    if not sinceBegin:
        CTIME = nt
        CTIMES = ntimes

def title_soundex(title):
    """Return the soundex code for the given title; the (optional) starting
    article is pruned.  It assumes to receive a title without year/imdbIndex
    or kind indications, but just the title string, as the one in the
    analyze_title(title)['title'] value."""
    if not title: return None
    # Convert to canonical format.
    title = canonicalTitle(title)
    ts = title.split(', ')
    # Strip the ending article, if any.
    if ts[-1].lower() in _articles:
        title = ', '.join(ts[:-1])
    return soundex(title)

def name_soundexes(name, character=False):
    """Return three soundex codes for the given name; the name is assumed
    to be in the 'surname, name' format, without the imdbIndex indication,
    as the one in the analyze_name(name)['name'] value.
    The first one is the soundex of the name in the canonical format.
    The second is the soundex of the name in the normal format, if different
    from the first one.
    The third is the soundex of the surname, if different from the
    other two values."""
    ##if not isinstance(name, unicode): name = unicode(name, 'utf_8')
    # Prune non-ascii chars from the string.
    ##name = name.encode('ascii', 'ignore')
    if not name: return (None, None, None)
    s1 = soundex(name)
    name_normal = normalizeName(name)
    s2 = soundex(name_normal)
    if s1 == s2: s2 = None
    if not character:
        namesplit = name.split(', ')
        s3 = soundex(namesplit[0])
    else:
        s3 = soundex(name.split(' ')[-1])
    if s3 and s3 in (s1, s2): s3 = None
    return (s1, s2, s3)


# Tags to identify where the meaningful data begin/end in files.
MOVIES = 'movies.list.gz'
MOVIES_START = ('MOVIES LIST', '===========', '')
MOVIES_STOP = '--------------------------------------------------'
CAST_START = ('Name', '----')
CAST_STOP = '-----------------------------'
RAT_START = ('MOVIE RATINGS REPORT', '',
            'New  Distribution  Votes  Rank  Title')
RAT_STOP = '\n'
RAT_TOP250_START = ('note: for this top 250', '', 'New  Distribution')
RAT_BOT10_START = ('BOTTOM 10 MOVIES', '', 'New  Distribution')
TOPBOT_STOP = '\n'
AKAT_START = ('AKA TITLES LIST', '=============', '', '', '')
AKAT_IT_START = ('AKA TITLES LIST ITALIAN', '=======================', '', '')
AKAT_DE_START = ('AKA TITLES LIST GERMAN', '======================', '')
AKAT_ISO_START = ('AKA TITLES LIST ISO', '===================', '')
AKAT_HU_START = ('AKA TITLES LIST HUNGARIAN', '=========================', '')
AKAT_NO_START = ('AKA TITLES LIST NORWEGIAN', '=========================', '')
AKAN_START = ('AKA NAMES LIST', '=============', '')
AV_START = ('ALTERNATE VERSIONS LIST', '=======================', '', '')
MINHASH_STOP = '-------------------------'
GOOFS_START = ('GOOFS LIST', '==========', '')
QUOTES_START = ('QUOTES LIST', '=============')
CC_START = ('CRAZY CREDITS', '=============')
BIO_START = ('BIOGRAPHY LIST', '==============')
BUS_START = ('BUSINESS LIST', '=============', '')
BUS_STOP = '                                    ====='
CER_START = ('CERTIFICATES LIST', '=================')
COL_START = ('COLOR INFO LIST', '===============')
COU_START = ('COUNTRIES LIST', '==============')
DIS_START = ('DISTRIBUTORS LIST', '=================', '')
GEN_START = ('8: THE GENRES LIST', '==================', '')
KEY_START = ('8: THE KEYWORDS LIST', '====================', '')
LAN_START = ('LANGUAGE LIST', '=============')
LOC_START = ('LOCATIONS LIST', '==============', '')
MIS_START = ('MISCELLANEOUS COMPANY LIST', '============================')
MIS_STOP = '--------------------------------------------------------------------------------'
PRO_START = ('PRODUCTION COMPANIES LIST', '=========================', '')
RUN_START = ('RUNNING TIMES LIST', '==================')
SOU_START = ('SOUND-MIX LIST', '==============')
SFX_START = ('SFXCO COMPANIES LIST', '====================', '')
TCN_START = ('TECHNICAL LIST', '==============', '', '')
LSD_START = ('LASERDISC LIST', '==============', '------------------------')
LIT_START = ('LITERATURE LIST', '===============', '')
LIT_STOP = 'COPYING POLICY'
LINK_START = ('MOVIE LINKS LIST', '================', '')
MPAA_START = ('MPAA RATINGS REASONS LIST', '=========================')
PLOT_START = ('PLOT SUMMARIES LIST', '===================', '')
RELDATE_START = ('RELEASE DATES LIST', '==================')
SNDT_START = ('SOUNDTRACKS', '=============', '', '', '')
TAGL_START = ('TAG LINES LIST', '==============', '', '')
TAGL_STOP = '-----------------------------------------'
TRIV_START = ('FILM TRIVIA', '===========', '')
COMPCAST_START = ('CAST COVERAGE TRACKING LIST', '===========================')
COMPCREW_START = ('CREW COVERAGE TRACKING LIST', '===========================')
COMP_STOP = '---------------'

GzipFileRL = GzipFile.readline
class SourceFile(GzipFile):
    """Instances of this class are used to read gzipped files,
    starting from a defined line to a (optionally) given end."""
    def __init__(self, filename=None, mode=None, start=(), stop=None,
                    pwarning=1, *args, **kwds):
        filename = os.path.join(IMDB_PTDF_DIR, filename)
        try:
            GzipFile.__init__(self, filename, mode, *args, **kwds)
        except IOError, e:
            if not pwarning: raise
            print 'WARNING WARNING WARNING'
            print 'WARNING unable to read the "%s" file.' % filename
            print 'WARNING The file will be skipped, and the contained'
            print 'WARNING information will NOT be stored in the database.'
            print 'WARNING Complete error: ', e
            # re-raise the exception.
            raise
        self.start = start
        for item in start:
            itemlen = len(item)
            for line in self:
                if line[:itemlen] == item: break
        self.set_stop(stop)

    def set_stop(self, stop):
        if stop is not None:
            self.stop = stop
            self.stoplen = len(self.stop)
            self.readline = self.readline_checkEnd
        else:
            self.readline = self.readline_NOcheckEnd

    def readline_NOcheckEnd(self, size=-1):
        line = GzipFile.readline(self, size)
        return unicode(line, 'latin_1').encode('utf_8')

    def readline_checkEnd(self, size=-1):
        line = GzipFile.readline(self, size)
        if self.stop is not None and line[:self.stoplen] == self.stop: return ''
        return unicode(line, 'latin_1').encode('utf_8')

    def getByHashSections(self):
        return getSectionHash(self)

    def getByNMMVSections(self):
        return getSectionNMMV(self)


def getSectionHash(fp):
    """Return sections separated by lines starting with #."""
    curSectList = []
    curSectListApp = curSectList.append
    curTitle = ''
    joiner = ''.join
    for line in fp:
        if line and line[0] == '#':
            if curSectList and curTitle:
                yield curTitle, joiner(curSectList)
                curSectList[:] = []
                curTitle = ''
            curTitle = line[2:]
        else: curSectListApp(line)
    if curSectList and curTitle:
        yield curTitle, joiner(curSectList)
        curSectList[:] = []
        curTitle = ''

NMMVSections = dict([(x, None) for x in ('MV: ', 'NM: ', 'OT: ', 'MOVI')])
def getSectionNMMV(fp):
    """Return sections separated by lines starting with 'NM: ', 'MV: ',
    'OT: ' or 'MOVI'."""
    curSectList = []
    curSectListApp = curSectList.append
    curNMMV = ''
    joiner = ''.join
    for line in fp:
        if line[:4] in NMMVSections:
            if curSectList and curNMMV:
                yield curNMMV, joiner(curSectList)
                curSectList[:] = []
                curNMMV = ''
            if line[:4] == 'MOVI': curNMMV = line[6:]
            else: curNMMV = line[4:]
        elif not (line and line[0] == '-'): curSectListApp(line)
    if curSectList and curNMMV:
        yield curNMMV, joiner(curSectList)
        curSectList[:] = []
        curNMMV = ''

def counter(initValue=1):
    """A counter implemented using a generator."""
    i = initValue
    while 1:
        yield i
        i += 1

class _BaseCache(dict):
    """Base class for Movie and Person basic information."""
    def __init__(self, d=None, flushEvery=100000):
        dict.__init__(self)
        # Flush data into the SQL database every flushEvery entries.
        self.flushEvery = flushEvery
        self._tmpDict = {}
        self._flushing = 0
        self._deferredData = {}
        self._recursionLevel = 0
        self._table_name = ''
        self._id_for_custom_q = ''
        if d is not None:
            for k, v in d.iteritems(): self[k] = v

    def __setitem__(self, key, counter):
        """Every time a key is set, its value is the counter;
        every flushEvery, the temporary dictionary is
        flushed to the database, and then zeroed."""
        if counter % self.flushEvery == 0:
            self.flush()
        dict.__setitem__(self, key, counter)
        if not self._flushing:
            self._tmpDict[key] = counter
        else:
            self._deferredData[key] = counter

    def flush(self, quiet=0, _recursionLevel=0):
        """Flush to the database."""
        if self._flushing: return
        self._flushing = 1
        if _recursionLevel >= MAX_RECURSION:
            print 'WARNING recursion level exceded trying to flush data'
            print 'WARNING this batch of data is lost (%s).' % self.className
            self._tmpDict.clear()
            return
        if self._tmpDict:
            # Horrible hack to know if AFTER_%s_TODB has run.
            _after_has_run = False
            keys = {'table': self._table_name}
            try:
                executeCustomQueries('BEFORE_%s_TODB' % self._id_for_custom_q,
                                    _keys=keys, _timeit=False)
                self._toDB(quiet)
                executeCustomQueries('AFTER_%s_TODB' % self._id_for_custom_q,
                                    _keys=keys, _timeit=False)
                _after_has_run = True
                self._tmpDict.clear()
            except OperationalError, e:
                # XXX: I'm not sure this is the right thing (and way)
                #      to proceed.
                if not _after_has_run:
                    executeCustomQueries('AFTER_%s_TODB'%self._id_for_custom_q,
                                        _keys=keys, _timeit=False)
                # Dataset too large; split it in two and retry.
                # XXX: new code!
                # the same class instance (self) is used, instead of
                # creating two separated objects.
                _recursionLevel += 1
                self._flushing = 0
                firstHalf = {}
                poptmpd = self._tmpDict.popitem
                originalLength = len(self._tmpDict)
                for x in xrange(1, 1 + originalLength/2):
                    k, v = poptmpd()
                    firstHalf[k] = v
                self._secondHalf = self._tmpDict
                self._tmpDict = firstHalf
                print ' * TOO MANY DATA (%s items in %s), recursion: %s' % \
                                                        (originalLength,
                                                        self.className,
                                                        _recursionLevel)
                print '   * SPLITTING (run 1 of 2), recursion: %s' % \
                                                        _recursionLevel
                self.flush(quiet=quiet, _recursionLevel=_recursionLevel)
                self._tmpDict = self._secondHalf
                print '   * SPLITTING (run 2 of 2), recursion: %s' % \
                                                        _recursionLevel
                self.flush(quiet=quiet, _recursionLevel=_recursionLevel)
                self._tmpDict.clear()
            except Exception, e:
                if isinstance(e, KeyboardInterrupt):
                    raise
                print 'WARNING: unknown exception caught committing the data'
                print 'WARNING: to the database; report this as a bug, since'
                print 'WARNING: many data (%d items) were lost: %s' % \
                        (len(self._tmpDict), e)
        self._flushing = 0
        # Flush also deferred data.
        if self._deferredData:
            self._tmpDict = self._deferredData
            self.flush(quiet=1)
            self._deferredData = {}
        connectObject.commit()

    def populate(self):
        """Populate the dictionary from the database."""
        raise NotImplementedError

    def _toDB(self, quiet=0):
        """Write the dictionary to the database."""
        raise NotImplementedError

    def add(self, key, miscData=None):
        """Insert a new key and return its value."""
        c = self.counter.next()
        # miscData=[('a_dict', 'value')] will set self.a_dict's c key
        # to 'value'.
        if miscData is not None:
            for d_name, data in miscData:
                getattr(self, d_name)[c] = data
        self[key] = c
        return c

    def addUnique(self, key, miscData=None):
        """Insert a new key and return its value; if the key is already
        in the dictionary, its previous  value is returned."""
        if key in self: return self[key]
        else: return self.add(key, miscData)


def fetchsome(curs, size=20000):
    """Yes, I've read the Python Cookbook! :-)"""
    while 1:
        res = curs.fetchmany(size)
        if not res: break
        for r in res: yield r


class MoviesCache(_BaseCache):
    """Manage the movies list."""
    className = 'MoviesCache'
    counter = counter()

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self.movieYear = {}
        self._table_name = tableName(Title)
        self._id_for_custom_q = 'MOVIES'
        self.sqlstr, self.converter = createSQLstr(Title, ('id', 'title',
                                    'imdbIndex', 'kindID', 'productionYear',
                                    'imdbID', 'phoneticCode', 'episodeOfID',
                                    'seasonNr', 'episodeNr', 'seriesYears',
                                    'md5sum'))

    def populate(self):
        print ' * POPULATING %s...' % self.className
        titleTbl = tableName(Title)
        movieidCol = colName(Title, 'id')
        titleCol = colName(Title, 'title')
        kindidCol = colName(Title, 'kindID')
        yearCol = colName(Title, 'productionYear')
        imdbindexCol = colName(Title, 'imdbIndex')
        episodeofidCol = colName(Title, 'episodeOfID')
        seasonNrCol = colName(Title, 'seasonNr')
        episodeNrCol = colName(Title, 'episodeNr')
        sqlPop = 'SELECT %s, %s, %s, %s, %s, %s, %s, %s FROM %s;' % \
                (movieidCol, titleCol, kindidCol, yearCol, imdbindexCol,
                episodeofidCol, seasonNrCol, episodeNrCol, titleTbl)
        CURS.execute(sqlPop)
        _oldcacheValues = Title.sqlmeta.cacheValues
        Title.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            mdict = {'title': x[1], 'kind': KIND_STRS[x[2]],
                    'year': x[3], 'imdbIndex': x[4]}
            if mdict['imdbIndex'] is None: del mdict['imdbIndex']
            if mdict['year'] is None: del mdict['year']
            else: mdict['year'] = str(mdict['year'])
            episodeOfID = x[5]
            if episodeOfID is not None:
                s = Title.get(episodeOfID)
                series_d = {'title': s.title,
                            'kind': str(KIND_STRS[s.kindID]),
                            'year': s.productionYear, 'imdbIndex': s.imdbIndex}
                if series_d['imdbIndex'] is None: del series_d['imdbIndex']
                if series_d['year'] is None: del series_d['year']
                else: series_d['year'] = str(series_d['year'])
                mdict['episode of'] = series_d
            title = build_title(mdict, ptdf=1, _emptyString='')
            dict.__setitem__(self, title, x[0])
        self.counter = counter(Title.select().count() + 1)
        Title.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print ' * FLUSHING %s...' % self.className
            sys.stdout.flush()
        l = []
        lapp = l.append
        tmpDictiter = self._tmpDict.iteritems
        for k, v in tmpDictiter():
            try:
                t = analyze_title(k, _emptyString='')
            except IMDbParserError:
                if k and k.strip():
                    print 'WARNING %s._toDB() invalid title:' % self.className,
                    print _(k)
                continue
            tget = t.get
            episodeOf = None
            kind = tget('kind')
            if kind == 'episode':
                # Series title.
                stitle = build_title(tget('episode of'), _emptyString='', ptdf=1)
                episodeOf = self.addUnique(stitle)
                del t['episode of']
                year = self.movieYear.get(v)
                if year is not None and year != '????':
                    try: t['year'] = int(year)
                    except ValueError: pass
            elif kind in ('tv series', 'tv mini series'):
                t['series years'] = self.movieYear.get(v)
            title = tget('title')
            soundex = title_soundex(title)
            lapp((v, title, tget('imdbIndex'), KIND_IDS[kind],
                    tget('year'), None, soundex, episodeOf,
                    tget('season'), tget('episode'), tget('series years'),
                    md5(k).hexdigest()))
        self._runCommand(l)

    def _runCommand(self, dataList):
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(dataList))
        else:
            CSV_CURS.executemany(self.sqlstr, dataList)

    def addUnique(self, key, miscData=None):
        """Insert a new key and return its value; if the key is already
        in the dictionary, its previous  value is returned."""
        if key.endswith('{{SUSPENDED}}'):
            return None
        # DONE: to be removed when it will be no more needed!
        #if FIX_OLD_STYLE_TITLES:
        #    key = build_title(analyze_title(key, canonical=False,
        #                    _emptyString=''), ptdf=1, _emptyString='')
        if key in self: return self[key]
        else: return self.add(key, miscData)


class PersonsCache(_BaseCache):
    """Manage the persons list."""
    className = 'PersonsCache'
    counter = counter()

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self.personGender = {}
        self._table_name = tableName(Name)
        self._id_for_custom_q = 'PERSONS'
        self.sqlstr, self.converter = createSQLstr(Name, ['id', 'name',
                                'imdbIndex', 'imdbID', 'gender', 'namePcodeCf',
                                'namePcodeNf', 'surnamePcode', 'md5sum'])

    def populate(self):
        print ' * POPULATING PersonsCache...'
        nameTbl = tableName(Name)
        personidCol = colName(Name, 'id')
        nameCol = colName(Name, 'name')
        imdbindexCol = colName(Name, 'imdbIndex')
        CURS.execute('SELECT %s, %s, %s FROM %s;' % (personidCol, nameCol,
                                                    imdbindexCol, nameTbl))
        _oldcacheValues = Name.sqlmeta.cacheValues
        Name.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            nd = {'name': x[1]}
            if x[2]: nd['imdbIndex'] = x[2]
            name = build_name(nd)
            dict.__setitem__(self, name, x[0])
        self.counter = counter(Name.select().count() + 1)
        Name.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print ' * FLUSHING PersonsCache...'
            sys.stdout.flush()
        l = []
        lapp = l.append
        tmpDictiter = self._tmpDict.iteritems
        for k, v in tmpDictiter():
            try:
                t = analyze_name(k)
            except IMDbParserError:
                if k and k.strip():
                    print 'WARNING PersonsCache._toDB() invalid name:', _(k)
                continue
            tget = t.get
            name = tget('name')
            namePcodeCf, namePcodeNf, surnamePcode = name_soundexes(name)
            gender = self.personGender.get(v)
            lapp((v, name, tget('imdbIndex'), None, gender,
                namePcodeCf, namePcodeNf, surnamePcode,
                md5(k).hexdigest()))
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(l))
        else:
            CSV_CURS.executemany(self.sqlstr, l)


class CharactersCache(_BaseCache):
    """Manage the characters list."""
    counter = counter()
    className = 'CharactersCache'

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self._table_name = tableName(CharName)
        self._id_for_custom_q = 'CHARACTERS'
        self.sqlstr, self.converter = createSQLstr(CharName, ['id', 'name',
                                'imdbIndex', 'imdbID', 'namePcodeNf',
                                'surnamePcode', 'md5sum'])

    def populate(self):
        print ' * POPULATING CharactersCache...'
        nameTbl = tableName(CharName)
        personidCol = colName(CharName, 'id')
        nameCol = colName(CharName, 'name')
        imdbindexCol = colName(CharName, 'imdbIndex')
        CURS.execute('SELECT %s, %s, %s FROM %s;' % (personidCol, nameCol,
                                                    imdbindexCol, nameTbl))
        _oldcacheValues = CharName.sqlmeta.cacheValues
        CharName.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            nd = {'name': x[1]}
            if x[2]: nd['imdbIndex'] = x[2]
            name = build_name(nd)
            dict.__setitem__(self, name, x[0])
        self.counter = counter(CharName.select().count() + 1)
        CharName.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print ' * FLUSHING CharactersCache...'
            sys.stdout.flush()
        l = []
        lapp = l.append
        tmpDictiter = self._tmpDict.iteritems
        for k, v in tmpDictiter():
            try:
                t = analyze_name(k)
            except IMDbParserError:
                if k and k.strip():
                    print 'WARNING CharactersCache._toDB() invalid name:', _(k)
                continue
            tget = t.get
            name = tget('name')
            namePcodeCf, namePcodeNf, surnamePcode = name_soundexes(name,
                                                                character=True)
            lapp((v, name, tget('imdbIndex'), None,
                namePcodeCf, surnamePcode, md5(k).hexdigest()))
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(l))
        else:
            CSV_CURS.executemany(self.sqlstr, l)


class CompaniesCache(_BaseCache):
    """Manage the companies list."""
    counter = counter()
    className = 'CompaniesCache'

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self._table_name = tableName(CompanyName)
        self._id_for_custom_q = 'COMPANIES'
        self.sqlstr, self.converter = createSQLstr(CompanyName, ['id', 'name',
                                'countryCode', 'imdbID', 'namePcodeNf',
                                'namePcodeSf', 'md5sum'])

    def populate(self):
        print ' * POPULATING CharactersCache...'
        nameTbl = tableName(CompanyName)
        companyidCol = colName(CompanyName, 'id')
        nameCol = colName(CompanyName, 'name')
        countryCodeCol = colName(CompanyName, 'countryCode')
        CURS.execute('SELECT %s, %s, %s FROM %s;' % (companyidCol, nameCol,
                                                    countryCodeCol, nameTbl))
        _oldcacheValues = CompanyName.sqlmeta.cacheValues
        CompanyName.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            nd = {'name': x[1]}
            if x[2]: nd['country'] = x[2]
            name = build_company_name(nd)
            dict.__setitem__(self, name, x[0])
        self.counter = counter(CompanyName.select().count() + 1)
        CompanyName.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print ' * FLUSHING CompaniesCache...'
            sys.stdout.flush()
        l = []
        lapp = l.append
        tmpDictiter = self._tmpDict.iteritems
        for k, v in tmpDictiter():
            try:
                t = analyze_company_name(k)
            except IMDbParserError:
                if k and k.strip():
                    print 'WARNING CompaniesCache._toDB() invalid name:', _(k)
                continue
            tget = t.get
            name = tget('name')
            namePcodeNf = soundex(name)
            namePcodeSf = None
            country = tget('country')
            if k != name:
                namePcodeSf = soundex(k)
            lapp((v, name, country, None, namePcodeNf, namePcodeSf,
                    md5(k).hexdigest()))
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(l))
        else:
            CSV_CURS.executemany(self.sqlstr, l)


class KeywordsCache(_BaseCache):
    """Manage the list of keywords."""
    counter = counter()
    className = 'KeywordsCache'

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self._table_name = tableName(CompanyName)
        self._id_for_custom_q = 'KEYWORDS'
        self.flushEvery = 10000
        self.sqlstr, self.converter = createSQLstr(Keyword, ['id', 'keyword',
                                'phoneticCode'])

    def populate(self):
        print ' * POPULATING KeywordsCache...'
        nameTbl = tableName(CompanyName)
        keywordidCol = colName(Keyword, 'id')
        keyCol = colName(Keyword, 'name')
        CURS.execute('SELECT %s, %s FROM %s;' % (keywordidCol, keyCol,
                                                    nameTbl))
        _oldcacheValues = Keyword.sqlmeta.cacheValues
        Keyword.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            dict.__setitem__(self, x[1], x[0])
        self.counter = counter(Keyword.select().count() + 1)
        Keyword.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print ' * FLUSHING KeywordsCache...'
            sys.stdout.flush()
        l = []
        lapp = l.append
        tmpDictiter = self._tmpDict.iteritems
        for k, v in tmpDictiter():
            keySoundex = soundex(k)
            lapp((v, k, keySoundex))
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(l))
        else:
            CSV_CURS.executemany(self.sqlstr, l)


class SQLData(dict):
    """Variable set of information, to be stored from time to time
    to the SQL database."""
    def __init__(self, table=None, cols=None, sqlString='', converter=None,
                d={}, flushEvery=20000, counterInit=1):
        if not sqlString:
            if not (table and cols):
                raise TypeError('"table" or "cols" unspecified')
            sqlString, converter = createSQLstr(table, cols)
        elif converter is None:
            raise TypeError('"sqlString" or "converter" unspecified')
        dict.__init__(self)
        self.counterInit = counterInit
        self.counter = counterInit
        self.flushEvery = flushEvery
        self.sqlString = sqlString
        self.converter = converter
        self._recursionLevel = 1
        self._table = table
        self._table_name = tableName(table)
        for k, v in d.items(): self[k] = v

    def __setitem__(self, key, value):
        """The value is discarded, the counter is used as the 'real' key
        and the user's 'key' is used as its values."""
        counter = self.counter
        if counter % self.flushEvery == 0:
            self.flush()
        dict.__setitem__(self, counter, key)
        self.counter += 1

    def add(self, key):
        self[key] = None

    def flush(self, _resetRecursion=1):
        if not self: return
        # XXX: it's safer to flush MoviesCache and PersonsCache, to preserve
        #      consistency of ForeignKey, but it can also slow down everything
        #      a bit...
        CACHE_MID.flush(quiet=1)
        CACHE_PID.flush(quiet=1)
        if _resetRecursion: self._recursionLevel = 1
        if self._recursionLevel >= MAX_RECURSION:
            print 'WARNING recursion level exceded trying to flush data'
            print 'WARNING this batch of data is lost.'
            self.clear()
            self.counter = self.counterInit
            return
        keys = {'table': self._table_name}
        _after_has_run = False
        try:
            executeCustomQueries('BEFORE_SQLDATA_TODB', _keys=keys,
                                _timeit=False)
            self._toDB()
            executeCustomQueries('AFTER_SQLDATA_TODB', _keys=keys,
                                _timeit=False)
            _after_has_run = True
            self.clear()
            self.counter = self.counterInit
        except OperationalError, e:
            if not _after_has_run:
                executeCustomQueries('AFTER_SQLDATA_TODB', _keys=keys,
                                    _timeit=False)
            print ' * TOO MANY DATA (%s items), SPLITTING (run #%d)...' % \
                    (len(self), self._recursionLevel)
            self._recursionLevel += 1
            newdata = self.__class__(table=self._table,
                                    sqlString=self.sqlString,
                                    converter=self.converter)
            newdata._recursionLevel = self._recursionLevel
            newflushEvery = self.flushEvery / 2
            if newflushEvery < 1:
                print 'WARNING recursion level exceded trying to flush data'
                print 'WARNING this batch of data is lost.'
                self.clear()
                self.counter = self.counterInit
                return
            self.flushEvery = newflushEvery
            newdata.flushEvery = newflushEvery
            popitem = self.popitem
            dsi = dict.__setitem__
            for x in xrange(len(self)/2):
                k, v = popitem()
                dsi(newdata, k, v)
            newdata.flush(_resetRecursion=0)
            del newdata
            self.flush(_resetRecursion=0)
            self.clear()
            self.counter = self.counterInit
        except Exception, e:
            if isinstance(e, KeyboardInterrupt):
                raise
            print 'WARNING: unknown exception caught committing the data'
            print 'WARNING: to the database; report this as a bug, since'
            print 'WARNING: many data (%d items) were lost: %s' % \
                    (len(self), e)
        connectObject.commit()

    def _toDB(self):
        print ' * FLUSHING SQLData...'
        if not CSV_DIR:
            CURS.executemany(self.sqlString, self.converter(self.values()))
        else:
            CSV_CURS.executemany(self.sqlString, self.values())


# Miscellaneous functions.

def unpack(line, headers, sep='\t'):
    """Given a line, split at seps and return a dictionary with key
    from the header list.
    E.g.:
        line = '      0000000124    8805   8.4  Incredibles, The (2004)'
        header = ('votes distribution', 'votes', 'rating', 'title')
        seps=('  ',)

    will returns: {'votes distribution': '0000000124', 'votes': '8805',
                    'rating': '8.4', 'title': 'Incredibles, The (2004)'}
    """
    r = {}
    ls1 = filter(None, line.split(sep))
    for index, item in enumerate(ls1):
        try: name = headers[index]
        except IndexError: name = 'item%s' % index
        r[name] = item.strip()
    return r

def _parseMinusList(fdata):
    """Parse a list of lines starting with '- '."""
    rlist = []
    tmplist = []
    for line in fdata:
        if line and line[:2] == '- ':
            if tmplist: rlist.append(' '.join(tmplist))
            l = line[2:].strip()
            if l: tmplist[:] = [l]
            else: tmplist[:] = []
        else:
            l = line.strip()
            if l: tmplist.append(l)
    if tmplist: rlist.append(' '.join(tmplist))
    return rlist


def _parseColonList(lines, replaceKeys):
    """Parser for lists with "TAG: value" strings."""
    out = {}
    for line in lines:
        line = line.strip()
        if not line: continue
        cols = line.split(':', 1)
        if len(cols) < 2: continue
        k = cols[0]
        k = replaceKeys.get(k, k)
        v = ' '.join(cols[1:]).strip()
        if k not in out: out[k] = []
        out[k].append(v)
    return out


# Functions used to manage data files.

def readMovieList():
    """Read the movies.list.gz file."""
    try: mdbf = SourceFile(MOVIES, start=MOVIES_START, stop=MOVIES_STOP)
    except IOError: return
    count = 0
    for line in mdbf:
        line_d = unpack(line, ('title', 'year'))
        title = line_d['title']
        yearData = None
        # Collect 'year' column for tv "series years" and episodes' year.
        if title[0] == '"':
            yearData = [('movieYear', line_d['year'])]
        mid = CACHE_MID.addUnique(title, yearData)
        if mid is None:
            continue
        if count % 10000 == 0:
            print 'SCANNING movies:', _(title),
            print '(movieID: %s)' % mid
        count += 1
    CACHE_MID.flush()
    CACHE_MID.movieYear.clear()
    mdbf.close()


def doCast(fp, roleid, rolename):
    """Populate the cast table."""
    pid = None
    count = 0
    name = ''
    roleidVal = RawValue('roleID', roleid)
    sqldata = SQLData(table=CastInfo, cols=['personID', 'movieID',
                        'personRoleID', 'note', 'nrOrder', roleidVal])
    if rolename == 'miscellaneous crew': sqldata.flushEvery = 10000
    for line in fp:
        if line and line[0] != '\t':
            if line[0] == '\n': continue
            sl = filter(None, line.split('\t'))
            if len(sl) != 2: continue
            name, line = sl
            miscData = None
            if rolename == 'actor':
                miscData = [('personGender', 'm')]
            elif rolename == 'actress':
                miscData = [('personGender', 'f')]
            pid = CACHE_PID.addUnique(name.strip(), miscData)
        line = line.strip()
        ll = line.split('  ')
        title = ll[0]
        note = None
        role = None
        order = None
        for item in ll[1:]:
            if not item: continue
            if item[0] == '[':
                # Quite inefficient, but there are some very strange
                # cases of garbage in the plain text data files to handle...
                role = item[1:]
                if role[-1:] == ']':
                    role = role[:-1]
                if role[-1:] == ')':
                    nidx = role.find('(')
                    if nidx != -1:
                        note = role[nidx:]
                        role = role[:nidx].rstrip()
                        if not role: role = None
            elif item[0] == '(':
                if note is None:
                    note = item
                else:
                    note = '%s %s' % (note, item)
            elif item[0] == '<':
                textor = item[1:-1]
                try:
                    order = long(textor)
                except ValueError:
                    os = textor.split(',')
                    if len(os) == 3:
                        try:
                            order = ((long(os[2])-1) * 1000) + \
                                    ((long(os[1])-1) * 100) + (long(os[0])-1)
                        except ValueError:
                            pass
        movieid = CACHE_MID.addUnique(title)
        if movieid is None:
            continue
        if role is not None:
            roles = filter(None, [x.strip() for x in role.split('/')])
            for role in roles:
                cid = CACHE_CID.addUnique(role)
                sqldata.add((pid, movieid, cid, note, order))
        else:
            sqldata.add((pid, movieid, None, note, order))
        if count % 10000 == 0:
            print 'SCANNING %s:' % rolename,
            print _(name)
        count += 1
    sqldata.flush()
    CACHE_PID.flush()
    CACHE_PID.personGender.clear()
    print 'CLOSING %s...' % rolename


def castLists():
    """Read files listed in the 'role' column of the 'roletypes' table."""
    rt = [(x.id, x.role) for x in RoleType.select()]
    for roleid, rolename in rt:
        if rolename == 'guest':
            continue
        fname = rolename
        fname = fname.replace(' ', '-')
        if fname == 'actress': fname = 'actresses.list.gz'
        elif fname == 'miscellaneous-crew': fname = 'miscellaneous.list.gz'
        else: fname = fname + 's.list.gz'
        print 'DOING', fname
        try:
            f = SourceFile(fname, start=CAST_START, stop=CAST_STOP)
        except IOError:
            if rolename == 'actress':
                CACHE_CID.flush()
                if not CSV_DIR:
                    CACHE_CID.clear()
            continue
        doCast(f, roleid, rolename)
        f.close()
        if rolename == 'actress':
            CACHE_CID.flush()
            if not CSV_DIR:
                CACHE_CID.clear()
        t('castLists(%s)' % rolename)


def doAkaNames():
    """People's akas."""
    pid = None
    count = 0
    try: fp = SourceFile('aka-names.list.gz', start=AKAN_START)
    except IOError: return
    sqldata = SQLData(table=AkaName, cols=['personID', 'name', 'imdbIndex',
                            'namePcodeCf', 'namePcodeNf', 'surnamePcode',
                            'md5sum'])
    for line in fp:
        if line and line[0] != ' ':
            if line[0] == '\n': continue
            pid = CACHE_PID.addUnique(line.strip())
        else:
            line = line.strip()
            if line[:5] == '(aka ': line = line[5:]
            if line[-1:] == ')': line = line[:-1]
            try:
                name_dict = analyze_name(line)
            except IMDbParserError:
                if line: print 'WARNING doAkaNames wrong name:', _(line)
                continue
            name = name_dict.get('name')
            namePcodeCf, namePcodeNf, surnamePcode = name_soundexes(name)
            sqldata.add((pid, name, name_dict.get('imdbIndex'),
                        namePcodeCf, namePcodeNf, surnamePcode,
                        md5(line).hexdigest()))
            if count % 10000 == 0:
                print 'SCANNING akanames:', _(line)
            count += 1
    sqldata.flush()
    fp.close()


class AkasMoviesCache(MoviesCache):
    """A MoviesCache-like class used to populate the AkaTitle table."""
    className = 'AkasMoviesCache'
    counter = counter()

    def __init__(self, *args, **kdws):
        MoviesCache.__init__(self, *args, **kdws)
        self.flushEvery = 50000
        self._mapsIDsToTitles = True
        self.notes = {}
        self.ids = {}
        self._table_name = tableName(AkaTitle)
        self._id_for_custom_q = 'AKAMOVIES'
        self.sqlstr, self.converter = createSQLstr(AkaTitle, ('id', 'movieID',
                            'title', 'imdbIndex', 'kindID', 'productionYear',
                            'phoneticCode', 'episodeOfID', 'seasonNr',
                            'episodeNr', 'note', 'md5sum'))

    def flush(self, *args, **kwds):
        # Preserve consistency of ForeignKey.
        CACHE_MID.flush(quiet=1)
        super(AkasMoviesCache, self).flush(*args, **kwds)

    def _runCommand(self, dataList):
        new_dataList = []
        new_dataListapp = new_dataList.append
        while dataList:
            item = list(dataList.pop())
            # Remove the imdbID.
            del item[5]
            # id used to store this entry.
            the_id = item[0]
            # id of the referred title.
            original_title_id = self.ids.get(the_id) or 0
            new_item = [the_id, original_title_id]
            md5sum = item[-1]
            new_item += item[1:-2]
            new_item.append(self.notes.get(the_id))
            new_item.append(md5sum)
            new_dataListapp(tuple(new_item))
        new_dataList.reverse()
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(new_dataList))
        else:
            CSV_CURS.executemany(self.sqlstr, new_dataList)
CACHE_MID_AKAS = AkasMoviesCache()


def doAkaTitles():
    """Movies' akas."""
    mid = None
    count = 0
    for fname, start in (('aka-titles.list.gz',AKAT_START),
                    ('italian-aka-titles.list.gz',AKAT_IT_START),
                    ('german-aka-titles.list.gz',AKAT_DE_START),
                    ('iso-aka-titles.list.gz',AKAT_ISO_START),
                    (os.path.join('contrib','hungarian-aka-titles.list.gz'),
                        AKAT_HU_START),
                    (os.path.join('contrib','norwegian-aka-titles.list.gz'),
                        AKAT_NO_START)):
        incontrib = 0
        pwarning = 1
        # Looks like that the only up-to-date AKA file is aka-titles.
        obsolete = False
        if fname != 'aka-titles.list.gz':
            obsolete = True
        if start in (AKAT_HU_START, AKAT_NO_START):
            pwarning = 0
            incontrib = 1
        try:
            fp = SourceFile(fname, start=start,
                            stop='---------------------------',
                            pwarning=pwarning)
        except IOError:
            continue
        isEpisode = False
        seriesID = None
        doNotAdd = False
        for line in fp:
            if line and line[0] != ' ':
                # Reading the official title.
                doNotAdd = False
                if line[0] == '\n': continue
                line = line.strip()
                if obsolete:
                    try:
                        tonD = analyze_title(line, _emptyString='')
                    except IMDbParserError:
                        if line:
                            print 'WARNING doAkaTitles(obsol O) invalid title:',
                            print _(line)
                        continue
                    tonD['title'] = normalizeTitle(tonD['title'])
                    line = build_title(tonD, ptdf=1, _emptyString='')
                    # Aka information for titles in obsolete files are
                    # added only if the movie already exists in the cache.
                    if line not in CACHE_MID:
                        doNotAdd = True
                        continue
                mid = CACHE_MID.addUnique(line)
                if mid is None:
                    continue
                if line[0] == '"':
                    try:
                        titleDict = analyze_title(line, _emptyString='')
                    except IMDbParserError:
                        if line:
                            print 'WARNING doAkaTitles (O) invalid title:',
                            print _(line)
                        continue
                    if 'episode of' in titleDict:
                        if obsolete:
                            titleDict['episode of']['title'] = \
                                normalizeTitle(titleDict['episode of']['title'])
                        series = build_title(titleDict['episode of'],
                                            ptdf=1, _emptyString='')
                        seriesID = CACHE_MID.addUnique(series)
                        if seriesID is None:
                            continue
                        isEpisode = True
                    else:
                        seriesID = None
                        isEpisode = False
                else:
                    seriesID = None
                    isEpisode = False
            else:
                # Reading an aka title.
                if obsolete and doNotAdd:
                    continue
                res = unpack(line.strip(), ('title', 'note'))
                note = res.get('note')
                if incontrib:
                    if res.get('note'): note += ' '
                    else: note = ''
                    if start == AKAT_HU_START: note += '(Hungary)'
                    elif start == AKAT_NO_START: note += '(Norway)'
                akat = res.get('title', '')
                if akat[:5] == '(aka ': akat = akat[5:]
                if akat[-2:] in ('))', '})'): akat = akat[:-1]
                akat = akat.strip()
                if not akat:
                    continue
                if obsolete:
                    try:
                        akatD = analyze_title(akat, _emptyString='')
                    except IMDbParserError:
                        if line:
                            print 'WARNING doAkaTitles(obsol) invalid title:',
                            print _(akat)
                        continue
                    akatD['title'] = normalizeTitle(akatD['title'])
                    akat = build_title(akatD, ptdf=1, _emptyString='')
                if count % 10000 == 0:
                    print 'SCANNING %s:' % fname[:-8].replace('-', ' '),
                    print _(akat)
                if isEpisode and seriesID is not None:
                    # Handle series for which only single episodes have
                    # aliases.
                    try:
                        akaDict = analyze_title(akat, _emptyString='')
                    except IMDbParserError:
                        if line:
                            print 'WARNING doAkaTitles (epis) invalid title:',
                            print _(akat)
                        continue
                    if 'episode of' in akaDict:
                        if obsolete:
                            akaDict['episode of']['title'] = normalizeTitle(
                                            akaDict['episode of']['title'])
                        akaSeries = build_title(akaDict['episode of'], ptdf=1)
                        CACHE_MID_AKAS.add(akaSeries, [('ids', seriesID)])
                append_data = [('ids', mid)]
                if note is not None:
                    append_data.append(('notes', note))
                CACHE_MID_AKAS.add(akat, append_data)
                count += 1
        fp.close()
    CACHE_MID_AKAS.flush()
    CACHE_MID_AKAS.clear()
    CACHE_MID_AKAS.notes.clear()
    CACHE_MID_AKAS.ids.clear()


def doMovieLinks():
    """Connections between movies."""
    mid = None
    count = 0
    sqldata = SQLData(table=MovieLink,
                cols=['movieID', 'linkedMovieID', 'linkTypeID'],
                flushEvery=10000)
    try: fp = SourceFile('movie-links.list.gz', start=LINK_START)
    except IOError: return
    for line in fp:
        if line and line[0] != ' ':
            if line[0] == '\n': continue
            title = line.strip()
            mid = CACHE_MID.addUnique(title)
            if mid is None:
                continue
            if count % 10000 == 0:
                print 'SCANNING movielinks:', _(title)
        else:
            if mid == None:
               continue
            line = line.strip()
            link_txt = unicode(line, 'utf_8').encode('ascii', 'replace')
            theid = None
            for k, lenkp1, v in MOVIELINK_IDS:
                if link_txt and link_txt[0] == '(' \
                        and link_txt[1:lenkp1+1] == k:
                    theid = v
                    break
            if theid is None: continue
            totitle = line[lenkp1+2:-1].strip()
            totitleid = CACHE_MID.addUnique(totitle)
            if totitleid is None:
                continue
            sqldata.add((mid, totitleid, theid))
        count += 1
    sqldata.flush()
    fp.close()


def minusHashFiles(fp, funct, defaultid, descr):
    """A file with lines starting with '# ' and '- '."""
    sqldata = SQLData(table=MovieInfo,
                        cols=['movieID', 'infoTypeID', 'info', 'note'])
    sqldata.flushEvery = 2500
    if descr == 'quotes': sqldata.flushEvery = 4000
    elif descr == 'soundtracks': sqldata.flushEvery = 3000
    elif descr == 'trivia': sqldata.flushEvery = 3000
    count = 0
    for title, text in fp.getByHashSections():
        title = title.strip()
        d = funct(text.split('\n'))
        if not d:
            print 'WARNING skipping empty information about title:',
            print _(title)
            continue
        if not title:
            print 'WARNING skipping information associated to empty title:',
            print _(d[0], truncateAt=40)
            continue
        mid = CACHE_MID.addUnique(title)
        if mid is None:
            continue
        if count % 5000 == 0:
            print 'SCANNING %s:' % descr,
            print _(title)
        for data in d:
            sqldata.add((mid, defaultid, data, None))
        count += 1
    sqldata.flush()


def doMinusHashFiles():
    """Files with lines starting with '# ' and '- '."""
    for fname, start in [('alternate versions',AV_START),
                         ('goofs',GOOFS_START), ('crazy credits',CC_START),
                         ('quotes',QUOTES_START),
                         ('soundtracks',SNDT_START),
                         ('trivia',TRIV_START)]:
        try:
            fp = SourceFile(fname.replace(' ', '-')+'.list.gz', start=start,
                        stop=MINHASH_STOP)
        except IOError:
            continue
        funct = _parseMinusList
        if fname == 'quotes': funct = getQuotes
        index = fname
        if index == 'soundtracks': index = 'soundtrack'
        minusHashFiles(fp, funct, INFO_TYPES[index], fname)
        fp.close()


def getTaglines():
    """Movie's taglines."""
    try: fp = SourceFile('taglines.list.gz', start=TAGL_START, stop=TAGL_STOP)
    except IOError: return
    sqldata = SQLData(table=MovieInfo,
                cols=['movieID', 'infoTypeID', 'info', 'note'],
                flushEvery=10000)
    count = 0
    for title, text in fp.getByHashSections():
        title = title.strip()
        mid = CACHE_MID.addUnique(title)
        if mid is None:
            continue
        for tag in text.split('\n'):
            tag = tag.strip()
            if not tag: continue
            if count % 10000 == 0:
                print 'SCANNING taglines:', _(title)
            sqldata.add((mid, INFO_TYPES['taglines'], tag, None))
        count += 1
    sqldata.flush()
    fp.close()


def getQuotes(lines):
    """Movie's quotes."""
    quotes = []
    qttl = []
    for line in lines:
        if line and line[:2] == '  ' and qttl and qttl[-1] and \
                not qttl[-1].endswith('::'):
            line = line.lstrip()
            if line: qttl[-1] += ' %s' % line
        elif not line.strip():
            if qttl: quotes.append('::'.join(qttl))
            qttl[:] = []
        else:
            line = line.lstrip()
            if line: qttl.append(line)
    if qttl: quotes.append('::'.join(qttl))
    return quotes


_bus = {'BT': 'budget',
        'WG': 'weekend gross',
        'GR': 'gross',
        'OW': 'opening weekend',
        'RT': 'rentals',
        'AD': 'admissions',
        'SD': 'filming dates',
        'PD': 'production dates',
        'ST': 'studios',
        'CP': 'copyright holder'
}
_usd = '$'
_gbp = unichr(0x00a3).encode('utf_8')
_eur = unichr(0x20ac).encode('utf_8')
def getBusiness(lines):
    """Movie's business information."""
    bd = _parseColonList(lines, _bus)
    for k in bd.keys():
        nv = []
        for v in bd[k]:
            v = v.replace('USD ',_usd).replace('GBP ',_gbp).replace('EUR',_eur)
            nv.append(v)
        bd[k] = nv
    return bd


_ldk = {'OT': 'original title',
        'PC': 'production country',
        'YR': 'year',
        'CF': 'certification',
        'CA': 'category',
        'GR': 'group genre',
        'LA': 'language',
        'SU': 'subtitles',
        'LE': 'length',
        'RD': 'release date',
        'ST': 'status of availablility',
        'PR': 'official retail price',
        'RC': 'release country',
        'VS': 'video standard',
        'CO': 'color information',
        'SE': 'sound encoding',
        'DS': 'digital sound',
        'AL': 'analog left',
        'AR': 'analog right',
        'MF': 'master format',
        'PP': 'pressing plant',
        'SZ': 'disc size',
        'SI': 'number of sides',
        'DF': 'disc format',
        'PF': 'picture format',
        'AS': 'aspect ratio',
        'CC': 'close captions-teletext-ld-g',
        'CS': 'number of chapter stops',
        'QP': 'quality program',
        'IN': 'additional information',
        'SL': 'supplement',
        'RV': 'review',
        'V1': 'quality of source',
        'V2': 'contrast',
        'V3': 'color rendition',
        'V4': 'sharpness',
        'V5': 'video noise',
        'V6': 'video artifacts',
        'VQ': 'video quality',
        'A1': 'frequency response',
        'A2': 'dynamic range',
        'A3': 'spaciality',
        'A4': 'audio noise',
        'A5': 'dialogue intellegibility',
        'AQ': 'audio quality',
        'LN': 'number',
        'LB': 'label',
        'CN': 'catalog number',
        'LT': 'laserdisc title'
}
# Handle laserdisc keys.
for key, value in _ldk.items():
    _ldk[key] = 'LD %s' % value

def getLaserDisc(lines):
    """Laserdisc information."""
    d = _parseColonList(lines, _ldk)
    for k, v in d.iteritems():
        d[k] = ' '.join(v)
    return d


_lit = {'SCRP': 'screenplay-teleplay',
        'NOVL': 'novel',
        'ADPT': 'adaption',
        'BOOK': 'book',
        'PROT': 'production process protocol',
        'IVIW': 'interviews',
        'CRIT': 'printed media reviews',
        'ESSY': 'essays',
        'OTHR': 'other literature'
}
def getLiterature(lines):
    """Movie's literature information."""
    return _parseColonList(lines, _lit)


_mpaa = {'RE': 'mpaa'}
def getMPAA(lines):
    """Movie's mpaa information."""
    d = _parseColonList(lines, _mpaa)
    for k, v in d.iteritems():
        d[k] = ' '.join(v)
    return d


re_nameImdbIndex = re.compile(r'\(([IVXLCDM]+)\)')

def nmmvFiles(fp, funct, fname):
    """Files with sections separated by 'MV: ' or 'NM: '."""
    count = 0
    sqlsP = (PersonInfo, ['personID', 'infoTypeID', 'info', 'note'])
    sqlsM = (MovieInfo, ['movieID', 'infoTypeID', 'info', 'note'])

    if fname == 'biographies.list.gz':
        datakind = 'person'
        sqls = sqlsP
        guestid = RoleType.select(RoleType.q.role == 'guest')[0].id
        roleid = str(guestid)
        guestdata = SQLData(table=CastInfo,
                cols=['personID', 'movieID', 'personRoleID', 'note',
                RawValue('roleID', roleid)], flushEvery=10000)
        akanamesdata = SQLData(table=AkaName, cols=['personID', 'name',
                'imdbIndex', 'namePcodeCf', 'namePcodeNf', 'surnamePcode',
                'md5sum'])
    else:
        datakind = 'movie'
        sqls = sqlsM
        guestdata = None
        akanamesdata = None
    sqldata = SQLData(table=sqls[0], cols=sqls[1])
    if fname == 'plot.list.gz': sqldata.flushEvery = 1100
    elif fname == 'literature.list.gz': sqldata.flushEvery = 5000
    elif fname == 'business.list.gz': sqldata.flushEvery = 10000
    elif fname == 'biographies.list.gz': sqldata.flushEvery = 5000
    islaserdisc = False
    if fname == 'laserdisc.list.gz':
        islaserdisc = True
    _ltype = type([])
    for ton, text in fp.getByNMMVSections():
        ton = ton.strip()
        if not ton: continue
        note = None
        if datakind == 'movie':
            if islaserdisc:
                tonD = analyze_title(ton, _emptyString='')
                tonD['title'] = normalizeTitle(tonD['title'])
                ton = build_title(tonD, ptdf=1, _emptyString='')
                # Skips movies that are not already in the cache, since
                # laserdisc.list.gz is an obsolete file.
                if ton not in CACHE_MID:
                    continue
            mopid = CACHE_MID.addUnique(ton)
            if mopid is None:
                continue
        else: mopid = CACHE_PID.addUnique(ton)
        if count % 6000 == 0:
            print 'SCANNING %s:' % fname[:-8].replace('-', ' '),
            print _(ton)
        d = funct(text.split('\n'))
        for k, v in d.iteritems():
            if k != 'notable tv guest appearances':
                theid = INFO_TYPES.get(k)
                if theid is None:
                    print 'WARNING key "%s" of ToN' % k,
                    print _(ton),
                    print 'not in INFO_TYPES'
                    continue
            if type(v) is _ltype:
                for i in v:
                    if k == 'notable tv guest appearances':
                        # Put "guest" information in the cast table; these
                        # are a list of Movie object (yes, imdb.Movie.Movie)
                        # FIXME: no more used?
                        title = i.get('long imdb canonical title')
                        if not title: continue
                        movieid = CACHE_MID.addUnique(title)
                        if movieid is None:
                            continue
                        crole = i.currentRole
                        if isinstance(crole, list):
                            crole = ' / '.join([x.get('long imdb name', u'')
                                                for x in crole])
                        if not crole:
                            crole = None
                        else:
                            crole = unicode(crole).encode('utf_8')
                        guestdata.add((mopid, movieid, crole,
                                        i.notes or None))
                        continue
                    if k in ('plot', 'mini biography'):
                        s = i.split('::')
                        if len(s) == 2:
                            #if note: note += ' '
                            #else: note = ''
                            #note += '(author: %s)' % s[1]
                            note = s[1]
                            i = s[0]
                    if i: sqldata.add((mopid, theid, i, note))
                    note = None
            else:
                if v: sqldata.add((mopid, theid, v, note))
            if k in ('nick names', 'birth name') and v:
                # Put also the birth name/nick names in the list of aliases.
                if k == 'birth name': realnames = [v]
                else: realnames = v
                for realname in realnames:
                    imdbIndex = re_nameImdbIndex.findall(realname) or None
                    if imdbIndex:
                        imdbIndex = imdbIndex[0]
                        realname = re_nameImdbIndex.sub('', realname)
                    if realname:
                        # XXX: check for duplicates?
                        ##if k == 'birth name':
                        ##    realname = canonicalName(realname)
                        ##else:
                        ##    realname = normalizeName(realname)
                        namePcodeCf, namePcodeNf, surnamePcode = \
                                    name_soundexes(realname)
                        akanamesdata.add((mopid, realname, imdbIndex,
                                    namePcodeCf, namePcodeNf, surnamePcode,
                                    md5(realname).hexdigest()))
        count += 1
    if guestdata is not None: guestdata.flush()
    if akanamesdata is not None: akanamesdata.flush()
    sqldata.flush()


# ============
# Code from the old 'local' data access system.

def _parseList(l, prefix, mline=1):
    """Given a list of lines l, strips prefix and join consecutive lines
    with the same prefix; if mline is True, there can be multiple info with
    the same prefix, and the first line starts with 'prefix: * '."""
    resl = []
    reslapp = resl.append
    ltmp = []
    ltmpapp = ltmp.append
    fistl = '%s: * ' % prefix
    otherl = '%s:   ' % prefix
    if not mline:
        fistl = fistl[:-2]
        otherl = otherl[:-2]
    firstlen = len(fistl)
    otherlen = len(otherl)
    parsing = 0
    joiner = ' '.join
    for line in l:
        if line[:firstlen] == fistl:
            parsing = 1
            if ltmp:
                reslapp(joiner(ltmp))
                ltmp[:] = []
            data = line[firstlen:].strip()
            if data: ltmpapp(data)
        elif mline and line[:otherlen] == otherl:
            data = line[otherlen:].strip()
            if data: ltmpapp(data)
        else:
            if ltmp:
                reslapp(joiner(ltmp))
                ltmp[:] = []
            if parsing:
                if ltmp: reslapp(joiner(ltmp))
                break
    return resl


def _parseBioBy(l):
    """Return a list of biographies."""
    bios = []
    biosappend = bios.append
    tmpbio = []
    tmpbioappend = tmpbio.append
    joiner = ' '.join
    for line in l:
        if line[:4] == 'BG: ':
            tmpbioappend(line[4:].strip())
        elif line[:4] == 'BY: ':
            if tmpbio:
                biosappend(joiner(tmpbio) + '::' + line[4:].strip())
                tmpbio[:] = []
    # Cut mini biographies up to 2**16-1 chars, to prevent errors with
    # some MySQL versions - when used by the imdbpy2sql.py script.
    bios[:] = [bio[:65535] for bio in bios]
    return bios


def _parseBiography(biol):
    """Parse the biographies.data file."""
    res = {}
    bio = ' '.join(_parseList(biol, 'BG', mline=0))
    bio = _parseBioBy(biol)
    if bio: res['mini biography'] = bio

    for x in biol:
        x4 = x[:4]
        x6 = x[:6]
        if x4 == 'DB: ':
            date, notes = date_and_notes(x[4:])
            if date:
                res['birth date'] = date
            if notes:
                res['birth notes'] = notes
        elif x4 == 'DD: ':
            date, notes = date_and_notes(x[4:])
            if date:
                res['death date'] = date
            if notes:
                res['death notes'] = notes
        elif x6 == 'SP: * ':
            res.setdefault('spouse', []).append(x[6:].strip())
        elif x4 == 'RN: ':
            n = x[4:].strip()
            if not n: continue
            try:
                rn = build_name(analyze_name(n, canonical=1), canonical=1)
                res['birth name'] = rn
            except IMDbParserError:
                if line: print 'WARNING _parseBiography wrong name:', _(n)
                continue
        elif x6 == 'AT: * ':
            res.setdefault('article', []).append(x[6:].strip())
        elif x4 == 'HT: ':
            res['height'] = x[4:].strip()
        elif x6 == 'PT: * ':
            res.setdefault('pictorial', []).append(x[6:].strip())
        elif x6 == 'CV: * ':
            res.setdefault('magazine cover photo', []).append(x[6:].strip())
        elif x4 == 'NK: ':
            res.setdefault('nick names', []).append(normalizeName(x[4:]))
        elif x6 == 'PI: * ':
            res.setdefault('portrayed in', []).append(x[6:].strip())
        elif x6 == 'SA: * ':
            sal = x[6:].strip().replace(' -> ', '::')
            res.setdefault('salary history', []).append(sal)
    trl = _parseList(biol, 'TR')
    if trl: res['trivia'] = trl
    quotes = _parseList(biol, 'QU')
    if quotes: res['quotes'] = quotes
    otherworks = _parseList(biol, 'OW')
    if otherworks: res['other works'] = otherworks
    books = _parseList(biol, 'BO')
    if books: res['books'] = books
    agent = _parseList(biol, 'AG')
    if agent: res['agent address'] = agent
    wherenow = _parseList(biol, 'WN')
    if wherenow: res['where now'] = wherenow[0]
    biomovies = _parseList(biol, 'BT')
    if biomovies: res['biographical movies'] = biomovies
    tm = _parseList(biol, 'TM')
    if tm: res['trade mark'] = tm
    interv = _parseList(biol, 'IT')
    if interv: res['interviews'] = interv
    return res

# ============


def doNMMVFiles():
    """Files with large sections, about movies and persons."""
    for fname, start, funct in [
            ('biographies.list.gz', BIO_START, _parseBiography),
            ('business.list.gz', BUS_START, getBusiness),
            ('laserdisc.list.gz', LSD_START, getLaserDisc),
            ('literature.list.gz', LIT_START, getLiterature),
            ('mpaa-ratings-reasons.list.gz', MPAA_START, getMPAA),
            ('plot.list.gz', PLOT_START, getPlot)]:
    ##for fname, start, funct in [('business.list.gz',BUS_START,getBusiness)]:
        try:
            fp = SourceFile(fname, start=start)
        except IOError:
            continue
        if fname == 'literature.list.gz': fp.set_stop(LIT_STOP)
        elif fname == 'business.list.gz': fp.set_stop(BUS_STOP)
        nmmvFiles(fp, funct, fname)
        fp.close()
        t('doNMMVFiles(%s)' % fname[:-8].replace('-', ' '))


def doMovieCompaniesInfo():
    """Files with information on a single line about movies,
    concerning companies."""
    sqldata = SQLData(table=MovieCompanies,
                cols=['movieID', 'companyID', 'companyTypeID', 'note'])
    for dataf in (('distributors.list.gz', DIS_START),
                    ('miscellaneous-companies.list.gz', MIS_START),
                    ('production-companies.list.gz', PRO_START),
                    ('special-effects-companies.list.gz', SFX_START)):
        try:
            fp = SourceFile(dataf[0], start=dataf[1])
        except IOError:
            continue
        typeindex = dataf[0][:-8].replace('-', ' ')
        infoid =  COMP_TYPES[typeindex]
        count = 0
        for line in fp:
            data = unpack(line.strip(), ('title', 'company', 'note'))
            if 'title' not in data: continue
            if 'company' not in data: continue
            title = data['title']
            company = data['company']
            mid = CACHE_MID.addUnique(title)
            if mid is None:
                continue
            cid = CACHE_COMPID.addUnique(company)
            note = None
            if 'note' in data:
                note = data['note']
            if count % 10000 == 0:
                print 'SCANNING %s:' % dataf[0][:-8].replace('-', ' '),
                print _(data['title'])
            sqldata.add((mid, cid, infoid, note))
            count += 1
        sqldata.flush()
        CACHE_COMPID.flush()
        fp.close()
        t('doMovieCompaniesInfo(%s)' % dataf[0][:-8].replace('-', ' '))


def doMiscMovieInfo():
    """Files with information on a single line about movies."""
    for dataf in (('certificates.list.gz',CER_START),
                    ('color-info.list.gz',COL_START),
                    ('countries.list.gz',COU_START),
                    ('genres.list.gz',GEN_START),
                    ('keywords.list.gz',KEY_START),
                    ('language.list.gz',LAN_START),
                    ('locations.list.gz',LOC_START),
                    ('running-times.list.gz',RUN_START),
                    ('sound-mix.list.gz',SOU_START),
                    ('technical.list.gz',TCN_START),
                    ('release-dates.list.gz',RELDATE_START)):
        try:
            fp = SourceFile(dataf[0], start=dataf[1])
        except IOError:
            continue
        typeindex = dataf[0][:-8].replace('-', ' ')
        if typeindex == 'running times': typeindex = 'runtimes'
        elif typeindex == 'technical': typeindex = 'tech info'
        elif typeindex == 'language': typeindex = 'languages'
        if typeindex != 'keywords':
            sqldata = SQLData(table=MovieInfo,
                        cols=['movieID', 'infoTypeID', 'info', 'note'])
        else:
            sqldata = SQLData(table=MovieKeyword,
                        cols=['movieID', 'keywordID'])
        infoid =  INFO_TYPES[typeindex]
        count = 0
        if dataf[0] == 'locations.list.gz':
            sqldata.flushEvery = 10000
        else:
            sqldata.flushEvery = 20000
        for line in fp:
            data = unpack(line.strip(), ('title', 'info', 'note'))
            if 'title' not in data: continue
            if 'info' not in data: continue
            title = data['title']
            mid = CACHE_MID.addUnique(title)
            if mid is None:
                continue
            note = None
            if 'note' in data:
                note = data['note']
            if count % 10000 == 0:
                print 'SCANNING %s:' % dataf[0][:-8].replace('-', ' '),
                print _(data['title'])
            info = data['info']
            if typeindex == 'keywords':
                keywordID = CACHE_KWRDID.addUnique(info)
                sqldata.add((mid, keywordID))
            else:
                sqldata.add((mid, infoid, info, note))
            count += 1
        sqldata.flush()
        if typeindex == 'keywords':
            CACHE_KWRDID.flush()
            CACHE_KWRDID.clear()
        fp.close()
        t('doMiscMovieInfo(%s)' % dataf[0][:-8].replace('-', ' '))


def getRating():
    """Movie's rating."""
    try: fp = SourceFile('ratings.list.gz', start=RAT_START, stop=RAT_STOP)
    except IOError: return
    sqldata = SQLData(table=MovieInfoIdx, cols=['movieID', 'infoTypeID',
                                                'info', 'note'])
    count = 0
    for line in fp:
        data = unpack(line, ('votes distribution', 'votes', 'rating', 'title'),
                        sep='  ')
        if 'title' not in data: continue
        title = data['title'].strip()
        mid = CACHE_MID.addUnique(title)
        if mid is None:
            continue
        if count % 10000 == 0:
            print 'SCANNING rating:', _(title)
        sqldata.add((mid, INFO_TYPES['votes distribution'],
                    data.get('votes distribution'), None))
        sqldata.add((mid, INFO_TYPES['votes'], data.get('votes'), None))
        sqldata.add((mid, INFO_TYPES['rating'], data.get('rating'), None))
        count += 1
    sqldata.flush()
    fp.close()


def getTopBottomRating():
    """Movie's rating, scanning for top 250 and bottom 10."""
    for what in ('top 250 rank', 'bottom 10 rank'):
        if what == 'top 250 rank': st = RAT_TOP250_START
        else: st = RAT_BOT10_START
        try: fp = SourceFile('ratings.list.gz', start=st, stop=TOPBOT_STOP)
        except IOError: break
        sqldata = SQLData(table=MovieInfoIdx,
                    cols=['movieID',
                        RawValue('infoTypeID', INFO_TYPES[what]),
                        'info', 'note'])
        count = 1
        print 'SCANNING %s...' % what
        for line in fp:
            data = unpack(line, ('votes distribution', 'votes', 'rank',
                                'title'), sep='  ')
            if 'title' not in data: continue
            title = data['title'].strip()
            mid = CACHE_MID.addUnique(title)
            if mid is None:
                continue
            if what == 'top 250 rank': rank = count
            else: rank = 11 - count
            sqldata.add((mid, str(rank), None))
            count += 1
        sqldata.flush()
        fp.close()


def getPlot(lines):
    """Movie's plot."""
    plotl = []
    plotlappend = plotl.append
    plotltmp = []
    plotltmpappend = plotltmp.append
    for line in lines:
        linestart = line[:4]
        if linestart == 'PL: ':
            plotltmpappend(line[4:])
        elif linestart == 'BY: ':
            plotlappend('%s::%s' % (' '.join(plotltmp), line[4:].strip()))
            plotltmp[:] = []
    return {'plot': plotl}


def completeCast():
    """Movie's complete cast/crew information."""
    CCKind = {}
    cckinds = [(x.id, x.kind) for x in CompCastType.select()]
    for k, v in cckinds:
        CCKind[v] = k
    for fname, start in [('complete-cast.list.gz',COMPCAST_START),
                        ('complete-crew.list.gz',COMPCREW_START)]:
        try:
            fp = SourceFile(fname, start=start, stop=COMP_STOP)
        except IOError:
            continue
        if fname == 'complete-cast.list.gz': obj = 'cast'
        else: obj = 'crew'
        subID = str(CCKind[obj])
        sqldata = SQLData(table=CompleteCast,
                cols=['movieID', RawValue('subjectID', subID),
                'statusID'])
        count = 0
        for line in fp:
            ll = [x for x in line.split('\t') if x]
            if len(ll) != 2: continue
            title = ll[0]
            mid = CACHE_MID.addUnique(title)
            if mid is None:
                continue
            if count % 10000 == 0:
                print 'SCANNING %s:' % fname[:-8].replace('-', ' '),
                print _(title)
            sqldata.add((mid, CCKind[ll[1].lower().strip()]))
            count += 1
        fp.close()
        sqldata.flush()


# global instances
CACHE_MID = MoviesCache()
CACHE_PID = PersonsCache()
CACHE_CID = CharactersCache()
CACHE_CID.className = 'CharactersCache'
CACHE_COMPID = CompaniesCache()
CACHE_KWRDID = KeywordsCache()

def _cmpfunc(x, y):
    """Sort a list of tuples, by the length of the first item (in reverse)."""
    lx = len(x[0])
    ly = len(y[0])
    if lx > ly: return -1
    elif lx < ly: return 1
    return 0

INFO_TYPES = {}
MOVIELINK_IDS = []
KIND_IDS = {}
KIND_STRS = {}
CCAST_TYPES = {}
COMP_TYPES = {}

def readConstants():
    """Read constants from the database."""
    global INFO_TYPES, MOVIELINK_IDS, KIND_IDS, KIND_STRS, \
            CCAST_TYPES, COMP_TYPES

    for x in InfoType.select():
        INFO_TYPES[x.info] = x.id

    for x in LinkType.select():
        MOVIELINK_IDS.append((x.link, len(x.link), x.id))
    MOVIELINK_IDS.sort(_cmpfunc)

    for x in KindType.select():
        KIND_IDS[x.kind] = x.id
        KIND_STRS[x.id] = x.kind

    for x in CompCastType.select():
        CCAST_TYPES[x.kind] = x.id

    for x in CompanyType.select():
        COMP_TYPES[x.kind] = x.id


def _imdbIDsFileName(fname):
    """Return a file name, adding the optional
    CSV_DIR directory."""
    return os.path.join(*(filter(None, [CSV_DIR, fname])))


def _countRows(tableName):
    """Return the number of rows in a table."""
    try:
        CURS.execute('SELECT COUNT(*) FROM %s' % tableName)
        return (CURS.fetchone() or [0])[0]
    except Exception, e:
        print 'WARNING: unable to count rows of table %s: %s' % (tableName, e)
        return 0


def storeNotNULLimdbIDs(cls):
    """Store in a temporary table or in a dbm database a mapping between
    md5sum (of title or name) and imdbID, when the latter
    is present in the database."""
    if cls is Title: cname = 'movies'
    elif cls is Name: cname = 'people'
    elif cls is CompanyName: cname = 'companies'
    else: cname = 'characters'
    table_name = tableName(cls)
    md5sum_col = colName(cls, 'md5sum')
    imdbID_col = colName(cls, 'imdbID')

    print 'SAVING imdbID values for %s...' % cname,
    sys.stdout.flush()
    if _get_imdbids_method() == 'table':
        try:
            try:
                CURS.execute('DROP TABLE %s_extract' % table_name)
            except:
                pass
            try:
                CURS.execute('SELECT * FROM %s LIMIT 1' % table_name)
            except Exception, e:
                print 'missing "%s" table (ok if this is the first run)' % table_name
                return
            query = 'CREATE TEMPORARY TABLE %s_extract AS SELECT %s, %s FROM %s WHERE %s IS NOT NULL' % \
                    (table_name, md5sum_col, imdbID_col,
                    table_name, imdbID_col)
            CURS.execute(query)
            CURS.execute('CREATE INDEX %s_md5sum_idx ON %s_extract (%s)' % (table_name, table_name, md5sum_col))
            CURS.execute('CREATE INDEX %s_imdbid_idx ON %s_extract (%s)' % (table_name, table_name, imdbID_col))
            rows = _countRows('%s_extract' % table_name)
            print 'DONE! (%d entries using a temporary table)' % rows
            return
        except Exception, e:
            print 'WARNING: unable to store imdbIDs in a temporary table (falling back to dbm): %s' % e
    try:
        db = anydbm.open(_imdbIDsFileName('%s_imdbIDs.db' % cname), 'c')
    except Exception, e:
        print 'WARNING: unable to store imdbIDs: %s' % str(e)
        return
    try:
        CURS.execute('SELECT %s, %s FROM %s WHERE %s IS NOT NULL' %
                    (md5sum_col, imdbID_col, table_name, imdbID_col))
        res = CURS.fetchmany(10000)
        while res:
            db.update(dict((str(x[0]), str(x[1])) for x in res))
            res = CURS.fetchmany(10000)
    except Exception, e:
        print 'SKIPPING: unable to retrieve data: %s' % e
        return
    print 'DONE! (%d entries)' % len(db)
    db.close()
    return


def iterbatch(iterable, size):
    """Process an iterable 'size' items at a time."""
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.next()], batchiter)


def restoreImdbIDs(cls):
    """Restore imdbIDs for movies, people, companies and characters."""
    if cls is Title:
        cname = 'movies'
    elif cls is Name:
        cname = 'people'
    elif cls is CompanyName:
        cname = 'companies'
    else:
        cname = 'characters'
    print 'RESTORING imdbIDs values for %s...' % cname,
    sys.stdout.flush()
    table_name = tableName(cls)
    md5sum_col = colName(cls, 'md5sum')
    imdbID_col = colName(cls, 'imdbID')

    if _get_imdbids_method() == 'table':
        try:
            try:
                CURS.execute('SELECT * FROM %s_extract LIMIT 1' % table_name)
            except Exception, e:
                raise Exception('missing "%s_extract" table (ok if this is the first run)' % table_name)

            if DB_NAME == 'mysql':
                query = 'UPDATE %s INNER JOIN %s_extract USING (%s) SET %s.%s = %s_extract.%s' % \
                        (table_name, table_name, md5sum_col,
                        table_name, imdbID_col, table_name, imdbID_col)
            else:
                query = 'UPDATE %s SET %s = %s_extract.%s FROM %s_extract WHERE %s.%s = %s_extract.%s' % \
                        (table_name, imdbID_col, table_name,
                        imdbID_col, table_name, table_name,
                        md5sum_col, table_name, md5sum_col)
            CURS.execute(query)
            affected_rows = 'an unknown number of'
            try:
                CURS.execute('SELECT COUNT(*) FROM %s WHERE %s IS NOT NULL' %
                        (table_name, imdbID_col))
                affected_rows = (CURS.fetchone() or [0])[0]
            except Exception, e:
                pass
            rows = _countRows('%s_extract' % table_name)
            print 'DONE! (restored %s entries out of %d)' % (affected_rows, rows)
            t('restore %s' % cname)
            try: CURS.execute('DROP TABLE %s_extract' % table_name)
            except: pass
            return
        except Exception, e:
            print 'WARNING: unable to restore imdbIDs using the temporary table (falling back to dbm): %s' % e
    try:
        db = anydbm.open(_imdbIDsFileName('%s_imdbIDs.db' % cname), 'r')
    except Exception, e:
        print 'WARNING: unable to restore imdbIDs (ok if this is the first run)'
        return
    count = 0
    sql = "UPDATE " + table_name + " SET " + imdbID_col + \
            " = CASE " + md5sum_col + " %s END WHERE " + \
            md5sum_col + " IN (%s)"
    def _restore(query, batch):
        """Execute a query to restore a batch of imdbIDs"""
        items = list(batch)
        case_clause = ' '.join("WHEN '%s' THEN %s" % (k, v) for k, v in items)
        where_clause = ', '.join("'%s'" % x[0] for x in items)
        success = _executeQuery(query % (case_clause, where_clause))
        if success:
            return len(items)
        return 0
    for batch in iterbatch(db.iteritems(), 10000):
        count += _restore(sql, batch)
    print 'DONE! (restored %d entries out of %d)' % (count, len(db))
    t('restore %s' % cname)
    db.close()
    return

def restoreAll_imdbIDs():
    """Restore imdbIDs for movies, persons, companies and characters."""
    # Restoring imdbIDs for movies and persons (moved after the
    # built of indexes, so that it can take advantage of them).
    runSafely(restoreImdbIDs, 'failed to restore imdbIDs for movies',
            None, Title)
    runSafely(restoreImdbIDs, 'failed to restore imdbIDs for people',
            None, Name)
    runSafely(restoreImdbIDs, 'failed to restore imdbIDs for characters',
            None, CharName)
    runSafely(restoreImdbIDs, 'failed to restore imdbIDs for companies',
            None, CompanyName)


def runSafely(funct, fmsg, default, *args, **kwds):
    """Run the function 'funct' with arguments args and
    kwds, catching every exception; fmsg is printed out (along
    with the exception message) in case of trouble; the return
    value of the function is returned (or 'default')."""
    try:
        return funct(*args, **kwds)
    except Exception, e:
        print 'WARNING: %s: %s' % (fmsg, e)
    return default


def _executeQuery(query):
    """Execute a query on the CURS object."""
    if len(query) > 60:
        s_query = query[:60] + '...'
    else:
        s_query = query
    print 'EXECUTING "%s"...' % (s_query),
    sys.stdout.flush()
    try:
        CURS.execute(query)
        print 'DONE!'
        return True
    except Exception, e:
        print 'FAILED (%s)!' % e
        return False


def executeCustomQueries(when, _keys=None, _timeit=True):
    """Run custom queries as specified on the command line."""
    if _keys is None: _keys = {}
    for query in CUSTOM_QUERIES.get(when, []):
        print 'EXECUTING "%s:%s"...' % (when, query)
        sys.stdout.flush()
        if query.startswith('FOR_EVERY_TABLE:'):
            query = query[16:]
            CURS.execute('SHOW TABLES;')
            tables = [x[0] for x in CURS.fetchall()]
            for table in tables:
                try:
                    keys = {'table': table}
                    keys.update(_keys)
                    _executeQuery(query % keys)
                    if _timeit:
                        t('%s command' % when)
                except Exception, e:
                    print 'FAILED (%s)!' % e
                    continue
        else:
            try:
                _executeQuery(query % _keys)
            except Exception, e:
                print 'FAILED (%s)!' % e
                continue
            if _timeit:
                t('%s command' % when)


def buildIndexesAndFK():
    """Build indexes and Foreign Keys."""
    executeCustomQueries('BEFORE_INDEXES')
    print 'building database indexes (this may take a while)'
    sys.stdout.flush()
    # Build database indexes.
    idx_errors = createIndexes(DB_TABLES)
    for idx_error in idx_errors:
        print 'ERROR caught exception creating an index: %s' % idx_error
    t('createIndexes()')
    print 'adding foreign keys (this may take a while)'
    sys.stdout.flush()
    # Add FK.
    fk_errors = createForeignKeys(DB_TABLES)
    for fk_error in fk_errors:
        print 'ERROR caught exception creating a foreign key: %s' % fk_error
    t('createForeignKeys()')


def restoreCSV():
    """Only restore data from a set of CSV files."""
    CSV_CURS.buildFakeFileNames()
    print 'loading CSV files into the database'
    executeCustomQueries('BEFORE_CSV_LOAD')
    loadCSVFiles()
    t('loadCSVFiles()')
    executeCustomQueries('BEFORE_RESTORE')
    t('TOTAL TIME TO LOAD CSV FILES', sinceBegin=True)
    buildIndexesAndFK()
    restoreAll_imdbIDs()
    executeCustomQueries('END')
    t('FINAL', sinceBegin=True)


# begin the iterations...
def run():
    print 'RUNNING imdbpy2sql.py using the %s ORM' % USED_ORM

    executeCustomQueries('BEGIN')

    # Storing imdbIDs for movies and persons.
    runSafely(storeNotNULLimdbIDs, 'failed to read imdbIDs for movies',
            None, Title)
    runSafely(storeNotNULLimdbIDs, 'failed to read imdbIDs for people',
            None, Name)
    runSafely(storeNotNULLimdbIDs, 'failed to read imdbIDs for characters',
            None, CharName)
    runSafely(storeNotNULLimdbIDs, 'failed to read imdbIDs for companies',
            None, CompanyName)

    # Truncate the current database.
    print 'DROPPING current database...',
    sys.stdout.flush()
    dropTables(DB_TABLES)
    print 'DONE!'

    executeCustomQueries('BEFORE_CREATE')
    # Rebuild the database structure.
    print 'CREATING new tables...',
    sys.stdout.flush()
    createTables(DB_TABLES)
    print 'DONE!'
    t('dropping and recreating the database')
    executeCustomQueries('AFTER_CREATE')

    # Read the constants.
    readConstants()

    # Populate the CACHE_MID instance.
    readMovieList()
    # Comment readMovieList() and uncomment the following two lines
    # to keep the current info in the name and title tables.
    ##CACHE_MID.populate()
    t('readMovieList()')

    executeCustomQueries('BEFORE_COMPANIES')

    # distributors, miscellaneous-companies, production-companies,
    # special-effects-companies.
    ##CACHE_COMPID.populate()
    doMovieCompaniesInfo()
    # Do this now, and free some memory.
    CACHE_COMPID.flush()
    CACHE_COMPID.clear()

    executeCustomQueries('BEFORE_CAST')

    # actors, actresses, producers, writers, cinematographers, composers,
    # costume-designers, directors, editors, miscellaneous,
    # production-designers.
    castLists()
    ##CACHE_PID.populate()
    ##CACHE_CID.populate()

    # Aka names and titles.
    doAkaNames()
    t('doAkaNames()')
    doAkaTitles()
    t('doAkaTitles()')

    # alternate-versions, goofs, crazy-credits, quotes, soundtracks, trivia.
    doMinusHashFiles()
    t('doMinusHashFiles()')

    # biographies, business, laserdisc, literature, mpaa-ratings-reasons, plot.
    doNMMVFiles()

    # certificates, color-info, countries, genres, keywords, language,
    # locations, running-times, sound-mix, technical, release-dates.
    doMiscMovieInfo()
    # movie-links.
    doMovieLinks()
    t('doMovieLinks()')

    # ratings.
    getRating()
    t('getRating()')
    # taglines.
    getTaglines()
    t('getTaglines()')
    # ratings (top 250 and bottom 10 movies).
    getTopBottomRating()
    t('getTopBottomRating()')
    # complete-cast, complete-crew.
    completeCast()
    t('completeCast()')

    if CSV_DIR:
        CSV_CURS.closeAll()

    # Flush caches.
    CACHE_MID.flush()
    CACHE_PID.flush()
    CACHE_CID.flush()
    CACHE_MID.clear()
    CACHE_PID.clear()
    CACHE_CID.clear()
    t('fushing caches...')

    if CSV_ONLY_WRITE:
        t('TOTAL TIME TO WRITE CSV FILES', sinceBegin=True)
        executeCustomQueries('END')
        t('FINAL', sinceBegin=True)
        return

    if CSV_DIR:
        print 'loading CSV files into the database'
        executeCustomQueries('BEFORE_CSV_LOAD')
        loadCSVFiles()
        t('loadCSVFiles()')
        executeCustomQueries('BEFORE_RESTORE')

    t('TOTAL TIME TO INSERT/WRITE DATA', sinceBegin=True)

    buildIndexesAndFK()

    restoreAll_imdbIDs()

    executeCustomQueries('END')

    t('FINAL', sinceBegin=True)


_HEARD = 0
def _kdb_handler(signum, frame):
    """Die gracefully."""
    global _HEARD
    if _HEARD:
        print "EHI!  DON'T PUSH ME!  I'VE HEARD YOU THE FIRST TIME! :-)"
        return
    print 'INTERRUPT REQUEST RECEIVED FROM USER.  FLUSHING CACHES...'
    _HEARD = 1
    # XXX: trap _every_ error?
    try: CACHE_MID.flush()
    except IntegrityError: pass
    try: CACHE_PID.flush()
    except IntegrityError: pass
    try: CACHE_CID.flush()
    except IntegrityError: pass
    try: CACHE_COMPID.flush()
    except IntegrityError: pass
    print 'DONE! (in %d minutes, %d seconds)' % \
            divmod(int(time.time())-BEGIN_TIME, 60)
    sys.exit()


if __name__ == '__main__':
    try:
        print 'IMPORTING psyco...',
        sys.stdout.flush()
        #import DONOTIMPORTPSYCO
        import psyco
        #psyco.log()
        psyco.profile()
        print 'DONE!'
        print ''
    except ImportError:
        print 'FAILED (not a big deal, everything is alright...)'
        print ''
    import signal
    signal.signal(signal.SIGINT, _kdb_handler)
    if CSV_ONLY_LOAD:
        restoreCSV()
    else:
        run()
