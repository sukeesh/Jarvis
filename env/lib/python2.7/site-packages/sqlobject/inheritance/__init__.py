from functools import reduce

from sqlobject import dbconnection
from sqlobject import classregistry
from sqlobject import events
from sqlobject import sqlbuilder
from sqlobject.col import StringCol, ForeignKey
from sqlobject.main import sqlmeta, SQLObject, SelectResults, \
    makeProperties, unmakeProperties, getterName, setterName
from sqlobject.compat import string_type
from . import iteration


def tablesUsedSet(obj, db):
    if hasattr(obj, "tablesUsedSet"):
        return obj.tablesUsedSet(db)
    elif isinstance(obj, (tuple, list, set, frozenset)):
        s = set()
        for component in obj:
            s.update(tablesUsedSet(component, db))
        return s
    else:
        return set()


class InheritableSelectResults(SelectResults):
    IterationClass = iteration.InheritableIteration

    def __init__(self, sourceClass, clause, clauseTables=None,
                 inheritedTables=None, **ops):
        if clause is None or isinstance(clause, str) and clause == 'all':
            clause = sqlbuilder.SQLTrueClause

        dbName = (ops.get('connection', None) or
                  sourceClass._connection).dbName

        tablesSet = tablesUsedSet(clause, dbName)
        tablesSet.add(str(sourceClass.sqlmeta.table))
        orderBy = ops.get('orderBy')
        if inheritedTables:
            for tableName in inheritedTables:
                tablesSet.add(str(tableName))
        if orderBy and not isinstance(orderBy, string_type):
            tablesSet.update(tablesUsedSet(orderBy, dbName))
        # DSM: if this class has a parent, we need to link it
        # DSM: and be sure the parent is in the table list.
        # DSM: The following code is before clauseTables
        # DSM: because if the user uses clauseTables
        # DSM: (and normal string SELECT), he must know what he wants
        # DSM: and will do himself the relationship between classes.
        if not isinstance(clause, str):
            tableRegistry = {}
            allClasses = classregistry.registry(
                sourceClass.sqlmeta.registry).allClasses()
            for registryClass in allClasses:
                if str(registryClass.sqlmeta.table) in tablesSet:
                    # DSM: By default, no parents are needed for the clauses
                    tableRegistry[registryClass] = registryClass
            tableRegistryCopy = tableRegistry.copy()
            for childClass in tableRegistryCopy:
                if childClass not in tableRegistry:
                    continue
                currentClass = childClass
                while currentClass:
                    if currentClass in tableRegistryCopy:
                        if currentClass in tableRegistry:
                            # DSM: Remove this class as it is a parent one
                            # DSM: of a needed children
                            del tableRegistry[currentClass]
                        # DSM: Must keep the last parent needed
                        # DSM: (to limit the number of join needed)
                        tableRegistry[childClass] = currentClass
                    currentClass = currentClass.sqlmeta.parentClass
            # DSM: Table registry contains only the last children
            # DSM: or standalone classes
            parentClause = []
            for (currentClass, minParentClass) in tableRegistry.items():
                while (currentClass != minParentClass) \
                        and currentClass.sqlmeta.parentClass:
                    parentClass = currentClass.sqlmeta.parentClass
                    parentClause.append(currentClass.q.id == parentClass.q.id)
                    currentClass = parentClass
                    tablesSet.add(str(currentClass.sqlmeta.table))
            clause = reduce(sqlbuilder.AND, parentClause, clause)

        super(InheritableSelectResults, self).__init__(
            sourceClass, clause, clauseTables, **ops)

    def accumulateMany(self, *attributes, **kw):
        if kw.get("skipInherited"):
            return super(InheritableSelectResults, self).\
                accumulateMany(*attributes)
        tables = []
        for func_name, attribute in attributes:
            if not isinstance(attribute, string_type):
                tables.append(attribute.tableName)
        clone = self.__class__(self.sourceClass, self.clause,
                               self.clauseTables, inheritedTables=tables,
                               **self.ops)
        return clone.accumulateMany(skipInherited=True, *attributes)


