import re
from sqlobject import col
from sqlobject.dbconnection import DBAPI
from sqlobject.compat import PY2


class MSSQLConnection(DBAPI):

    supportTransactions = True
    dbName = 'mssql'
    schemes = [dbName]

    limit_re = re.compile('^\s*(select )(.*)', re.IGNORECASE)

    odbc_keywords = ('Server', 'Port', 'User Id', 'Password', 'Database')

    def __init__(self, db, user, password='', host='localhost', port=None,
                 autoCommit=0, **kw):
        drivers = kw.pop('driver', None) or 'adodb,pymssql'
        for driver in drivers.split(','):
            driver = driver.strip()
            if not driver:
                continue
            try:
                if driver in ('adodb', 'adodbapi'):
                    import adodbapi as sqlmodule
                elif driver == 'pymssql':
                    import pymssql as sqlmodule
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
                        'Unknown MSSQL driver "%s", '
                        'expected adodb, pymssql, '
                        'odbc, pyodbc or pypyodbc' % driver)
            except ImportError:
                pass
            else:
                break
        else:
            raise ImportError(
                'Cannot find an MSSQL driver, tried %s' % drivers)

        if driver in ('odbc', 'pyodbc', 'pypyodbc'):
            self.make_odbc_conn_str(kw.pop('odbcdrv', 'SQL Server'),
                                    db, host, port, user, password
                                    )

        elif driver in ('adodb', 'adodbapi'):
            self.module = sqlmodule
            self.dbconnection = sqlmodule.connect
            # ADO uses unicode only (AFAIK)
            self.usingUnicodeStrings = True

            # Need to use SQLNCLI provider for SQL Server Express Edition
            if kw.get("ncli"):
                conn_str = "Provider=SQLNCLI;"
            else:
                conn_str = "Provider=SQLOLEDB;"

            conn_str += "Data Source=%s;Initial Catalog=%s;"

            # MSDE does not allow SQL server login
            if kw.get("sspi"):
                conn_str += \
                    "Integrated Security=SSPI;Persist Security Info=False"
                self.make_conn_str = lambda keys: conn_str % (
                    keys.host, keys.db)
            else:
                conn_str += "User Id=%s;Password=%s"
                self.make_conn_str = lambda keys: conn_str % (
                    keys.host, keys.db, keys.user, keys.password)

            kw.pop("ncli", None)
            kw.pop("sspi", None)

        elif driver == 'pymssql':
            self.module = sqlmodule
            self.dbconnection = sqlmodule.connect
            sqlmodule.Binary = lambda st: str(st)
            # don't know whether pymssql uses unicode
            self.usingUnicodeStrings = False

            timeout = kw.pop('timeout', None)
            if timeout:
                timeout = int(timeout)
            self.timeout = timeout

            def _make_conn_str(keys):
                keys_dict = {}
                for attr, value in (
                    ('database', keys.db),
                    ('user', keys.user),
                    ('password', keys.password),
                    ('host', keys.host),
                    ('port', keys.port),
                    ('timeout', keys.timeout),
                ):
                    if value:
                        keys_dict[attr] = value
                return keys_dict
            self.make_conn_str = _make_conn_str
        self.driver = driver

        self.autoCommit = int(autoCommit)
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db = db
        self._server_version = None
        self._can_use_max_types = None
        self._can_use_microseconds = None
        DBAPI.__init__(self, **kw)

    @classmethod
    def _connectionFromParams(cls, user, password, host, port, path, args):
        path = path.strip('/')
        return cls(user=user, password=password,
                   host=host or 'localhost', port=port, db=path, **args)

    def insert_id(self, conn):
        """
        insert_id method.
        """
        c = conn.cursor()
        # converting the identity to an int is ugly, but it gets returned
        # as a decimal otherwise :S
        c.execute('SELECT CONVERT(INT, @@IDENTITY)')
        return c.fetchone()[0]

    def makeConnection(self):
        if self.driver in ('odbc', 'pyodbc', 'pypyodbc'):
            self.debugWriter.write(
                "ODBC connect string: " + self.odbc_conn_str)
            conn = self.module.connect(self.odbc_conn_str)
        else:
            conn_descr = self.make_conn_str(self)
            if isinstance(conn_descr, dict):
                conn = self.dbconnection(**conn_descr)
            else:
                conn = self.dbconnection(conn_descr)
        cur = conn.cursor()
        cur.execute('SET ANSI_NULLS ON')
        cur.execute("SELECT CAST('12345.21' AS DECIMAL(10, 2))")
        self.decimalSeparator = str(cur.fetchone()[0])[-3]
        cur.close()
        return conn

    HAS_IDENTITY = """
       select 1
       from INFORMATION_SCHEMA.COLUMNS
       where TABLE_NAME = '%s'
       and COLUMNPROPERTY(object_id(TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 1
    """

    def _hasIdentity(self, conn, table):
        query = self.HAS_IDENTITY % table
        c = conn.cursor()
        c.execute(query)
        r = c.fetchone()
        return r is not None

    def _queryInsertID(self, conn, soInstance, id, names, values):
        """
            Insert the Initial with names and values, using id.
        """
        table = soInstance.sqlmeta.table
        idName = soInstance.sqlmeta.idName
        c = conn.cursor()
        has_identity = self._hasIdentity(conn, table)
        if id is not None:
            names = [idName] + names
            values = [id] + values
        elif has_identity and idName in names:
            try:
                i = names.index(idName)
                if i:
                    del names[i]
                    del values[i]
            except ValueError:
                pass

        if has_identity:
            if id is not None:
                c.execute('SET IDENTITY_INSERT %s ON' % table)
            else:
                c.execute('SET IDENTITY_INSERT %s OFF' % table)

        if names and values:
            q = self._insertSQL(table, names, values)
        else:
            q = "INSERT INTO %s DEFAULT VALUES" % table
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        c.execute(q)
        if has_identity:
            c.execute('SET IDENTITY_INSERT %s OFF' % table)

        if id is None:
            id = self.insert_id(conn)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    @classmethod
    def _queryAddLimitOffset(cls, query, start, end):
        if end and not start:
            limit_str = "SELECT TOP %i" % end

            match = cls.limit_re.match(query)
            if match and len(match.groups()) == 2:
                return ' '.join([limit_str, match.group(2)])
        else:
            return query

    def createReferenceConstraint(self, soClass, col):
        return col.mssqlCreateReferenceConstraint()

    def createColumn(self, soClass, col):
        return col.mssqlCreateSQL(self)

    def createIDColumn(self, soClass):
        key_type = {int: "INT", str: "TEXT"}[soClass.sqlmeta.idType]
        return '%s %s IDENTITY UNIQUE' % (soClass.sqlmeta.idName, key_type)

    def createIndexSQL(self, soClass, index):
        return index.mssqlCreateIndexSQL(soClass)

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    SHOW_TABLES = "SELECT name FROM sysobjects WHERE type='U'"

    def tableExists(self, tableName):
        for (table,) in self.queryAll(self.SHOW_TABLES):
            if table.lower() == tableName.lower():
                return True
        return False

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD %s' %
                   (tableName,
                    column.mssqlCreateSQL(self)))

    def delColumn(self, sqlmeta, column):
        self.query('ALTER TABLE %s DROP COLUMN %s' % (sqlmeta.table,
                                                      column.dbName))

    # Precision and scale is gotten from column table
    # so that we can create decimal columns if needed.
    SHOW_COLUMNS = """
        select
                name,
                length,
                (       select name
                        from systypes
                        where cast(xusertype as int)= cast(sc.xtype as int)
                ) datatype,
                prec,
                scale,
                isnullable,
                cdefault,
                m.text default_text,
                isnull(len(autoval),0) is_identity
        from syscolumns sc
        LEFT OUTER JOIN syscomments m on sc.cdefault = m.id
                AND m.colid = 1
        where
                sc.id in (select id
                        from sysobjects
                where name = '%s')
        order by
                colorder"""

    def columnsFromSchema(self, tableName, soClass):
        colData = self.queryAll(self.SHOW_COLUMNS
                                % tableName)
        results = []
        for (field, size, t, precision, scale, nullAllowed,
                default, defaultText, is_identity) in colData:
            if field == soClass.sqlmeta.idName:
                continue
            # precision is needed for decimal columns
            colClass, kw = self.guessClass(t, size, precision, scale)
            kw['name'] = str(soClass.sqlmeta.style.dbColumnToPythonAttr(field))
            kw['dbName'] = str(field)
            kw['notNone'] = not nullAllowed
            if (defaultText):
                # Strip ( and )
                defaultText = defaultText[1:-1]
                if defaultText[0] == "'":
                    defaultText = defaultText[1:-1]
                else:
                    if t in ("int", "float", "numeric") and \
                            defaultText[0] == "(":
                        defaultText = defaultText[1:-1]
                    if t == "int":
                        defaultText = int(defaultText)
                    if t == "float":
                        defaultText = float(defaultText)
                    if t == "numeric":
                        defaultText = float(defaultText)
                    # TODO need to access the "column" to_python method here --
                    # but the object doesn't exists yet.

            # @@ skip key...
            kw['default'] = defaultText

            results.append(colClass(**kw))
        return results

    def _setAutoCommit(self, conn, auto):
        # raise Exception(repr(auto))
        return
        # conn.auto_commit = auto
        option = "ON"
        if auto == 0:
            option = "OFF"
        c = conn.cursor()
        c.execute("SET AUTOCOMMIT " + option)

    # precision and scale is needed for decimal columns
    def guessClass(self, t, size, precision, scale):
        """
        Here we take raw values coming out of syscolumns
        and map to SQLObject class types.

        """
        if t.startswith('int'):
            return col.IntCol, {}
        elif t.startswith('varchar'):
            if self.usingUnicodeStrings:
                return col.UnicodeCol, {'length': size}
            return col.StringCol, {'length': size}
        elif t.startswith('char'):
            if self.usingUnicodeStrings:
                return col.UnicodeCol, {'length': size,
                                        'varchar': False}
            return col.StringCol, {'length': size,
                                   'varchar': False}
        elif t.startswith('datetime'):
            return col.DateTimeCol, {}
        elif t.startswith('decimal'):
            # be careful for awkward naming
            return col.DecimalCol, {'size': precision,
                                    'precision': scale}
        else:
            return col.Col, {}

    def server_version(self):
        """Get server version:
            8 - 2000
            9 - 2005
            10 - 2008
            11 - 2012
            12 - 2014
            13 - 2016
        """
        if self._server_version is not None:
            return self._server_version
        try:
            server_version = self.queryOne(
                "SELECT SERVERPROPERTY('productversion')")[0]
            if not PY2 and isinstance(server_version, bytes):
                server_version = server_version.decode('ascii')
            server_version = server_version.split('.')[0]
            server_version = int(server_version)
        except Exception:
            server_version = None  # unknown
        self._server_version = server_version
        return server_version

    def can_use_max_types(self):
        if self._can_use_max_types is not None:
            return self._can_use_max_types
        server_version = self.server_version()
        self._can_use_max_types = can_use_max_types = \
            (server_version is not None) and (server_version >= 9)
        return can_use_max_types

    def can_use_microseconds(self):
        if self._can_use_microseconds is not None:
            return self._can_use_microseconds
        server_version = self.server_version()
        self._can_use_microseconds = can_use_microseconds = \
            (server_version is not None) and (server_version >= 10)
        return can_use_microseconds
