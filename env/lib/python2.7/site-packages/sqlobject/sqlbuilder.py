"""
sqlobject.sqlbuilder
--------------------

:author: Ian Bicking <ianb@colorstudy.com>

Builds SQL expressions from normal Python expressions.

Disclaimer
----------

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 2.1 of the
License, or (at your option any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301,
USA.

Instructions
------------

To begin a SQL expression, you must use some sort of SQL object -- a
field, table, or SQL statement (``SELECT``, ``INSERT``, etc.)  You can
then use normal operators, with the exception of: `and`, `or`, `not`,
and `in`.  You can use the `AND`, `OR`, `NOT`, and `IN` functions
instead, or you can also use `&`, `|`, and `~` for `and`, `or`, and
`not` respectively (however -- the precidence for these operators
doesn't work as you would want, so you must use many parenthesis).

To create a sql field, table, or constant/function, use the namespaces
`table`, `const`, and `func`.  For instance, ``table.address`` refers
to the ``address`` table, and ``table.address.state`` refers to the
``state`` field in the address table.  ``const.NULL`` is the ``NULL``
SQL constant, and ``func.NOW()`` is the ``NOW()`` function call
(`const` and `func` are actually identicle, but the two names are
provided for clarity).  Once you create this object, expressions
formed with it will produce SQL statements.

The ``sqlrepr(obj)`` function gets the SQL representation of these
objects, as well as the proper SQL representation of basic Python
types (None==NULL).

There are a number of DB-specific SQL features that this does not
implement.  There are a bunch of normal ANSI features also not present.

See the bottom of this module for some examples, and run it (i.e.
``python sql.py``) to see the results of those examples.

"""

########################################
# Constants
########################################

import fnmatch
import operator
import re
import threading
import types
import weakref

from . import classregistry
from .converters import registerConverter, sqlrepr, quote_str, unquote_str
from .compat import PY2, string_type


class VersionError(Exception):
    pass


class NoDefault:
    pass


class SQLObjectState(object):
    def __init__(self, soObject, connection=None):
        self.soObject = weakref.proxy(soObject)
        self.connection = connection


safeSQLRE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$')


def sqlIdentifier(obj):
    # some db drivers return unicode column names
    return isinstance(obj, string_type) and bool(safeSQLRE.search(obj.strip()))


def execute(expr, executor):
    if hasattr(expr, 'execute'):
        return expr.execute(executor)
    else:
        return expr


def _str_or_sqlrepr(expr, db):
    if isinstance(expr, string_type):
        return expr
    return sqlrepr(expr, db)


########################################
# Expression generation
########################################


class SQLExpression:
    def __add__(self, other):
        return SQLOp("+", self, other)

    def __radd__(self, other):
        return SQLOp("+", other, self)

    def __sub__(self, other):
        return SQLOp("-", self, other)

    def __rsub__(self, other):
        return SQLOp("-", other, self)

    def __mul__(self, other):
        return SQLOp("*", self, other)

    def __rmul__(self, other):
        return SQLOp("*", other, self)

    def __div__(self, other):
        return SQLOp("/", self, other)

    def __rdiv__(self, other):
        return SQLOp("/", other, self)

    def __truediv__(self, other):
        return SQLOp("/", self, other)

    def __rtruediv__(self, other):
        return SQLOp("/", other, self)

    def __floordiv__(self, other):
        return SQLConstant("FLOOR")(SQLOp("/", self, other))

    def __rfloordiv__(self, other):
        return SQLConstant("FLOOR")(SQLOp("/", other, self))

    def __pos__(self):
        return SQLPrefix("+", self)

    def __neg__(self):
        return SQLPrefix("-", self)

    def __pow__(self, other):
        return SQLConstant("POW")(self, other)

    def __rpow__(self, other):
        return SQLConstant("POW")(other, self)

    def __abs__(self):
        return SQLConstant("ABS")(self)

    def __mod__(self, other):
        return SQLModulo(self, other)

    def __rmod__(self, other):
        return SQLConstant("MOD")(other, self)

    def __lt__(self, other):
        return SQLOp("<", self, other)

    def __le__(self, other):
        return SQLOp("<=", self, other)

    def __gt__(self, other):
        return SQLOp(">", self, other)

    def __ge__(self, other):
        return SQLOp(">=", self, other)

    def __eq__(self, other):
        if other is None:
            return ISNULL(self)
        else:
            return SQLOp("=", self, other)

    def __ne__(self, other):
        if other is None:
            return ISNOTNULL(self)
        else:
            return SQLOp("<>", self, other)

    def __and__(self, other):
        return SQLOp("AND", self, other)

    def __rand__(self, other):
        return SQLOp("AND", other, self)

    def __or__(self, other):
        return SQLOp("OR", self, other)

    def __ror__(self, other):
        return SQLOp("OR", other, self)

    def __invert__(self):
        return SQLPrefix("NOT", self)

    def __call__(self, *args):
        return SQLCall(self, args)

    def __repr__(self):
        try:
            return self.__sqlrepr__(None)
        except AssertionError:
            return '<%s %s>' % (
                self.__class__.__name__, hex(id(self))[2:])

    def __str__(self):
        return repr(self)

    def __cmp__(self, other):
        raise VersionError("Python 2.1+ required")

    def __rcmp__(self, other):
        raise VersionError("Python 2.1+ required")

    def startswith(self, s):
        return STARTSWITH(self, s)

    def endswith(self, s):
        return ENDSWITH(self, s)

    def contains(self, s):
        return CONTAINSSTRING(self, s)

    def components(self):
        return []

    def tablesUsed(self, db):
        return self.tablesUsedSet(db)

    def tablesUsedSet(self, db):
        tables = set()
        for table in self.tablesUsedImmediate():
            if hasattr(table, '__sqlrepr__'):
                table = sqlrepr(table, db)
            tables.add(table)
        for component in self.components():
            tables.update(tablesUsedSet(component, db))
        return tables

    def tablesUsedImmediate(self):
        return []


