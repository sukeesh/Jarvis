"""
SQLObject
---------

:author: Ian Bicking <ianb@colorstudy.com>

SQLObject is a object-relational mapper.  See SQLObject.html or
SQLObject.rst for more.

With the help by Oleg Broytman and many other contributors.
See Authors.rst.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 2.1 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301,
USA.
"""
import sys
import threading
import weakref
import types
import warnings
from . import sqlbuilder
from . import dbconnection
from . import col
from . import styles
from . import joins
from . import index
from . import classregistry
from . import declarative
from . import events
from .sresults import SelectResults
from .util.threadinglocal import local
from sqlobject.compat import PY2, with_metaclass, string_type, unicode_type

if ((sys.version_info[0] == 2) and (sys.version_info[:2] < (2, 7))) or \
   ((sys.version_info[0] == 3) and (sys.version_info[:2] < (3, 4))):
    raise ImportError("SQLObject requires Python 2.7 or 3.4+")

if not PY2:
    # alias for python 3 compatability
    long = int

"""
This thread-local storage is needed for RowCreatedSignals. It gathers
code-blocks to execute _after_ the whole hierachy of inherited SQLObjects
is created. See SQLObject._create
"""

NoDefault = sqlbuilder.NoDefault


class SQLObjectNotFound(LookupError):
    pass


class SQLObjectIntegrityError(Exception):
    pass


def makeProperties(obj):
    """
    This function takes a dictionary of methods and finds
    methods named like:
    * _get_attr
    * _set_attr
    * _del_attr
    * _doc_attr
    Except for _doc_attr, these should be methods.  It
    then creates properties from these methods, like
    property(_get_attr, _set_attr, _del_attr, _doc_attr).
    Missing methods are okay.
    """

    if isinstance(obj, dict):
        def setFunc(var, value):
            obj[var] = value
        d = obj
    else:
        def setFunc(var, value):
            setattr(obj, var, value)
        d = obj.__dict__

    props = {}
    for var, value in d.items():
        if var.startswith('_set_'):
            props.setdefault(var[5:], {})['set'] = value
        elif var.startswith('_get_'):
            props.setdefault(var[5:], {})['get'] = value
        elif var.startswith('_del_'):
            props.setdefault(var[5:], {})['del'] = value
        elif var.startswith('_doc_'):
            props.setdefault(var[5:], {})['doc'] = value
    for var, setters in props.items():
        if len(setters) == 1 and 'doc' in setters:
            continue
        if var in d:
            if isinstance(d[var], (types.MethodType, types.FunctionType)):
                warnings.warn(
                    "I tried to set the property %r, but it was "
                    "already set, as a method (%r).  Methods have "
                    "significantly different semantics than properties, "
                    "and this may be a sign of a bug in your code."
                    % (var, d[var]))
            continue
        setFunc(var,
                property(setters.get('get'), setters.get('set'),
                         setters.get('del'), setters.get('doc')))


def unmakeProperties(obj):
    if isinstance(obj, dict):
        def delFunc(obj, var):
            del obj[var]
        d = obj
    else:
        delFunc = delattr
        d = obj.__dict__

    for var, value in list(d.items()):
        if isinstance(value, property):
            for prop in [value.fget, value.fset, value.fdel]:
                if prop and prop.__name__ not in d:
                    delFunc(obj, var)
                    break


def findDependencies(name, registry=None):
    depends = []
    for klass in classregistry.registry(registry).allClasses():
        if findDependantColumns(name, klass):
            depends.append(klass)
        else:
            for join in klass.sqlmeta.joins:
                if isinstance(join, joins.SORelatedJoin) and \
                        join.otherClassName == name:
                    depends.append(klass)
                    break
    return depends


def findDependantColumns(name, klass):
    depends = []
    for _col in klass.sqlmeta.columnList:
        if _col.foreignKey == name and _col.cascade is not None:
            depends.append(_col)
    return depends


def _collectAttributes(cls, new_attrs, look_for_class):
    """Finds all attributes in `new_attrs` that are instances of
    `look_for_class`. The ``.name`` attribute is set for any matching objects.
    Returns them as a list.

    """
    result = []
    for attr, value in new_attrs.items():
        if isinstance(value, look_for_class):
            value.name = attr
            delattr(cls, attr)
            result.append(value)
    return result


class CreateNewSQLObject:
    """
    Dummy singleton to use in place of an ID, to signal we want
    a new object.
    """
    pass


