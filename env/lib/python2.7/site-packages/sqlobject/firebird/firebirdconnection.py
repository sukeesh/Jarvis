import os
import re
import warnings
from sqlobject import col
from sqlobject.dbconnection import DBAPI


class FirebirdConnection(DBAPI):

    supportTransactions = False
    dbName = 'firebird'
    schemes = [dbName]

    limit_re = re.compile('^\s*(select )(.*)', re.IGNORECASE)

    def __init__(self, host, db, port='3050', user='sysdba',
                 password='masterkey', autoCommit=1,
                 dialect=None, role=None, charset=None, **kw):
        drivers = kw.pop('driver', None) or 'fdb,kinterbasdb'
        for driver in drivers.split(','):
            driver = driver.strip()
            if not driver:
                continue
            try:
                if driver == 'fdb':
                    import fdb
                    self.module = fdb
                elif driver == 'kinterbasdb':
                    import kinterbasdb
                    # See
                    # http://kinterbasdb.sourceforge.net/dist_docs/usage.html
                    # for an explanation; in short: use datetime, decimal and
                    # unicode.
                    kinterbasdb.init(type_conv=200)
                    self.module = kinterbasdb
                elif driver in ('firebirdsql', 'pyfirebirdsql'):
                    import firebirdsql
                    self.module = firebirdsql
                else:
                    raise ValueError(
                        'Unknown FireBird driver "%s", '
                        'expected fdb, kinterbasdb or firebirdsql' % driver)
            except ImportError:
                pass
            else:
                break
        else:
            raise ImportError(
                'Cannot find an FireBird driver, tried %s' % drivers)
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        if dialect:
            self.dialect = int(dialect)
        else:
            self.dialect = None
        self.role = role
        if charset:
            # Encoding defined by user in the connection string.
            self.dbEncoding = charset.replace('-', '')
        else:
            self.dbEncoding = charset
        # Encoding defined during database creation and stored in the database.
        self.defaultDbEncoding = ''
        DBAPI.__init__(self, **kw)

    @classmethod
    def _connectionFromParams(cls, auth, password, host, port, path, args):
        if not password:
            password = 'masterkey'
        if not auth:
            auth = 'sysdba'
        # check for alias using
        if (path[0] == '/') and path[-3:].lower() not in ('fdb', 'gdb'):
            path = path[1:]
        path = path.replace('/', os.sep)
        return cls(host, port=port, db=path, user=auth, password=password,
                   **args)

    def _runWithConnection(self, meth, *args):
        if not self.autoCommit:
            return DBAPI._runWithConnection(self, meth, args)
        conn = self.getConnection()
        # @@: Horrible auto-commit implementation.  Just horrible!
        try:
            conn.begin()
        except self.module.ProgrammingError:
            pass
        try:
            val = meth(conn, *args)
            try:
                conn.commit()
            except self.module.ProgrammingError:
                pass
        finally:
            self.releaseConnection(conn)
        return val

    def _setAutoCommit(self, conn, auto):
        # Only _runWithConnection does "autocommit", so we don't
        # need to worry about that.
        pass

    def makeConnection(self):
        extra = {}
        if self.dialect:
            extra['dialect'] = self.dialect
        return self.module.connect(
            host=self.host,
            port=self.port,
            database=self.db,
            user=self.user,
            password=self.password,
            role=self.role,
            charset=self.dbEncoding,
            **extra
        )

    def _queryInsertID(self, conn, soInstance, id, names, values):
        """Firebird uses 'generators' to create new ids for a table.
        The users needs to create a generator named GEN_<tablename>
        for each table this method to work."""
        table = soInstance.sqlmeta.table
        idName = soInstance.sqlmeta.idName
        sequenceName = soInstance.sqlmeta.idSequence or 'GEN_%s' % table
        c = conn.cursor()
        if id is None:
            c.execute('SELECT gen_id(%s,1) FROM rdb$database' % sequenceName)
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
    def _queryAddLimitOffset(cls, query, start, end):
        """Firebird slaps the limit and offset (actually 'first' and
        'skip', respectively) statement right after the select."""
        if not start:
            limit_str = "SELECT FIRST %i" % end
        if not end:
            limit_str = "SELECT SKIP %i" % start
        else:
            limit_str = "SELECT FIRST %i SKIP %i" % (end - start, start)

        match = cls.limit_re.match(query)
        if match and len(match.groups()) == 2:
            return ' '.join([limit_str, match.group(2)])
        else:
            return query

    def createTable(self, soClass):
        self.query('CREATE TABLE %s (\n%s\n)' %
                   (soClass.sqlmeta.table, self.createColumns(soClass)))
        self.query("CREATE GENERATOR GEN_%s" % soClass.sqlmeta.table)
        return []

    def createReferenceConstraint(self, soClass, col):
        return None

    def createColumn(self, soClass, col):
        return col.firebirdCreateSQL()

    def createIDColumn(self, soClass):
        key_type = {int: "INT", str: "VARCHAR(255)"}[soClass.sqlmeta.idType]
        return '%s %s NOT NULL PRIMARY KEY' % (soClass.sqlmeta.idName,
                                               key_type)

    def createIndexSQL(self, soClass, index):
        return index.firebirdCreateIndexSQL(soClass)

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        # there's something in the database by this name...let's
        # assume it's a table.  By default, fb 1.0 stores EVERYTHING
        # it cares about in uppercase.
        result = self.queryOne(
            "SELECT COUNT(rdb$relation_name) FROM rdb$relations "
            "WHERE rdb$relation_name = '%s'" % tableName.upper())
        return result[0]

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD %s' %
                   (tableName,
                    column.firebirdCreateSQL()))

    def dropTable(self, tableName, cascade=False):
        self.query("DROP TABLE %s" % tableName)
        self.query("DROP GENERATOR GEN_%s" % tableName)

    def delColumn(self, sqlmeta, column):
        self.query('ALTER TABLE %s DROP %s' % (sqlmeta.table, column.dbName))

    def readDefaultEncodingFromDB(self):
        # Get out if encoding is known allready (can by None as well).
        if self.defaultDbEncoding == "":
            self.defaultDbEncoding = str(self.queryOne(
                "SELECT rdb$character_set_name FROM rdb$database")[0].
                strip().lower())  # encoding defined during db creation
            if self.defaultDbEncoding == "none":
                self.defaultDbEncoding = None
            if self.dbEncoding != self.defaultDbEncoding:
                warningText = """\n
                   Database charset: %s is different """ \
                   """from connection charset: %s.\n""" % (
                   self.defaultDbEncoding, self.dbEncoding)
                warnings.warn(warningText)
                # TODO: ??? print out the uri string,
                # so user can see what is going on
                warningText = """\n
                   Every CHAR or VARCHAR field can (or, better: must) """ \
                   """have a character set defined in Firebird.
                   In the case, field charset is not defined, """ \
                   """SQLObject try to use a db default encoding instead.
                   Firebird is unable to transliterate between character sets.
                   So you must set the correct values on the server """ \
                   "and on the client if everything is to work smoothely.\n"
                warnings.warn(warningText)

            if not self.dbEncoding:  # defined by user in the connection string
                self.dbEncoding = self.defaultDbEncoding
                warningText = """\n
                   encoding: %s will be used as default """ \
                   """for this connection\n""" % self.dbEncoding
                warnings.warn(warningText)

    def columnsFromSchema(self, tableName, soClass):
        """
        Look at the given table and create Col instances (or
        subclasses of Col) for the fields it finds in that table.
        """

        self.readDefaultEncodingFromDB()

        fieldQuery = """\
        SELECT r.RDB$FIELD_NAME AS field_name,
                CASE f.RDB$FIELD_TYPE
                when 7 then 'smallint'
                when 8 then 'integer'
                when 16 then 'int64'
                when 9 then 'quad'
                when 10 then 'float'
                when 11 then 'd_float'
                when 17 then 'boolean'
                when 27 then 'double'
                when 12 then 'date'
                when 13 then 'time'
                when 35 then 'timestamp'
                when 261 then 'blob'
                when 37 then 'varchar'
                when 14 then 'char'
                when 40 then 'cstring'
                when 45 then 'blob_id'
                  ELSE 'UNKNOWN'
                END AS field_type,
                case f.rdb$field_type
                when 7 then
                case f.rdb$field_sub_type
                    when 1 then 'numeric'
                    when 2 then 'decimal'
                end
                when 8 then
                case f.rdb$field_sub_type
                    when 1 then 'numeric'
                    when 2 then 'decimal'
                end
                when 16 then
                case f.rdb$field_sub_type
                    when 1 then 'numeric'
                    when 2 then 'decimal'
                    else 'bigint'
                end
                when 14 then
                case f.rdb$field_sub_type
                    when 0 then 'unspecified'
                    when 1 then 'binary'
                    when 3 then 'acl'
                    else
                    case
                        when f.rdb$field_sub_type is null then 'unspecified'
                    end
                end
                when 37 then
                case f.rdb$field_sub_type
                    when 0 then 'unspecified'
                    when 1 then 'text'
                    when 3 then 'acl'
                    else
                    case
                        when f.rdb$field_sub_type is null then 'unspecified'
                    end
                end
                when 261 then
                case f.rdb$field_sub_type
                    when 0 then 'unspecified'
                    when 1 then 'text'
                    when 2 then 'blr'
                    when 3 then 'acl'
                    when 4 then 'reserved'
                    when 5 then 'encoded-meta-data'
                    when 6 then 'irregular-finished-multi-db-tx'
                    when 7 then 'transactional_description'
                    when 8 then 'external_file_description'
                end
            end as "ActualSubType",
                f.RDB$FIELD_LENGTH AS field_length,
                f.RDB$FIELD_PRECISION AS field_precision,
                f.RDB$FIELD_SCALE AS field_scale,
                cset.RDB$CHARACTER_SET_NAME AS field_charset,
                coll.RDB$COLLATION_NAME AS field_collation,
                r.rdb$default_source,
                r.RDB$NULL_FLAG AS field_not_null_constraint,
                r.RDB$DESCRIPTION AS field_description
           FROM RDB$RELATION_FIELDS r
           LEFT JOIN RDB$FIELDS f ON r.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
           LEFT JOIN RDB$COLLATIONS coll
                ON f.RDB$COLLATION_ID = coll.RDB$COLLATION_ID
           LEFT JOIN RDB$CHARACTER_SETS cset
                ON f.RDB$CHARACTER_SET_ID = cset.RDB$CHARACTER_SET_ID
          WHERE r.RDB$RELATION_NAME='%s'  -- table name
        ORDER BY r.RDB$FIELD_POSITION
        """

        colData = self.queryAll(fieldQuery % tableName.upper())
        results = []
        for (field, fieldType, fieldSubtype, fieldLength, fieldPrecision,
                fieldScale, fieldCharset, collationName, defaultSource,
                fieldNotNullConstraint, fieldDescription) in colData:
            field = field.strip().lower()
            fieldType = fieldType.strip()
            if fieldCharset:
                fieldCharset = str(fieldCharset.strip())
                # 'UNICODE_FSS' is less strict
                # Firebird/Interbase UTF8 definition
                if fieldCharset.startswith('UNICODE_FSS'):
                    fieldCharset = "UTF8"
            if fieldSubtype:
                fieldSubtype = fieldSubtype.strip()
                if fieldType == "int64":
                    fieldType = fieldSubtype

            # can look like: "DEFAULT 0", "DEFAULT 'default text'", None
            if defaultSource:
                defaultSource = defaultSource.split(' ')[1]
                if defaultSource.startswith("'") and \
                        defaultSource.endswith("'"):
                    defaultSource = str(defaultSource[1:-1])
                elif fieldType in ("integer", "smallint", "bigint"):
                    defaultSource = int(defaultSource)
                elif fieldType in ("float", "double"):
                    defaultSource = float(defaultSource)
            # TODO: other types for defaultSource
            #    elif fieldType == "datetime":

            idName = str(soClass.sqlmeta.idName or 'id').upper()
            if field.upper() == idName:
                continue
            if fieldScale:
                # PRECISION refers to the total number of digits,
                # and SCALE refers to the number of digits
                # to the right of the decimal point.
                # Both numbers can be from 1 to 18 (SQL dialect 1: 1-15),
                # but SCALE mustbe less than or equal to PRECISION.
                if fieldScale > fieldLength:
                    fieldScale = fieldLength
            colClass, kw = self.guessClass(fieldType, fieldLength,
                                           fieldCharset, fieldScale)
            kw['name'] = str(
                soClass.sqlmeta.style.dbColumnToPythonAttr(field).strip())
            kw['dbName'] = str(field)
            kw['notNone'] = not fieldNotNullConstraint
            kw['default'] = defaultSource
            results.append(colClass(**kw))
        return results

    def guessClass(self, t, flength, fCharset, fscale=None):
        """
        An internal method that tries to figure out what Col subclass
        is appropriate given whatever introspective information is
        available -- both very database-specific.
        """

        # TODO: check if negative values are allowed for fscale

        if t == 'smallint':        # -32,768 to +32,767, 16 bits
            return col.IntCol, {}
        elif t == 'integer':       # -2,147,483,648 to +2,147,483,647, 32 bits
            return col.IntCol, {}
        elif t == 'bigint':
            # -2^63 to 2^63-1 or
            # -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807, 64 bits
            return col.IntCol, {}
        elif t == 'float':
            # 32 bits, 3.4x10^-38 to 3.4x10^38, 7 digit precision
            # (7 significant decimals)
            return col.FloatCol, {}
        elif t == 'double':
            # 64 bits, 1.7x10^-308 to 1.7x10^308, 15 digit precision
            # (15 significant decimals)
            return col.FloatCol, {}
        elif t == 'numeric':
            # Numeric and Decimal are internally stored as smallint,
            # integer or bigint depending on the size.
            # They can handle up to 18 digits.
            if (not flength or not fscale):
                # If neither PRECISION nor SCALE are specified,
                # Firebird/InterBase defines the column as INTEGER
                # instead of NUMERIC and stores only the integer portion
                # of the value
                return col.IntCol, {}
            # check if negative values are allowed for fscale
            return col.DecimalCol, {'size': flength, 'precision': fscale}

        elif t == 'decimal':
            # Check if negative values are allowed for fscale
            return col.DecimalCol, {'size': flength, 'precision': fscale}
        elif t == 'date':  # 32 bits, 1 Jan 100. to 29 Feb 32768.
            return col.DateCol, {}
        elif t == 'time':  # 32 bits, 00:00 to 23:59.9999
            return col.TimeCol, {}
        elif t == 'timestamp':  # 64 bits, 1 Jan 100 to 28 Feb 32768.
            return col.DateTimeCol, {}
        elif t == 'char':  # 32767 bytes
            if fCharset and (fCharset != "NONE"):
                return col.UnicodeCol, {'length': flength, 'varchar': False,
                                        'dbEncoding': fCharset}
            elif self.dbEncoding:
                return col.UnicodeCol, {'length': flength, 'varchar': False,
                                        'dbEncoding': self.dbEncoding}
            else:
                return col.StringCol, {'length': flength, 'varchar': False}
        elif t == 'varchar':  # 32767 bytes
            if fCharset and (fCharset != "NONE"):
                return col.UnicodeCol, {'length': flength, 'varchar': True,
                                        'dbEncoding': fCharset}
            elif self.dbEncoding:
                return col.UnicodeCol, {'length': flength, 'varchar': True,
                                        'dbEncoding': self.dbEncoding}
            else:
                return col.StringCol, {'length': flength, 'varchar': True}

        elif t == 'blob':  # 32GB
            return col.BLOBCol, {}
        else:
            return col.Col, {}

    def createEmptyDatabase(self):
        self.module.create_database(
            "CREATE DATABASE '%s' user '%s' password '%s'" %
            (self.db, self.user, self.password))

    def dropDatabase(self):
        self.module.drop_database()