#######################################
# Converter for SQLExpression instances
#######################################


def SQLExprConverter(value, db):
    return value.__sqlrepr__()

registerConverter(SQLExpression, SQLExprConverter)


def tablesUsedSet(obj, db):
    if hasattr(obj, "tablesUsedSet"):
        return obj.tablesUsedSet(db)
    else:
        return {}


if PY2:
    div = operator.div
else:
    div = operator.truediv


operatorMap = {
    "+": operator.add,
    "/": div,
    "-": operator.sub,
    "*": operator.mul,
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
    "IN": operator.contains,
    "IS": operator.eq,
}


class SQLOp(SQLExpression):
    def __init__(self, op, expr1, expr2):
        self.op = op.upper()
        self.expr1 = expr1
        self.expr2 = expr2

    def __sqlrepr__(self, db):
        s1 = sqlrepr(self.expr1, db)
        s2 = sqlrepr(self.expr2, db)
        if s1[0] != '(' and s1 != 'NULL':
            s1 = '(' + s1 + ')'
        if s2[0] != '(' and s2 != 'NULL':
            s2 = '(' + s2 + ')'
        return "(%s %s %s)" % (s1, self.op, s2)

    def components(self):
        return [self.expr1, self.expr2]

    def execute(self, executor):
        if self.op == "AND":
            return execute(self.expr1, executor) \
                and execute(self.expr2, executor)
        elif self.op == "OR":
            return execute(self.expr1, executor) \
                or execute(self.expr2, executor)
        else:
            return operatorMap[self.op.upper()](execute(self.expr1, executor),
                                                execute(self.expr2, executor))

registerConverter(SQLOp, SQLExprConverter)


class SQLModulo(SQLOp):
    def __init__(self, expr1, expr2):
        SQLOp.__init__(self, '%', expr1, expr2)

    def __sqlrepr__(self, db):
        if db == 'sqlite':
            return SQLOp.__sqlrepr__(self, db)
        s1 = sqlrepr(self.expr1, db)
        s2 = sqlrepr(self.expr2, db)
        return "MOD(%s, %s)" % (s1, s2)

registerConverter(SQLModulo, SQLExprConverter)


class SQLCall(SQLExpression):
    def __init__(self, expr, args):
        self.expr = expr
        self.args = args

    def __sqlrepr__(self, db):
        return "%s%s" % (sqlrepr(self.expr, db), sqlrepr(self.args, db))

    def components(self):
        return [self.expr] + list(self.args)

    def execute(self, executor):
        raise ValueError("I don't yet know how to locally execute functions")

registerConverter(SQLCall, SQLExprConverter)


class SQLPrefix(SQLExpression):
    def __init__(self, prefix, expr):
        self.prefix = prefix
        self.expr = expr

    def __sqlrepr__(self, db):
        return "%s %s" % (self.prefix, sqlrepr(self.expr, db))

    def components(self):
        return [self.expr]

    def execute(self, executor):
        prefix = self.prefix
        expr = execute(self.expr, executor)
        if prefix == "+":
            return expr
        elif prefix == "-":
            return -expr
        elif prefix.upper() == "NOT":
            return not expr

registerConverter(SQLPrefix, SQLExprConverter)


class SQLConstant(SQLExpression):
    def __init__(self, const):
        self.const = const

    def __sqlrepr__(self, db):
        return self.const

    def execute(self, executor):
        raise ValueError("I don't yet know how to execute SQL constants")

registerConverter(SQLConstant, SQLExprConverter)


class SQLTrueClauseClass(SQLExpression):
    def __sqlrepr__(self, db):
        return "1 = 1"

    def execute(self, executor):
        return 1

SQLTrueClause = SQLTrueClauseClass()

registerConverter(SQLTrueClauseClass, SQLExprConverter)

########################################
# Namespaces
########################################


class Field(SQLExpression):
    def __init__(self, tableName, fieldName):
        self.tableName = tableName
        self.fieldName = fieldName

    def __sqlrepr__(self, db):
        return self.tableName + "." + self.fieldName

    def tablesUsedImmediate(self):
        return [self.tableName]

    def execute(self, executor):
        return executor.field(self.tableName, self.fieldName)


class SQLObjectField(Field):
    def __init__(self, tableName, fieldName, original, soClass, column):
        Field.__init__(self, tableName, fieldName)
        self.original = original
        self.soClass = soClass
        self.column = column

    def _from_python(self, value):
        column = self.column
        if not isinstance(value, SQLExpression) and \
                column and column.from_python:
            value = column.from_python(value, SQLObjectState(self.soClass))
        return value

    def __eq__(self, other):
        if other is None:
            return ISNULL(self)
        other = self._from_python(other)
        return SQLOp('=', self, other)

    def __ne__(self, other):
        if other is None:
            return ISNOTNULL(self)
        other = self._from_python(other)
        return SQLOp('<>', self, other)

    def startswith(self, s):
        s = self._from_python(s)
        return STARTSWITH(self, s)

    def endswith(self, s):
        s = self._from_python(s)
        return ENDSWITH(self, s)

    def contains(self, s):
        s = self._from_python(s)
        return CONTAINSSTRING(self, s)

registerConverter(SQLObjectField, SQLExprConverter)


