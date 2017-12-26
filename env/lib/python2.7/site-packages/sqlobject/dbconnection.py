import atexit
import inspect
import sys
import os
import threading
import types
try:
    from urlparse import urlparse, parse_qsl
    from urllib import unquote, quote, urlencode
except ImportError:
    from urllib.parse import urlparse, parse_qsl, unquote, quote, urlencode

import warnings
import weakref

from .cache import CacheSet
from . import classregistry
from . import col
from .converters import sqlrepr
from . import sqlbuilder
from .util.threadinglocal import local as threading_local
from .compat import PY2, string_type, unicode_type

warnings.filterwarnings("ignore", "DB-API extension cursor.lastrowid used")

_connections = {}


def _closeConnection(ref):
    conn = ref()
    if conn is not None:
        conn.close()


class ConsoleWriter:
    def __init__(self, connection, loglevel):
        # loglevel: None or empty string for stdout; or 'stderr'
        self.loglevel = loglevel or "stdout"
        self.dbEncoding = getattr(connection, "dbEncoding", None) or "ascii"

    def write(self, text):
        logfile = getattr(sys, self.loglevel)
        if PY2 and isinstance(text, unicode_type):
            try:
                text = text.encode(self.dbEncoding)
            except UnicodeEncodeError:
                text = repr(text)[2:-1]  # Remove u'...' from the repr
        logfile.write(text + '\n')


class LogWriter:
    def __init__(self, connection, logger, loglevel):
        self.logger = logger
        self.loglevel = loglevel
        self.logmethod = getattr(logger, loglevel)

    def write(self, text):
        self.logmethod(text)


def makeDebugWriter(connection, loggerName, loglevel):
    if not loggerName:
        return ConsoleWriter(connection, loglevel)
    import logging
    logger = logging.getLogger(loggerName)
    return LogWriter(connection, logger, loglevel)


class Boolean(object):
    """A bool class that also understands some special string keywords

    Understands: yes/no, true/false, on/off, 1/0, case ignored.

    """
    _keywords = {'1': True, 'yes': True, 'true': True, 'on': True,
                 '0': False, 'no': False, 'false': False, 'off': False}

    def __new__(cls, value):
        try:
            return Boolean._keywords[value.lower()]
        except (AttributeError, KeyError):
            return bool(value)


