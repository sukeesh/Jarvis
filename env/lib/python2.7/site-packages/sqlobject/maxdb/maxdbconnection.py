"""
Contributed by Edigram SAS, Paris France Tel:01 44 77 94 00
Ahmed MOHAMED ALI <ahmedmoali@yahoo.com> 27 April 2004

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

connection creation sample::

    __connection__ = DBConnection.maxdbConnection(
        host=hostname, database=dbname,
        user=user_name, password=user_password, autoCommit=1, debug=1)
"""

import os
from sqlobject.dbconnection import DBAPI
from sqlobject import col


class maxdbException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LowerBoundOfSliceIsNotSupported(maxdbException):
    def __init__(self, value):
        maxdbException.__init__(self, '')


class IncorrectIDStyleError(maxdbException):
    def __init__(self, value):
        maxdbException.__init__(
            self,
            'This primary key name is not in the expected style, '
            'please rename the column to %r or switch to another style'
            % value)


class StyleMismatchError(maxdbException):
    def __init__(self, value):
        maxdbException.__init__(
            self,
            'The name %r is only permitted for primary key, change the '
            'column name or switch to another style' % value)


class PrimaryKeyNotFounded(maxdbException):
    def __init__(self, value):
        maxdbException.__init__(
            self,
            "No primary key was defined on table %r" % value)


SAPDBMAX_ID_LENGTH = 32


