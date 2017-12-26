from itertools import count
from .converters import sqlrepr


creationOrder = count()


class SODatabaseIndex(object):

    def __init__(self,
                 soClass,
                 name,
                 columns,
                 creationOrder,
                 unique=False):
        self.soClass = soClass
        self.name = name
        self.descriptions = self.convertColumns(columns)
        self.creationOrder = creationOrder
        self.unique = unique

    def get(self, *args, **kw):
        if not self.unique:
            raise AttributeError(
                "'%s' object has no attribute 'get' "
                "(index is not unique)" % self.name)
        connection = kw.pop('connection', None)
        if args and kw:
            raise TypeError("You cannot mix named and unnamed arguments")
        columns = [d['column'] for d in self.descriptions if 'column' in d]
        if kw and len(kw) != len(columns) or \
                args and len(args) != len(columns):
            raise TypeError(
                "get() takes exactly %d argument and an optional "
                "named argument 'connection' (%d given)" % (
                    len(columns), len(args) + len(kw)))
        if args:
            kw = {}
            for i in range(len(args)):
                if columns[i].foreignName is not None:
                    kw[columns[i].foreignName] = args[i]
                else:
                    kw[columns[i].name] = args[i]
        return self.soClass.selectBy(connection=connection, **kw).getOne()

    def convertColumns(self, columns):
        """
        Converts all the columns to dictionary descriptors;
        dereferences string column names.
        """
        new = []
        for desc in columns:
            if not isinstance(desc, dict):
                desc = {'column': desc}
            if 'expression' in desc:
                assert 'column' not in desc, (
                    'You cannot provide both an expression and a column '
                    '(for %s in index %s in %s)' %
                    (desc, self.name, self.soClass))
                assert 'length' not in desc, (
                    'length does not apply to expressions (for %s in '
                    'index %s in %s)' %
                    (desc, self.name, self.soClass))
                new.append(desc)
                continue
            columnName = desc['column']
            if not isinstance(columnName, str):
                columnName = columnName.name
            colDict = self.soClass.sqlmeta.columns
            if columnName not in colDict:
                for possible in colDict.values():
                    if possible.origName == columnName:
                        column = possible
                        break
                else:
                    # None found
                    raise ValueError(
                        "The column by the name %r was not found "
                        "in the class %r" % (columnName, self.soClass))
            else:
                column = colDict[columnName]
            desc['column'] = column
            new.append(desc)
        return new

    def getExpression(self, desc, db):
        if isinstance(desc['expression'], str):
            return desc['expression']
        else:
            return sqlrepr(desc['expression'], db)

    def sqliteCreateIndexSQL(self, soClass):
        if self.unique:
            uniqueOrIndex = 'UNIQUE INDEX'
        else:
            uniqueOrIndex = 'INDEX'
        spec = []
        for desc in self.descriptions:
            if 'expression' in desc:
                spec.append(self.getExpression(desc, 'sqlite'))
            else:
                spec.append(desc['column'].dbName)
        ret = 'CREATE %s %s_%s ON %s (%s)' % \
              (uniqueOrIndex,
               self.soClass.sqlmeta.table,
               self.name,
               self.soClass.sqlmeta.table,
               ', '.join(spec))
        return ret

    postgresCreateIndexSQL = maxdbCreateIndexSQL = mssqlCreateIndexSQL = \
        sybaseCreateIndexSQL = firebirdCreateIndexSQL = sqliteCreateIndexSQL

    def mysqlCreateIndexSQL(self, soClass):
        if self.unique:
            uniqueOrIndex = 'UNIQUE'
        else:
            uniqueOrIndex = 'INDEX'
        spec = []
        for desc in self.descriptions:
            if 'expression' in desc:
                spec.append(self.getExpression(desc, 'mysql'))
            elif 'length' in desc:
                spec.append('%s(%d)' % (desc['column'].dbName, desc['length']))
            else:
                spec.append(desc['column'].dbName)

        return 'ALTER TABLE %s ADD %s %s (%s)' % \
               (soClass.sqlmeta.table, uniqueOrIndex,
                self.name,
                ', '.join(spec))


class DatabaseIndex(object):
    """
    This takes a variable number of parameters, each of which is a
    column for indexing.  Each column may be a column object or the
    string name of the column (*not* the database name).  You may also
    use dictionaries, to further customize the indexing of the column.
    The dictionary may have certain keys:

    'column':
        The column object or string identifier.
    'length':
        MySQL will only index the first N characters if this is
        given.  For other databases this is ignored.
    'expression':
        You can create an index based on an expression, e.g.,
        'lower(column)'.  This can either be a string or a sqlbuilder
        expression.

    Further keys may be added to the column specs in the future.

    The class also take the keyword argument `unique`; if true then
    a UNIQUE index is created.
    """

    baseClass = SODatabaseIndex

    def __init__(self, *columns, **kw):
        kw['columns'] = columns
        self.kw = kw
        self.creationOrder = next(creationOrder)

    def setName(self, value):
        assert self.kw.get('name') is None, \
            "You cannot change a name after it has already been set " \
            "(from %s to %s)" % (self.kw['name'], value)
        self.kw['name'] = value

    def _get_name(self):
        return self.kw['name']

    def _set_name(self, value):
        self.setName(value)

    name = property(_get_name, _set_name)

    def withClass(self, soClass):
        return self.baseClass(soClass=soClass,
                              creationOrder=self.creationOrder, **self.kw)

    def __repr__(self):
        return '<%s %s %s>' % (
            self.__class__.__name__,
            hex(abs(id(self)))[2:],
            self.kw)

__all__ = ['DatabaseIndex']