class DBConnection:

    def __init__(self, name=None, debug=False, debugOutput=False,
                 cache=True, style=None, autoCommit=True,
                 debugThreading=False, registry=None,
                 logger=None, loglevel=None):
        self.name = name
        self.debug = Boolean(debug)
        self.debugOutput = Boolean(debugOutput)
        self.debugThreading = Boolean(debugThreading)
        self.debugWriter = makeDebugWriter(self, logger, loglevel)
        self.doCache = Boolean(cache)
        self.cache = CacheSet(cache=self.doCache)
        self.style = style
        self._connectionNumbers = {}
        self._connectionCount = 1
        self.autoCommit = Boolean(autoCommit)
        self.registry = registry or None
        classregistry.registry(self.registry).addCallback(self.soClassAdded)
        registerConnectionInstance(self)
        atexit.register(_closeConnection, weakref.ref(self))

    def oldUri(self):
        auth = getattr(self, 'user', '') or ''
        if auth:
            if self.password:
                auth = auth + ':' + self.password
            auth = auth + '@'
        else:
            assert not getattr(self, 'password', None), (
                'URIs cannot express passwords without usernames')
        uri = '%s://%s' % (self.dbName, auth)
        if self.host:
            uri += self.host
            if self.port:
                uri += ':%d' % self.port
        uri += '/'
        db = self.db
        if db.startswith('/'):
            db = db[1:]
        return uri + db

    def uri(self):
        auth = getattr(self, 'user', '') or ''
        if auth:
            auth = quote(auth)
            if self.password:
                auth = auth + ':' + quote(self.password)
            auth = auth + '@'
        else:
            assert not getattr(self, 'password', None), (
                'URIs cannot express passwords without usernames')
        uri = '%s://%s' % (self.dbName, auth)
        if self.host:
            uri += self.host
            if self.port:
                uri += ':%d' % self.port
        uri += '/'
        db = self.db
        if db.startswith('/'):
            db = db[1:]
        return uri + quote(db)

    @classmethod
    def connectionFromOldURI(cls, uri):
        return cls._connectionFromParams(*cls._parseOldURI(uri))

    @classmethod
    def connectionFromURI(cls, uri):
        return cls._connectionFromParams(*cls._parseURI(uri))

    @staticmethod
    def _parseOldURI(uri):
        schema, rest = uri.split(':', 1)
        assert rest.startswith('/'), \
            "URIs must start with scheme:/ -- " \
            "you did not include a / (in %r)" % rest
        if rest.startswith('/') and not rest.startswith('//'):
            host = None
            rest = rest[1:]
        elif rest.startswith('///'):
            host = None
            rest = rest[3:]
        else:
            rest = rest[2:]
            if rest.find('/') == -1:
                host = rest
                rest = ''
            else:
                host, rest = rest.split('/', 1)
        if host and host.find('@') != -1:
            user, host = host.rsplit('@', 1)
            if user.find(':') != -1:
                user, password = user.split(':', 1)
            else:
                password = None
        else:
            user = password = None
        if host and host.find(':') != -1:
            _host, port = host.split(':')
            try:
                port = int(port)
            except ValueError:
                raise ValueError("port must be integer, "
                                 "got '%s' instead" % port)
            if not (1 <= port <= 65535):
                raise ValueError("port must be integer in the range 1-65535, "
                                 "got '%d' instead" % port)
            host = _host
        else:
            port = None
        path = '/' + rest
        if os.name == 'nt':
            if (len(rest) > 1) and (rest[1] == '|'):
                path = "%s:%s" % (rest[0], rest[2:])
        args = {}
        if path.find('?') != -1:
            path, arglist = path.split('?', 1)
            arglist = arglist.split('&')
            for single in arglist:
                argname, argvalue = single.split('=', 1)
                argvalue = unquote(argvalue)
                args[argname] = argvalue
        return user, password, host, port, path, args

    @staticmethod
    def _parseURI(uri):
        parsed = urlparse(uri)
        host, path = parsed.hostname, parsed.path
        user, password, port = None, None, None
        if parsed.username:
            user = unquote(parsed.username)
        if parsed.password:
            password = unquote(parsed.password)
        if parsed.port:
            port = int(parsed.port)

        path = unquote(path)
        if (os.name == 'nt') and (len(path) > 2):
            # Preserve backward compatibility with URIs like /C|/path;
            # replace '|' by ':'
            if path[2] == '|':
                path = "%s:%s" % (path[0:2], path[3:])
            # Remove leading slash
            if (path[0] == '/') and (path[2] == ':'):
                path = path[1:]

        query = parsed.query
        # hash-tag / fragment is ignored

        args = {}
        if query:
            for name, value in parse_qsl(query):
                args[name] = value

        return user, password, host, port, path, args

    def soClassAdded(self, soClass):
        """
        This is called for each new class; we use this opportunity
        to create an instance method that is bound to the class
        and this connection.
        """
        name = soClass.__name__
        assert not hasattr(self, name), (
            "Connection %r already has an attribute with the name "
            "%r (and you just created the conflicting class %r)"
            % (self, name, soClass))
        setattr(self, name, ConnWrapper(soClass, self))

    def expireAll(self):
        """
        Expire all instances of objects for this connection.
        """
        cache_set = self.cache
        cache_set.weakrefAll()
        for item in cache_set.getAll():
            item.expire()


class ConnWrapper(object):

    """
    This represents a SQLObject class that is bound to a specific
    connection (instances have a connection instance variable, but
    classes are global, so this is binds the connection variable
    lazily when a class method is accessed)
    """
    # @@: methods that take connection arguments should be explicitly
    # marked up instead of the implicit use of a connection argument
    # and inspect.getargspec()

    def __init__(self, soClass, connection):
        self._soClass = soClass
        self._connection = connection

    def __call__(self, *args, **kw):
        kw['connection'] = self._connection
        return self._soClass(*args, **kw)

    def __getattr__(self, attr):
        meth = getattr(self._soClass, attr)
        if not isinstance(meth, types.MethodType):
            # We don't need to wrap non-methods
            return meth
        try:
            takes_conn = meth.takes_connection
        except AttributeError:
            args, varargs, varkw, defaults = inspect.getargspec(meth)
            assert not varkw and not varargs, (
                "I cannot tell whether I must wrap this method, "
                "because it takes **kw: %r"
                % meth)
            takes_conn = 'connection' in args
            meth.__func__.takes_connection = takes_conn
        if not takes_conn:
            return meth
        return ConnMethodWrapper(meth, self._connection)