class sqlmeta(with_metaclass(declarative.DeclarativeMeta, object)):
    """
    This object is the object we use to keep track of all sorts of
    information.  Subclasses are made for each SQLObject subclass
    (dynamically if necessary), and instances are created to go
    alongside every SQLObject instance.
    """

    table = None
    idName = None
    idSequence = None
    # This function is used to coerce IDs into the proper format,
    # so you should replace it with str, or another function, if you
    # aren't using integer IDs
    idType = int
    style = None
    lazyUpdate = False
    defaultOrder = None
    cacheValues = True
    registry = None
    fromDatabase = False
    # Default is false, but we set it to true for the *instance*
    # when necessary: (bad clever? maybe)
    expired = False

    # This is a mapping from column names to SOCol (or subclass)
    # instances:
    columns = {}
    columnList = []

    # This is a mapping from column names to Col (or subclass)
    # instances; these objects don't have the logic that the SOCol
    # objects do, and are not attached to this class closely.
    columnDefinitions = {}

    # These are lists of the join and index objects:
    indexes = []
    indexDefinitions = []
    joins = []
    joinDefinitions = []

    # These attributes shouldn't be shared with superclasses:
    _unshared_attributes = ['table', 'columns', 'childName']

    # These are internal bookkeeping attributes; the class-level
    # definition is a default for the instances, instances will
    # reset these values.

    # When an object is being created, it has an instance
    # variable _creating, which is true.  This way all the
    # setters can be captured until the object is complete,
    # and then the row is inserted into the database.  Once
    # that happens, _creating is deleted from the instance,
    # and only the class variable (which is always false) is
    # left.
    _creating = False
    _obsolete = False
    # Sometimes an intance is attached to a connection, not
    # globally available.  In that case, self.sqlmeta._perConnection
    # will be true.  It's false by default:
    _perConnection = False

    # Inheritance definitions:
    parentClass = None  # A reference to the parent class
    childClasses = {}  # References to child classes, keyed by childName
    childName = None  # Class name for inheritance child object creation

    # Does the row require syncing?
    dirty = False

    # Default encoding for UnicodeCol's
    dbEncoding = None

    def __classinit__(cls, new_attrs):
        for attr in cls._unshared_attributes:
            if attr not in new_attrs:
                setattr(cls, attr, None)
        declarative.setup_attributes(cls, new_attrs)

    def __init__(self, instance):
        self.instance = weakref.proxy(instance)

    @classmethod
    def send(cls, signal, *args, **kw):
        events.send(signal, cls.soClass, *args, **kw)

    @classmethod
    def setClass(cls, soClass):
        cls.soClass = soClass
        if not cls.style:
            cls.style = styles.defaultStyle
            try:
                if cls.soClass._connection and cls.soClass._connection.style:
                    cls.style = cls.soClass._connection.style
            except AttributeError:
                pass
        if cls.table is None:
            cls.table = cls.style.pythonClassToDBTable(cls.soClass.__name__)
        if cls.idName is None:
            cls.idName = cls.style.idForTable(cls.table)

        # plainSetters are columns that haven't been overridden by the
        # user, so we can contact the database directly to set them.
        # Note that these can't set these in the SQLObject class
        # itself, because they specific to this subclass of SQLObject,
        # and cannot be shared among classes.
        cls._plainSetters = {}
        cls._plainGetters = {}
        cls._plainForeignSetters = {}
        cls._plainForeignGetters = {}
        cls._plainJoinGetters = {}
        cls._plainJoinAdders = {}
        cls._plainJoinRemovers = {}

        # This is a dictionary of columnName: columnObject
        # None of these objects can be shared with superclasses
        cls.columns = {}
        cls.columnList = []
        # These, however, can be shared:
        cls.columnDefinitions = cls.columnDefinitions.copy()
        cls.indexes = []
        cls.indexDefinitions = cls.indexDefinitions[:]
        cls.joins = []
        cls.joinDefinitions = cls.joinDefinitions[:]

    ############################################################
    # Adding special values, like columns and indexes
    ############################################################

    ########################################
    # Column handling
    ########################################

    @classmethod
    def addColumn(cls, columnDef, changeSchema=False, connection=None):
        post_funcs = []
        cls.send(events.AddColumnSignal, cls.soClass, connection,
                 columnDef.name, columnDef, changeSchema, post_funcs)
        sqlmeta = cls
        soClass = cls.soClass
        del cls
        column = columnDef.withClass(soClass)
        name = column.name
        assert name != 'id', (
            "The 'id' column is implicit, and should not be defined as "
            "a column")
        assert name not in sqlmeta.columns, (
            "The class %s.%s already has a column %r (%r), you cannot "
            "add the column %r"
            % (soClass.__module__, soClass.__name__, name,
               sqlmeta.columnDefinitions[name], columnDef))
        # Collect columns from the parent classes to test
        # if the column is not in a parent class
        parent_columns = []
        for base in soClass.__bases__:
            if hasattr(base, "sqlmeta"):
                parent_columns.extend(base.sqlmeta.columns.keys())
        if hasattr(soClass, name):
            assert (name in parent_columns) or (name == "childName"), (
                "The class %s.%s already has a variable or method %r, "
                "you cannot add the column %r" % (
                    soClass.__module__, soClass.__name__, name, name))
        sqlmeta.columnDefinitions[name] = columnDef
        sqlmeta.columns[name] = column
        # A stable-ordered version of the list...
        sqlmeta.columnList.append(column)

        ###################################################
        # Create the getter function(s).  We'll start by
        # creating functions like _SO_get_columnName,
        # then if there's no function named _get_columnName
        # we'll alias that to _SO_get_columnName.  This
        # allows a sort of super call, even though there's
        # no superclass that defines the database access.
        if sqlmeta.cacheValues:
            # We create a method here, which is just a function
            # that takes "self" as the first argument.
            getter = eval(
                'lambda self: self._SO_loadValue(%s)' %
                repr(instanceName(name)))

        else:
            # If we aren't caching values, we just call the
            # function _SO_getValue, which fetches from the
            # database.
            getter = eval('lambda self: self._SO_getValue(%s)' % repr(name))
        setattr(soClass, rawGetterName(name), getter)

        # Here if the _get_columnName method isn't in the
        # definition, we add it with the default
        # _SO_get_columnName definition.
        if not hasattr(soClass, getterName(name)) or (name == 'childName'):
            setattr(soClass, getterName(name), getter)
            sqlmeta._plainGetters[name] = 1

        #################################################
        # Create the setter function(s)
        # Much like creating the getters, we will create
        # _SO_set_columnName methods, and then alias them
        # to _set_columnName if the user hasn't defined
        # those methods themself.

        # @@: This is lame; immutable right now makes it unsettable,
        # making the table read-only
        if not column.immutable:
            # We start by just using the _SO_setValue method
            setter = eval(
                'lambda self, val: self._SO_setValue'
                '(%s, val, self.%s, self.%s)' % (
                    repr(name),
                    '_SO_from_python_%s' % name, '_SO_to_python_%s' % name))
            setattr(soClass, '_SO_from_python_%s' % name, column.from_python)
            setattr(soClass, '_SO_to_python_%s' % name, column.to_python)
            setattr(soClass, rawSetterName(name), setter)
            # Then do the aliasing
            if not hasattr(soClass, setterName(name)) or (name == 'childName'):
                setattr(soClass, setterName(name), setter)
                # We keep track of setters that haven't been
                # overridden, because we can combine these
                # set columns into one SQL UPDATE query.
                sqlmeta._plainSetters[name] = 1

        ##################################################
        # Here we check if the column is a foreign key, in
        # which case we need to make another method that
        # fetches the key and constructs the sister
        # SQLObject instance.
        if column.foreignKey:

            # We go through the standard _SO_get_columnName deal
            # we're giving the object, not the ID of the
            # object this time:
            origName = column.origName
            if sqlmeta.cacheValues:
                # self._SO_class_className is a reference
                # to the class in question.
                getter = eval(
                    'lambda self: self._SO_foreignKey'
                    '(self._SO_loadValue(%r), self._SO_class_%s, %s)' %
                    (instanceName(name), column.foreignKey,
                     column.refColumn and repr(column.refColumn)))
            else:
                # Same non-caching version as above.
                getter = eval(
                    'lambda self: self._SO_foreignKey'
                    '(self._SO_getValue(%s), self._SO_class_%s, %s)' %
                    (repr(name), column.foreignKey,
                     column.refColumn and repr(column.refColumn)))
            setattr(soClass, rawGetterName(origName), getter)

            # And we set the _get_columnName version
            if not hasattr(soClass, getterName(origName)):
                setattr(soClass, getterName(origName), getter)
                sqlmeta._plainForeignGetters[origName] = 1

            if not column.immutable:
                # The setter just gets the ID of the object,
                # and then sets the real column.
                setter = eval(
                    'lambda self, val: '
                    'setattr(self, %s, self._SO_getID(val, %s))' %
                    (repr(name), column.refColumn and repr(column.refColumn)))
                setattr(soClass, rawSetterName(origName), setter)
                if not hasattr(soClass, setterName(origName)):
                    setattr(soClass, setterName(origName), setter)
                    sqlmeta._plainForeignSetters[origName] = 1

            classregistry.registry(sqlmeta.registry).addClassCallback(
                column.foreignKey,
                lambda foreign, me, attr: setattr(me, attr, foreign),
                soClass, '_SO_class_%s' % column.foreignKey)

        if column.alternateMethodName:
            func = eval(
                'lambda cls, val, connection=None: '
                'cls._SO_fetchAlternateID(%s, %s, val, connection=connection)'
                % (repr(column.name), repr(column.dbName)))
            setattr(soClass, column.alternateMethodName, classmethod(func))

        if changeSchema:
            conn = connection or soClass._connection
            conn.addColumn(sqlmeta.table, column)

        if soClass._SO_finishedClassCreation:
            makeProperties(soClass)

        for func in post_funcs:
            func(soClass, column)

    @classmethod
    def addColumnsFromDatabase(sqlmeta, connection=None):
        soClass = sqlmeta.soClass
        conn = connection or soClass._connection
        for columnDef in conn.columnsFromSchema(sqlmeta.table, soClass):
            if columnDef.name not in sqlmeta.columnDefinitions:
                if isinstance(columnDef.name, unicode_type) and PY2:
                    columnDef.name = columnDef.name.encode('ascii')
                sqlmeta.addColumn(columnDef)

    @classmethod
    def delColumn(cls, column, changeSchema=False, connection=None):
        sqlmeta = cls
        soClass = sqlmeta.soClass
        if isinstance(column, str):
            if column in sqlmeta.columns:
                column = sqlmeta.columns[column]
            elif column + 'ID' in sqlmeta.columns:
                column = sqlmeta.columns[column + 'ID']
            else:
                raise ValueError('Unknown column ' + column)
        if isinstance(column, col.Col):
            for c in sqlmeta.columns.values():
                if column is c.columnDef:
                    column = c
                    break
            else:
                raise IndexError(
                    "Column with definition %r not found" % column)
        post_funcs = []
        cls.send(events.DeleteColumnSignal, cls.soClass, connection,
                 column.name, column, post_funcs)
        name = column.name
        del sqlmeta.columns[name]
        del sqlmeta.columnDefinitions[name]
        sqlmeta.columnList.remove(column)
        delattr(soClass, rawGetterName(name))
        if name in sqlmeta._plainGetters:
            delattr(soClass, getterName(name))
        delattr(soClass, rawSetterName(name))
        if name in sqlmeta._plainSetters:
            delattr(soClass, setterName(name))
        if column.foreignKey:
            delattr(soClass,
                    rawGetterName(soClass.sqlmeta.style.
                                  instanceIDAttrToAttr(name)))
            if name in sqlmeta._plainForeignGetters:
                delattr(soClass, getterName(name))
            delattr(soClass,
                    rawSetterName(soClass.sqlmeta.style.
                                  instanceIDAttrToAttr(name)))
            if name in sqlmeta._plainForeignSetters:
                delattr(soClass, setterName(name))
        if column.alternateMethodName:
            delattr(soClass, column.alternateMethodName)

        if changeSchema:
            conn = connection or soClass._connection
            conn.delColumn(sqlmeta, column)

        if soClass._SO_finishedClassCreation:
            unmakeProperties(soClass)
            makeProperties(soClass)

        for func in post_funcs:
            func(soClass, column)

    ########################################
    # Join handling
    ########################################

    @classmethod
    def addJoin(cls, joinDef):
        sqlmeta = cls
        soClass = cls.soClass
        # The name of the method we'll create.  If it's
        # automatically generated, it's generated by the
        # join class.
        join = joinDef.withClass(soClass)
        meth = join.joinMethodName

        sqlmeta.joins.append(join)
        index = len(sqlmeta.joins) - 1
        if joinDef not in sqlmeta.joinDefinitions:
            sqlmeta.joinDefinitions.append(joinDef)

        # The function fetches the join by index, and
        # then lets the join object do the rest of the
        # work:
        func = eval(
            'lambda self: self.sqlmeta.joins[%i].performJoin(self)' % index)

        # And we do the standard _SO_get_... _get_... deal
        setattr(soClass, rawGetterName(meth), func)
        if not hasattr(soClass, getterName(meth)):
            setattr(soClass, getterName(meth), func)
            sqlmeta._plainJoinGetters[meth] = 1

        # Some joins allow you to remove objects from the
        # join.
        if hasattr(join, 'remove'):
            # Again, we let it do the remove, and we do the
            # standard naming trick.
            func = eval(
                'lambda self, obj: self.sqlmeta.joins[%i].remove(self, obj)' %
                index)
            setattr(soClass, '_SO_remove' + join.addRemoveName, func)
            if not hasattr(soClass, 'remove' + join.addRemoveName):
                setattr(soClass, 'remove' + join.addRemoveName, func)
                sqlmeta._plainJoinRemovers[meth] = 1

        # Some joins allow you to add objects.
        if hasattr(join, 'add'):
            # And again...
            func = eval(
                'lambda self, obj: self.sqlmeta.joins[%i].add(self, obj)' %
                index)
            setattr(soClass, '_SO_add' + join.addRemoveName, func)
            if not hasattr(soClass, 'add' + join.addRemoveName):
                setattr(soClass, 'add' + join.addRemoveName, func)
                sqlmeta._plainJoinAdders[meth] = 1

        if soClass._SO_finishedClassCreation:
            makeProperties(soClass)

    @classmethod
    def delJoin(sqlmeta, joinDef):
        soClass = sqlmeta.soClass
        for join in sqlmeta.joins:
            # previously deleted joins will be None, so it must
            # be skipped or it'll error out on the next line.
            if join is None:
                continue
            if joinDef is join.joinDef:
                break
        else:
            raise IndexError(
                "Join %r not found in class %r (from %r)"
                % (joinDef, soClass, sqlmeta.joins))
        meth = join.joinMethodName
        sqlmeta.joinDefinitions.remove(joinDef)
        for i in range(len(sqlmeta.joins)):
            if sqlmeta.joins[i] is join:
                # Have to leave None, because we refer to joins
                # by index.
                sqlmeta.joins[i] = None
        delattr(soClass, rawGetterName(meth))
        if meth in sqlmeta._plainJoinGetters:
            delattr(soClass, getterName(meth))
        if hasattr(join, 'remove'):
            delattr(soClass, '_SO_remove' + join.addRemovePrefix)
            if meth in sqlmeta._plainJoinRemovers:
                delattr(soClass, 'remove' + join.addRemovePrefix)
        if hasattr(join, 'add'):
            delattr(soClass, '_SO_add' + join.addRemovePrefix)
            if meth in sqlmeta._plainJoinAdders:
                delattr(soClass, 'add' + join.addRemovePrefix)

        if soClass._SO_finishedClassCreation:
            unmakeProperties(soClass)
            makeProperties(soClass)

    ########################################
    # Indexes
    ########################################

    @classmethod
    def addIndex(cls, indexDef):
        cls.indexDefinitions.append(indexDef)
        index = indexDef.withClass(cls.soClass)
        cls.indexes.append(index)
        setattr(cls.soClass, index.name, index)

    ########################################
    # Utility methods
    ########################################

    @classmethod
    def getColumns(sqlmeta):
        return sqlmeta.columns.copy()

    def asDict(self):
        """
        Return the object as a dictionary of columns to values.
        """
        result = {}
        for key in self.getColumns():
            result[key] = getattr(self.instance, key)
        result['id'] = self.instance.id
        return result

    @classmethod
    def expireAll(sqlmeta, connection=None):
        """
        Expire all instances of this class.
        """
        soClass = sqlmeta.soClass
        connection = connection or soClass._connection
        cache_set = connection.cache
        cache_set.weakrefAll(soClass)
        for item in cache_set.getAll(soClass):
            item.expire()