class Table(SQLExpression):
    FieldClass = Field

    def __init__(self, tableName):
        self.tableName = tableName

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return self.FieldClass(self.tableName, attr)

    def __sqlrepr__(self, db):
        return _str_or_sqlrepr(self.tableName, db)

    def execute(self, executor):
        raise ValueError("Tables don't have values")


class SQLObjectTable(Table):
    FieldClass = SQLObjectField

    def __init__(self, soClass):
        self.soClass = soClass
        assert soClass.sqlmeta.table, (
            "Bad table name in class %r: %r"
            % (soClass, soClass.sqlmeta.table))
        Table.__init__(self, soClass.sqlmeta.table)

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        if attr == 'id':
            return self._getattrFromID(attr)
        elif attr in self.soClass.sqlmeta.columns:
            column = self.soClass.sqlmeta.columns[attr]
            return self._getattrFromColumn(column, attr)
        elif attr + 'ID' in \
            [k for (k, v) in self.soClass.sqlmeta.columns.items()
                if v.foreignKey]:
            attr += 'ID'
            column = self.soClass.sqlmeta.columns[attr]
            return self._getattrFromColumn(column, attr)
        else:
            raise AttributeError(
                "%s instance has no attribute '%s'" % (self.soClass.__name__,
                                                       attr))

    def _getattrFromID(self, attr):
        return self.FieldClass(self.tableName, self.soClass.sqlmeta.idName,
                               attr, self.soClass, None)

    def _getattrFromColumn(self, column, attr):
        return self.FieldClass(self.tableName, column.dbName, attr,
                               self.soClass, column)


class SQLObjectTableWithJoins(SQLObjectTable):

    def __getattr__(self, attr):
        if attr + 'ID' in \
            [k for (k, v) in self.soClass.sqlmeta.columns.items()
                if v.foreignKey]:
            column = self.soClass.sqlmeta.columns[attr + 'ID']
            return self._getattrFromForeignKey(column, attr)
        elif attr in [x.joinMethodName for x in self.soClass.sqlmeta.joins]:
            join = [x for x in self.soClass.sqlmeta.joins
                    if x.joinMethodName == attr][0]
            return self._getattrFromJoin(join, attr)
        else:
            return SQLObjectTable.__getattr__(self, attr)

    def _getattrFromForeignKey(self, column, attr):
        ret = getattr(self, column.name) == \
            getattr(self.soClass, '_SO_class_' + column.foreignKey).q.id
        return ret

    def _getattrFromJoin(self, join, attr):
        if hasattr(join, 'otherColumn'):
            return AND(
                join.otherClass.q.id == Field(join.intermediateTable,
                                              join.otherColumn),
                Field(join.intermediateTable,
                      join.joinColumn) == self.soClass.q.id)
        else:
            return getattr(join.otherClass.q, join.joinColumn) == \
                self.soClass.q.id


class TableSpace:
    TableClass = Table

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return self.TableClass(attr)


class ConstantSpace:
    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return SQLConstant(attr)


########################################
# Table aliases
########################################

class AliasField(Field):
    def __init__(self, tableName, fieldName, alias, aliasTable):
        Field.__init__(self, tableName, fieldName)
        self.alias = alias
        self.aliasTable = aliasTable

    def __sqlrepr__(self, db):
        fieldName = self.fieldName
        if isinstance(fieldName, SQLExpression):
            fieldName = sqlrepr(fieldName, db)
        return self.alias + "." + fieldName

    def tablesUsedImmediate(self):
        return [self.aliasTable]


class AliasTable(Table):
    as_string = ''  # set it to "AS" if your database requires it
    FieldClass = AliasField

    _alias_lock = threading.Lock()
    _alias_counter = 0

    def __init__(self, table, alias=None):
        if hasattr(table, "sqlmeta"):
            tableName = SQLConstant(table.sqlmeta.table)
        elif isinstance(table, (Select, Union)):
            assert alias is not None, \
                "Alias name cannot be constructed from Select instances, " \
                "please provide an 'alias' keyword."
            tableName = Subquery('', table)
            table = None
        else:
            tableName = SQLConstant(table)
            table = None
        Table.__init__(self, tableName)
        self.table = table
        if alias is None:
            self._alias_lock.acquire()
            try:
                AliasTable._alias_counter += 1
                alias = "%s_alias%d" % (tableName, AliasTable._alias_counter)
            finally:
                self._alias_lock.release()
        self.alias = alias

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        if self.table:
            attr = getattr(self.table.q, attr).fieldName
        return self.FieldClass(self.tableName, attr, self.alias, self)

    def __sqlrepr__(self, db):
        return "%s %s %s" % (sqlrepr(self.tableName, db), self.as_string,
                             self.alias)


class Alias(SQLExpression):
    def __init__(self, table, alias=None):
        self.q = AliasTable(table, alias)

    def __sqlrepr__(self, db):
        return sqlrepr(self.q, db)

    def components(self):
        return [self.q]


class Union(SQLExpression):
    def __init__(self, *tables):
        tabs = []
        for t in tables:
            if not isinstance(t, SQLExpression) and hasattr(t, 'sqlmeta'):
                t = t.sqlmeta.table
                if isinstance(t, Alias):
                    t = t.q
                if isinstance(t, Table):
                    t = t.tableName
                if not isinstance(t, SQLExpression):
                    t = SQLConstant(t)
            tabs.append(t)
        self.tables = tabs

    def __sqlrepr__(self, db):
        return " UNION ".join([str(sqlrepr(t, db)) for t in self.tables])

########################################
# SQL Statements
########################################