class ConnMethodWrapper(object):

    def __init__(self, method, connection):
        self._method = method
        self._connection = connection

    def __getattr__(self, attr):
        return getattr(self._method, attr)

    def __call__(self, *args, **kw):
        kw['connection'] = self._connection
        return self._method(*args, **kw)

    def __repr__(self):
        return '<Wrapped %r with connection %r>' % (
            self._method, self._connection)


class DBAPI(DBConnection):

    """
    Subclass must define a `makeConnection()` method, which
    returns a newly-created connection object.

    ``queryInsertID`` must also be defined.
    """
    dbName = None

    def __init__(self, **kw):
        self._pool = []
        self._poolLock = threading.Lock()
        DBConnection.__init__(self, **kw)
        self._binaryType = type(self.module.Binary(b''))

    def _runWithConnection(self, meth, *args):
        conn = self.getConnection()
        try:
            val = meth(conn, *args)
        finally:
            self.releaseConnection(conn)
        return val

    def getConnection(self):
        self._poolLock.acquire()
        try:
            if not self._pool:
                conn = self.makeConnection()
                self._connectionNumbers[id(conn)] = self._connectionCount
                self._connectionCount += 1
            else:
                conn = self._pool.pop()
            if self.debug:
                s = 'ACQUIRE'
                if self._pool is not None:
                    s += ' pool=[%s]' % ', '.join(
                        [str(self._connectionNumbers[id(v)])
                            for v in self._pool])
                self.printDebug(conn, s, 'Pool')
            return conn
        finally:
            self._poolLock.release()

    def releaseConnection(self, conn, explicit=False):
        if self.debug:
            if explicit:
                s = 'RELEASE (explicit)'
            else:
                s = 'RELEASE (implicit, autocommit=%s)' % self.autoCommit
            if self._pool is None:
                s += ' no pooling'
            else:
                s += ' pool=[%s]' % ', '.join(
                    [str(self._connectionNumbers[id(v)]) for v in self._pool])
            self.printDebug(conn, s, 'Pool')
        if self.supportTransactions and not explicit:
            if self.autoCommit == 'exception':
                if self.debug:
                    self.printDebug(conn, 'auto/exception', 'ROLLBACK')
                conn.rollback()
                raise Exception('Object used outside of a transaction; '
                                'implicit COMMIT or ROLLBACK not allowed')
            elif self.autoCommit:
                if self.debug:
                    self.printDebug(conn, 'auto', 'COMMIT')
                if not getattr(conn, 'autocommit', False):
                    conn.commit()
            else:
                if self.debug:
                    self.printDebug(conn, 'auto', 'ROLLBACK')
                conn.rollback()
        if self._pool is not None:
            if conn not in self._pool:
                # @@: We can get duplicate releasing of connections with
                # the __del__ in Iteration (unfortunately, not sure why
                # it happens)
                self._pool.insert(0, conn)
        else:
            conn.close()

    def printDebug(self, conn, s, name, type='query'):
        if name == 'Pool' and self.debug != 'Pool':
            return
        if type == 'query':
            sep = ': '
        else:
            sep = '->'
            s = repr(s)
        n = self._connectionNumbers[id(conn)]
        spaces = ' ' * (8 - len(name))
        if self.debugThreading:
            threadName = threading.currentThread().getName()
            threadName = (':' + threadName + ' ' * (8 - len(threadName)))
        else:
            threadName = ''
        msg = '%(n)2i%(threadName)s/%(name)s%(spaces)s%(sep)s %(s)s' % locals()
        self.debugWriter.write(msg)

    def _executeRetry(self, conn, cursor, query):
        if self.debug:
            self.printDebug(conn, query, 'QueryR')
        return cursor.execute(query)

    def _query(self, conn, s):
        if self.debug:
            self.printDebug(conn, s, 'Query')
        self._executeRetry(conn, conn.cursor(), s)

    def query(self, s):
        return self._runWithConnection(self._query, s)

    def _queryAll(self, conn, s):
        if self.debug:
            self.printDebug(conn, s, 'QueryAll')
        c = conn.cursor()
        self._executeRetry(conn, c, s)
        value = c.fetchall()
        if self.debugOutput:
            self.printDebug(conn, value, 'QueryAll', 'result')
        return value

    def queryAll(self, s):
        return self._runWithConnection(self._queryAll, s)

    def _queryAllDescription(self, conn, s):
        """
        Like queryAll, but returns (description, rows), where the
        description is cursor.description (which gives row types)
        """
        if self.debug:
            self.printDebug(conn, s, 'QueryAllDesc')
        c = conn.cursor()
        self._executeRetry(conn, c, s)
        value = c.fetchall()
        if self.debugOutput:
            self.printDebug(conn, value, 'QueryAll', 'result')
        return c.description, value

    def queryAllDescription(self, s):
        return self._runWithConnection(self._queryAllDescription, s)

    def _queryOne(self, conn, s):
        if self.debug:
            self.printDebug(conn, s, 'QueryOne')
        c = conn.cursor()
        self._executeRetry(conn, c, s)
        value = c.fetchone()
        if self.debugOutput:
            self.printDebug(conn, value, 'QueryOne', 'result')
        return value

    def queryOne(self, s):
        return self._runWithConnection(self._queryOne, s)

    def _insertSQL(self, table, names, values):
        return ("INSERT INTO %s (%s) VALUES (%s)" %
                (table, ', '.join(names),
                 ', '.join([self.sqlrepr(v) for v in values])))

    def transaction(self):
        return Transaction(self)

    def queryInsertID(self, soInstance, id, names, values):
        return self._runWithConnection(self._queryInsertID, soInstance, id,
                                       names, values)

    def iterSelect(self, select):
        return select.IterationClass(self, self.getConnection(),
                                     select, keepConnection=False)

    def accumulateSelect(self, select, *expressions):
        """ Apply an accumulate function(s) (SUM, COUNT, MIN, AVG, MAX, etc...)
            to the select object.
        """
        q = select.queryForSelect().newItems(expressions).\
            unlimited().orderBy(None)
        q = self.sqlrepr(q)
        val = self.queryOne(q)
        if len(expressions) == 1:
            val = val[0]
        return val

    def queryForSelect(self, select):
        return self.sqlrepr(select.queryForSelect())

    def _SO_createJoinTable(self, join):
        self.query(self._SO_createJoinTableSQL(join))

    def _SO_createJoinTableSQL(self, join):
        return ('CREATE TABLE %s (\n%s %s,\n%s %s\n)' %
                (join.intermediateTable,
                 join.joinColumn,
                 self.joinSQLType(join),
                 join.otherColumn,
                 self.joinSQLType(join)))

    def _SO_dropJoinTable(self, join):
        self.query("DROP TABLE %s" % join.intermediateTable)

    def _SO_createIndex(self, soClass, index):
        self.query(self.createIndexSQL(soClass, index))

    def createIndexSQL(self, soClass, index):
        assert 0, 'Implement in subclasses'

    def createTable(self, soClass):
        createSql, constraints = self.createTableSQL(soClass)
        self.query(createSql)

        return constraints

    def createReferenceConstraints(self, soClass):
        refConstraints = [self.createReferenceConstraint(soClass, column)
                          for column in soClass.sqlmeta.columnList
                          if isinstance(column, col.SOForeignKey)]
        refConstraintDefs = [constraint for constraint in refConstraints
                             if constraint]
        return refConstraintDefs

    def createSQL(self, soClass):
        tableCreateSQLs = getattr(soClass.sqlmeta, 'createSQL', None)
        if tableCreateSQLs:
            assert isinstance(tableCreateSQLs, (str, list, dict, tuple)), (
                '%s.sqlmeta.createSQL must be a str, list, dict or tuple.' %
                (soClass.__name__))
            if isinstance(tableCreateSQLs, dict):
                tableCreateSQLs = tableCreateSQLs.get(
                    soClass._connection.dbName, [])
            if isinstance(tableCreateSQLs, str):
                tableCreateSQLs = [tableCreateSQLs]
            if isinstance(tableCreateSQLs, tuple):
                tableCreateSQLs = list(tableCreateSQLs)
            assert isinstance(tableCreateSQLs, list), (
                'Unable to create a list from %s.sqlmeta.createSQL' %
                (soClass.__name__))
        return tableCreateSQLs or []

    def createTableSQL(self, soClass):
        constraints = self.createReferenceConstraints(soClass)
        extraSQL = self.createSQL(soClass)
        createSql = ('CREATE TABLE %s (\n%s\n)' %
                     (soClass.sqlmeta.table, self.createColumns(soClass)))
        return createSql, constraints + extraSQL

    def createColumns(self, soClass):
        columnDefs = [self.createIDColumn(soClass)] \
            + [self.createColumn(soClass, col)
               for col in soClass.sqlmeta.columnList]
        return ",\n".join(["    %s" % c for c in columnDefs])

    def createReferenceConstraint(self, soClass, col):
        assert 0, "Implement in subclasses"

    def createColumn(self, soClass, col):
        assert 0, "Implement in subclasses"

    def dropTable(self, tableName, cascade=False):
        self.query("DROP TABLE %s" % tableName)

    def clearTable(self, tableName):
        # 3-03 @@: Should this have a WHERE 1 = 1 or similar
        # clause?  In some configurations without the WHERE clause
        # the query won't go through, but maybe we shouldn't override
        # that.
        self.query("DELETE FROM %s" % tableName)

    def createBinary(self, value):
        """
        Create a binary object wrapper for the given database.
        """
        # Default is Binary() function from the connection driver.
        return self.module.Binary(value)

    # The _SO_* series of methods are sorts of "friend" methods
    # with SQLObject.  They grab values from the SQLObject instances
    # or classes freely, but keep the SQLObject class from accessing
    # the database directly.  This way no SQL is actually created
    # in the SQLObject class.

    def _SO_update(self, so, values):
        self.query("UPDATE %s SET %s WHERE %s = (%s)" %
                   (so.sqlmeta.table,
                    ", ".join(["%s = (%s)" % (dbName, self.sqlrepr(value))
                               for dbName, value in values]),
                    so.sqlmeta.idName,
                    self.sqlrepr(so.id)))

    def _SO_selectOne(self, so, columnNames):
        return self._SO_selectOneAlt(so, columnNames, so.q.id == so.id)

    def _SO_selectOneAlt(self, so, columnNames, condition):
        if columnNames:
            columns = [isinstance(x, string_type) and
                       sqlbuilder.SQLConstant(x) or
                       x for x in columnNames]
        else:
            columns = None
        return self.queryOne(self.sqlrepr(sqlbuilder.Select(
            columns, staticTables=[so.sqlmeta.table], clause=condition)))

    def _SO_delete(self, so):
        self.query("DELETE FROM %s WHERE %s = (%s)" %
                   (so.sqlmeta.table,
                    so.sqlmeta.idName,
                    self.sqlrepr(so.id)))

    def _SO_selectJoin(self, soClass, column, value):
        return self.queryAll("SELECT %s FROM %s WHERE %s = (%s)" %
                             (soClass.sqlmeta.idName,
                              soClass.sqlmeta.table,
                              column,
                              self.sqlrepr(value)))

    def _SO_intermediateJoin(self, table, getColumn, joinColumn, value):
        return self.queryAll("SELECT %s FROM %s WHERE %s = (%s)" %
                             (getColumn,
                              table,
                              joinColumn,
                              self.sqlrepr(value)))

    def _SO_intermediateDelete(self, table, firstColumn, firstValue,
                               secondColumn, secondValue):
        self.query("DELETE FROM %s WHERE %s = (%s) AND %s = (%s)" %
                   (table,
                    firstColumn,
                    self.sqlrepr(firstValue),
                    secondColumn,
                    self.sqlrepr(secondValue)))

    def _SO_intermediateInsert(self, table, firstColumn, firstValue,
                               secondColumn, secondValue):
        self.query("INSERT INTO %s (%s, %s) VALUES (%s, %s)" %
                   (table,
                    firstColumn,
                    secondColumn,
                    self.sqlrepr(firstValue),
                    self.sqlrepr(secondValue)))

    def _SO_columnClause(self, soClass, kw):
        from . import main
        ops = {None: "IS"}
        data = []
        if 'id' in kw:
            data.append((soClass.sqlmeta.idName, kw.pop('id')))
        for soColumn in soClass.sqlmeta.columnList:
            key = soColumn.name
            if key in kw:
                val = kw.pop(key)
                if soColumn.from_python:
                    val = soColumn.from_python(
                        val,
                        sqlbuilder.SQLObjectState(soClass, connection=self))
                data.append((soColumn.dbName, val))
            elif soColumn.foreignName in kw:
                obj = kw.pop(soColumn.foreignName)
                if isinstance(obj, main.SQLObject):
                    data.append((soColumn.dbName, obj.id))
                else:
                    data.append((soColumn.dbName, obj))
        if kw:
            # pick the first key from kw to use to raise the error,
            raise TypeError("got an unexpected keyword argument(s): "
                            "%r" % kw.keys())

        if not data:
            return None
        return ' AND '.join(
            ['%s %s %s' %
             (dbName, ops.get(value, "="), self.sqlrepr(value))
             for dbName, value
             in data])

    def sqlrepr(self, v):
        return sqlrepr(v, self.dbName)

    def __del__(self):
        self.close()

    def close(self):
        if not hasattr(self, '_pool'):
            # Probably there was an exception while creating this
            # instance, so it is incomplete.
            return
        if not self._pool:
            return
        self._poolLock.acquire()
        try:
            if not self._pool:  # _pool could be filled in a different thread
                return
            conns = self._pool[:]
            self._pool[:] = []
            for conn in conns:
                try:
                    conn.close()
                except self.module.Error:
                    pass
            del conn
            del conns
        finally:
            self._poolLock.release()

    def createEmptyDatabase(self):
        """
        Create an empty database.
        """
        raise NotImplementedError

    def make_odbc_conn_str(self, odb_source, db, host=None, port=None,
                           user=None, password=None):
        odbc_conn_parts = ['Driver={%s}' % odb_source]
        for odbc_keyword, value in \
                zip(self.odbc_keywords, (host, port, user, password, db)):
            if value is not None:
                odbc_conn_parts.append('%s=%s' % (odbc_keyword, value))
        self.odbc_conn_str = ';'.join(odbc_conn_parts)


