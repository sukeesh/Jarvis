import os

from sqlobject import col, dberrors
from sqlobject.compat import PY2
from sqlobject.dbconnection import DBAPI


class ErrorMessage(str):
    def __new__(cls, e, append_msg=''):
        obj = str.__new__(cls, e.args[1] + append_msg)
        try:
            obj.code = int(e.args[0])
        except ValueError:
            obj.code = e.args[0]
        obj.module = e.__module__
        obj.exception = e.__class__.__name__
        return obj

mysql_Bin = None


class MySQLConnection(DBAPI):

    supportTransactions = False
    dbName = 'mysql'
    schemes = [dbName]

    odbc_keywords = ('Server', 'Port', 'UID', 'Password', 'Database')

    def __init__(self, db, user, password='', host='localhost', port=0, **kw):
        drivers = kw.pop('driver', None) or 'mysqldb'
        for driver in drivers.split(','):
            driver = driver.strip()
            if not driver:
                continue
            try:
                if driver.lower() in ('mysqldb', 'pymysql'):
                    if driver.lower() == 'pymysql':
                        import pymysql
                        pymysql.install_as_MySQLdb()
                    import MySQLdb
                    if driver.lower() == 'mysqldb':
                        if MySQLdb.version_info[:3] < (1, 2, 2):
                            raise ValueError(
                                'SQLObject requires MySQLdb 1.2.2 or later')
                    import MySQLdb.constants.CR
                    import MySQLdb.constants.ER
                    self.module = MySQLdb
                    if driver.lower() == 'mysqldb':
                        self.CR_SERVER_GONE_ERROR = \
                            MySQLdb.constants.CR.SERVER_GONE_ERROR
                        self.CR_SERVER_LOST = \
                            MySQLdb.constants.CR.SERVER_LOST
                    else:
                        self.CR_SERVER_GONE_ERROR = \
                            MySQLdb.constants.CR.CR_SERVER_GONE_ERROR
                        self.CR_SERVER_LOST = \
                            MySQLdb.constants.CR.CR_SERVER_LOST
                    self.ER_DUP_ENTRY = MySQLdb.constants.ER.DUP_ENTRY
                elif driver == 'connector':
                    import mysql.connector
                    self.module = mysql.connector
                    self.CR_SERVER_GONE_ERROR = \
                        mysql.connector.errorcode.CR_SERVER_GONE_ERROR
                    self.CR_SERVER_LOST = \
                        mysql.connector.errorcode.CR_SERVER_LOST
                    self.ER_DUP_ENTRY = mysql.connector.errorcode.ER_DUP_ENTRY
                elif driver == 'oursql':
                    import oursql
                    self.module = oursql
                    self.CR_SERVER_GONE_ERROR = \
                        oursql.errnos['CR_SERVER_GONE_ERROR']
                    self.CR_SERVER_LOST = oursql.errnos['CR_SERVER_LOST']
                    self.ER_DUP_ENTRY = oursql.errnos['ER_DUP_ENTRY']
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
                        'Unknown MySQL driver "%s", '
                        'expected mysqldb, connector, '
                        'oursql, pymysql, '
                        'odbc, pyodbc or pypyodbc' % driver)
            except ImportError:
                pass
            else:
                break
        else:
            raise ImportError(
                'Cannot find a MySQL driver, tried %s' % drivers)
        self.host = host
        self.port = port or 3306
        self.db = db
        self.user = user
        self.password = password
        self.kw = {}
        for key in ("unix_socket", "init_command",
                    "read_default_file", "read_default_group", "conv"):
            if key in kw:
                self.kw[key] = kw.pop(key)
        for key in ("connect_timeout", "compress", "named_pipe", "use_unicode",
                    "client_flag", "local_infile"):
            if key in kw:
                self.kw[key] = int(kw.pop(key))
        for key in ("ssl_key", "ssl_cert", "ssl_ca", "ssl_capath"):
            if key in kw:
                if "ssl" not in self.kw:
                    self.kw["ssl"] = {}
                self.kw["ssl"][key[4:]] = kw.pop(key)
        if "charset" in kw:
            self.dbEncoding = self.kw["charset"] = kw.pop("charset")
        else:
            self.dbEncoding = None
        self.driver = driver

        if driver in ('odbc', 'pyodbc', 'pypyodbc'):
            self.make_odbc_conn_str(kw.pop('odbcdrv',
                                           'MySQL ODBC 5.3 ANSI Driver'),
                                    db, host, port, user, password
                                    )
            self.CR_SERVER_GONE_ERROR = 2006
            self.CR_SERVER_LOST = 2013
            self.ER_DUP_ENTRY = '23000'

        global mysql_Bin
        if not PY2 and mysql_Bin is None:
            mysql_Bin = self.module.Binary
            self.module.Binary = lambda x: mysql_Bin(x).decode(
                'ascii', errors='surrogateescape')

        self._server_version = None
        self._can_use_microseconds = None
        DBAPI.__init__(self, **kw)

    @classmethod
    def _connectionFromParams(cls, user, password, host, port, path, args):
        return cls(db=path.strip('/'),
                   user=user or '', password=password or '',
                   host=host or 'localhost', port=port, **args)

    def makeConnection(self):
        dbEncoding = self.dbEncoding
        if dbEncoding:
            if self.driver.lower() in ('mysqldb', 'pymysql'):
                from MySQLdb.connections import Connection
                if not hasattr(Connection, 'set_character_set'):
                    # monkeypatch pre MySQLdb 1.2.1
                    def character_set_name(self):
                        return dbEncoding + '_' + dbEncoding
                    Connection.character_set_name = character_set_name
        if self.driver == 'connector':
            self.kw['consume_results'] = True
        try:
            if self.driver in ('odbc', 'pyodbc', 'pypyodbc'):
                self.debugWriter.write(
                    "ODBC connect string: " + self.odbc_conn_str)
                conn = self.module.connect(self.odbc_conn_str)
            else:
                conn = self.module.connect(
                    host=self.host, port=self.port, db=self.db,
                    user=self.user, passwd=self.password, **self.kw)
                if self.driver != 'oursql':
                    # Attempt to reconnect. This setting is persistent.
                    conn.ping(True)
        except self.module.OperationalError as e:
            conninfo = ("; used connection string: "
                        "host=%(host)s, port=%(port)s, "
                        "db=%(db)s, user=%(user)s" % self.__dict__)
            raise dberrors.OperationalError(ErrorMessage(e, conninfo))

        self._setAutoCommit(conn, bool(self.autoCommit))

        if dbEncoding:
            if self.driver in ('odbc', 'pyodbc'):
                conn.setdecoding(self.module.SQL_CHAR, encoding=dbEncoding)
                conn.setdecoding(self.module.SQL_WCHAR, encoding=dbEncoding)
                if PY2:
                    conn.setencoding(str, encoding=dbEncoding)
                    conn.setencoding(unicode, encoding=dbEncoding)  # noqa
                else:
                    conn.setencoding(encoding=dbEncoding)
            elif hasattr(conn, 'set_character_set'):
                conn.set_character_set(dbEncoding)
            elif self.driver == 'oursql':
                conn.charset = dbEncoding
            elif hasattr(conn, 'query'):
                # works along with monkeypatching code above
                conn.query("SET NAMES %s" % dbEncoding)

        return conn

    def _setAutoCommit(self, conn, auto):
        if hasattr(conn, 'autocommit'):
            try:
                conn.autocommit(auto)
            except TypeError:
                # mysql-connector has autocommit as a property
                conn.autocommit = auto

    def _force_reconnect(self, conn):
        if self.driver.lower() == 'pymysql':
            conn.ping(True)
            self._setAutoCommit(conn, bool(self.autoCommit))
            if self.dbEncoding:
                conn.query("SET NAMES %s" % self.dbEncoding)

    def _executeRetry(self, conn, cursor, query):
        if self.debug:
            self.printDebug(conn, query, 'QueryR')
        dbEncoding = self.dbEncoding
        if dbEncoding and not isinstance(query, bytes) and (
                self.driver == 'connector'):
            query = query.encode(dbEncoding, 'surrogateescape')
        # When a server connection is lost and a query is attempted, most of
        # the time the query will raise a SERVER_LOST exception, then at the
        # second attempt to execute it, the mysql lib will reconnect and
        # succeed. However is a few cases, the first attempt raises the
        # SERVER_GONE exception, the second attempt the SERVER_LOST exception
        # and only the third succeeds. Thus the 3 in the loop count.
        # If it doesn't reconnect even after 3 attempts, while the database is
        # up and running, it is because a 5.0.3 (or newer) server is used
        # which no longer permits autoreconnects by default. In that case a
        # reconnect flag must be set when making the connection to indicate
        # that autoreconnecting is desired. In MySQLdb 1.2.2 or newer this is
        # done by calling ping(True) on the connection.
        # PyMySQL needs explicit reconnect
        # each time we detect connection timeout.
        for count in range(3):
            try:
                return cursor.execute(query)
            except self.module.OperationalError as e:
                if e.args[0] in (self.CR_SERVER_GONE_ERROR,
                                 self.CR_SERVER_LOST):
                    if count == 2:
                        raise dberrors.OperationalError(ErrorMessage(e))
                    if self.debug:
                        self.printDebug(conn, str(e), 'ERROR')
                    if self.driver.lower() == 'pymysql':
                        self._force_reconnect(conn)
                else:
                    raise dberrors.OperationalError(ErrorMessage(e))
            except self.module.IntegrityError as e:
                msg = ErrorMessage(e)
                if e.args[0] == self.ER_DUP_ENTRY:
                    raise dberrors.DuplicateEntryError(msg)
                else:
                    raise dberrors.IntegrityError(msg)
            except self.module.InternalError as e:
                raise dberrors.InternalError(ErrorMessage(e))
            except self.module.ProgrammingError as e:
                if e.args[0] is not None:
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
        if id is None:
            try:
                id = c.lastrowid
            except AttributeError:
                try:
                    id = c.insert_id
                except AttributeError:
                    self._executeRetry(conn, c, "SELECT LAST_INSERT_ID();")
                    id = c.fetchone()[0]
                else:
                    id = c.insert_id()
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    @classmethod
    def _queryAddLimitOffset(cls, query, start, end):
        if not start:
            return "%s LIMIT %i" % (query, end)
        if not end:
            return "%s LIMIT %i, -1" % (query, start)
        return "%s LIMIT %i, %i" % (query, start, end - start)

    def createReferenceConstraint(self, soClass, col):
        return col.mysqlCreateReferenceConstraint()

    def createColumn(self, soClass, col):
        return col.mysqlCreateSQL(self)

    def createIndexSQL(self, soClass, index):
        return index.mysqlCreateIndexSQL(soClass)

    def createIDColumn(self, soClass):
        if soClass.sqlmeta.idType == str:
            return '%s TEXT PRIMARY KEY' % soClass.sqlmeta.idName
        return '%s INT PRIMARY KEY AUTO_INCREMENT' % soClass.sqlmeta.idName

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        try:
            # Use DESCRIBE instead of SHOW TABLES because SHOW TABLES
            # assumes there is a default database selected
            # which is not always True (for an embedded application, e.g.)
            self.query('DESCRIBE %s' % (tableName))
            return True
        except dberrors.ProgrammingError as e:
            if e.args[0].code in (1146, '42S02'):  # ER_NO_SUCH_TABLE
                return False
            raise

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.mysqlCreateSQL(self)))

    def delColumn(self, sqlmeta, column):
        self.query('ALTER TABLE %s DROP COLUMN %s' % (sqlmeta.table,
                                                      column.dbName))

    def columnsFromSchema(self, tableName, soClass):
        colData = self.queryAll("SHOW COLUMNS FROM %s"
                                % tableName)
        results = []
        for field, t, nullAllowed, key, default, extra in colData:
            if field == soClass.sqlmeta.idName:
                continue
            colClass, kw = self.guessClass(t)
            if self.kw.get('use_unicode') and colClass is col.StringCol:
                colClass = col.UnicodeCol
                if self.dbEncoding:
                    kw['dbEncoding'] = self.dbEncoding
            kw['name'] = soClass.sqlmeta.style.dbColumnToPythonAttr(field)
            kw['dbName'] = field

            # Since MySQL 5.0, 'NO' is returned in the NULL column
            # (SQLObject expected '')
            kw['notNone'] = (nullAllowed.upper() != 'YES' and True or False)

            if default and t.startswith('int'):
                kw['default'] = int(default)
            elif default and t.startswith('float'):
                kw['default'] = float(default)
            elif default == 'CURRENT_TIMESTAMP' and t == 'timestamp':
                kw['default'] = None
            elif default and colClass is col.BoolCol:
                kw['default'] = int(default) and True or False
            else:
                kw['default'] = default
            # @@ skip key...
            # @@ skip extra...
            results.append(colClass(**kw))
        return results

    def guessClass(self, t):
        if t.startswith('int'):
            return col.IntCol, {}
        elif t.startswith('enum'):
            values = []
            for i in t[5:-1].split(','):  # take the enum() off and split
                values.append(i[1:-1])  # remove the surrounding \'
            return col.EnumCol, {'enumValues': values}
        elif t.startswith('double'):
            return col.FloatCol, {}
        elif t.startswith('varchar'):
            colType = col.StringCol
            if self.kw.get('use_unicode', False):
                colType = col.UnicodeCol
            if t.endswith('binary'):
                return colType, {'length': int(t[8:-8]),
                                 'char_binary': True}
            else:
                return colType, {'length': int(t[8:-1])}
        elif t.startswith('char'):
            if t.endswith('binary'):
                return col.StringCol, {'length': int(t[5:-8]),
                                       'varchar': False,
                                       'char_binary': True}
            else:
                return col.StringCol, {'length': int(t[5:-1]),
                                       'varchar': False}
        elif t.startswith('datetime'):
            return col.DateTimeCol, {}
        elif t.startswith('date'):
            return col.DateCol, {}
        elif t.startswith('time'):
            return col.TimeCol, {}
        elif t.startswith('timestamp'):
            return col.TimestampCol, {}
        elif t.startswith('bool'):
            return col.BoolCol, {}
        elif t.startswith('tinyblob'):
            return col.BLOBCol, {"length": 2 ** 8 - 1}
        elif t.startswith('tinytext'):
            return col.StringCol, {"length": 2 ** 8 - 1, "varchar": True}
        elif t.startswith('blob'):
            return col.BLOBCol, {"length": 2 ** 16 - 1}
        elif t.startswith('text'):
            return col.StringCol, {"length": 2 ** 16 - 1, "varchar": True}
        elif t.startswith('mediumblob'):
            return col.BLOBCol, {"length": 2 ** 24 - 1}
        elif t.startswith('mediumtext'):
            return col.StringCol, {"length": 2 ** 24 - 1, "varchar": True}
        elif t.startswith('longblob'):
            return col.BLOBCol, {"length": 2 ** 32}
        elif t.startswith('longtext'):
            return col.StringCol, {"length": 2 ** 32, "varchar": True}
        else:
            return col.Col, {}

    def listTables(self):
        return [v[0] for v in self.queryAll("SHOW TABLES")]

    def listDatabases(self):
        return [v[0] for v in self.queryAll("SHOW DATABASES")]

    def _createOrDropDatabase(self, op="CREATE"):
        self.query('%s DATABASE %s' % (op, self.db))

    def createEmptyDatabase(self):
        self._createOrDropDatabase()

    def dropDatabase(self):
        self._createOrDropDatabase(op="DROP")

    def server_version(self):
        if self._server_version is not None:
            return self._server_version
        try:
            server_version = self.queryOne("SELECT VERSION()")[0]
            server_version = server_version.split('-', 1)
            db_tag = "MySQL"
            if len(server_version) == 2:
                if "MariaDB" in server_version[1]:
                    db_tag = "MariaDB"
                server_version = server_version[0]
            server_version = tuple(int(v) for v in server_version.split('.'))
            server_version = (server_version, db_tag)
        except Exception:
            server_version = None  # unknown
        self._server_version = server_version
        return server_version

    def can_use_microseconds(self):
        if self._can_use_microseconds is not None:
            return self._can_use_microseconds
        if os.environ.get('APPVEYOR') or os.environ.get('TRAVIS'):
            self._can_use_microseconds = False
            return False
        server_version = self.server_version()
        if server_version is None:
            return None
        server_version, db_tag = server_version
        if db_tag == "MariaDB":
            can_use_microseconds = (server_version >= (5, 3, 0))
        else:  # MySQL
            can_use_microseconds = (server_version >= (5, 6, 4))
        self._can_use_microseconds = can_use_microseconds
        return can_use_microseconds