class InheritableSQLMeta(sqlmeta):
    @classmethod
    def addColumn(sqlmeta, columnDef, changeSchema=False, connection=None,
                  childUpdate=False):
        soClass = sqlmeta.soClass
        # DSM: Try to add parent properties to the current class
        # DSM: Only do this once if possible at object creation and once for
        # DSM: each new dynamic column to refresh the current class
        if sqlmeta.parentClass:
            for col in sqlmeta.parentClass.sqlmeta.columnList:
                cname = col.name
                if cname == 'childName':
                    continue
                if cname.endswith("ID"):
                    cname = cname[:-2]
                setattr(soClass, getterName(cname), eval(
                    'lambda self: self._parent.%s' % cname))
                if not col.immutable:
                    def make_setfunc(cname):
                        def setfunc(self, val):
                            if not self.sqlmeta._creating and \
                               not getattr(self.sqlmeta,
                                           "row_update_sig_suppress", False):
                                self.sqlmeta.send(events.RowUpdateSignal, self,
                                                  {cname: val})

                            setattr(self._parent, cname, val)
                        return setfunc

                    setfunc = make_setfunc(cname)
                    setattr(soClass, setterName(cname), setfunc)
            if childUpdate:
                makeProperties(soClass)
                return

        if columnDef:
            super(InheritableSQLMeta, sqlmeta).addColumn(columnDef,
                                                         changeSchema,
                                                         connection)

        # DSM: Update each child class if needed and existing (only for new
        # DSM: dynamic column as no child classes exists at object creation)
        if columnDef and hasattr(soClass, "q"):
            q = getattr(soClass.q, columnDef.name, None)
        else:
            q = None
        for c in sqlmeta.childClasses.values():
            c.sqlmeta.addColumn(columnDef, connection=connection,
                                childUpdate=True)
            if q:
                setattr(c.q, columnDef.name, q)

    @classmethod
    def delColumn(sqlmeta, column, changeSchema=False, connection=None,
                  childUpdate=False):
        if childUpdate:
            soClass = sqlmeta.soClass
            unmakeProperties(soClass)
            makeProperties(soClass)

            if isinstance(column, str):
                name = column
            else:
                name = column.name
            delattr(soClass, name)
            delattr(soClass.q, name)
            return

        super(InheritableSQLMeta, sqlmeta).delColumn(column, changeSchema,
                                                     connection)

        # DSM: Update each child class if needed
        # DSM: and delete properties for this column
        for c in sqlmeta.childClasses.values():
            c.sqlmeta.delColumn(column, changeSchema=changeSchema,
                                connection=connection, childUpdate=True)

    @classmethod
    def addJoin(sqlmeta, joinDef, childUpdate=False):
        soClass = sqlmeta.soClass
        # DSM: Try to add parent properties to the current class
        # DSM: Only do this once if possible at object creation and once for
        # DSM: each new dynamic join to refresh the current class
        if sqlmeta.parentClass:
            for join in sqlmeta.parentClass.sqlmeta.joins:
                jname = join.joinMethodName
                jarn = join.addRemoveName
                setattr(
                    soClass, getterName(jname),
                    eval('lambda self: self._parent.%s' % jname))
                if hasattr(join, 'remove'):
                    setattr(
                        soClass, 'remove' + jarn,
                        eval('lambda self,o: self._parent.remove%s(o)' % jarn))
                if hasattr(join, 'add'):
                    setattr(
                        soClass, 'add' + jarn,
                        eval('lambda self,o: self._parent.add%s(o)' % jarn))
            if childUpdate:
                makeProperties(soClass)
                return

        if joinDef:
            super(InheritableSQLMeta, sqlmeta).addJoin(joinDef)

        # DSM: Update each child class if needed and existing (only for new
        # DSM: dynamic join as no child classes exists at object creation)
        for c in sqlmeta.childClasses.values():
            c.sqlmeta.addJoin(joinDef, childUpdate=True)

    @classmethod
    def delJoin(sqlmeta, joinDef, childUpdate=False):
        if childUpdate:
            soClass = sqlmeta.soClass
            unmakeProperties(soClass)
            makeProperties(soClass)
            return

        super(InheritableSQLMeta, sqlmeta).delJoin(joinDef)

        # DSM: Update each child class if needed
        # DSM: and delete properties for this join
        for c in sqlmeta.childClasses.values():
            c.sqlmeta.delJoin(joinDef, childUpdate=True)

    @classmethod
    def getAllColumns(sqlmeta):
        columns = sqlmeta.columns.copy()
        sm = sqlmeta
        while sm.parentClass:
            columns.update(sm.parentClass.sqlmeta.columns)
            sm = sm.parentClass.sqlmeta
        return columns

    @classmethod
    def getColumns(sqlmeta):
        columns = sqlmeta.getAllColumns()
        if 'childName' in columns:
            del columns['childName']
        return columns


