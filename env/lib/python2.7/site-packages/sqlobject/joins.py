from itertools import count
from . import boundattributes
from . import classregistry
from . import events
from . import styles
from . import sqlbuilder
from .styles import capword

__all__ = ['MultipleJoin', 'SQLMultipleJoin', 'RelatedJoin', 'SQLRelatedJoin',
           'SingleJoin', 'ManyToMany', 'OneToMany']

creationOrder = count()
NoDefault = sqlbuilder.NoDefault


def getID(obj):
    try:
        return obj.id
    except AttributeError:
        return int(obj)


class Join(object):

    def __init__(self, otherClass=None, **kw):
        kw['otherClass'] = otherClass
        self.kw = kw
        self._joinMethodName = self.kw.pop('joinMethodName', None)
        self.creationOrder = next(creationOrder)

    def _set_joinMethodName(self, value):
        assert self._joinMethodName == value or self._joinMethodName is None, \
            "You have already given an explicit joinMethodName (%s), " \
            "and you are now setting it to %s" % (self._joinMethodName, value)
        self._joinMethodName = value

    def _get_joinMethodName(self):
        return self._joinMethodName

    joinMethodName = property(_get_joinMethodName, _set_joinMethodName)
    name = joinMethodName

    def withClass(self, soClass):
        if 'joinMethodName' in self.kw:
            self._joinMethodName = self.kw['joinMethodName']
            del self.kw['joinMethodName']
        return self.baseClass(creationOrder=self.creationOrder,
                              soClass=soClass,
                              joinDef=self,
                              joinMethodName=self._joinMethodName,
                              **self.kw)


# A join is separate from a foreign key, i.e., it is
# many-to-many, or one-to-many where the *other* class
# has the foreign key.


class SOJoin(object):

    def __init__(self,
                 creationOrder,
                 soClass=None,
                 otherClass=None,
                 joinColumn=None,
                 joinMethodName=None,
                 orderBy=NoDefault,
                 joinDef=None):
        self.creationOrder = creationOrder
        self.soClass = soClass
        self.joinDef = joinDef
        self.otherClassName = otherClass
        classregistry.registry(soClass.sqlmeta.registry).addClassCallback(
            otherClass, self._setOtherClass)
        self.joinColumn = joinColumn
        self.joinMethodName = joinMethodName
        self._orderBy = orderBy
        if not self.joinColumn:
            # Here we set up the basic join, which is
            # one-to-many, where the other class points to
            # us.
            self.joinColumn = styles.getStyle(
                self.soClass).tableReference(self.soClass.sqlmeta.table)

    def orderBy(self):
        if self._orderBy is NoDefault:
            self._orderBy = self.otherClass.sqlmeta.defaultOrder
        return self._orderBy
    orderBy = property(orderBy)

    def _setOtherClass(self, cls):
        self.otherClass = cls

    def hasIntermediateTable(self):
        return False

    def _applyOrderBy(self, results, defaultSortClass):
        if self.orderBy is not None:
            doSort(results, self.orderBy)
        return results


class MinType(object):
    """Sort less than everything, for handling None's in the results"""
    # functools.total_ordering would simplify this

    def __lt__(self, other):
        if self is other:
            return False
        return True

    def __eq__(self, other):
        return self is other

    def __gt__(self, other):
        return False

    def __le__(self, other):
        return True

    def __ge__(self, other):
        if self is other:
            return True
        return False


Min = MinType()


def doSort(results, orderBy):
    if isinstance(orderBy, (tuple, list)):
        if len(orderBy) == 1:
            orderBy = orderBy[0]
        else:
            # Rely on stable sort results, since this is simpler
            # than trying to munge everything into a single sort key
            doSort(results, orderBy[0])
            doSort(results, orderBy[1:])
            return
    if isinstance(orderBy, sqlbuilder.DESC) \
       and isinstance(orderBy.expr, sqlbuilder.SQLObjectField):
        orderBy = '-' + orderBy.expr.original
    elif isinstance(orderBy, sqlbuilder.SQLObjectField):
        orderBy = orderBy.original
    # @@: but we don't handle more complex expressions for orderings
    if orderBy.startswith('-'):
        orderBy = orderBy[1:]
        reverse = True
    else:
        reverse = False

    def sortkey(x, attr=orderBy):
        a = getattr(x, attr)
        if a is None:
            return Min
        return a
    results.sort(key=sortkey, reverse=reverse)