sqlhub = dbconnection.ConnectionHub()


# Turning it on gives earlier warning about things
# that will be deprecated (having this off we won't flood people
# with warnings right away).
warnings_level = 1
exception_level = None
# Current levels:
#  1) Actively deprecated
#  2) Deprecated after 1
#  3) Deprecated after 2


def deprecated(message, level=1, stacklevel=2):
    if exception_level is not None and exception_level <= level:
        raise NotImplementedError(message)
    if warnings_level is not None and warnings_level <= level:
        warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)

# if sys.version_info[:2] < (2, 7):
#     deprecated("Support for Python 2.6 has been declared obsolete "
#                "and will be removed in the next release of SQLObject")


def setDeprecationLevel(warning=1, exception=None):
    """
    Set the deprecation level for SQLObject.  Low levels are more
    actively being deprecated.  Any warning at a level at or below
    ``warning`` will give a warning.  Any warning at a level at or
    below ``exception`` will give an exception.  You can use a higher
    ``exception`` level for tests to help upgrade your code.  ``None``
    for either value means never warn or raise exceptions.

    The levels currently mean:

      1) Deprecated in current version.  Will be removed in next version.

      2) Planned to deprecate in next version, remove later.

      3) Planned to deprecate sometime, remove sometime much later.

    As the SQLObject versions progress, the deprecation level of
    specific features will go down, indicating the advancing nature of
    the feature's doom.  We'll try to keep features at 1 for a major
    revision.

    As time continues there may be a level 0, which will give a useful
    error message (better than ``AttributeError``) but where the
    feature has been fully removed.
    """
    global warnings_level, exception_level
    warnings_level = warning
    exception_level = exception


