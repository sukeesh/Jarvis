import base64
import os
try:
    from _thread import get_ident
except ImportError:
    from thread import get_ident
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote
from sqlobject import col
from sqlobject import dberrors
from sqlobject.dbconnection import DBAPI, Boolean


sqlite2_Binary = None


class ErrorMessage(str):
    def __new__(cls, e):
        obj = str.__new__(cls, e.args[0])
        obj.code = None
        obj.module = e.__module__
        obj.exception = e.__class__.__name__
        return obj


class SQLiteConnection(DBAPI):

    supportTransactions = True
    dbName = 'sqlite'
    schemes = [dbName]

    def __init__(self, filename, autoCommit=1, **kw):
        drivers = kw.pop('driver', None) or 'pysqlite2,sqlite3,sqlite'
        for driver in drivers.split(','):
            driver = driver.strip()
            if not driver:
                continue
            try:
                if driver in ('sqlite2', 'pysqlite2'):
                        from pysqlite2 import dbapi2 as sqlite
                        self.using_sqlite2 = True
                elif driver == 'sqlite3':
                        import sqlite3 as sqlite
                        self.using_sqlite2 = True
                elif driver in ('sqlite', 'sqlite1'):
                        import sqlite
                        self.using_sqlite2 = False
                else:
                    raise ValueError(
                        'Unknown SQLite driver "%s", '
                        'expected pysqlite2, sqlite3 or sqlite' % driver)
            except ImportError:
                pass
            else:
                break
        else:
            raise ImportError(
                'Cannot find an SQLite driver, tried %s' % drivers)
        if self.using_sqlite2:
            sqlite.encode = base64.b64encode
            sqlite.decode = base64.b64decode
        self.module = sqlite
        self.filename = filename  # full path to sqlite-db-file
        self._memory = filename == ':memory:'
        if self._memory and not self.using_sqlite2:
            raise ValueError("You must use sqlite2 to use in-memory databases")
        # connection options
        opts = {}
        if self.using_sqlite2:
            if autoCommit:
                opts["isolation_level"] = None
            global sqlite2_Binary
            if sqlite2_Binary is None:
                sqlite2_Binary = sqlite.Binary
                sqlite.Binary = lambda s: sqlite2_Binary(sqlite.encode(s))
            if 'factory' in kw:
                factory = kw.pop('factory')
                if isinstance(factory, str):
                    factory = globals()[factory]
                opts['factory'] = factory(sqlite)
        else:
            opts['autocommit'] = Boolean(autoCommit)
            if 'encoding' in kw:
                opts['encoding'] = kw.pop('encoding')
            if 'mode' in kw:
                opts['mode'] = int(kw.pop('mode'), 0)
        if 'timeout' in kw:
            if self.using_sqlite2:
                opts['timeout'] = float(kw.pop('timeout'))
            else:
                opts['timeout'] = int(float(kw.pop('timeout')) * 1000)
        if 'check_same_thread' in kw:
            opts["check_same_thread"] = Boolean(kw.pop('check_same_thread'))
        # use only one connection for sqlite - supports multiple)
        # cursors per connection
        self._connOptions = opts
        self.use_table_info = Boolean(kw.pop("use_table_info", True))
        DBAPI.__init__(self, **kw)
        self._threadPool = {}
        self._threadOrigination = {}
        if self._memory:
            self.makeMemoryConnection()

    @classmethod
    def _connectionFromParams(cls, user, password, host, port, path, args):
        assert host is None and port is None, (
            "SQLite can only be used locally (with a URI like "
            "sqlite:/file or sqlite:///file, not sqlite://%s%s)" %
            (host, port and ':%r' % port or ''))
        assert user is None and password is None, (
            "You may not provide usernames or passwords for SQLite "
            "databases")
        if path == "/:memory:":
            path = ":memory:"
        return cls(filename=path, **args)

    def oldUri(self):
        path = self.filename
        if path == ":memory:":
            path = "/:memory:"
        else:
            path = "//" + path
        return 'sqlite:%s' % path

    def uri(self):
        path = self.filename
        if path == ":memory:":
            path = "/:memory:"
        else:
            if path.startswith('/'):
                path = "//" + path
            else:
                path = "///" + path
            path = quote(path)
        return 'sqlite:%s' % path

    def getConnection(self):
        # SQLite can't share connections between threads, and so can't
        # pool connections.  Since we are isolating threads here, we
        # don't have to worry about locking as much.
        if self._memory:
            conn = self.makeConnection()
            self._connectionNumbers[id(conn)] = self._connectionCount
            self._connectionCount += 1
            return conn
        threadid = get_ident()
        if (self._pool is not None and threadid in self._threadPool):
            conn = self._threadPool[threadid]
            del self._threadPool[threadid]
            if conn in self._pool:
                self._pool.remove(conn)
        else:
            conn = self.makeConnection()
            if self._pool is not None:
                self._threadOrigination[id(conn)] = threadid
            self._connectionNumbers[id(conn)] = self._connectionCount
            self._connectionCount += 1
        if self.debug:
            s = 'ACQUIRE'
            if self._pool is not None:
                s += ' pool=[%s]' % ', '.join(
                    [str(self._connectionNumbers[id(v)]) for v in self._pool])
            self.printDebug(conn, s, 'Pool')
        return conn

    def releaseConnection(self, conn, explicit=False):
        if self._memory:
            return
        threadid = self._threadOrigination.get(id(conn))
        DBAPI.releaseConnection(self, conn, explicit=explicit)
        if (self._pool is not None and threadid and
                threadid not in self._threadPool):
            self._threadPool[threadid] = conn
        else:
            if self._pool and conn in self._pool:
                self._pool.remove(conn)
            conn.close()

    def _setAutoCommit(self, conn, auto):
        if self.using_sqlite2:
            if auto:
                conn.isolation_level = None
            else:
                conn.isolation_level = ""
        else:
            conn.autocommit = auto

    def _setIsolationLevel(self, conn, level):
        if not self.using_sqlite2:
            return
        conn.isolation_level = level

    def makeMemoryConnection(self):
        self._memoryConn = self.module.connect(
            self.filename, **self._connOptions)
        # Convert text data from SQLite to str, not unicode -
        # SQLObject converts it to unicode itself.
        self._memoryConn.text_factory = str

    def makeConnection(self):
        if self._memory:
            return self._memoryConn
        conn = self.module.connect(self.filename, **self._connOptions)
        conn.text_factory = str  # Convert text data to str, not unicode
        return conn

    def close(self):
        DBAPI.close(self)
        self._threadPool = {}
        if self._memory:
            self._memoryConn.close()
            self.makeMemoryConnection()

    def _executeRetry(self, conn, cursor, query):
        if self.debug:
            self.printDebug(conn, query, 'QueryR')
        try:
            return cursor.execute(query)
        except self.module.OperationalError as e:
            raise dberrors.OperationalError(ErrorMessage(e))
        except self.module.IntegrityError as e:
            msg = ErrorMessage(e)
            if msg.startswith('column') and msg.endswith('not unique') \
                    or msg.startswith('UNIQUE constraint failed:'):
                raise dberrors.DuplicateEntryError(msg)
            else:
                raise dberrors.IntegrityError(msg)
        except self.module.InternalError as e:
            raise dberrors.InternalError(ErrorMessage(e))
        except self.module.ProgrammingError as e:
            raise dberrors.ProgrammingError(ErrorMessage(e))
        except self.module.DataError as e:
            raise dberrors.DataError(ErrorMessage(e))
        except self.module.NotSupportedError as e:
            raise dberrors.NotSupportedError(ErrorMessage(e))
        except self.module.DatabaseError as e:
            raise dberrors.DatabaseError(ErrorMessage(e))
        except self.module.InterfaceError as e:
            raise dberrors.InterfaceError(ErrorMessage(e))
        except self.module.Warning as e:
            raise Warning(ErrorMessage(e))
        except self.module.Error as e:
            raise dberrors.Error(ErrorMessage(e))

    def _queryInsertID(self, conn, soInstance, id, names, values):
        table = soInstance.sqlmeta.table
        idName = soInstance.sqlmeta.idName
        c = conn.cursor()
        if id is not None:
            names = [idName] + names
            values = [id] + values
        q = self._insertSQL(table, names, values)
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        self._executeRetry(conn, c, q)
        # lastrowid is a DB-API extension from "PEP 0249":
        if id is None:
            id = int(c.lastrowid)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    def _insertSQL(self, table, names, values):
        if not names:
            assert not values
            # INSERT INTO table () VALUES () isn't allowed in
            # SQLite (though it is in other databases)
            return ("INSERT INTO %s VALUES (NULL)" % table)
        else:
            return DBAPI._insertSQL(self, table, names, values)

    @classmethod
    def _queryAddLimitOffset(cls, query, start, end):
        if not start:
            return "%s LIMIT %i" % (query, end)
        if not end:
            return "%s LIMIT 0 OFFSET %i" % (query, start)
        return "%s LIMIT %i OFFSET %i" % (query, end - start, start)

    def createColumn(self, soClass, col):
        return col.sqliteCreateSQL()

    def createReferenceConstraint(self, soClass, col):
        return None

    def createIDColumn(self, soClass):
        return self._createIDColumn(soClass.sqlmeta)

    def _createIDColumn(self, sqlmeta):
        if sqlmeta.idType == str:
            return '%s TEXT PRIMARY KEY' % sqlmeta.idName
        return '%s INTEGER PRIMARY KEY AUTOINCREMENT' % sqlmeta.idName

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        result = self.queryOne(
            "SELECT tbl_name FROM sqlite_master "
            "WHERE type='table' AND tbl_name = '%s'" % tableName)
        # turn it into a boolean:
        return not not result

    def createIndexSQL(self, soClass, index):
        return index.sqliteCreateIndexSQL(soClass)

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.sqliteCreateSQL()))
        self.query('VACUUM')

    def delColumn(self, sqlmeta, column):
        self.recreateTableWithoutColumn(sqlmeta, column)

    def recreateTableWithoutColumn(self, sqlmeta, column):
        new_name = sqlmeta.table + '_ORIGINAL'
        self.query('ALTER TABLE %s RENAME TO %s' % (sqlmeta.table, new_name))
        cols = [self._createIDColumn(sqlmeta)] + \
            [self.createColumn(None, col)
                for col in sqlmeta.columnList if col.name != column.name]
        cols = ",\n".join(["    %s" % c for c in cols])
        self.query('CREATE TABLE %s (\n%s\n)' % (sqlmeta.table, cols))
        all_columns = ', '.join(
            [sqlmeta.idName] + [col.dbName for col in sqlmeta.columnList])
        self.query('INSERT INTO %s (%s) SELECT %s FROM %s' % (
            sqlmeta.table, all_columns, all_columns, new_name))
        self.query('DROP TABLE %s' % new_name)

    def columnsFromSchema(self, tableName, soClass):
        if self.use_table_info:
            return self._columnsFromSchemaTableInfo(tableName, soClass)
        else:
            return self._columnsFromSchemaParse(tableName, soClass)

    def _columnsFromSchemaTableInfo(self, tableName, soClass):
        colData = self.queryAll("PRAGMA table_info(%s)" % tableName)
        results = []
        for index, field, t, nullAllowed, default, key in colData:
            if field == soClass.sqlmeta.idName:
                continue
            colClass, kw = self.guessClass(t)
            if default == 'NULL':
                nullAllowed = True
                default = None
            kw['name'] = soClass.sqlmeta.style.dbColumnToPythonAttr(field)
            kw['dbName'] = field
            kw['notNone'] = not nullAllowed
            kw['default'] = default
            # @@ skip key...
            # @@ skip extra...
            results.append(colClass(**kw))
        return results

    def _columnsFromSchemaParse(self, tableName, soClass):
        colData = self.queryOne(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='%s'" %
            tableName)
        if not colData:
            raise ValueError(
                'The table %s was not found in the database. Load failed.' %
                tableName)
        colData = colData[0].split('(', 1)[1].strip()[:-2]
        while True:
            start = colData.find('(')
            if start == -1:
                break
            end = colData.find(')', start)
            if end == -1:
                break
            colData = colData[:start] + colData[end + 1:]
        results = []
        for colDesc in colData.split(','):
            parts = colDesc.strip().split(' ', 2)
            field = parts[0].strip()
            # skip comments
            if field.startswith('--'):
                continue
            # get rid of enclosing quotes
            if field[0] == field[-1] == '"':
                field = field[1:-1]
            if field == getattr(soClass.sqlmeta, 'idName', 'id'):
                continue
            colClass, kw = self.guessClass(parts[1].strip())
            if len(parts) == 2:
                index_info = ''
            else:
                index_info = parts[2].strip().upper()
            kw['name'] = soClass.sqlmeta.style.dbColumnToPythonAttr(field)
            kw['dbName'] = field
            import re
            nullble = re.search(r'(\b\S*)\sNULL', index_info)
            default = re.search(
                r"DEFAULT\s((?:\d[\dA-FX.]*)|(?:'[^']*')|(?:#[^#]*#))",
                index_info)
            kw['notNone'] = nullble and nullble.group(1) == 'NOT'
            kw['default'] = default and default.group(1)
            # @@ skip key...
            # @@ skip extra...
            results.append(colClass(**kw))
        return results

    def guessClass(self, t):
        t = t.upper()
        if t.find('INT') >= 0:
            return col.IntCol, {}
        elif t.find('TEXT') >= 0 or t.find('CHAR') >= 0 or t.find('CLOB') >= 0:
            return col.StringCol, {'length': 2 ** 32 - 1}
        elif t.find('BLOB') >= 0:
            return col.BLOBCol, {"length": 2 ** 32 - 1}
        elif t.find('REAL') >= 0 or t.find('FLOAT') >= 0:
            return col.FloatCol, {}
        elif t.find('DECIMAL') >= 0:
            return col.DecimalCol, {'size': None, 'precision': None}
        elif t.find('BOOL') >= 0:
            return col.BoolCol, {}
        else:
            return col.Col, {}

    def listTables(self):
        return [v[0] for v in self.queryAll(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]

    def listDatabases(self):
        # The pragma returns a list of (index, name, filename)
        return [v[1] for v in self.queryAll("PRAGMA database_list")]

    def createEmptyDatabase(self):
        if self._memory:
            return
        open(self.filename, 'w').close()

    def dropDatabase(self):
        if self._memory:
            return
        os.unlink(self.filename)