class Select(SQLExpression):
    def __init__(self, items=NoDefault, where=NoDefault, groupBy=NoDefault,
                 having=NoDefault, orderBy=NoDefault, limit=NoDefault,
                 join=NoDefault, lazyColumns=False, distinct=False,
                 start=0, end=None, reversed=False, forUpdate=False,
                 clause=NoDefault, staticTables=NoDefault,
                 distinctOn=NoDefault):
        self.ops = {}
        if not isinstance(items, (list, tuple, types.GeneratorType)):
            items = [items]
        if clause is NoDefault and where is not NoDefault:
            clause = where
        if staticTables is NoDefault:
            staticTables = []
        self.ops['items'] = items
        self.ops['clause'] = clause
        self.ops['groupBy'] = groupBy
        self.ops['having'] = having
        self.ops['orderBy'] = orderBy
        self.ops['limit'] = limit
        self.ops['join'] = join
        self.ops['lazyColumns'] = lazyColumns
        self.ops['distinct'] = distinct
        self.ops['distinctOn'] = distinctOn
        self.ops['start'] = start
        self.ops['end'] = end
        self.ops['reversed'] = reversed
        self.ops['forUpdate'] = forUpdate
        self.ops['staticTables'] = staticTables

    def clone(self, **newOps):
        ops = self.ops.copy()
        ops.update(newOps)
        return self.__class__(**ops)

    def newItems(self, items):
        return self.clone(items=items)

    def newClause(self, new_clause):
        return self.clone(clause=new_clause)

    def orderBy(self, orderBy):
        return self.clone(orderBy=orderBy)

    def unlimited(self):
        return self.clone(limit=NoDefault, start=0, end=None)

    def limit(self, limit):
        self.clone(limit=limit)

    def lazyColumns(self, value):
        return self.clone(lazyColumns=value)

    def reversed(self):
        return self.clone(reversed=not self.ops.get('reversed', False))

    def distinct(self):
        return self.clone(distinct=True)

    def filter(self, filter_clause):
        if filter_clause is None:
            # None doesn't filter anything, it's just a no-op:
            return self
        clause = self.ops['clause']
        if isinstance(clause, string_type):
            clause = SQLConstant('(%s)' % clause)
        return self.newClause(AND(clause, filter_clause))

    def __sqlrepr__(self, db):

        select = "SELECT"
        if self.ops['distinct']:
            select += " DISTINCT"
            if self.ops['distinctOn'] is not NoDefault:
                select += " ON(%s)" % _str_or_sqlrepr(
                    self.ops['distinctOn'], db)
        if not self.ops['lazyColumns']:
            select += " %s" % ", ".join(
                [str(_str_or_sqlrepr(v, db)) for v in self.ops['items']])
        else:
            select += " %s" % _str_or_sqlrepr(self.ops['items'][0], db)

        join = []
        join_str = ''
        if self.ops['join'] is not NoDefault and self.ops['join'] is not None:
            _join = self.ops['join']
            if isinstance(_join, str):
                join_str = " " + _join
            elif isinstance(_join, SQLJoin):
                join.append(_join)
            else:
                join.extend(_join)
        tables = set()
        for x in self.ops['staticTables']:
            if isinstance(x, SQLExpression):
                x = sqlrepr(x, db)
            tables.add(x)
        things = list(self.ops['items']) + join
        if self.ops['clause'] is not NoDefault:
            things.append(self.ops['clause'])
        for thing in things:
            if isinstance(thing, SQLExpression):
                tables.update(tablesUsedSet(thing, db))
        for j in join:
            t1 = _str_or_sqlrepr(j.table1, db)
            if t1 in tables:
                tables.remove(t1)
            t2 = _str_or_sqlrepr(j.table2, db)
            if t2 in tables:
                tables.remove(t2)
        if tables:
            select += " FROM %s" % ", ".join(sorted(tables))
        elif join:
            select += " FROM"
        tablesYet = tables
        for j in join:
            if tablesYet and j.table1:
                sep = ", "
            else:
                sep = " "
            select += sep + sqlrepr(j, db)
            tablesYet = True

        if join_str:
            select += join_str

        if self.ops['clause'] is not NoDefault:
            select += " WHERE %s" % _str_or_sqlrepr(self.ops['clause'], db)
        if self.ops['groupBy'] is not NoDefault:
            groupBy = _str_or_sqlrepr(self.ops['groupBy'], db)
            if isinstance(self.ops['groupBy'], (list, tuple)):
                groupBy = groupBy[1:-1]  # Remove parens
            select += " GROUP BY %s" % groupBy
        if self.ops['having'] is not NoDefault:
            select += " HAVING %s" % _str_or_sqlrepr(self.ops['having'], db)
        if self.ops['orderBy'] is not NoDefault and \
           self.ops['orderBy'] is not None:
            orderBy = self.ops['orderBy']
            if self.ops['reversed']:
                reverser = DESC
            else:
                def reverser(x):
                    return x
            if isinstance(orderBy, (list, tuple)):
                select += " ORDER BY %s" % ", ".join(
                    [_str_or_sqlrepr(reverser(_x), db) for _x in orderBy])
            else:
                select += " ORDER BY %s" % _str_or_sqlrepr(
                    reverser(orderBy), db)
        start, end = self.ops['start'], self.ops['end']
        if self.ops['limit'] is not NoDefault:
            end = start + self.ops['limit']
        if start or end:
            from .dbconnection import dbConnectionForScheme
            select = dbConnectionForScheme(db)._queryAddLimitOffset(select,
                                                                    start, end)
        if self.ops['forUpdate']:
            select += " FOR UPDATE"
        return select

registerConverter(Select, SQLExprConverter)


