from getpass import getuser
import re
from sqlobject import col
from sqlobject import dberrors
from sqlobject import sqlbuilder
from sqlobject.compat import PY2
from sqlobject.converters import registerConverter, sqlrepr
from sqlobject.dbconnection import DBAPI


class ErrorMessage(str):
    def __new__(cls, e, append_msg=''):
        obj = str.__new__(cls, e.args[0] + append_msg)
        if e.__module__ == 'psycopg2':
            obj.code = getattr(e, 'pgcode', None)
            obj.error = getattr(e, 'pgerror', None)
        else:
            obj.code = getattr(e, 'code', None)
            obj.error = getattr(e, 'error', None)
        obj.module = e.__module__
        obj.exception = e.__class__.__name__
        return obj


class PostgresConnection(DBAPI):

    supportTransactions = True
    dbName = 'postgres'
    schemes = [dbName, 'postgresql']

    odbc_keywords = ('Server', 'Port', 'UID', 'Password', 'Database')

    def __init__(self, dsn=None, host=None, port=None, db=None,
                 user=None, password=None, **kw):
        drivers = kw.pop('driver', None) or 'psycopg'
        for driver in drivers.split(','):
            driver = driver.strip()
            if not driver:
                continue
            try:
                if driver == 'psycopg2':
                    import psycopg2 as psycopg
                    self.module = psycopg
                elif driver == 'psycopg1':
                    import psycopg
                    self.module = psycopg
                elif driver == 'psycopg':
                    try:
                        import psycopg2 as psycopg
                    except ImportError:
                        import psycopg
                    self.module = psycopg
                elif driver == 'pygresql':
                    import pgdb
                    self.module = pgdb
                elif driver in ('py-postgresql', 'pypostgresql'):
                    from postgresql.driver import dbapi20
                    self.module = dbapi20
                elif driver == 'pg8000':
                    import pg8000
                    self.module = pg8000
                elif driver == 'pyodbc':
                    import pyodbc
                    self.module = pyodbc
                elif driver == 'pypyodbc':
                    import pypyodbc
                    self.module = pypyodbc
                elif driver == 'odbc':
                    try:
                        import pyodbc
                    except ImportError:
                        import pypyodbc as pyodbc
                    self.module = pyodbc
                else:
                    raise ValueError(
                        'Unknown PostgreSQL driver "%s", '
                        'expected psycopg, psycopg2, psycopg1, '
                        'pygresql, pypostgresql, pg8000, '
                        'odbc, pyodbc or pypyodbc' % driver)
            except ImportError:
                pass
            else:
                break
        else:
            raise ImportError(
                'Cannot find a PostgreSQL driver, tried %s' % drivers)

        if driver.startswith('psycopg'):
            # Register a converter for psycopg Binary type.
            registerConverter(type(self.module.Binary('')),
                              PsycoBinaryConverter)
        elif driver in ('pygresql', 'py-postgresql', 'pypostgresql', 'pg8000'):
            registerConverter(type(self.module.Binary(b'')),
                              PostgresBinaryConverter)
        elif driver in ('odbc', 'pyodbc', 'pypyodbc'):
            registerConverter(bytearray, OdbcBinaryConverter)

        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        if driver in ('odbc', 'pyodbc', 'pypyodbc'):
            self.make_odbc_conn_str(kw.pop('odbcdrv', 'PostgreSQL ANSI'),
                                    db, host, port, user, password
                                    )
            sslmode = kw.pop("sslmode", None)
            if sslmode:
                self.odbc_conn_str += ';sslmode=require'
        else:
            self.dsn_dict = dsn_dict = {}
            if host:
                dsn_dict["host"] = host
            if port:
                if driver == 'pygresql':
                    dsn_dict["host"] = "%s:%d" % (host, port)
                elif driver.startswith('psycopg') and \
                        psycopg.__version__.split('.')[0] == '1':
                    dsn_dict["port"] = str(port)
                else:
                    dsn_dict["port"] = port
            if db:
                dsn_dict["database"] = db
            if user:
                dsn_dict["user"] = user
            if password:
                dsn_dict["password"] = password
            sslmode = kw.pop("sslmode", None)
            if sslmode:
                dsn_dict["sslmode"] = sslmode
            self.use_dsn = dsn is not None
            if dsn is None:
                if driver == 'pygresql':
                    dsn = ''
                    if host:
                        dsn += host
                    dsn += ':'
                    if db:
                        dsn += db
                    dsn += ':'
                    if user:
                        dsn += user
                    dsn += ':'
                    if password:
                        dsn += password
                else:
                    dsn = []
                    if db:
                        dsn.append('dbname=%s' % db)
                    if user:
                        dsn.append('user=%s' % user)
                    if password:
                        dsn.append('password=%s' % password)
                    if host:
                        dsn.append('host=%s' % host)
                    if port:
                        dsn.append('port=%d' % port)
                    if sslmode:
                        dsn.append('sslmode=%s' % sslmode)
                    dsn = ' '.join(dsn)
            if driver in ('py-postgresql', 'pypostgresql'):
                if host and host.startswith('/'):
                    dsn_dict["host"] = dsn_dict["port"] = None
                    dsn_dict["unix"] = host
                else:
                    if "unix" in dsn_dict:
                        del dsn_dict["unix"]
            if driver == 'pg8000':
                if host and host.startswith('/'):
                    dsn_dict["host"] = None
                    dsn_dict["unix_sock"] = host
                if user is None:
                    dsn_dict["user"] = getuser()
            self.dsn = dsn
        self.driver = driver
        self.unicodeCols = kw.pop('unicodeCols', False)
        self.schema = kw.pop('schema', None)
        self.dbEncoding = kw.pop("charset", None)
        DBAPI.__init__(self, **kw)

    @classmethod
    def _connectionFromParams(cls, user, password, host, port, path, args):
        path = path.strip('/')
        if (host is None) and path.count('/'):  # Non-default unix socket
            path_parts = path.split('/')
            host = '/' + '/'.join(path_parts[:-1])
            path = path_parts[-1]
        return cls(host=host, port=port, db=path,
                   user=user, password=password, **args)

    def _setAutoCommit(self, conn, auto):
        # psycopg2 does not have an autocommit method.
        if hasattr(conn, 'autocommit'):
            try:
                conn.autocommit(auto)
            except TypeError:
                conn.autocommit = auto

    def makeConnection(self):
        try:
            if self.driver in ('odbc', 'pyodbc', 'pypyodbc'):
                self.debugWriter.write(
                    "ODBC connect string: " + self.odbc_conn_str)
                conn = self.module.connect(self.odbc_conn_str)
            elif self.use_dsn:
                conn = self.module.connect(self.dsn)
            else:
                conn = self.module.connect(**self.dsn_dict)
        except self.module.OperationalError as e:
            raise dberrors.OperationalError(
                ErrorMessage(e, "used connection string %r" % self.dsn))

        # For printDebug in _executeRetry
        self._connectionNumbers[id(conn)] = self._connectionCount

        if self.autoCommit:
            self._setAutoCommit(conn, 1)
        c = conn.cursor()
        if self.schema:
            self._executeRetry(conn, c, "SET search_path TO " + self.schema)
        dbEncoding = self.dbEncoding
        if dbEncoding:
            if self.driver in ('odbc', 'pyodbc'):
                conn.setdecoding(self.module.SQL_CHAR, encoding=dbEncoding)
                conn.setdecoding(self.module.SQL_WCHAR, encoding=dbEncoding)
                if PY2:
                    conn.setencoding(str, encoding=dbEncoding)
                    conn.setencoding(unicode, encoding=dbEncoding)  # noqa
                else:
                    conn.setencoding(encoding=dbEncoding)
            self._executeRetry(conn, c,
                               "SET client_encoding TO '%s'" % dbEncoding)
        return conn

    def _executeRetry(self, conn, cursor, query):
        if self.debug:
            self.printDebug(conn, query, 'QueryR')
        dbEncoding = self.dbEncoding
        if dbEncoding and isinstance(query, bytes) and (
                self.driver == 'pg8000'):
            query = query.decode(dbEncoding)
        try:
            return cursor.execute(query)
        except self.module.OperationalError as e:
            raise dberrors.OperationalError(ErrorMessage(e))
        except self.module.IntegrityError as e:
            msg = ErrorMessage(e)
            if getattr(e, 'code', -1) == '23505' or \
                    getattr(e, 'pgcode', -1) == '23505' or \
                    getattr(e, 'sqlstate', -1) == '23505' or \
                    e.args[0] == '23505':
                raise dberrors.DuplicateEntryError(msg)
            else:
                raise dberrors.IntegrityError(msg)
        except self.module.InternalError as e:
            raise dberrors.InternalError(ErrorMessage(e))
        except self.module.ProgrammingError as e:
            msg = ErrorMessage(e)
            if (
                (len(e.args) > 2) and (e.args[1] == 'ERROR') and
                    (e.args[2] == '23505')) \
                    or ((len(e.args) >= 2) and (e.args[1] == '23505')):
                raise dberrors.DuplicateEntryError(msg)
            else:
                raise dberrors.ProgrammingError(msg)
        except self.module.DataError as e:
            raise dberrors.DataError(ErrorMessage(e))
        except self.module.NotSupportedError as e:
            raise dberrors.NotSupportedError(ErrorMessage(e))
        except self.module.DatabaseError as e:
            msg = ErrorMessage(e)
            if 'duplicate key value violates unique constraint' in msg:
                raise dberrors.DuplicateEntryError(msg)
            else:
                raise dberrors.DatabaseError(msg)
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
        if id is None and self.driver in ('py-postgresql', 'pypostgresql'):
            sequenceName = soInstance.sqlmeta.idSequence or \
                '%s_%s_seq' % (table, idName)
            self._executeRetry(conn, c, "SELECT NEXTVAL('%s')" % sequenceName)
            id = c.fetchone()[0]
        if id is not None:
            names = [idName] + names
            values = [id] + values
        if names and values:
            q = self._insertSQL(table, names, values)
        else:
            q = "INSERT INTO %s DEFAULT VALUES" % table
        if id is None:
            q += " RETURNING " + idName
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        self._executeRetry(conn, c, q)
        if id is None:
            id = c.fetchone()[0]
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    @classmethod
    def _queryAddLimitOffset(cls, query, start, end):
        if not start:
            return "%s LIMIT %i" % (query, end)
        if not end:
            return "%s OFFSET %i" % (query, start)
        return "%s LIMIT %i OFFSET %i" % (query, end - start, start)

    def createColumn(self, soClass, col):
        return col.postgresCreateSQL()

    def createReferenceConstraint(self, soClass, col):
        return col.postgresCreateReferenceConstraint()

    def createIndexSQL(self, soClass, index):
        return index.postgresCreateIndexSQL(soClass)

    def createIDColumn(self, soClass):
        key_type = {int: "SERIAL", str: "TEXT"}[soClass.sqlmeta.idType]
        return '%s %s PRIMARY KEY' % (soClass.sqlmeta.idName, key_type)

    def dropTable(self, tableName, cascade=False):
        self.query("DROP TABLE %s %s" % (tableName,
                                         cascade and 'CASCADE' or ''))

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        result = self.queryOne(
            "SELECT COUNT(relname) FROM pg_class WHERE relname = %s" %
            self.sqlrepr(tableName))
        return result[0]

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.postgresCreateSQL()))

    def delColumn(self, sqlmeta, column):
        self.query('ALTER TABLE %s DROP COLUMN %s' % (sqlmeta.table,
                                                      column.dbName))

    def columnsFromSchema(self, tableName, soClass):

        keyQuery = """
        SELECT pg_catalog.pg_get_constraintdef(oid) as condef
        FROM pg_catalog.pg_constraint r
        WHERE r.conrelid = %s::regclass AND r.contype = 'f'"""

        colQuery = """
        SELECT a.attname,
        pg_catalog.format_type(a.atttypid, a.atttypmod), a.attnotnull,
        (SELECT substring(d.adsrc for 128) FROM pg_catalog.pg_attrdef d
        WHERE d.adrelid=a.attrelid AND d.adnum = a.attnum)
        FROM pg_catalog.pg_attribute a
        WHERE a.attrelid =%s::regclass
        AND a.attnum > 0 AND NOT a.attisdropped
        ORDER BY a.attnum"""

        primaryKeyQuery = """
        SELECT pg_index.indisprimary,
            pg_catalog.pg_get_indexdef(pg_index.indexrelid)
        FROM pg_catalog.pg_class c, pg_catalog.pg_class c2,
            pg_catalog.pg_index AS pg_index
        WHERE c.relname = %s
            AND c.oid = pg_index.indrelid
            AND pg_index.indexrelid = c2.oid
            AND pg_index.indisprimary
        """

        otherKeyQuery = """
        SELECT pg_index.indisprimary,
            pg_catalog.pg_get_indexdef(pg_index.indexrelid)
        FROM pg_catalog.pg_class c, pg_catalog.pg_class c2,
            pg_catalog.pg_index AS pg_index
        WHERE c.relname = %s
            AND c.oid = pg_index.indrelid
            AND pg_index.indexrelid = c2.oid
            AND NOT pg_index.indisprimary
        """

        keyData = self.queryAll(keyQuery % self.sqlrepr(tableName))
        keyRE = re.compile(r"\((.+)\) REFERENCES (.+)\(")
        keymap = {}

        for (condef,) in keyData:
            match = keyRE.search(condef)
            if match:
                field, reftable = match.groups()
                keymap[field] = reftable.capitalize()

        primaryData = self.queryAll(primaryKeyQuery % self.sqlrepr(tableName))
        primaryRE = re.compile(r'CREATE .*? USING .* \((.+?)\)')
        primaryKey = None
        for isPrimary, indexDef in primaryData:
            match = primaryRE.search(indexDef)
            assert match, "Unparseable contraint definition: %r" % indexDef
            assert primaryKey is None, \
                "Already found primary key (%r), " \
                "then found: %r" % (primaryKey, indexDef)
            primaryKey = match.group(1)
        if primaryKey is None:
            # VIEWs don't have PRIMARY KEYs - accept help from user
            primaryKey = soClass.sqlmeta.idName
        assert primaryKey, "No primary key found in table %r" % tableName
        if primaryKey.startswith('"'):
            assert primaryKey.endswith('"')
            primaryKey = primaryKey[1:-1]

        otherData = self.queryAll(otherKeyQuery % self.sqlrepr(tableName))
        otherRE = primaryRE
        otherKeys = []
        for isPrimary, indexDef in otherData:
            match = otherRE.search(indexDef)
            assert match, "Unparseable constraint definition: %r" % indexDef
            otherKey = match.group(1)
            if otherKey.startswith('"'):
                assert otherKey.endswith('"')
                otherKey = otherKey[1:-1]
            otherKeys.append(otherKey)

        colData = self.queryAll(colQuery % self.sqlrepr(tableName))
        results = []
        if self.unicodeCols:
            client_encoding = self.queryOne("SHOW client_encoding")[0]
        for field, t, notnull, defaultstr in colData:
            if field == primaryKey:
                continue
            if field in keymap:
                colClass = col.ForeignKey
                kw = {'foreignKey': soClass.sqlmeta.style.
                      dbTableToPythonClass(keymap[field])}
                name = soClass.sqlmeta.style.dbColumnToPythonAttr(field)
                if name.endswith('ID'):
                    name = name[:-2]
                kw['name'] = name
            else:
                colClass, kw = self.guessClass(t)
                if self.unicodeCols and colClass is col.StringCol:
                    colClass = col.UnicodeCol
                    kw['dbEncoding'] = client_encoding
                kw['name'] = soClass.sqlmeta.style.dbColumnToPythonAttr(field)
            kw['dbName'] = field
            kw['notNone'] = notnull
            if defaultstr is not None:
                kw['default'] = self.defaultFromSchema(colClass, defaultstr)
            elif not notnull:
                kw['default'] = None
            if field in otherKeys:
                kw['alternateID'] = True
            results.append(colClass(**kw))
        return results

    def guessClass(self, t):
        if t.count('point'):  # poINT before INT
            return col.StringCol, {}
        elif t.count('int'):
            return col.IntCol, {}
        elif t.count('varying') or t.count('varchar'):
            if '(' in t:
                return col.StringCol, {'length': int(t[t.index('(') + 1:-1])}
            else:  # varchar without length in Postgres means any length
                return col.StringCol, {}
        elif t.startswith('character('):
            return col.StringCol, {'length': int(t[t.index('(') + 1:-1]),
                                   'varchar': False}
        elif t.count('float') or t.count('real') or t.count('double'):
            return col.FloatCol, {}
        elif t == 'text':
            return col.StringCol, {}
        elif t.startswith('timestamp'):
            return col.DateTimeCol, {}
        elif t.startswith('datetime'):
            return col.DateTimeCol, {}
        elif t.startswith('date'):
            return col.DateCol, {}
        elif t.startswith('bool'):
            return col.BoolCol, {}
        elif t.startswith('bytea'):
            return col.BLOBCol, {}
        else:
            return col.Col, {}

    def defaultFromSchema(self, colClass, defaultstr):
        """
        If the default can be converted to a python constant, convert it.
        Otherwise return is as a sqlbuilder constant.
        """
        if colClass == col.BoolCol:
            if defaultstr == 'false':
                return False
            elif defaultstr == 'true':
                return True
        return getattr(sqlbuilder.const, defaultstr)

    def _createOrDropDatabase(self, op="CREATE"):
        # We have to connect to *some* database, so we'll connect to
        # template1, which is a common open database.
        # @@: This doesn't use self.use_dsn or self.dsn_dict
        if self.driver == 'pygresql':
            dsn = '%s:template1:%s:%s' % (
                self.host or '', self.user or '', self.password or '')
        else:
            dsn = 'dbname=template1'
            if self.user:
                dsn += ' user=%s' % self.user
            if self.password:
                dsn += ' password=%s' % self.password
            if self.host:
                dsn += ' host=%s' % self.host
        conn = self.module.connect(dsn)
        cur = conn.cursor()
        # We must close the transaction with a commit so that
        # the CREATE DATABASE can work (which can't be in a transaction):
        try:
            self._executeRetry(conn, cur, 'COMMIT')
            self._executeRetry(conn, cur, '%s DATABASE %s' % (op, self.db))
        finally:
            cur.close()
            conn.close()

    def listTables(self):
        return [v[0] for v in self.queryAll(
            """SELECT c.relname FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r','') AND
            n.nspname NOT IN ('pg_catalog', 'pg_toast') AND
            pg_catalog.pg_table_is_visible(c.oid)""")]

    def listDatabases(self):
        return [v[0] for v in self.queryAll("SELECT datname FROM pg_database")]

    def createEmptyDatabase(self):
        self._createOrDropDatabase()

    def dropDatabase(self):
        self._createOrDropDatabase(op="DROP")


# Converter for Binary types
def PsycoBinaryConverter(value, db):
    assert db == 'postgres'
    return str(value)


if PY2:
    def escape_bytea(value):
        return ''.join(
            ['\\' + (x[1:].rjust(3, '0'))
                for x in (oct(ord(c)) for c in value)]
        )
else:
    def escape_bytea(value):
        return ''.join(
            ['\\' + (x[2:].rjust(3, '0'))
                for x in (oct(ord(c)) for c in value.decode('latin1'))]
        )


def PostgresBinaryConverter(value, db):
    assert db == 'postgres'
    return sqlrepr(escape_bytea(value), db)


def OdbcBinaryConverter(value, db):
    assert db == 'postgres'
    value = bytes(value)
    if not PY2:
        value = value.decode('latin1')
    return value