class Iteration(object):

    def __init__(self, dbconn, rawconn, select, keepConnection=False):
        self.dbconn = dbconn
        self.rawconn = rawconn
        self.select = select
        self.keepConnection = keepConnection
        self.cursor = rawconn.cursor()
        self.query = self.dbconn.queryForSelect(select)
        if dbconn.debug:
            dbconn.printDebug(rawconn, self.query, 'Select')
        self.dbconn._executeRetry(self.rawconn, self.cursor, self.query)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        result = self.cursor.fetchone()
        if result is None:
            self._cleanup()
            raise StopIteration
        if result[0] is None:
            return None
        if self.select.ops.get('lazyColumns', 0):
            obj = self.select.sourceClass.get(result[0],
                                              connection=self.dbconn)
            return obj
        else:
            obj = self.select.sourceClass.get(result[0],
                                              selectResults=result[1:],
                                              connection=self.dbconn)
            return obj

    def _cleanup(self):
        if getattr(self, 'query', None) is None:
            # already cleaned up
            return
        self.query = None
        if not self.keepConnection:
            self.dbconn.releaseConnection(self.rawconn)
        self.dbconn = self.rawconn = self.select = self.cursor = None

    def __del__(self):
        self._cleanup()


class Transaction(object):

    def __init__(self, dbConnection):
        # this is to skip __del__ in case of an exception in this __init__
        self._obsolete = True
        self._dbConnection = dbConnection
        self._connection = dbConnection.getConnection()
        self._dbConnection._setAutoCommit(self._connection, 0)
        self.cache = CacheSet(cache=dbConnection.doCache)
        self._deletedCache = {}
        self._obsolete = False

    def assertActive(self):
        assert not self._obsolete, \
            "This transaction has already gone through ROLLBACK; " \
            "begin another transaction"

    def query(self, s):
        self.assertActive()
        return self._dbConnection._query(self._connection, s)

    def queryAll(self, s):
        self.assertActive()
        return self._dbConnection._queryAll(self._connection, s)

    def queryOne(self, s):
        self.assertActive()
        return self._dbConnection._queryOne(self._connection, s)

    def queryInsertID(self, soInstance, id, names, values):
        self.assertActive()
        return self._dbConnection._queryInsertID(
            self._connection, soInstance, id, names, values)

    def iterSelect(self, select):
        self.assertActive()
        # We can't keep the cursor open with results in a transaction,
        # because we might want to use the connection while we're
        # still iterating through the results.
        # @@: But would it be okay for psycopg, with threadsafety
        # level 2?
        return iter(list(select.IterationClass(self, self._connection,
                                               select, keepConnection=True)))

    def _SO_delete(self, inst):
        cls = inst.__class__.__name__
        if cls not in self._deletedCache:
            self._deletedCache[cls] = []
        self._deletedCache[cls].append(inst.id)
        if PY2:
            meth = types.MethodType(self._dbConnection._SO_delete.__func__,
                                    self, self.__class__)
        else:
            meth = types.MethodType(self._dbConnection._SO_delete.__func__,
                                    self)
        return meth(inst)

    def commit(self, close=False):
        if self._obsolete:
            # @@: is it okay to get extraneous commits?
            return
        if self._dbConnection.debug:
            self._dbConnection.printDebug(self._connection, '', 'COMMIT')
        self._connection.commit()
        subCaches = [(sub[0], sub[1].allIDs())
                     for sub in self.cache.allSubCachesByClassNames().items()]
        subCaches.extend([(x[0], x[1]) for x in self._deletedCache.items()])
        for cls, ids in subCaches:
            for id in list(ids):
                inst = self._dbConnection.cache.tryGetByName(id, cls)
                if inst is not None:
                    inst.expire()
        if close:
            self._makeObsolete()

    def rollback(self):
        if self._obsolete:
            # @@: is it okay to get extraneous rollbacks?
            return
        if self._dbConnection.debug:
            self._dbConnection.printDebug(self._connection, '', 'ROLLBACK')
        subCaches = [(sub, sub.allIDs()) for sub in self.cache.allSubCaches()]
        self._connection.rollback()

        for subCache, ids in subCaches:
            for id in list(ids):
                inst = subCache.tryGet(id)
                if inst is not None:
                    inst.expire()
        self._makeObsolete()

    def __getattr__(self, attr):
        """
        If nothing else works, let the parent connection handle it.
        Except with this transaction as 'self'.  Poor man's
        acquisition?  Bad programming?  Okay, maybe.
        """
        self.assertActive()
        attr = getattr(self._dbConnection, attr)
        try:
            func = attr.__func__
        except AttributeError:
            if isinstance(attr, ConnWrapper):
                return ConnWrapper(attr._soClass, self)
            else:
                return attr
        else:
            if PY2:
                meth = types.MethodType(func, self, self.__class__)
            else:
                meth = types.MethodType(func, self)
            return meth

    def _makeObsolete(self):
        self._obsolete = True
        if self._dbConnection.autoCommit:
            self._dbConnection._setAutoCommit(self._connection, 1)
        self._dbConnection.releaseConnection(self._connection,
                                             explicit=True)
        self._connection = None
        self._deletedCache = {}

    def begin(self):
        # @@: Should we do this, or should begin() be a no-op when we're
        # not already obsolete?
        assert self._obsolete, \
            "You cannot begin a new transaction session " \
            "without rolling back this one"
        self._obsolete = False
        self._connection = self._dbConnection.getConnection()
        self._dbConnection._setAutoCommit(self._connection, 0)

    def __del__(self):
        if self._obsolete:
            return
        self.rollback()

    def close(self):
        raise TypeError('You cannot just close transaction - '
                        'you should either call rollback(), commit() '
                        'or commit(close=True) '
                        'to close the underlying connection.')