class Insert(SQLExpression):
    def __init__(self, table, valueList=None, values=None, template=NoDefault):
        self.template = template
        self.table = table
        if valueList:
            if values:
                raise TypeError("You may only give valueList *or* values")
            self.valueList = valueList
        else:
            self.valueList = [values]

    def __sqlrepr__(self, db):
        if not self.valueList:
            return ''
        insert = "INSERT INTO %s" % self.table
        allowNonDict = True
        template = self.template
        if (template is NoDefault) and isinstance(self.valueList[0], dict):
            template = list(sorted(self.valueList[0].keys()))
            allowNonDict = False
        if template is not NoDefault:
            insert += " (%s)" % ", ".join(template)
        insert += " VALUES "
        listToJoin = []
        listToJoin_app = listToJoin.append
        for value in self.valueList:
            if isinstance(value, dict):
                if template is NoDefault:
                    raise TypeError(
                        "You can't mix non-dictionaries with dictionaries "
                        "in an INSERT if you don't provide a template (%s)" %
                        repr(value))
                value = dictToList(template, value)
            elif not allowNonDict:
                raise TypeError(
                    "You can't mix non-dictionaries with dictionaries "
                    "in an INSERT if you don't provide a template (%s)" %
                    repr(value))
            listToJoin_app("(%s)" % ", ".join([sqlrepr(v, db) for v in value]))
        insert = "%s%s" % (insert, ", ".join(listToJoin))
        return insert

registerConverter(Insert, SQLExprConverter)


def dictToList(template, dict):
    list = []
    for key in template:
        list.append(dict[key])
    if len(dict.keys()) > len(template):
        raise TypeError(
            "Extra entries in dictionary that aren't asked for in template "
            "(template=%s, dict=%s)" % (repr(template), repr(dict)))
    return list


class Update(SQLExpression):
    def __init__(self, table, values, template=NoDefault, where=NoDefault):
        self.table = table
        self.values = values
        self.template = template
        self.whereClause = where

    def __sqlrepr__(self, db):
        update = "%s %s" % (self.sqlName(), self.table)
        update += " SET"
        first = True
        if self.template is not NoDefault:
            for i in range(len(self.template)):
                if first:
                    first = False
                else:
                    update += ","
                update += " %s=%s" % (self.template[i],
                                      sqlrepr(self.values[i], db))
        else:
            for key, value in sorted(self.values.items()):
                if first:
                    first = False
                else:
                    update += ","
                update += " %s=%s" % (key, sqlrepr(value, db))
        if self.whereClause is not NoDefault:
            update += " WHERE %s" % _str_or_sqlrepr(self.whereClause, db)
        return update

    def sqlName(self):
        return "UPDATE"

registerConverter(Update, SQLExprConverter)


class Delete(SQLExpression):
    """To be safe, this will signal an error if there is no where clause,
    unless you pass in where=None to the constructor."""
    def __init__(self, table, where=NoDefault):
        self.table = table
        if where is NoDefault:
            raise TypeError(
                "You must give a where clause or pass in None "
                "to indicate no where clause")
        self.whereClause = where

    def __sqlrepr__(self, db):
        whereClause = self.whereClause
        if whereClause is None:
            return "DELETE FROM %s" % self.table
        whereClause = _str_or_sqlrepr(whereClause, db)
        return "DELETE FROM %s WHERE %s" % (self.table, whereClause)

registerConverter(Delete, SQLExprConverter)


class Replace(Update):
    def sqlName(self):
        return "REPLACE"

registerConverter(Replace, SQLExprConverter)

########################################
# SQL Builtins
########################################


class DESC(SQLExpression):

    def __init__(self, expr):
        self.expr = expr

    def __sqlrepr__(self, db):
        if isinstance(self.expr, DESC):
            return sqlrepr(self.expr.expr, db)
        return '%s DESC' % sqlrepr(self.expr, db)


def AND(*ops):
    if not ops:
        return None
    op1 = ops[0]
    ops = ops[1:]
    if ops:
        return SQLOp("AND", op1, AND(*ops))
    else:
        return op1


def OR(*ops):
    if not ops:
        return None
    op1 = ops[0]
    ops = ops[1:]
    if ops:
        return SQLOp("OR", op1, OR(*ops))
    else:
        return op1


def NOT(op):
    return SQLPrefix("NOT", op)


def _IN(item, list):
    return SQLOp("IN", item, list)


def IN(item, list):
    from .sresults import SelectResults  # Import here to avoid circular import
    if isinstance(list, SelectResults):
        query = list.queryForSelect()
        query.ops['items'] = [list.sourceClass.q.id]
        list = query
    if isinstance(list, Select):
        return INSubquery(item, list)
    else:
        return _IN(item, list)


def NOTIN(item, list):
    if isinstance(list, Select):
        return NOTINSubquery(item, list)
    else:
        return NOT(_IN(item, list))


def STARTSWITH(expr, pattern):
    return LIKE(expr, _LikeQuoted(pattern) + '%', escape='\\')


def ENDSWITH(expr, pattern):
    return LIKE(expr, '%' + _LikeQuoted(pattern), escape='\\')


def CONTAINSSTRING(expr, pattern):
    return LIKE(expr, '%' + _LikeQuoted(pattern) + '%', escape='\\')


def ISNULL(expr):
    return SQLOp("IS", expr, None)


def ISNOTNULL(expr):
    return SQLOp("IS NOT", expr, None)


class ColumnAS(SQLOp):
    ''' Just like SQLOp('AS', expr, name) except without the parentheses '''
    def __init__(self, expr, name):
        if isinstance(name, string_type):
            name = SQLConstant(name)
        SQLOp.__init__(self, 'AS', expr, name)

    def __sqlrepr__(self, db):
        return "%s %s %s" % (sqlrepr(self.expr1, db), self.op,
                             sqlrepr(self.expr2, db))


