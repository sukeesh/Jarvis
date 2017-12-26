from .main import SQLObject
from .sqlbuilder import AND, Alias, ColumnAS, LEFTJOINOn, \
    NoDefault, SQLCall, SQLConstant, SQLObjectField, SQLObjectTable, SQLOp, \
    Select, sqlrepr


class ViewSQLObjectField(SQLObjectField):
    def __init__(self, alias, *arg):
        SQLObjectField.__init__(self, *arg)
        self.alias = alias

    def __sqlrepr__(self, db):
        return self.alias + "." + self.fieldName

    def tablesUsedImmediate(self):
        return [self.tableName]


class ViewSQLObjectTable(SQLObjectTable):
    FieldClass = ViewSQLObjectField

    def __getattr__(self, attr):
        if attr == 'sqlmeta':
            raise AttributeError
        return SQLObjectTable.__getattr__(self, attr)

    def _getattrFromID(self, attr):
        return self.FieldClass(self.soClass.sqlmeta.alias, self.tableName,
                               'id', attr, self.soClass, None)

    def _getattrFromColumn(self, column, attr):
        return self.FieldClass(self.soClass.sqlmeta.alias, self.tableName,
                               column.name, attr, self.soClass, column)


class ViewSQLObject(SQLObject):
    """
    A SQLObject class that derives all it's values from other SQLObject
    classes. Columns on subclasses should use SQLBuilder constructs for dbName,
    and sqlmeta should specify:

    * idName as a SQLBuilder construction
    * clause as SQLBuilder clause for specifying join conditions
      or other restrictions
    * table as an optional alternate name for the class alias

    See test_views.py for simple examples.
    """

    def __classinit__(cls, new_attrs):
        SQLObject.__classinit__(cls, new_attrs)
        # like is_base
        if cls.__name__ != 'ViewSQLObject':
            dbName = hasattr(cls, '_connection') and \
                (cls._connection and cls._connection.dbName) or None

            if getattr(cls.sqlmeta, 'table', None):
                cls.sqlmeta.alias = cls.sqlmeta.table
            else:
                cls.sqlmeta.alias = \
                    cls.sqlmeta.style.pythonClassToDBTable(cls.__name__)
            alias = cls.sqlmeta.alias
            columns = [ColumnAS(cls.sqlmeta.idName, 'id')]
            # {sqlrepr-key: [restriction, *aggregate-column]}
            aggregates = {'': [None]}
            inverseColumns = dict(
                [(y, x) for x, y in cls.sqlmeta.columns.items()])
            for col in cls.sqlmeta.columnList:
                n = inverseColumns[col]
                ascol = ColumnAS(col.dbName, n)
                if isAggregate(col.dbName):
                    restriction = getattr(col, 'aggregateClause', None)
                    if restriction:
                        restrictkey = sqlrepr(restriction, dbName)
                        aggregates[restrictkey] = \
                            aggregates.get(restrictkey, [restriction]) + \
                            [ascol]
                    else:
                        aggregates[''].append(ascol)
                else:
                    columns.append(ascol)

            metajoin = getattr(cls.sqlmeta, 'join', NoDefault)
            clause = getattr(cls.sqlmeta, 'clause', NoDefault)
            select = Select(columns,
                            distinct=True,
                            # @@ LDO check if this really mattered
                            # for performance
                            # @@ Postgres (and MySQL?) extension!
                            # distinctOn=cls.sqlmeta.idName,
                            join=metajoin,
                            clause=clause)

            aggregates = aggregates.values()

            if aggregates != [[None]]:
                join = []
                last_alias = "%s_base" % alias
                last_id = "id"
                last = Alias(select, last_alias)
                columns = [
                    ColumnAS(SQLConstant("%s.%s" % (last_alias, x.expr2)),
                             x.expr2) for x in columns]

                for i, agg in enumerate(aggregates):
                    restriction = agg[0]
                    if restriction is None:
                        restriction = clause
                    else:
                        restriction = AND(clause, restriction)
                    agg = agg[1:]
                    agg_alias = "%s_%s" % (alias, i)
                    agg_id = '%s_id' % agg_alias
                    if not last.q.alias.endswith('base'):
                        last = None
                    new_alias = Alias(Select(
                        [ColumnAS(cls.sqlmeta.idName, agg_id)] + agg,
                        groupBy=cls.sqlmeta.idName,
                        join=metajoin,
                        clause=restriction),
                        agg_alias)
                    agg_join = LEFTJOINOn(last, new_alias,
                                          "%s.%s = %s.%s" % (
                                              last_alias, last_id,
                                              agg_alias, agg_id))

                    join.append(agg_join)
                    for col in agg:
                        columns.append(
                            ColumnAS(SQLConstant(
                                "%s.%s" % (agg_alias, col.expr2)),
                                col.expr2))

                    last = new_alias
                    last_alias = agg_alias
                    last_id = agg_id
                select = Select(columns,
                                join=join)

            cls.sqlmeta.table = Alias(select, alias)
            cls.q = ViewSQLObjectTable(cls)
            for n, col in cls.sqlmeta.columns.items():
                col.dbName = n


def isAggregate(expr):
    if isinstance(expr, SQLCall):
        return True
    if isinstance(expr, SQLOp):
        return isAggregate(expr.expr1) or isAggregate(expr.expr2)
    return False