class ConnectionHub(object):

    """
    This object serves as a hub for connections, so that you can pass
    in a ConnectionHub to a SQLObject subclass as though it was a
    connection, but actually bind a real database connection later.
    You can also bind connections on a per-thread basis.

    You must hang onto the original ConnectionHub instance, as you
    cannot retrieve it again from the class or instance.

    To use the hub, do something like::

        hub = ConnectionHub()
        class MyClass(SQLObject):
            _connection = hub

        hub.threadConnection = connectionFromURI('...')

    """

    def __init__(self):
        self.threadingLocal = threading_local()

    def __get__(self, obj, type=None):
        # I'm a little surprised we have to do this, but apparently
        # the object's private dictionary of attributes doesn't
        # override this descriptor.
        if (obj is not None) and '_connection' in obj.__dict__:
            return obj.__dict__['_connection']
        return self.getConnection()

    def __set__(self, obj, value):
        obj.__dict__['_connection'] = value

    def getConnection(self):
        try:
            return self.threadingLocal.connection
        except AttributeError:
            try:
                return self.processConnection
            except AttributeError:
                raise AttributeError(
                    "No connection has been defined for this thread "
                    "or process")

    def doInTransaction(self, func, *args, **kw):
        """
        This routine can be used to run a function in a transaction,
        rolling the transaction back if any exception is raised from
        that function, and committing otherwise.

        Use like::

            sqlhub.doInTransaction(process_request, os.environ)

        This will run ``process_request(os.environ)``.  The return
        value will be preserved.
        """
        # @@: In Python 2.5, something usable with with: should also
        # be added.
        try:
            old_conn = self.threadingLocal.connection
            old_conn_is_threading = True
        except AttributeError:
            old_conn = self.processConnection
            old_conn_is_threading = False
        conn = old_conn.transaction()
        if old_conn_is_threading:
            self.threadConnection = conn
        else:
            self.processConnection = conn
        try:
            try:
                value = func(*args, **kw)
            except Exception:
                conn.rollback()
                raise
            else:
                conn.commit(close=True)
                return value
        finally:
            if old_conn_is_threading:
                self.threadConnection = old_conn
            else:
                self.processConnection = old_conn

    def _set_threadConnection(self, value):
        self.threadingLocal.connection = value

    def _get_threadConnection(self):
        return self.threadingLocal.connection

    def _del_threadConnection(self):
        del self.threadingLocal.connection

    threadConnection = property(_get_threadConnection,
                                _set_threadConnection,
                                _del_threadConnection)