class _LikeQuoted:
    # It assumes prefix and postfix are strings; usually just a percent sign.

    # @@: I'm not sure what the quoting rules really are for all the
    # databases

    def __init__(self, expr):
        self.expr = expr
        self.prefix = ''
        self.postfix = ''

    def __radd__(self, s):
        self.prefix = s + self.prefix
        return self

    def __add__(self, s):
        self.postfix += s
        return self

    def __sqlrepr__(self, db):
        s = self.expr
        if isinstance(s, SQLExpression):
            values = []
            if self.prefix:
                values.append(quote_str(self.prefix, db))
            s = _quote_like_special(sqlrepr(s, db), db)
            values.append(s)
            if self.postfix:
                values.append(quote_str(self.postfix, db))
            if db == "mysql":
                return "CONCAT(%s)" % ", ".join(values)
            elif db in ("mssql", "sybase"):
                return " + ".join(values)
            else:
                return " || ".join(values)
        elif isinstance(s, string_type):
            s = _quote_like_special(unquote_str(sqlrepr(s, db)), db)
            return quote_str("%s%s%s" % (self.prefix, s, self.postfix), db)
        else:
            raise TypeError(
                "expected str, unicode or SQLExpression, got %s" % type(s))


def _quote_like_special(s, db):
    if db in ('postgres', 'rdbhost'):
        escape = r'\\'
    else:
        escape = '\\'
    s = s.replace('\\', r'\\').\
        replace('%', escape + '%').\
        replace('_', escape + '_')
    return s


class CONCAT(SQLExpression):
    def __init__(self, *expressions):
        self.expressions = expressions

    def __sqlrepr__(self, db):
        values = [sqlrepr(expr, db) for expr in self.expressions]
        if db == "mysql":
            return "CONCAT(%s)" % ", ".join(values)
        elif db in ("mssql", "sybase"):
            return " + ".join(values)
        else:
            return " || ".join(values)

########################################
# SQL JOINs
########################################


class SQLJoin(SQLExpression):
    def __init__(self, table1, table2, op=','):
        if hasattr(table1, 'sqlmeta'):
            table1 = table1.sqlmeta.table
        if hasattr(table2, 'sqlmeta'):
            table2 = table2.sqlmeta.table
        if isinstance(table1, str):
            table1 = SQLConstant(table1)
        if isinstance(table2, str):
            table2 = SQLConstant(table2)
        self.table1 = table1
        self.table2 = table2
        self.op = op

    def __sqlrepr__(self, db):
        if self.table1:
            return "%s%s %s" % (sqlrepr(self.table1, db), self.op,
                                sqlrepr(self.table2, db))
        else:
            return "%s %s" % (self.op, sqlrepr(self.table2, db))

registerConverter(SQLJoin, SQLExprConverter)


def JOIN(table1, table2):
    return SQLJoin(table1, table2, " JOIN")


def INNERJOIN(table1, table2):
    return SQLJoin(table1, table2, " INNER JOIN")


def CROSSJOIN(table1, table2):
    return SQLJoin(table1, table2, " CROSS JOIN")


def STRAIGHTJOIN(table1, table2):
    return SQLJoin(table1, table2, " STRAIGHT JOIN")


def LEFTJOIN(table1, table2):
    return SQLJoin(table1, table2, " LEFT JOIN")


def LEFTOUTERJOIN(table1, table2):
    return SQLJoin(table1, table2, " LEFT OUTER JOIN")


def NATURALJOIN(table1, table2):
    return SQLJoin(table1, table2, " NATURAL JOIN")


def NATURALLEFTJOIN(table1, table2):
    return SQLJoin(table1, table2, " NATURAL LEFT JOIN")


def NATURALLEFTOUTERJOIN(table1, table2):
    return SQLJoin(table1, table2, " NATURAL LEFT OUTER JOIN")


def RIGHTJOIN(table1, table2):
    return SQLJoin(table1, table2, " RIGHT JOIN")


def RIGHTOUTERJOIN(table1, table2):
    return SQLJoin(table1, table2, " RIGHT OUTER JOIN")


def NATURALRIGHTJOIN(table1, table2):
    return SQLJoin(table1, table2, " NATURAL RIGHT JOIN")


def NATURALRIGHTOUTERJOIN(table1, table2):
    return SQLJoin(table1, table2, " NATURAL RIGHT OUTER JOIN")


def FULLJOIN(table1, table2):
    return SQLJoin(table1, table2, " FULL JOIN")


def FULLOUTERJOIN(table1, table2):
    return SQLJoin(table1, table2, " FULL OUTER JOIN")


def NATURALFULLJOIN(table1, table2):
    return SQLJoin(table1, table2, " NATURAL FULL JOIN")


def NATURALFULLOUTERJOIN(table1, table2):
    return SQLJoin(table1, table2, " NATURAL FULL OUTER JOIN")