class _sqlmeta_attr(object):

    def __init__(self, name, deprecation_level):
        self.name = name
        self.deprecation_level = deprecation_level

    def __get__(self, obj, type=None):
        if self.deprecation_level is not None:
            deprecated(
                'Use of this attribute should be replaced with '
                '.sqlmeta.%s' % self.name, level=self.deprecation_level)
        return getattr((type or obj).sqlmeta, self.name)


_postponed_local = local()


# SQLObject is the superclass for all SQLObject classes, of
# course.  All the deeper magic is done in MetaSQLObject, and
# only lesser magic is done here.  All the actual work is done
# here, though -- just automatic method generation (like
# methods and properties for each column) is done in
# MetaSQLObject.


class SQLObject(with_metaclass(declarative.DeclarativeMeta, object)):

    _connection = sqlhub

    sqlmeta = sqlmeta

    # DSM: The _inheritable attribute controls wheter the class can by
    # DSM: inherited 'logically' with a foreignKey and a back reference.
    _inheritable = False  # Is this class inheritable?
    _parent = None  # A reference to the parent instance
    childName = None  # Children name (to be able to get a subclass)

    # The law of Demeter: the class should not call another classes by name
    SelectResultsClass = SelectResults

    def __classinit__(cls, new_attrs):

        # This is true if we're initializing the SQLObject class,
        # instead of a subclass:
        is_base = cls.__bases__ == (object,)

        cls._SO_setupSqlmeta(new_attrs, is_base)

        implicitColumns = _collectAttributes(cls, new_attrs, col.Col)
        implicitJoins = _collectAttributes(cls, new_attrs, joins.Join)
        implicitIndexes = _collectAttributes(cls, new_attrs,
                                             index.DatabaseIndex)

        if not is_base:
            cls._SO_cleanDeprecatedAttrs(new_attrs)

        if '_connection' in new_attrs:
            connection = new_attrs['_connection']
            del cls._connection
            assert 'connection' not in new_attrs
        elif 'connection' in new_attrs:
            connection = new_attrs['connection']
            del cls.connection
        else:
            connection = None

        cls._SO_finishedClassCreation = False

        ######################################################
        # Set some attributes to their defaults, if necessary.
        # First we get the connection:
        if not connection and not getattr(cls, '_connection', None):
            mod = sys.modules[cls.__module__]
            # See if there's a __connection__ global in
            # the module, use it if there is.
            if hasattr(mod, '__connection__'):
                connection = mod.__connection__

        # Do not check hasattr(cls, '_connection') here - it is possible
        # SQLObject parent class has a connection attribute that came
        # from sqlhub, e.g.; check __dict__ only.
        if connection and ('_connection' not in cls.__dict__):
            cls.setConnection(connection)

        sqlmeta = cls.sqlmeta

        # We have to check if there are columns in the inherited
        # _columns where the attribute has been set to None in this
        # class.  If so, then we need to remove that column from
        # _columns.
        for key in sqlmeta.columnDefinitions.keys():
            if (key in new_attrs and new_attrs[key] is None):
                del sqlmeta.columnDefinitions[key]

        for column in sqlmeta.columnDefinitions.values():
            sqlmeta.addColumn(column)

        for column in implicitColumns:
            sqlmeta.addColumn(column)

        # Now the class is in an essentially OK-state, so we can
        # set up any magic attributes:
        declarative.setup_attributes(cls, new_attrs)

        if sqlmeta.fromDatabase:
            sqlmeta.addColumnsFromDatabase()

        for j in implicitJoins:
            sqlmeta.addJoin(j)
        for i in implicitIndexes:
            sqlmeta.addIndex(i)

        def order_getter(o):
            return o.creationOrder
        sqlmeta.columnList.sort(key=order_getter)
        sqlmeta.indexes.sort(key=order_getter)
        sqlmeta.indexDefinitions.sort(key=order_getter)
        # Joins cannot be sorted because addJoin created accessors
        # that remember indexes.
        # sqlmeta.joins.sort(key=order_getter)
        sqlmeta.joinDefinitions.sort(key=order_getter)

        # We don't setup the properties until we're finished with the
        # batch adding of all the columns...
        cls._notifyFinishClassCreation()
        cls._SO_finishedClassCreation = True
        makeProperties(cls)

        # We use the magic "q" attribute for accessing lazy
        # SQL where-clause generation.  See the sql module for
        # more.
        if not is_base:
            cls.q = sqlbuilder.SQLObjectTable(cls)
            cls.j = sqlbuilder.SQLObjectTableWithJoins(cls)

        classregistry.registry(sqlmeta.registry).addClass(cls)

    @classmethod
    def _SO_setupSqlmeta(cls, new_attrs, is_base):
        """
        This fixes up the sqlmeta attribute.  It handles both the case
        where no sqlmeta was given (in which we need to create another
        subclass), or the sqlmeta given doesn't have the proper
        inheritance.  Lastly it calls sqlmeta.setClass, which handles
        much of the setup.
        """
        if ('sqlmeta' not in new_attrs and not is_base):
            # We have to create our own subclass, usually.
            # type(className, bases_tuple, attr_dict) creates a new subclass.
            cls.sqlmeta = type('sqlmeta', (cls.sqlmeta,), {})
        if not issubclass(cls.sqlmeta, sqlmeta):
            # We allow no superclass and an object superclass, instead
            # of inheriting from sqlmeta; but in that case we replace
            # the class and just move over its attributes:
            assert cls.sqlmeta.__bases__ in ((), (object,)), (
                "If you do not inherit your sqlmeta class from "
                "sqlobject.sqlmeta, it must not inherit from any other "
                "class (your sqlmeta inherits from: %s)"
                % cls.sqlmeta.__bases__)
            for base in cls.__bases__:
                superclass = getattr(base, 'sqlmeta', None)
                if superclass:
                    break
            else:
                assert 0, (
                    "No sqlmeta class could be found in any superclass "
                    "(while fixing up sqlmeta %r inheritance)"
                    % cls.sqlmeta)
            values = dict(cls.sqlmeta.__dict__)
            for key in list(values.keys()):
                if key.startswith('__') and key.endswith('__'):
                    # Magic values shouldn't be passed through:
                    del values[key]
            cls.sqlmeta = type('sqlmeta', (superclass,), values)

        if not is_base:  # Do not pollute the base sqlmeta class
            cls.sqlmeta.setClass(cls)

    @classmethod
    def _SO_cleanDeprecatedAttrs(cls, new_attrs):
        """
        This removes attributes on SQLObject subclasses that have
        been deprecated; they are moved to the sqlmeta class, and
        a deprecation warning is given.
        """
        for attr in ():
            if attr in new_attrs:
                deprecated("%r is deprecated and read-only; please do "
                           "not use it in your classes until it is fully "
                           "deprecated" % attr, level=1, stacklevel=5)

    @classmethod
    def get(cls, id, connection=None, selectResults=None):

        assert id is not None, \
            'None is not a possible id for %s' % cls.__name__

        id = cls.sqlmeta.idType(id)

        if connection is None:
            cache = cls._connection.cache
        else:
            cache = connection.cache

        # This whole sequence comes from Cache.CacheFactory's
        # behavior, where a None returned means a cache miss.
        val = cache.get(id, cls)
        if val is None:
            try:
                val = cls(_SO_fetch_no_create=1)
                val._SO_validatorState = sqlbuilder.SQLObjectState(val)
                val._init(id, connection, selectResults)
                cache.put(id, cls, val)
            finally:
                cache.finishPut(cls)
        elif selectResults and not val.sqlmeta.dirty:
            val._SO_writeLock.acquire()
            try:
                val._SO_selectInit(selectResults)
                val.sqlmeta.expired = False
            finally:
                val._SO_writeLock.release()
        return val

    @classmethod
    def _notifyFinishClassCreation(cls):
        pass

    def _init(self, id, connection=None, selectResults=None):
        assert id is not None
        # This function gets called only when the object is
        # created, unlike __init__ which would be called
        # anytime the object was returned from cache.
        self.id = id
        self._SO_writeLock = threading.Lock()

        # If no connection was given, we'll inherit the class
        # instance variable which should have a _connection
        # attribute.
        if (connection is not None) and \
                (getattr(self, '_connection', None) is not connection):
            self._connection = connection
            # Sometimes we need to know if this instance is
            # global or tied to a particular connection.
            # This flag tells us that:
            self.sqlmeta._perConnection = True

        if not selectResults:
            dbNames = [col.dbName for col in self.sqlmeta.columnList]
            selectResults = self._connection._SO_selectOne(self, dbNames)
            if not selectResults:
                raise SQLObjectNotFound(
                    "The object %s by the ID %s does not exist" % (
                        self.__class__.__name__, self.id))
        self._SO_selectInit(selectResults)
        self._SO_createValues = {}
        self.sqlmeta.dirty = False

    def _SO_loadValue(self, attrName):
        try:
            return getattr(self, attrName)
        except AttributeError:
            try:
                self._SO_writeLock.acquire()
                try:
                    # Maybe, just in the moment since we got the lock,
                    # some other thread did a _SO_loadValue and we
                    # have the attribute!  Let's try and find out!  We
                    # can keep trying this all day and still beat the
                    # performance on the database call (okay, we can
                    # keep trying this for a few msecs at least)...
                    result = getattr(self, attrName)
                except AttributeError:
                    pass
                else:
                    return result
                self.sqlmeta.expired = False
                dbNames = [col.dbName for col in self.sqlmeta.columnList]
                selectResults = self._connection._SO_selectOne(self, dbNames)
                if not selectResults:
                    raise SQLObjectNotFound(
                        "The object %s by the ID %s has been deleted" % (
                            self.__class__.__name__, self.id))
                self._SO_selectInit(selectResults)
                result = getattr(self, attrName)
                return result
            finally:
                self._SO_writeLock.release()

    def sync(self):
        if self.sqlmeta.lazyUpdate and self._SO_createValues:
            self.syncUpdate()
        self._SO_writeLock.acquire()
        try:
            dbNames = [col.dbName for col in self.sqlmeta.columnList]
            selectResults = self._connection._SO_selectOne(self, dbNames)
            if not selectResults:
                raise SQLObjectNotFound(
                    "The object %s by the ID %s has been deleted" % (
                        self.__class__.__name__, self.id))
            self._SO_selectInit(selectResults)
            self.sqlmeta.expired = False
        finally:
            self._SO_writeLock.release()

    def syncUpdate(self):
        if not self._SO_createValues:
            return
        self._SO_writeLock.acquire()
        try:
            if self.sqlmeta.columns:
                columns = self.sqlmeta.columns
                values = [(columns[v[0]].dbName, v[1])
                          for v in sorted(
                              self._SO_createValues.items(),
                              key=lambda c: columns[c[0]].creationOrder)]
                self._connection._SO_update(self, values)
            self.sqlmeta.dirty = False
            self._SO_createValues = {}
        finally:
            self._SO_writeLock.release()

        post_funcs = []
        self.sqlmeta.send(events.RowUpdatedSignal, self, post_funcs)
        for func in post_funcs:
            func(self)

    def expire(self):
        if self.sqlmeta.expired:
            return
        self._SO_writeLock.acquire()
        try:
            if self.sqlmeta.expired:
                return
            for column in self.sqlmeta.columnList:
                delattr(self, instanceName(column.name))
            self.sqlmeta.expired = True
            self._connection.cache.expire(self.id, self.__class__)
            self._SO_createValues = {}
        finally:
            self._SO_writeLock.release()

    def _SO_setValue(self, name, value, from_python, to_python):
        # This is the place where we actually update the
        # database.

        # If we are _creating, the object doesn't yet exist
        # in the database, and we can't insert it until all
        # the parts are set.  So we just keep them in a
        # dictionary until later:
        d = {name: value}
        if not self.sqlmeta._creating and \
                not getattr(self.sqlmeta, "row_update_sig_suppress", False):
            self.sqlmeta.send(events.RowUpdateSignal, self, d)
        if len(d) != 1 or name not in d:
            # Already called RowUpdateSignal, don't call it again
            # inside .set()
            self.sqlmeta.row_update_sig_suppress = True
            self.set(**d)
            del self.sqlmeta.row_update_sig_suppress
        value = d[name]
        if from_python:
            dbValue = from_python(value, self._SO_validatorState)
        else:
            dbValue = value
        if to_python:
            value = to_python(dbValue, self._SO_validatorState)
        if self.sqlmeta._creating or self.sqlmeta.lazyUpdate:
            self.sqlmeta.dirty = True
            self._SO_createValues[name] = dbValue
            setattr(self, instanceName(name), value)
            return

        self._connection._SO_update(
            self, [(self.sqlmeta.columns[name].dbName,
                    dbValue)])

        if self.sqlmeta.cacheValues:
            setattr(self, instanceName(name), value)

        post_funcs = []
        self.sqlmeta.send(events.RowUpdatedSignal, self, post_funcs)
        for func in post_funcs:
            func(self)

    def set(self, _suppress_set_sig=False, **kw):
        if not self.sqlmeta._creating and \
                not getattr(self.sqlmeta, "row_update_sig_suppress", False) \
                and not _suppress_set_sig:
            self.sqlmeta.send(events.RowUpdateSignal, self, kw)
        # set() is used to update multiple values at once,
        # potentially with one SQL statement if possible.

        # Filter out items that don't map to column names.
        # Those will be set directly on the object using
        # setattr(obj, name, value).
        def is_column(_c):
            return _c in self.sqlmeta._plainSetters

        def f_is_column(item):
            return is_column(item[0])

        def f_not_column(item):
            return not is_column(item[0])
        items = kw.items()
        extra = dict(filter(f_not_column, items))
        kw = dict(filter(f_is_column, items))

        # _creating is special, see _SO_setValue
        if self.sqlmeta._creating or self.sqlmeta.lazyUpdate:
            for name, value in kw.items():
                from_python = getattr(self, '_SO_from_python_%s' % name, None)
                if from_python:
                    kw[name] = dbValue = from_python(value,
                                                     self._SO_validatorState)
                else:
                    dbValue = value
                to_python = getattr(self, '_SO_to_python_%s' % name, None)
                if to_python:
                    value = to_python(dbValue, self._SO_validatorState)
                setattr(self, instanceName(name), value)

            self._SO_createValues.update(kw)

            for name, value in extra.items():
                try:
                    getattr(self.__class__, name)
                except AttributeError:
                    if name not in self.sqlmeta.columns:
                        raise TypeError(
                            "%s.set() got an unexpected keyword argument "
                            "%s" % (self.__class__.__name__, name))
                try:
                    setattr(self, name, value)
                except AttributeError as e:
                    raise AttributeError('%s (with attribute %r)' % (e, name))

            self.sqlmeta.dirty = True
            return

        self._SO_writeLock.acquire()

        try:
            # We have to go through and see if the setters are
            # "plain", that is, if the user has changed their
            # definition in any way (put in something that
            # normalizes the value or checks for consistency,
            # for instance).  If so then we have to use plain
            # old setattr() to change the value, since we can't
            # read the user's mind.  We'll combine everything
            # else into a single UPDATE, if necessary.
            toUpdate = {}
            for name, value in kw.items():
                from_python = getattr(self, '_SO_from_python_%s' % name, None)
                if from_python:
                    dbValue = from_python(value, self._SO_validatorState)
                else:
                    dbValue = value
                to_python = getattr(self, '_SO_to_python_%s' % name, None)
                if to_python:
                    value = to_python(dbValue, self._SO_validatorState)
                if self.sqlmeta.cacheValues:
                    setattr(self, instanceName(name), value)
                toUpdate[name] = dbValue
            for name, value in extra.items():
                try:
                    getattr(self.__class__, name)
                except AttributeError:
                    if name not in self.sqlmeta.columns:
                        raise TypeError(
                            "%s.set() got an unexpected keyword argument "
                            "%s" % (self.__class__.__name__, name))
                try:
                    setattr(self, name, value)
                except AttributeError as e:
                    raise AttributeError('%s (with attribute %r)' % (e, name))

            if toUpdate:
                toUpdate = sorted(
                    toUpdate.items(),
                    key=lambda c: self.sqlmeta.columns[c[0]].creationOrder)
                args = [(self.sqlmeta.columns[name].dbName, value)
                        for name, value in toUpdate]
                self._connection._SO_update(self, args)
        finally:
            self._SO_writeLock.release()

        post_funcs = []
        self.sqlmeta.send(events.RowUpdatedSignal, self, post_funcs)
        for func in post_funcs:
            func(self)

    def _SO_selectInit(self, row):
        for _col, colValue in zip(self.sqlmeta.columnList, row):
            if _col.to_python:
                colValue = _col.to_python(colValue, self._SO_validatorState)
            setattr(self, instanceName(_col.name), colValue)

    def _SO_getValue(self, name):
        # Retrieves a single value from the database.  Simple.
        assert not self.sqlmeta._obsolete, (
            "%s with id %s has become obsolete"
            % (self.__class__.__name__, self.id))
        # @@: do we really need this lock?
        # self._SO_writeLock.acquire()
        column = self.sqlmeta.columns[name]
        results = self._connection._SO_selectOne(self, [column.dbName])
        # self._SO_writeLock.release()
        assert results is not None, "%s with id %s is not in the database" % (
            self.__class__.__name__, self.id)
        value = results[0]
        if column.to_python:
            value = column.to_python(value, self._SO_validatorState)
        return value

    def _SO_foreignKey(self, value, joinClass, idName=None):
        if value is None:
            return None
        if self.sqlmeta._perConnection:
            connection = self._connection
        else:
            connection = None
        if idName is None:  # Get by id
            return joinClass.get(value, connection=connection)
        return joinClass.select(
            getattr(joinClass.q, idName) == value,
            connection=connection).getOne()

    def __init__(self, **kw):
        # If we are the outmost constructor of a hiearchy of
        # InheritableSQLObjects (or simlpy _the_ constructor of a "normal"
        # SQLObject), we create a threadlocal list that collects the
        # RowCreatedSignals, and executes them if this very constructor is left
        try:
            _postponed_local.postponed_calls
            postponed_created = False
        except AttributeError:
            _postponed_local.postponed_calls = []
            postponed_created = True

        try:
            # We shadow the sqlmeta class with an instance of sqlmeta
            # that points to us (our sqlmeta buddy object; where the
            # sqlmeta class is our class's buddy class)
            self.sqlmeta = self.__class__.sqlmeta(self)
            # The get() classmethod/constructor uses a magic keyword
            # argument when it wants an empty object, fetched from the
            # database.  So we have nothing more to do in that case:
            if '_SO_fetch_no_create' in kw:
                return

            post_funcs = []
            self.sqlmeta.send(events.RowCreateSignal, self, kw, post_funcs)

            # Pass the connection object along if we were given one.
            if 'connection' in kw:
                connection = kw.pop('connection')
                if getattr(self, '_connection', None) is not connection:
                    self._connection = connection
                    self.sqlmeta._perConnection = True

            self._SO_writeLock = threading.Lock()

            if 'id' in kw:
                id = self.sqlmeta.idType(kw['id'])
                del kw['id']
            else:
                id = None

            self._create(id, **kw)

            for func in post_funcs:
                func(self)
        finally:
            # if we are the creator of the tl-storage, we
            # have to exectute and under all circumstances
            # remove the tl-storage
            if postponed_created:
                try:
                    for func in _postponed_local.postponed_calls:
                        func()
                finally:
                    del _postponed_local.postponed_calls

    def _create(self, id, **kw):

        self.sqlmeta._creating = True
        self._SO_createValues = {}
        self._SO_validatorState = sqlbuilder.SQLObjectState(self)

        # First we do a little fix-up on the keywords we were
        # passed:
        for column in self.sqlmeta.columnList:

            # Then we check if the column wasn't passed in, and
            # if not we try to get the default.
            if column.name not in kw and column.foreignName not in kw:
                default = column.default

                # If we don't get it, it's an error:
                # If we specified an SQL DEFAULT, then we should use that
                if default is NoDefault:
                    if column.defaultSQL is None:
                        raise TypeError(
                            "%s() did not get expected keyword argument "
                            "'%s'" % (self.__class__.__name__, column.name))
                    else:
                        # There is defaultSQL for the column -
                        # do not put the column to kw
                        # so that the backend creates the value.
                        continue

                # Otherwise we put it in as though they did pass
                # that keyword:

                kw[column.name] = default

        self.set(**kw)

        # Then we finalize the process:
        self._SO_finishCreate(id)

    def _SO_finishCreate(self, id=None):
        # Here's where an INSERT is finalized.
        # These are all the column values that were supposed
        # to be set, but were delayed until now:
        setters = self._SO_createValues.items()
        setters = sorted(
            setters, key=lambda c: self.sqlmeta.columns[c[0]].creationOrder)
        # Here's their database names:
        names = [self.sqlmeta.columns[v[0]].dbName for v in setters]
        values = [v[1] for v in setters]
        # Get rid of _SO_create*, we aren't creating anymore.
        # Doesn't have to be threadsafe because we're still in
        # new(), which doesn't need to be threadsafe.
        self.sqlmeta.dirty = False
        if not self.sqlmeta.lazyUpdate:
            del self._SO_createValues
        else:
            self._SO_createValues = {}
        del self.sqlmeta._creating

        # Do the insert -- most of the SQL in this case is left
        # up to DBConnection, since getting a new ID is
        # non-standard.
        id = self._connection.queryInsertID(self,
                                            id, names, values)
        cache = self._connection.cache
        cache.created(id, self.__class__, self)
        self._init(id)
        post_funcs = []
        kw = dict([('class', self.__class__), ('id', id)])

        def _send_RowCreatedSignal():
            self.sqlmeta.send(events.RowCreatedSignal, self, kw, post_funcs)
            for func in post_funcs:
                func(self)
        _postponed_local.postponed_calls.append(_send_RowCreatedSignal)

    def _SO_getID(self, obj, refColumn=None):
        return getID(obj, refColumn)

    @classmethod
    def _findAlternateID(cls, name, dbName, value, connection=None):
        if isinstance(name, str):
            name = (name,)
            value = (value,)
        if len(name) != len(value):
            raise ValueError(
                "'column' and 'value' tuples must be of the same size")
        new_value = []
        for n, v in zip(name, value):
            from_python = getattr(cls, '_SO_from_python_' + n)
            if from_python:
                v = from_python(
                    v, sqlbuilder.SQLObjectState(cls, connection=connection))
            new_value.append(v)
        condition = sqlbuilder.AND(
            *[getattr(cls.q, _n) == _v for _n, _v in zip(name, new_value)])
        return (connection or cls._connection)._SO_selectOneAlt(
            cls,
            [cls.sqlmeta.idName] +
            [column.dbName for column in cls.sqlmeta.columnList],
            condition), None

    @classmethod
    def _SO_fetchAlternateID(cls, name, dbName, value, connection=None,
                             idxName=None):
        result, obj = cls._findAlternateID(name, dbName, value, connection)
        if not result:
            if idxName is None:
                raise SQLObjectNotFound(
                    "The %s by alternateID %s = %s does not exist" % (
                        cls.__name__, name, repr(value)))
            else:
                names = []
                for i in range(len(name)):
                    names.append("%s = %s" % (name[i], repr(value[i])))
                names = ', '.join(names)
                raise SQLObjectNotFound(
                    "The %s by unique index %s(%s) does not exist" % (
                        cls.__name__, idxName, names))
        if obj:
            return obj
        if connection:
            obj = cls.get(result[0], connection=connection,
                          selectResults=result[1:])
        else:
            obj = cls.get(result[0], selectResults=result[1:])
        return obj

    @classmethod
    def _SO_depends(cls):
        return findDependencies(cls.__name__, cls.sqlmeta.registry)

    @classmethod
    def select(cls, clause=None, clauseTables=None,
               orderBy=NoDefault, limit=None,
               lazyColumns=False, reversed=False,
               distinct=False, connection=None,
               join=None, forUpdate=False):
        return cls.SelectResultsClass(cls, clause,
                                      clauseTables=clauseTables,
                                      orderBy=orderBy,
                                      limit=limit,
                                      lazyColumns=lazyColumns,
                                      reversed=reversed,
                                      distinct=distinct,
                                      connection=connection,
                                      join=join, forUpdate=forUpdate)

    @classmethod
    def selectBy(cls, connection=None, **kw):
        conn = connection or cls._connection
        return cls.SelectResultsClass(cls,
                                      conn._SO_columnClause(cls, kw),
                                      connection=conn)

    @classmethod
    def tableExists(cls, connection=None):
        conn = connection or cls._connection
        return conn.tableExists(cls.sqlmeta.table)

    @classmethod
    def dropTable(cls, ifExists=False, dropJoinTables=True, cascade=False,
                  connection=None):
        conn = connection or cls._connection
        if ifExists and not cls.tableExists(connection=conn):
            return
        extra_sql = []
        post_funcs = []
        cls.sqlmeta.send(events.DropTableSignal, cls, connection,
                         extra_sql, post_funcs)
        conn.dropTable(cls.sqlmeta.table, cascade)
        if dropJoinTables:
            cls.dropJoinTables(ifExists=ifExists, connection=conn)
        for sql in extra_sql:
            connection.query(sql)
        for func in post_funcs:
            func(cls, conn)

    @classmethod
    def createTable(cls, ifNotExists=False, createJoinTables=True,
                    createIndexes=True, applyConstraints=True,
                    connection=None):
        conn = connection or cls._connection
        if ifNotExists and cls.tableExists(connection=conn):
            return
        extra_sql = []
        post_funcs = []
        cls.sqlmeta.send(events.CreateTableSignal, cls, connection,
                         extra_sql, post_funcs)
        constraints = conn.createTable(cls)
        if applyConstraints:
            for constraint in constraints:
                conn.query(constraint)
        else:
            extra_sql.extend(constraints)
        if createJoinTables:
            cls.createJoinTables(ifNotExists=ifNotExists,
                                 connection=conn)
        if createIndexes:
            cls.createIndexes(ifNotExists=ifNotExists,
                              connection=conn)
        for func in post_funcs:
            func(cls, conn)
        return extra_sql

    @classmethod
    def createTableSQL(cls, createJoinTables=True, createIndexes=True,
                       connection=None):
        conn = connection or cls._connection
        sql, constraints = conn.createTableSQL(cls)
        if createJoinTables:
            join_sql = cls.createJoinTablesSQL(connection=conn)
            if join_sql:
                sql += ';\n' + join_sql
        if createIndexes:
            index_sql = cls.createIndexesSQL(connection=conn)
            if index_sql:
                sql += ';\n' + index_sql
        return sql, constraints

    @classmethod
    def createJoinTables(cls, ifNotExists=False, connection=None):
        conn = connection or cls._connection
        for join in cls._getJoinsToCreate():
            if (ifNotExists and
                    conn.tableExists(join.intermediateTable)):
                continue
            conn._SO_createJoinTable(join)

    @classmethod
    def createJoinTablesSQL(cls, connection=None):
        conn = connection or cls._connection
        sql = []
        for join in cls._getJoinsToCreate():
            sql.append(conn._SO_createJoinTableSQL(join))
        return ';\n'.join(sql)

    @classmethod
    def createIndexes(cls, ifNotExists=False, connection=None):
        conn = connection or cls._connection
        for _index in cls.sqlmeta.indexes:
            if not _index:
                continue
            conn._SO_createIndex(cls, _index)

    @classmethod
    def createIndexesSQL(cls, connection=None):
        conn = connection or cls._connection
        sql = []
        for _index in cls.sqlmeta.indexes:
            if not _index:
                continue
            sql.append(conn.createIndexSQL(cls, _index))
        return ';\n'.join(sql)

    @classmethod
    def _getJoinsToCreate(cls):
        joins = []
        for join in cls.sqlmeta.joins:
            if not join:
                continue
            if not join.hasIntermediateTable() or \
                    not getattr(join, 'createRelatedTable', True):
                continue
            if join.soClass.__name__ > join.otherClass.__name__:
                continue
            joins.append(join)
        return joins

    @classmethod
    def dropJoinTables(cls, ifExists=False, connection=None):
        conn = connection or cls._connection
        for join in cls.sqlmeta.joins:
            if not join:
                continue
            if not join.hasIntermediateTable() or \
                    not getattr(join, 'createRelatedTable', True):
                continue
            if join.soClass.__name__ > join.otherClass.__name__:
                continue
            if ifExists and \
               not conn.tableExists(join.intermediateTable):
                continue
            conn._SO_dropJoinTable(join)

    @classmethod
    def clearTable(cls, connection=None, clearJoinTables=True):
        # 3-03 @@: Maybe this should check the cache... but it's
        # kind of crude anyway, so...
        conn = connection or cls._connection
        conn.clearTable(cls.sqlmeta.table)
        if clearJoinTables:
            for join in cls._getJoinsToCreate():
                conn.clearTable(join.intermediateTable)

    def destroySelf(self):
        post_funcs = []
        self.sqlmeta.send(events.RowDestroySignal, self, post_funcs)
        # Kills this object.  Kills it dead!

        klass = self.__class__

        # Free related joins on the base class
        for join in klass.sqlmeta.joins:
            if isinstance(join, joins.SORelatedJoin):
                q = "DELETE FROM %s WHERE %s=%d" % (join.intermediateTable,
                                                    join.joinColumn, self.id)
                self._connection.query(q)

        depends = []
        depends = self._SO_depends()
        for k in depends:
            # Free related joins
            for join in k.sqlmeta.joins:
                if isinstance(join, joins.SORelatedJoin) and \
                        join.otherClassName == klass.__name__:
                    q = "DELETE FROM %s WHERE %s=%d" % (join.intermediateTable,
                                                        join.otherColumn,
                                                        self.id)
                    self._connection.query(q)

            cols = findDependantColumns(klass.__name__, k)

            # Don't confuse the rest of the process
            if len(cols) == 0:
                continue

            query = []
            delete = setnull = restrict = False
            for _col in cols:
                if _col.cascade is False:
                    # Found a restriction
                    restrict = True
                query.append(getattr(k.q, _col.name) == self.id)
                if _col.cascade == 'null':
                    setnull = _col.name
                elif _col.cascade:
                    delete = True
            assert delete or setnull or restrict, (
                "Class %s depends on %s accoriding to "
                "findDependantColumns, but this seems inaccurate"
                % (k, klass))
            query = sqlbuilder.OR(*query)
            results = k.select(query, connection=self._connection)
            if restrict:
                if results.count():
                    # Restrictions only apply if there are
                    # matching records on the related table
                    raise SQLObjectIntegrityError(
                        "Tried to delete %s::%s but "
                        "table %s has a restriction against it" %
                        (klass.__name__, self.id, k.__name__))
            else:
                for row in results:
                    if delete:
                        row.destroySelf()
                    else:
                        row.set(**{setnull: None})

        self.sqlmeta._obsolete = True
        self._connection._SO_delete(self)
        self._connection.cache.expire(self.id, self.__class__)

        for func in post_funcs:
            func(self)

        post_funcs = []
        self.sqlmeta.send(events.RowDestroyedSignal, self, post_funcs)
        for func in post_funcs:
            func(self)

    @classmethod
    def delete(cls, id, connection=None):
        obj = cls.get(id, connection=connection)
        obj.destroySelf()

    @classmethod
    def deleteMany(cls, where=NoDefault, connection=None):
        conn = connection or cls._connection
        conn.query(conn.sqlrepr(sqlbuilder.Delete(cls.sqlmeta.table, where)))

    @classmethod
    def deleteBy(cls, connection=None, **kw):
        conn = connection or cls._connection
        conn.query(conn.sqlrepr(sqlbuilder.Delete(
            cls.sqlmeta.table, conn._SO_columnClause(cls, kw))))

    def __repr__(self):
        if not hasattr(self, 'id'):
            # Object initialization not finished.  No attributes can be read.
            return '<%s (not initialized)>' % self.__class__.__name__
        return '<%s %r %s>' \
               % (self.__class__.__name__,
                  self.id,
                  ' '.join(
                      ['%s=%s' % (name, repr(value))
                       for name, value in self._reprItems()]))

    def __sqlrepr__(self, db):
        return str(self.id)

    @classmethod
    def sqlrepr(cls, value, connection=None):
        return (connection or cls._connection).sqlrepr(value)

    @classmethod
    def coerceID(cls, value):
        if isinstance(value, cls):
            return value.id
        else:
            return cls.sqlmeta.idType(value)

    def _reprItems(self):
        items = []
        for _col in self.sqlmeta.columnList:
            value = getattr(self, _col.name)
            r = repr(value)
            if len(r) > 20:
                value = r[:17] + "..." + r[-1]
            items.append((_col.name, value))
        return items

    @classmethod
    def setConnection(cls, value):
        if isinstance(value, string_type):
            value = dbconnection.connectionForURI(value)
        cls._connection = value

    def tablesUsedImmediate(self):
        return [self.__class__.q]

    # hash implementation

    def __hash__(self):
        # We hash on class name and id, since that should be
        # unique
        return hash((self.__class__.__name__, self.id))

    # Comparison

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            if self.id == other.id:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return NotImplemented

    def __le__(self, other):
        return NotImplemented

    def __gt__(self, other):
        return NotImplemented

    def __ge__(self, other):
        return NotImplemented

    # (De)serialization (pickle, etc.)

    def __getstate__(self):
        if self.sqlmeta._perConnection:
            from pickle import PicklingError
            raise PicklingError(
                'Cannot pickle an SQLObject instance '
                'that has a per-instance connection')
        if self.sqlmeta.lazyUpdate and self._SO_createValues:
            self.syncUpdate()
        d = self.__dict__.copy()
        del d['sqlmeta']
        del d['_SO_validatorState']
        del d['_SO_writeLock']
        del d['_SO_createValues']
        return d

    def __setstate__(self, d):
        self.__init__(_SO_fetch_no_create=1)
        self._SO_validatorState = sqlbuilder.SQLObjectState(self)
        self._SO_writeLock = threading.Lock()
        self._SO_createValues = {}
        self.__dict__.update(d)
        cls = self.__class__
        cache = self._connection.cache
        if cache.tryGet(self.id, cls) is not None:
            raise ValueError(
                "Cannot unpickle %s row with id=%s - "
                "a different instance with the id already exists "
                "in the cache" % (cls.__name__, self.id))
        cache.created(self.id, cls, self)


def setterName(name):
    return '_set_%s' % name


def rawSetterName(name):
    return '_SO_set_%s' % name


def getterName(name):
    return '_get_%s' % name


def rawGetterName(name):
    return '_SO_get_%s' % name


def instanceName(name):
    return '_SO_val_%s' % name


########################################
# Utility functions (for external consumption)
########################################

def getID(obj, refColumn=None):
    if isinstance(obj, SQLObject):
        return getattr(obj, refColumn or 'id')
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, long):
        return int(obj)
    elif isinstance(obj, str):
        try:
            return int(obj)
        except ValueError:
            return obj
    elif obj is None:
        return None


def getObject(obj, klass):
    if isinstance(obj, int):
        return klass(obj)
    elif isinstance(obj, long):
        return klass(int(obj))
    elif isinstance(obj, str):
        return klass(int(obj))
    elif obj is None:
        return None
    else:
        return obj

__all__ = [
    'NoDefault', 'SQLObject', 'SQLObjectIntegrityError', 'SQLObjectNotFound',
    'getID', 'getObject', 'sqlhub', 'sqlmeta',
]