# This is a one-to-many


class SOMultipleJoin(SOJoin):

    def __init__(self, addRemoveName=None, **kw):
        # addRemovePrefix is something like @@
        SOJoin.__init__(self, **kw)

        # Here we generate the method names
        if not self.joinMethodName:
            name = self.otherClassName[0].lower() + self.otherClassName[1:]
            if name.endswith('s'):
                name = name + "es"
            else:
                name = name + "s"
            self.joinMethodName = name
        if addRemoveName:
            self.addRemoveName = addRemoveName
        else:
            self.addRemoveName = capword(self.otherClassName)

    def performJoin(self, inst):
        ids = inst._connection._SO_selectJoin(
            self.otherClass,
            self.joinColumn,
            inst.id)
        if inst.sqlmeta._perConnection:
            conn = inst._connection
        else:
            conn = None
        return self._applyOrderBy(
            [self.otherClass.get(id, conn) for (id,) in ids if id is not None],
            self.otherClass)

    def _dbNameToPythonName(self):
        for column in self.otherClass.sqlmeta.columns.values():
            if column.dbName == self.joinColumn:
                return column.name
        return self.soClass.sqlmeta.style.dbColumnToPythonAttr(self.joinColumn)


class MultipleJoin(Join):
    baseClass = SOMultipleJoin


class SOSQLMultipleJoin(SOMultipleJoin):

    def performJoin(self, inst):
        if inst.sqlmeta._perConnection:
            conn = inst._connection
        else:
            conn = None
        pythonColumn = self._dbNameToPythonName()
        results = self.otherClass.select(
            getattr(self.otherClass.q, pythonColumn) == inst.id,
            connection=conn)
        return results.orderBy(self.orderBy)


class SQLMultipleJoin(Join):
    baseClass = SOSQLMultipleJoin


# This is a many-to-many join, with an intermediary table


class SORelatedJoin(SOMultipleJoin):

    def __init__(self,
                 otherColumn=None,
                 intermediateTable=None,
                 createRelatedTable=True,
                 **kw):
        self.intermediateTable = intermediateTable
        self.otherColumn = otherColumn
        self.createRelatedTable = createRelatedTable
        SOMultipleJoin.__init__(self, **kw)
        classregistry.registry(
            self.soClass.sqlmeta.registry).addClassCallback(
            self.otherClassName, self._setOtherRelatedClass)

    def _setOtherRelatedClass(self, otherClass):
        if not self.intermediateTable:
            names = [self.soClass.sqlmeta.table,
                     otherClass.sqlmeta.table]
            names.sort()
            self.intermediateTable = '%s_%s' % (names[0], names[1])
        if not self.otherColumn:
            self.otherColumn = self.soClass.sqlmeta.style.tableReference(
                otherClass.sqlmeta.table)

    def hasIntermediateTable(self):
        return True

    def performJoin(self, inst):
        ids = inst._connection._SO_intermediateJoin(
            self.intermediateTable,
            self.otherColumn,
            self.joinColumn,
            inst.id)
        if inst.sqlmeta._perConnection:
            conn = inst._connection
        else:
            conn = None
        return self._applyOrderBy(
            [self.otherClass.get(id, conn) for (id,) in ids if id is not None],
            self.otherClass)

    def remove(self, inst, other):
        inst._connection._SO_intermediateDelete(
            self.intermediateTable,
            self.joinColumn,
            getID(inst),
            self.otherColumn,
            getID(other))

    def add(self, inst, other):
        inst._connection._SO_intermediateInsert(
            self.intermediateTable,
            self.joinColumn,
            getID(inst),
            self.otherColumn,
            getID(other))


class RelatedJoin(MultipleJoin):
    baseClass = SORelatedJoin


# helper classes to SQLRelatedJoin


class OtherTableToJoin(sqlbuilder.SQLExpression):
    def __init__(self, otherTable, otherIdName, interTable, joinColumn):
        self.otherTable = otherTable
        self.otherIdName = otherIdName
        self.interTable = interTable
        self.joinColumn = joinColumn

    def tablesUsedImmediate(self):
        return [self.otherTable, self.interTable]

    def __sqlrepr__(self, db):
        return '%s.%s = %s.%s' % (self.otherTable, self.otherIdName,
                                  self.interTable, self.joinColumn)