class InheritableSQLObject(SQLObject):

    sqlmeta = InheritableSQLMeta
    _inheritable = True
    SelectResultsClass = InheritableSelectResults

    def set(self, **kw):
        if self._parent:
            SQLObject.set(self, _suppress_set_sig=True, **kw)
        else:
            SQLObject.set(self, **kw)

    def __classinit__(cls, new_attrs):
        SQLObject.__classinit__(cls, new_attrs)
        # if we are a child class, add sqlbuilder fields from parents
        currentClass = cls.sqlmeta.parentClass
        while currentClass:
            for column in currentClass.sqlmeta.columnDefinitions.values():
                if column.name == 'childName':
                    continue
                if isinstance(column, ForeignKey):
                    continue
                setattr(cls.q, column.name,
                        getattr(currentClass.q, column.name))
            currentClass = currentClass.sqlmeta.parentClass

    @classmethod
    def _SO_setupSqlmeta(cls, new_attrs, is_base):
        # Note: cannot use super(InheritableSQLObject, cls)._SO_setupSqlmeta -
        #       InheritableSQLObject is not defined when it's __classinit__
        #       is run.  Cannot use SQLObject._SO_setupSqlmeta, either:
        #       the method would be bound to wrong class.
        if cls.__name__ == "InheritableSQLObject":
            call_super = super(cls, cls)
        else:
            # InheritableSQLObject must be in globals yet
            call_super = super(InheritableSQLObject, cls)
        call_super._SO_setupSqlmeta(new_attrs, is_base)
        sqlmeta = cls.sqlmeta
        sqlmeta.childClasses = {}
        # locate parent class and register this class in it's children
        sqlmeta.parentClass = None
        for superclass in cls.__bases__:
            if getattr(superclass, '_inheritable', False) \
                    and (superclass.__name__ != 'InheritableSQLObject'):
                if sqlmeta.parentClass:
                    # already have a parent class;
                    # cannot inherit from more than one
                    raise NotImplementedError(
                        "Multiple inheritance is not implemented")
                sqlmeta.parentClass = superclass
                superclass.sqlmeta.childClasses[cls.__name__] = cls
        if sqlmeta.parentClass:
            # remove inherited column definitions
            cls.sqlmeta.columns = {}
            cls.sqlmeta.columnList = []
            cls.sqlmeta.columnDefinitions = {}
            # default inheritance child name
            if not sqlmeta.childName:
                sqlmeta.childName = cls.__name__

    @classmethod
    def get(cls, id, connection=None, selectResults=None,
            childResults=None, childUpdate=False):

        val = super(InheritableSQLObject, cls).get(id, connection,
                                                   selectResults)

        # DSM: If we are updating a child, we should never return a child...
        if childUpdate:
            return val
        # DSM: If this class has a child, return the child
        if 'childName' in cls.sqlmeta.columns:
            childName = val.childName
            if childName is not None:
                childClass = cls.sqlmeta.childClasses[childName]
                # If the class has no columns (which sometimes makes sense
                # and may be true for non-inheritable (leaf) classes only),
                # shunt the query to avoid almost meaningless SQL
                # like "SELECT NULL FROM child WHERE id=1".
                # This is based on assumption that child object exists
                # if parent object exists.  (If it doesn't your database
                # is broken and that is a job for database maintenance.)
                if not (childResults or childClass.sqlmeta.columns):
                    childResults = (None,)
                return childClass.get(id, connection=connection,
                                      selectResults=childResults)
        # DSM: Now, we know we are alone or the last child in a family...
        # DSM: It's time to find our parents
        inst = val
        while inst.sqlmeta.parentClass and not inst._parent:
            inst._parent = inst.sqlmeta.parentClass.get(
                id, connection=connection, childUpdate=True)
            inst = inst._parent
        # DSM: We can now return ourself
        return val

    @classmethod
    def _notifyFinishClassCreation(cls):
        sqlmeta = cls.sqlmeta
        # verify names of added columns
        if sqlmeta.parentClass:
            # FIXME: this does not check for grandparent column overrides
            parentCols = sqlmeta.parentClass.sqlmeta.columns.keys()
            for column in sqlmeta.columnList:
                if column.name == 'childName':
                    raise AttributeError(
                        "The column name 'childName' is reserved")
                if column.name in parentCols:
                    raise AttributeError(
                        "The column '%s' is already defined "
                        "in an inheritable parent" % column.name)
        # if this class is inheritable, add column for children distinction
        if cls._inheritable and (cls.__name__ != 'InheritableSQLObject'):
            sqlmeta.addColumn(
                StringCol(name='childName',
                          # limit string length to get VARCHAR and not CLOB
                          length=255, default=None))
        if not sqlmeta.columnList:
            # There are no columns - call addColumn to propagate columns
            # from parent classes to children
            sqlmeta.addColumn(None)
        if not sqlmeta.joins:
            # There are no joins - call addJoin to propagate joins
            # from parent classes to children
            sqlmeta.addJoin(None)

    def _create(self, id, **kw):

        # DSM: If we were called by a children class,
        # DSM: we must retreive the properties dictionary.
        # DSM: Note: we can't use the ** call paremeter directly
        # DSM: as we must be able to delete items from the dictionary
        # DSM: (and our children must know that the items were removed!)
        if 'kw' in kw:
            kw = kw['kw']
        # DSM: If we are the children of an inheritable class,
        # DSM: we must first create our parent
        if self.sqlmeta.parentClass:
            parentClass = self.sqlmeta.parentClass
            new_kw = {}
            parent_kw = {}
            for (name, value) in kw.items():
                if (name != 'childName') and hasattr(parentClass, name):
                    parent_kw[name] = value
                else:
                    new_kw[name] = value
            kw = new_kw

            # Need to check that we have enough data to sucesfully
            # create the current subclass otherwise we will leave
            # the database in an inconsistent state.
            for col in self.sqlmeta.columnList:
                if (col._default == sqlbuilder.NoDefault) and \
                        (col.name not in kw) and (col.foreignName not in kw):
                    raise TypeError(
                        "%s() did not get expected keyword argument "
                        "%s" % (self.__class__.__name__, col.name))

            parent_kw['childName'] = self.sqlmeta.childName
            self._parent = parentClass(kw=parent_kw,
                                       connection=self._connection)

            id = self._parent.id

        # TC: Create this record and catch all exceptions in order to destroy
        # TC: the parent if the child can not be created.
        try:
            super(InheritableSQLObject, self)._create(id, **kw)
        except Exception:
            # If we are outside a transaction and this is a child,
            # destroy the parent
            connection = self._connection
            if (not isinstance(connection, dbconnection.Transaction) and
                    connection.autoCommit) and self.sqlmeta.parentClass:
                self._parent.destroySelf()
                # TC: Do we need to do this??
                self._parent = None
            # TC: Reraise the original exception
            raise

    @classmethod
    def _findAlternateID(cls, name, dbName, value, connection=None):
        result = list(cls.selectBy(connection, **{name: value}))
        if not result:
            return result, None
        obj = result[0]
        return [obj.id], obj

    @classmethod
    def select(cls, clause=None, *args, **kwargs):
        parentClass = cls.sqlmeta.parentClass
        childUpdate = kwargs.pop('childUpdate', None)
        # childUpdate may have one of three values:
        #   True:
        #       select was issued by parent class to create child objects.
        #       Execute select without modifications.
        #   None (default):
        #       select is run by application.  If this class is inheritance
        #       child, delegate query to the parent class to utilize
        #       InheritableIteration optimizations.  Selected records
        #       are restricted to this (child) class by adding childName
        #       filter to the where clause.
        #   False:
        #       select is delegated from inheritance child which is parent
        #       of another class.  Delegate the query to parent if possible,
        #       but don't add childName restriction: selected records
        #       will be filtered by join to the table filtered by childName.
        if (not childUpdate) and parentClass:
            if childUpdate is None:
                # this is the first parent in deep hierarchy
                addClause = parentClass.q.childName == cls.sqlmeta.childName
                # if the clause was one of TRUE varians, replace it
                if (clause is None) or (clause is sqlbuilder.SQLTrueClause) \
                        or (
                            isinstance(clause, string_type) and
                            (clause == 'all')):
                    clause = addClause
                else:
                    # patch WHERE condition:
                    # change ID field of this class to ID of parent class
                    # XXX the clause is patched in place; it would be better
                    #     to build a new one if we have to replace field
                    clsID = cls.q.id
                    parentID = parentClass.q.id

                    def _get_patched(clause):
                        if isinstance(clause, sqlbuilder.SQLOp):
                            _patch_id_clause(clause)
                            return None
                        elif not isinstance(clause, sqlbuilder.Field):
                            return None
                        elif (clause.tableName == clsID.tableName) \
                                and (clause.fieldName == clsID.fieldName):
                            return parentID
                        else:
                            return None

                    def _patch_id_clause(clause):
                        if not isinstance(clause, sqlbuilder.SQLOp):
                            return
                        expr = _get_patched(clause.expr1)
                        if expr:
                            clause.expr1 = expr
                        expr = _get_patched(clause.expr2)
                        if expr:
                            clause.expr2 = expr
                    _patch_id_clause(clause)
                    # add childName filter
                    clause = sqlbuilder.AND(clause, addClause)
            return parentClass.select(clause, childUpdate=False,
                                      *args, **kwargs)
        else:
            return super(InheritableSQLObject, cls).select(
                clause, *args, **kwargs)

    @classmethod
    def selectBy(cls, connection=None, **kw):
        clause = []
        foreignColumns = {}
        currentClass = cls
        while currentClass:
            foreignColumns.update(dict(
                [(column.foreignName, name)
                    for (name, column) in currentClass.sqlmeta.columns.items()
                    if column.foreignKey
                 ]))
            currentClass = currentClass.sqlmeta.parentClass
        for name, value in kw.items():
            if name in foreignColumns:
                name = foreignColumns[name]  # translate "key" to "keyID"
                if isinstance(value, SQLObject):
                    value = value.id
            currentClass = cls
            while currentClass:
                try:
                    clause.append(getattr(currentClass.q, name) == value)
                    break
                except AttributeError:
                    pass
                currentClass = currentClass.sqlmeta.parentClass
            else:
                raise AttributeError(
                    "'%s' instance has no attribute '%s'" % (
                        cls.__name__, name))
        if clause:
            clause = reduce(sqlbuilder.AND, clause)
        else:
            clause = None  # select all
        conn = connection or cls._connection
        return cls.SelectResultsClass(cls, clause, connection=conn)

    def destroySelf(self):
        # DSM: If this object has parents, recursivly kill them
        if hasattr(self, '_parent') and self._parent:
            self._parent.destroySelf()
        super(InheritableSQLObject, self).destroySelf()

    def _reprItems(self):
        items = super(InheritableSQLObject, self)._reprItems()
        # add parent attributes (if any)
        if self.sqlmeta.parentClass:
            items.extend(self._parent._reprItems())
        # filter out our special column
        return [item for item in items if item[0] != 'childName']

__all__ = ['InheritableSQLObject']