class MaxdbConnection(DBAPI):

    supportTransactions = True
    dbName = 'maxdb'
    schemes = [dbName]

    def __init__(self, host='', port=None, user=None, password=None,
                 database=None, autoCommit=1, sqlmode='internal',
                 isolation=None, timeout=None, **kw):
        from sapdb import dbapi
        self.module = dbapi
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = database
        self.autoCommit = autoCommit
        self.sqlmode = sqlmode
        self.isolation = isolation
        self.timeout = timeout

        DBAPI.__init__(self, **kw)

    @classmethod
    def _connectionFromParams(cls, auth, password, host, port, path, args):
        path = path.replace('/', os.path.sep)
        return cls(host, port, user=auth, password=password, database=path,
                   **args)

    def _getConfigParams(self, sqlmode, auto):
        autocommit = 'off'
        if auto:
            autocommit = 'on'
        opt = {}
        opt["autocommit"] = autocommit
        opt["sqlmode"] = sqlmode
        if self.isolation:
            opt["isolation"] = self.isolation
        if self.timeout:
            opt["timeout"] = self.timeout
        return opt

    def _setAutoCommit(self, conn, auto):
        conn.close()
        conn.__init__(self.user, self.password, self.db, self.host,
                      **self._getConfigParams(self.sqlmode, auto))

    def createSequenceName(self, table):
        """
        sequence name are builded with the concatenation of the table
        name with '_SEQ' word we truncate the name of the
        sequence_name because sapdb identifier cannot exceed 32
        characters so that the name of the sequence does not exceed 32
        characters
        """
        return '%s_SEQ' % (table[:SAPDBMAX_ID_LENGTH - 4])

    def makeConnection(self):
        conn = self.module.Connection(
            self.user, self.password, self.db, self.host,
            **self._getConfigParams(self.sqlmode, self.autoCommit))
        return conn

    def _queryInsertID(self, conn, soInstance, id, names, values):
        table = soInstance.sqlmeta.table
        idName = soInstance.sqlmeta.idName
        c = conn.cursor()
        if id is None:
            c.execute(
                'SELECT %s.NEXTVAL FROM DUAL' % (
                    self.createSequenceName(table)))
            id = c.fetchone()[0]
        names = [idName] + names
        values = [id] + values
        q = self._insertSQL(table, names, values)
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        c.execute(q)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    @classmethod
    def sqlAddLimit(cls, query, limit):
        sql = query
        sql = sql.replace("SELECT", "SELECT ROWNO, ")
        if sql.find('WHERE') != -1:
            sql = sql + ' AND ' + limit
        else:
            sql = sql + 'WHERE ' + limit
        return sql

    @classmethod
    def _queryAddLimitOffset(cls, query, start, end):
        if start:
            raise LowerBoundOfSliceIsNotSupported
        limit = ' ROWNO   <= %d ' % (end)
        return cls.sqlAddLimit(query, limit)

    def createTable(self, soClass):
        # We create the table in a transaction because the addition of the
        # table and the sequence must be atomic.

        # I tried to use the transaction class
        # but I get a recursion limit error.
        # t=self.transaction()
        # t.query('CREATE TABLE %s (\n%s\n)' %
        #            (soClass.sqlmeta.table, self.createColumns(soClass)))
        #
        # t.query("CREATE SEQUENCE %s" %
        #         self.createSequenceName(soClass.sqlmeta.table))
        # t.commit()
        # so use transaction when the problem will be solved
        self.query('CREATE TABLE %s (\n%s\n)' %
                   (soClass.sqlmeta.table, self.createColumns(soClass)))
        self.query("CREATE SEQUENCE %s"
                   % self.createSequenceName(soClass.sqlmeta.table))
        return []

    def createReferenceConstraint(self, soClass, col):
        return col.maxdbCreateReferenceConstraint()

    def createColumn(self, soClass, col):
        return col.maxdbCreateSQL()

    def createIDColumn(self, soClass):
        key_type = {int: "INT", str: "TEXT"}[soClass.sqlmeta.idType]
        return '%s %s PRIMARY KEY' % (soClass.sqlmeta.idName, key_type)

    def createIndexSQL(self, soClass, index):
        return index.maxdbCreateIndexSQL(soClass)

    def dropTable(self, tableName, cascade=False):
        # We drop the table in a transaction because the removal of the
        # table and the sequence must be atomic.
        # I tried to use the transaction class
        # but I get a recursion limit error.
        # try:
        #     t=self.transaction()
        #     t.query("DROP TABLE %s" % tableName)
        #     t.query("DROP SEQUENCE %s" % self.createSequenceName(tableName))
        #     t.commit()
        # except:
        #     t.rollback()
        # so use transaction when the problem will be solved
        self.query("DROP TABLE %s" % tableName)
        self.query("DROP SEQUENCE %s" % self.createSequenceName(tableName))

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        for (table,) in self.queryAll(
                "SELECT OBJECT_NAME FROM ALL_OBJECTS "
                "WHERE OBJECT_TYPE='TABLE'"):
            if table.lower() == tableName.lower():
                return True
        return False

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD %s' %
                   (tableName,
                    column.maxdbCreateSQL()))

    def delColumn(self, sqlmeta, column):
        self.query('ALTER TABLE %s DROP COLUMN %s' % (sqlmeta.table,
                                                      column.dbName))

    GET_COLUMNS = """
    SELECT COLUMN_NAME, NULLABLE, DATA_DEFAULT, DATA_TYPE,
           DATA_LENGTH, DATA_SCALE
    FROM USER_TAB_COLUMNS WHERE TABLE_NAME=UPPER('%s')"""

    GET_PK_AND_FK = """
    SELECT constraint_cols.column_name, constraints.constraint_type,
           refname,reftablename
    FROM user_cons_columns constraint_cols
    INNER JOIN user_constraints constraints
    ON constraint_cols.constraint_name = constraints.constraint_name
    LEFT OUTER JOIN show_foreign_key fk
    ON constraint_cols.column_name = fk.columnname
    WHERE constraints.table_name =UPPER('%s')"""

    def columnsFromSchema(self, tableName, soClass):
        colData = self.queryAll(self.GET_COLUMNS
                                % tableName)

        results = []
        keymap = {}
        pkmap = {}
        fkData = self.queryAll(self.GET_PK_AND_FK % tableName)
        for _col, cons_type, refcol, reftable in fkData:
            col_name = _col.lower()
            pkmap[col_name] = False
            if cons_type == 'R':
                keymap[col_name] = reftable.lower()

            elif cons_type == 'P':
                pkmap[col_name] = True

        if len(pkmap) == 0:
            raise PrimaryKeyNotFounded(tableName)

        for (field, nullAllowed, default, data_type, data_len,
             data_scale) in colData:
            # id is defined as primary key --> ok
            # We let sqlobject raise error if the 'id' is used
            # for another column.
            field_name = field.lower()
            if (field_name == soClass.sqlmeta.idName) and pkmap[field_name]:
                continue

            colClass, kw = self.guessClass(data_type, data_len, data_scale)
            kw['name'] = field_name
            kw['dbName'] = field

            if nullAllowed == 'Y':
                nullAllowed = False
            else:
                nullAllowed = True

            kw['notNone'] = nullAllowed
            if default is not None:
                kw['default'] = default

            if field_name in keymap:
                kw['foreignKey'] = keymap[field_name]

            results.append(colClass(**kw))

        return results

    _numericTypes = ['INTEGER', 'INT', 'SMALLINT']
    _dateTypes = ['DATE', 'TIME', 'TIMESTAMP']

    def guessClass(self, t, flength, fscale=None):
        """
        An internal method that tries to figure out what Col subclass
        is appropriate given whatever introspective information is
        available -- both very database-specific.
        """
        if t in self._numericTypes:
            return col.IntCol, {}
        # The type returned by the sapdb library for LONG is
        # SapDB_LongReader To get the data call the read member with
        # desired size (default =-1 means get all)

        elif t.find('LONG') != -1:
            return col.StringCol, {'length': flength,
                                   'varchar': False}
        elif t in self._dateTypes:
            return col.DateTimeCol, {}
        elif t == 'FIXED':
            return col.CurrencyCol, {'size': flength,
                                     'precision': fscale}
        else:
            return col.Col, {}