class JoinToTable(sqlbuilder.SQLExpression):
    def __init__(self, table, idName, interTable, joinColumn):
        self.table = table
        self.idName = idName
        self.interTable = interTable
        self.joinColumn = joinColumn

    def tablesUsedImmediate(self):
        return [self.table, self.interTable]

    def __sqlrepr__(self, db):
        return '%s.%s = %s.%s' % (self.interTable, self.joinColumn, self.table,
                                  self.idName)


class TableToId(sqlbuilder.SQLExpression):
    def __init__(self, table, idName, idValue):
        self.table = table
        self.idName = idName
        self.idValue = idValue

    def tablesUsedImmediate(self):
        return [self.table]

    def __sqlrepr__(self, db):
        return '%s.%s = %s' % (self.table, self.idName, self.idValue)


class SOSQLRelatedJoin(SORelatedJoin):
    def performJoin(self, inst):
        if inst.sqlmeta._perConnection:
            conn = inst._connection
        else:
            conn = None
        results = self.otherClass.select(sqlbuilder.AND(
            OtherTableToJoin(
                self.otherClass.sqlmeta.table, self.otherClass.sqlmeta.idName,
                self.intermediateTable, self.otherColumn
            ),
            JoinToTable(
                self.soClass.sqlmeta.table, self.soClass.sqlmeta.idName,
                self.intermediateTable, self.joinColumn
            ),
            TableToId(self.soClass.sqlmeta.table, self.soClass.sqlmeta.idName,
                      inst.id),
        ), clauseTables=(self.soClass.sqlmeta.table,
                         self.otherClass.sqlmeta.table,
                         self.intermediateTable),
            connection=conn)
        return results.orderBy(self.orderBy)


class SQLRelatedJoin(RelatedJoin):
    baseClass = SOSQLRelatedJoin


class SOSingleJoin(SOMultipleJoin):

    def __init__(self, **kw):
        self.makeDefault = kw.pop('makeDefault', False)
        SOMultipleJoin.__init__(self, **kw)

    def performJoin(self, inst):
        if inst.sqlmeta._perConnection:
            conn = inst._connection
        else:
            conn = None
        pythonColumn = self._dbNameToPythonName()
        results = self.otherClass.select(
            getattr(self.otherClass.q, pythonColumn) == inst.id,
            connection=conn
        )
        if results.count() == 0:
            if not self.makeDefault:
                return None
            else:
                kw = {self.soClass.sqlmeta.style.
                      instanceIDAttrToAttr(pythonColumn): inst}
                # instanciating the otherClass with all
                return self.otherClass(**kw)
        else:
            return results[0]


class SingleJoin(Join):
    baseClass = SOSingleJoin


class SOManyToMany(object):

    def __init__(self, soClass, name, join,
                 intermediateTable, joinColumn, otherColumn,
                 createJoinTable, **attrs):
        self.name = name
        self.intermediateTable = intermediateTable
        self.joinColumn = joinColumn
        self.otherColumn = otherColumn
        self.createJoinTable = createJoinTable
        self.soClass = self.otherClass = None
        for name, value in attrs.items():
            setattr(self, name, value)
        classregistry.registry(
            soClass.sqlmeta.registry).addClassCallback(
            join, self._setOtherClass)
        classregistry.registry(
            soClass.sqlmeta.registry).addClassCallback(
            soClass.__name__, self._setThisClass)

    def _setThisClass(self, soClass):
        self.soClass = soClass
        if self.soClass and self.otherClass:
            self._finishSet()

    def _setOtherClass(self, otherClass):
        self.otherClass = otherClass
        if self.soClass and self.otherClass:
            self._finishSet()

    def _finishSet(self):
        if self.intermediateTable is None:
            names = [self.soClass.sqlmeta.table,
                     self.otherClass.sqlmeta.table]
            names.sort()
            self.intermediateTable = '%s_%s' % (names[0], names[1])
        if not self.otherColumn:
            self.otherColumn = self.soClass.sqlmeta.style.tableReference(
                self.otherClass.sqlmeta.table)
        if not self.joinColumn:
            self.joinColumn = styles.getStyle(
                self.soClass).tableReference(self.soClass.sqlmeta.table)
        events.listen(self.event_CreateTableSignal,
                      self.soClass, events.CreateTableSignal)
        events.listen(self.event_CreateTableSignal,
                      self.otherClass, events.CreateTableSignal)
        self.clause = (
            (self.otherClass.q.id ==
             sqlbuilder.Field(self.intermediateTable, self.otherColumn)) &
            (sqlbuilder.Field(self.intermediateTable, self.joinColumn) ==
             self.soClass.q.id))

    def __get__(self, obj, type):
        if obj is None:
            return self
        query = (
            (self.otherClass.q.id ==
             sqlbuilder.Field(self.intermediateTable, self.otherColumn)) &
            (sqlbuilder.Field(self.intermediateTable, self.joinColumn) ==
             obj.id))
        select = self.otherClass.select(query)
        return _ManyToManySelectWrapper(obj, self, select)

    def event_CreateTableSignal(self, soClass, connection, extra_sql,
                                post_funcs):
        if self.createJoinTable:
            post_funcs.append(self.event_CreateTableSignalPost)

    def event_CreateTableSignalPost(self, soClass, connection):
        if connection.tableExists(self.intermediateTable):
            return
        connection._SO_createJoinTable(self)