class SQLJoinConditional(SQLJoin):
    """Conditional JOIN"""
    def __init__(self, table1, table2, op,
                 on_condition=None, using_columns=None):
        """For condition you must give on_condition or using_columns
        but not both

        on_condition can be a string or SQLExpression, for example
            Table1.q.col1 == Table2.q.col2
        using_columns can be a string or a list of columns, e.g.
            (Table1.q.col1, Table2.q.col2)
        """
        if not on_condition and not using_columns:
            raise TypeError("You must give ON condition or USING columns")
        if on_condition and using_columns:
            raise TypeError(
                "You must give ON condition or USING columns but not both")
        SQLJoin.__init__(self, table1, table2, op)
        self.on_condition = on_condition
        self.using_columns = using_columns

    def __sqlrepr__(self, db):
        if self.on_condition:
            on_condition = self.on_condition
            if hasattr(on_condition, "__sqlrepr__"):
                on_condition = sqlrepr(on_condition, db)
            join = "%s %s ON %s" % (self.op, sqlrepr(self.table2, db),
                                    on_condition)
            if self.table1:
                join = "%s %s" % (sqlrepr(self.table1, db), join)
            return join
        elif self.using_columns:
            using_columns = []
            for col in self.using_columns:
                if hasattr(col, "__sqlrepr__"):
                    col = sqlrepr(col, db)
                using_columns.append(col)
            using_columns = ", ".join(using_columns)
            join = "%s %s USING (%s)" % (self.op, sqlrepr(self.table2, db),
                                         using_columns)
            if self.table1:
                join = "%s %s" % (sqlrepr(self.table1, db), join)
            return join
        else:
            RuntimeError, "Impossible error"

registerConverter(SQLJoinConditional, SQLExprConverter)


def INNERJOINConditional(table1, table2,
                         on_condition=None, using_columns=None):
    return SQLJoinConditional(table1, table2, "INNER JOIN",
                              on_condition, using_columns)


def LEFTJOINConditional(table1, table2, on_condition=None, using_columns=None):
    return SQLJoinConditional(table1, table2, "LEFT JOIN",
                              on_condition, using_columns)


def LEFTOUTERJOINConditional(table1, table2,
                             on_condition=None, using_columns=None):
    return SQLJoinConditional(table1, table2, "LEFT OUTER JOIN",
                              on_condition, using_columns)


def RIGHTJOINConditional(table1, table2,
                         on_condition=None, using_columns=None):
    return SQLJoinConditional(table1, table2, "RIGHT JOIN",
                              on_condition, using_columns)


def RIGHTOUTERJOINConditional(table1, table2,
                              on_condition=None, using_columns=None):
    return SQLJoinConditional(table1, table2, "RIGHT OUTER JOIN",
                              on_condition, using_columns)


def FULLJOINConditional(table1, table2, on_condition=None, using_columns=None):
    return SQLJoinConditional(table1, table2, "FULL JOIN",
                              on_condition, using_columns)


def FULLOUTERJOINConditional(table1, table2,
                             on_condition=None, using_columns=None):
    return SQLJoinConditional(table1, table2, "FULL OUTER JOIN",
                              on_condition, using_columns)


class SQLJoinOn(SQLJoinConditional):
    """Conditional JOIN ON"""
    def __init__(self, table1, table2, op, on_condition):
        SQLJoinConditional.__init__(self, table1, table2, op, on_condition)

registerConverter(SQLJoinOn, SQLExprConverter)


class SQLJoinUsing(SQLJoinConditional):
    """Conditional JOIN USING"""
    def __init__(self, table1, table2, op, using_columns):
        SQLJoinConditional.__init__(self, table1, table2,
                                    op, None, using_columns)

registerConverter(SQLJoinUsing, SQLExprConverter)


def INNERJOINOn(table1, table2, on_condition):
    return SQLJoinOn(table1, table2, "INNER JOIN", on_condition)


def LEFTJOINOn(table1, table2, on_condition):
    return SQLJoinOn(table1, table2, "LEFT JOIN", on_condition)


def LEFTOUTERJOINOn(table1, table2, on_condition):
    return SQLJoinOn(table1, table2, "LEFT OUTER JOIN", on_condition)


def RIGHTJOINOn(table1, table2, on_condition):
    return SQLJoinOn(table1, table2, "RIGHT JOIN", on_condition)


def RIGHTOUTERJOINOn(table1, table2, on_condition):
    return SQLJoinOn(table1, table2, "RIGHT OUTER JOIN", on_condition)


def FULLJOINOn(table1, table2, on_condition):
    return SQLJoinOn(table1, table2, "FULL JOIN", on_condition)


def FULLOUTERJOINOn(table1, table2, on_condition):
    return SQLJoinOn(table1, table2, "FULL OUTER JOIN", on_condition)


def INNERJOINUsing(table1, table2, using_columns):
    return SQLJoinUsing(table1, table2, "INNER JOIN", using_columns)


def LEFTJOINUsing(table1, table2, using_columns):
    return SQLJoinUsing(table1, table2, "LEFT JOIN", using_columns)


def LEFTOUTERJOINUsing(table1, table2, using_columns):
    return SQLJoinUsing(table1, table2, "LEFT OUTER JOIN", using_columns)


def RIGHTJOINUsing(table1, table2, using_columns):
    return SQLJoinUsing(table1, table2, "RIGHT JOIN", using_columns)


def RIGHTOUTERJOINUsing(table1, table2, using_columns):
    return SQLJoinUsing(table1, table2, "RIGHT OUTER JOIN", using_columns)


def FULLJOINUsing(table1, table2, using_columns):
    return SQLJoinUsing(table1, table2, "FULL JOIN", using_columns)


def FULLOUTERJOINUsing(table1, table2, using_columns):
    return SQLJoinUsing(table1, table2, "FULL OUTER JOIN", using_columns)


########################################
# Subqueries (subselects)
########################################

class OuterField(SQLObjectField):
    def tablesUsedImmediate(self):
        return []


class OuterTable(SQLObjectTable):
    FieldClass = OuterField


class Outer:
    def __init__(self, table):
        self.q = OuterTable(table)