class ConnectionURIOpener(object):

    def __init__(self):
        self.schemeBuilders = {}
        self.instanceNames = {}
        self.cachedURIs = {}

    def registerConnection(self, schemes, builder):
        for uriScheme in schemes:
            assert uriScheme not in self.schemeBuilders \
                or self.schemeBuilders[uriScheme] is builder, \
                "A driver has already been registered " \
                "for the URI scheme %s" % uriScheme
            self.schemeBuilders[uriScheme] = builder

    def registerConnectionInstance(self, inst):
        if inst.name:
            assert (inst.name not in self.instanceNames or
                    self.instanceNames[inst.name] is cls  # noqa
                ), ("A instance has already been registered "
                "with the name %s" % inst.name)
            assert inst.name.find(':') == -1, \
                "You cannot include ':' " \
                "in your class names (%r)" % cls.name  # noqa
            self.instanceNames[inst.name] = inst

    def connectionForURI(self, uri, oldUri=False, **args):
        if args:
            if '?' not in uri:
                uri += '?' + urlencode(args)
            else:
                uri += '&' + urlencode(args)
        if uri in self.cachedURIs:
            return self.cachedURIs[uri]
        if uri.find(':') != -1:
            scheme, rest = uri.split(':', 1)
            connCls = self.dbConnectionForScheme(scheme)
            if oldUri:
                conn = connCls.connectionFromOldURI(uri)
            else:
                conn = connCls.connectionFromURI(uri)
        else:
            # We just have a name, not a URI
            assert uri in self.instanceNames, \
                "No SQLObject driver exists under the name %s" % uri
            conn = self.instanceNames[uri]
        # @@: Do we care if we clobber another connection?
        self.cachedURIs[uri] = conn
        return conn

    def dbConnectionForScheme(self, scheme):
        assert scheme in self.schemeBuilders, (
            "No SQLObject driver exists for %s (only %s)" % (
                scheme,
                ', '.join(self.schemeBuilders.keys())))
        return self.schemeBuilders[scheme]()

TheURIOpener = ConnectionURIOpener()

registerConnection = TheURIOpener.registerConnection
registerConnectionInstance = TheURIOpener.registerConnectionInstance
connectionForURI = TheURIOpener.connectionForURI
dbConnectionForScheme = TheURIOpener.dbConnectionForScheme

# Register DB URI schemas -- do import for side effects
# noqa is a directive for flake8 to ignore seemingly unused imports
from . import firebird  # noqa
from . import maxdb  # noqa
from . import mssql  # noqa
from . import mysql  # noqa
from . import postgres  # noqa
from . import rdbhost  # noqa
from . import sqlite  # noqa
from . import sybase  # noqa