class ManyToMany(boundattributes.BoundFactory):
    factory_class = SOManyToMany
    __restrict_attributes__ = (
        'join', 'intermediateTable',
        'joinColumn', 'otherColumn', 'createJoinTable')
    __unpackargs__ = ('join',)

    # Default values:
    intermediateTable = None
    joinColumn = None
    otherColumn = None
    createJoinTable = True


class _ManyToManySelectWrapper(object):

    def __init__(self, forObject, join, select):
        self.forObject = forObject
        self.join = join
        self.select = select

    def __getattr__(self, attr):
        # @@: This passes through private variable access too... should it?
        # Also magic methods, like __str__
        return getattr(self.select, attr)

    def __repr__(self):
        return '<%s for: %s>' % (self.__class__.__name__, repr(self.select))

    def __str__(self):
        return str(self.select)

    def __iter__(self):
        return iter(self.select)

    def __getitem__(self, key):
        return self.select[key]

    def add(self, obj):
        obj._connection._SO_intermediateInsert(
            self.join.intermediateTable,
            self.join.joinColumn,
            getID(self.forObject),
            self.join.otherColumn,
            getID(obj))

    def remove(self, obj):
        obj._connection._SO_intermediateDelete(
            self.join.intermediateTable,
            self.join.joinColumn,
            getID(self.forObject),
            self.join.otherColumn,
            getID(obj))

    def create(self, **kw):
        obj = self.join.otherClass(**kw)
        self.add(obj)
        return obj


class SOOneToMany(object):

    def __init__(self, soClass, name, join, joinColumn, **attrs):
        self.soClass = soClass
        self.name = name
        self.joinColumn = joinColumn
        for name, value in attrs.items():
            setattr(self, name, value)
        classregistry.registry(
            soClass.sqlmeta.registry).addClassCallback(
            join, self._setOtherClass)

    def _setOtherClass(self, otherClass):
        self.otherClass = otherClass
        if not self.joinColumn:
            self.joinColumn = styles.getStyle(
                self.soClass).tableReference(self.soClass.sqlmeta.table)
        self.clause = (
            sqlbuilder.Field(self.otherClass.sqlmeta.table, self.joinColumn) ==
            self.soClass.q.id)

    def __get__(self, obj, type):
        if obj is None:
            return self
        query = (
            sqlbuilder.Field(self.otherClass.sqlmeta.table, self.joinColumn) ==
            obj.id)
        select = self.otherClass.select(query)
        return _OneToManySelectWrapper(obj, self, select)


class OneToMany(boundattributes.BoundFactory):
    factory_class = SOOneToMany
    __restrict_attributes__ = (
        'join', 'joinColumn')
    __unpackargs__ = ('join',)

    # Default values:
    joinColumn = None


class _OneToManySelectWrapper(object):

    def __init__(self, forObject, join, select):
        self.forObject = forObject
        self.join = join
        self.select = select

    def __getattr__(self, attr):
        # @@: This passes through private variable access too... should it?
        # Also magic methods, like __str__
        return getattr(self.select, attr)

    def __repr__(self):
        return '<%s for: %s>' % (self.__class__.__name__, repr(self.select))

    def __str__(self):
        return str(self.select)

    def __iter__(self):
        return iter(self.select)

    def __getitem__(self, key):
        return self.select[key]

    def create(self, **kw):
        kw[self.join.joinColumn] = self.forObject.id
        return self.join.otherClass(**kw)