class LIKE(SQLExpression):
    op = "LIKE"

    def __init__(self, expr, string, escape=None):
        self.expr = expr
        self.string = string
        self.escape = escape

    def __sqlrepr__(self, db):
        escape = self.escape
        like = "%s %s (%s)" % (sqlrepr(self.expr, db),
                               self.op, sqlrepr(self.string, db))
        if escape is None:
            return "(%s)" % like
        else:
            return "(%s ESCAPE %s)" % (like, sqlrepr(escape, db))

    def components(self):
        return [self.expr, self.string]

    def execute(self, executor):
        if not hasattr(self, '_regex'):
            # @@: Crude, not entirely accurate
            dest = self.string
            dest = dest.replace("%%", "\001")
            dest = dest.replace("*", "\002")
            dest = dest.replace("%", "*")
            dest = dest.replace("\001", "%")
            dest = dest.replace("\002", "[*]")
            self._regex = re.compile(fnmatch.translate(dest), re.I)
        return self._regex.search(execute(self.expr, executor))


class RLIKE(LIKE):
    op = "RLIKE"

    op_db = {
        'firebird': 'RLIKE',
        'maxdb': 'RLIKE',
        'mysql': 'RLIKE',
        'postgres': '~',
        'rdbhost': '~',
        'sqlite': 'REGEXP'
    }

    def _get_op(self, db):
        return self.op_db.get(db, 'LIKE')

    def __sqlrepr__(self, db):
        return "(%s %s (%s))" % (
            sqlrepr(self.expr, db), self._get_op(db), sqlrepr(self.string, db)
        )

    def execute(self, executor):
        self.op = self._get_op(self.db)
        return LIKE.execute(self, executor)


class INSubquery(SQLExpression):
    op = "IN"

    def __init__(self, item, subquery):
        self.item = item
        self.subquery = subquery

    def components(self):
        return [self.item]

    def __sqlrepr__(self, db):
        return "%s %s (%s)" % (sqlrepr(self.item, db),
                               self.op, sqlrepr(self.subquery, db))


class NOTINSubquery(INSubquery):
    op = "NOT IN"


class Subquery(SQLExpression):
    def __init__(self, op, subquery):
        self.op = op
        self.subquery = subquery

    def __sqlrepr__(self, db):
        return "%s (%s)" % (self.op, sqlrepr(self.subquery, db))


def EXISTS(subquery):
    return Subquery("EXISTS", subquery)


def NOTEXISTS(subquery):
    return Subquery("NOT EXISTS", subquery)


def SOME(subquery):
    return Subquery("SOME", subquery)


def ANY(subquery):
    return Subquery("ANY", subquery)


def ALL(subquery):
    return Subquery("ALL", subquery)


####


class ImportProxyField(SQLObjectField):
    def tablesUsedImmediate(self):
        return [str(self.tableName)]


class ImportProxy(SQLExpression):
    '''Class to be used in column definitions that rely on other tables that might
        not yet be in a classregistry.
    '''
    FieldClass = ImportProxyField

    def __init__(self, clsName, registry=None):
        self.tableName = _DelayClass(self, clsName)
        self.sqlmeta = _Delay_proxy(table=_DelayClass(self, clsName))
        self.q = self
        self.soClass = None
        classregistry.registry(registry).addClassCallback(
            clsName, lambda foreign, me: setattr(me, 'soClass', foreign), self)

    def __nonzero__(self):
        return True
    __bool__ = __nonzero__

    def __getattr__(self, attr):
        if self.soClass is None:
            return _Delay(self, attr)
        return getattr(self.soClass.q, attr)


class _Delay(SQLExpression):
    def __init__(self, proxy, attr):
        self.attr = attr
        self.proxy = proxy

    def __sqlrepr__(self, db):
        if self.proxy.soClass is None:
            return '_DELAYED_' + self.attr
        val = self._resolve()
        if isinstance(val, SQLExpression):
            val = sqlrepr(val, db)
        return val

    def tablesUsedImmediate(self):
        return getattr(self._resolve(), 'tablesUsedImmediate', lambda: [])()

    def components(self):
        return getattr(self._resolve(), 'components', lambda: [])()

    def _resolve(self):
        return getattr(self.proxy, self.attr)

    # For AliasTable etc
    def fieldName(self):
        class _aliasFieldName(SQLExpression):
            def __init__(self, proxy):
                self.proxy = proxy

            def __sqlrepr__(self, db):
                return self.proxy._resolve().fieldName
        return _aliasFieldName(self)
    fieldName = property(fieldName)


class _DelayClass(_Delay):
    def _resolve(self):
        return self.proxy.soClass.sqlmeta.table


class _Delay_proxy(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

######


########################################
# Global initializations
########################################

table = TableSpace()
const = ConstantSpace()
func = const

########################################
# Testing
########################################

if __name__ == "__main__":
    tests = """
>>> AND(table.address.name == "Ian Bicking", table.address.zip > 30000)
>>> table.address.name
>>> AND(LIKE(table.address.name, "this"), IN(table.address.zip, [100, 200, 300]))
>>> Select([table.address.name, table.address.state], where=LIKE(table.address.name, "%ian%"))
>>> Select([table.user.name], where=AND(table.user.state == table.states.abbrev))
>>> Insert(table.address, [{"name": "BOB", "address": "3049 N. 18th St."}, {"name": "TIM", "address": "409 S. 10th St."}])
>>> Insert(table.address, [("BOB", "3049 N. 18th St."), ("TIM", "409 S. 10th St.")], template=('name', 'address'))
>>> Delete(table.address, where="BOB"==table.address.name)
>>> Update(table.address, {"lastModified": const.NOW()})
>>> Replace(table.address, [("BOB", "3049 N. 18th St."), ("TIM", "409 S. 10th St.")], template=('name', 'address'))
"""  # noqa: allow long (> 79) lines
    for expr in tests.split('\n'):
        if not expr.strip():
            continue
        if expr.startswith('>>> '):
            expr = expr[4:]
