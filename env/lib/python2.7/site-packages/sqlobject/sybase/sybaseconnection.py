from sqlobject.dbconnection import DBAPI
from sqlobject import col


class SybaseConnection(DBAPI):

    supportTransactions = False
    dbName = 'sybase'
    schemes = [dbName]
    NumericType = None

    def __init__(self, db, user, password='', host='localhost', port=None,
                 locking=1, **kw):
        db = db.strip('/')
        import Sybase
        Sybase._ctx.debug = 0
        if SybaseConnection.NumericType is None:
            from Sybase import NumericType
            SybaseConnection.NumericType = NumericType
            from sqlobject.converters import registerConverter, IntConverter
            registerConverter(NumericType, IntConverter)
        self.module = Sybase
        self.locking = int(locking)
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        autoCommit = kw.get('autoCommit')
        if autoCommit:
            autoCommit = int(autoCommit)
        else:
            autoCommit = None
        kw['autoCommit'] = autoCommit
        DBAPI.__init__(self, **kw)

    @classmethod
    def _connectionFromParams(cls, user, password, host, port, path, args):
        return cls(user=user, password=password,
                   host=host or 'localhost', port=port, db=path, **args)

    def insert_id(self, conn):
        """
        Sybase adapter/cursor does not support the
        insert_id method.
        """
        c = conn.cursor()
        c.execute('SELECT @@IDENTITY')
        return c.fetchone()[0]

    def makeConnection(self):
        return self.module.connect(self.host, self.user, self.password,
                                   database=self.db,
                                   auto_commit=self.autoCommit,
                                   locking=self.locking)

    HAS_IDENTITY = """
       SELECT col.name, col.status, obj.name
       FROM syscolumns col
       JOIN sysobjects obj
       ON obj.id = col.id
       WHERE obj.name = '%s'
             AND (col.status & 0x80) = 0x80
    """

    def _hasIdentity(self, conn, table):
        query = self.HAS_IDENTITY % table
        c = conn.cursor()
        c.execute(query)
        r = c.fetchone()
        return r is not None

    def _queryInsertID(self, conn, soInstance, id, names, values):
        table = soInstance.sqlmeta.table
        idName = soInstance.sqlmeta.idName
        c = conn.cursor()
        if id is not None:
            names = [idName] + names
            values = [id] + values

        has_identity = self._hasIdentity(conn, table)
        identity_insert_on = False
        if has_identity and (id is not None):
            identity_insert_on = True
            c.execute('SET IDENTITY_INSERT %s ON' % table)

        if names and values:
            q = self._insertSQL(table, names, values)
        else:
            q = "INSERT INTO %s DEFAULT VALUES" % table
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        c.execute(q)
        if has_identity and identity_insert_on:
            c.execute('SET IDENTITY_INSERT %s OFF' % table)
        if id is None:
            id = self.insert_id(conn)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    @classmethod
    def _queryAddLimitOffset(cls, query, start, end):
        # XXX Sybase doesn't support OFFSET
        if end:
            return "SET ROWCOUNT %i %s SET ROWCOUNT 0" % (end, query)
        return query

    def createReferenceConstraint(self, soClass, col):
        return None

    def createColumn(self, soClass, col):
        return col.sybaseCreateSQL()

    def createIDColumn(self, soClass):
        key_type = {int: "NUMERIC(18,0)", str: "TEXT"}[soClass.sqlmeta.idType]
        return '%s %s IDENTITY UNIQUE' % (soClass.sqlmeta.idName, key_type)

    def createIndexSQL(self, soClass, index):
        return index.sybaseCreateIndexSQL(soClass)

    def joinSQLType(self, join):
        return 'NUMERIC(18,0) NOT NULL'

    SHOW_TABLES = "SELECT name FROM sysobjects WHERE type='U'"

    def tableExists(self, tableName):
        for (table,) in self.queryAll(self.SHOW_TABLES):
            if table.lower() == tableName.lower():
                return True
        return False

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.sybaseCreateSQL()))

    def delColumn(self, sqlmeta, column):
        self.query(
            'ALTER TABLE %s DROP COLUMN %s' % (sqlmeta.table, column.dbName))

    SHOW_COLUMNS = ('SELECT '
                    'COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT '
                    'FROM INFORMATION_SCHEMA.COLUMNS '
                    'WHERE TABLE_NAME = \'%s\'')

    def columnsFromSchema(self, tableName, soClass):
        colData = self.queryAll(self.SHOW_COLUMNS
                                % tableName)
        results = []
        for field, t, nullAllowed, default in colData:
            if field == soClass.sqlmeta.idName:
                continue
            colClass, kw = self.guessClass(t)
            kw['name'] = soClass.sqlmeta.style.dbColumnToPythonAttr(field)
            kw['dbName'] = field
            kw['notNone'] = not nullAllowed
            kw['default'] = default
            # @@ skip key...
            # @@ skip extra...
            kw['forceDBName'] = True
            results.append(colClass(**kw))
        return results

    def _setAutoCommit(self, conn, auto):
        conn.auto_commit = auto

    def guessClass(self, t):
        if t.startswith('int'):
            return col.IntCol, {}
        elif t.startswith('varchar'):
            return col.StringCol, {'length': int(t[8:-1])}
        elif t.startswith('char'):
            return col.StringCol, {'length': int(t[5:-1]),
                                   'varchar': False}
        elif t.startswith('datetime'):
            return col.DateTimeCol, {}
        else:
            return col.Col, {}
