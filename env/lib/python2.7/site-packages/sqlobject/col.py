"""
Col -- SQLObject columns

Note that each column object is named BlahBlahCol, and these are used
in class definitions.  But there's also a corresponding SOBlahBlahCol
object, which is used in SQLObject *classes*.

An explanation: when a SQLObject subclass is created, the metaclass
looks through your class definition for any subclasses of Col.  It
collects them together, and indexes them to do all the database stuff
you like, like the magic attributes and whatnot.  It then asks the Col
object to create an SOCol object (usually a subclass, actually).  The
SOCol object contains all the interesting logic, as well as a record
of the attribute name you used and the class it is bound to (set by
the metaclass).

So, in summary: Col objects are what you define, but SOCol objects
are what gets used.
"""

from array import array
from decimal import Decimal
from itertools import count
import json
try:
    import cPickle as pickle
except ImportError:
    import pickle
import time
from uuid import UUID
import weakref

from formencode import compound, validators
from .classregistry import findClass
# Sadly the name "constraints" conflicts with many of the function
# arguments in this module, so we rename it:
from . import constraints as constrs
from . import converters
from . import sqlbuilder
from .styles import capword
from .compat import PY2, string_type, unicode_type, buffer_type

import datetime
datetime_available = True

try:
    from mx import DateTime
except ImportError:
    try:
        # old version of mxDateTime,
        # or Zope's Version if we're running with Zope
        import DateTime
    except ImportError:
        mxdatetime_available = False
    else:
        mxdatetime_available = True
else:
    mxdatetime_available = True

DATETIME_IMPLEMENTATION = "datetime"
MXDATETIME_IMPLEMENTATION = "mxDateTime"

if mxdatetime_available:
    if hasattr(DateTime, "Time"):
        DateTimeType = type(DateTime.now())
        TimeType = type(DateTime.Time())
    else:  # Zope
        DateTimeType = type(DateTime.DateTime())
        TimeType = type(DateTime.DateTime.Time(DateTime.DateTime()))

__all__ = ["datetime_available", "mxdatetime_available",
           "default_datetime_implementation", "DATETIME_IMPLEMENTATION"]

if mxdatetime_available:
    __all__.append("MXDATETIME_IMPLEMENTATION")

default_datetime_implementation = DATETIME_IMPLEMENTATION

if not PY2:
    # alias for python 3 compatibility
    long = int
    # This is to satisfy flake8 under python 3
    unicode = str

NoDefault = sqlbuilder.NoDefault


def use_microseconds(use=True):
    if use:
        SODateTimeCol.datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
        SOTimeCol.timeFormat = '%H:%M:%S.%f'
        dt_types = [(datetime.datetime, converters.DateTimeConverterMS),
                    (datetime.time, converters.TimeConverterMS)]
    else:
        SODateTimeCol.datetimeFormat = '%Y-%m-%d %H:%M:%S'
        SOTimeCol.timeFormat = '%H:%M:%S'
        dt_types = [(datetime.datetime, converters.DateTimeConverter),
                    (datetime.time, converters.TimeConverter)]
    for dt_type, converter in dt_types:
        converters.registerConverter(dt_type, converter)


__all__.append("use_microseconds")


creationOrder = count()

########################################
# Columns
########################################

# Col is essentially a column definition, it doesn't have much logic to it.


class SOCol(object):

    def __init__(self,
                 name,
                 soClass,
                 creationOrder,
                 dbName=None,
                 default=NoDefault,
                 defaultSQL=None,
                 foreignKey=None,
                 alternateID=False,
                 alternateMethodName=None,
                 constraints=None,
                 notNull=NoDefault,
                 notNone=NoDefault,
                 unique=NoDefault,
                 sqlType=None,
                 columnDef=None,
                 validator=None,
                 validator2=None,
                 immutable=False,
                 cascade=None,
                 lazy=False,
                 noCache=False,
                 forceDBName=False,
                 title=None,
                 tags=[],
                 origName=None,
                 dbEncoding=None,
                 extra_vars=None):

        super(SOCol, self).__init__()

        # This isn't strictly true, since we *could* use backquotes or
        # " or something (database-specific) around column names, but
        # why would anyone *want* to use a name like that?
        # @@: I suppose we could actually add backquotes to the
        # dbName if we needed to...
        if not forceDBName:
            assert sqlbuilder.sqlIdentifier(name), (
                'Name must be SQL-safe '
                '(letters, numbers, underscores): %s (or use forceDBName=True)'
                % repr(name))
        assert name != 'id', (
            'The column name "id" is reserved for SQLObject use '
            '(and is implicitly created).')
        assert name, "You must provide a name for all columns"

        self.columnDef = columnDef
        self.creationOrder = creationOrder

        self.immutable = immutable

        # cascade can be one of:
        # None: no constraint is generated
        # True: a CASCADE constraint is generated
        # False: a RESTRICT constraint is generated
        # 'null': a SET NULL trigger is generated
        if isinstance(cascade, str):
            assert cascade == 'null', (
                "The only string value allowed for cascade is 'null' "
                "(you gave: %r)" % cascade)
        self.cascade = cascade

        if not isinstance(constraints, (list, tuple)):
            constraints = [constraints]
        self.constraints = self.autoConstraints() + constraints

        self.notNone = False
        if notNull is not NoDefault:
            self.notNone = notNull
            assert notNone is NoDefault or (not notNone) == (not notNull), (
                "The notNull and notNone arguments are aliases, "
                "and must not conflict.  "
                "You gave notNull=%r, notNone=%r" % (notNull, notNone))
        elif notNone is not NoDefault:
            self.notNone = notNone
        if self.notNone:
            self.constraints = [constrs.notNull] + self.constraints

        self.name = name
        self.soClass = soClass
        self._default = default
        self.defaultSQL = defaultSQL
        self.customSQLType = sqlType

        # deal with foreign keys
        self.foreignKey = foreignKey
        if self.foreignKey:
            if origName is not None:
                idname = soClass.sqlmeta.style.instanceAttrToIDAttr(origName)
            else:
                idname = soClass.sqlmeta.style.instanceAttrToIDAttr(name)
            if self.name != idname:
                self.foreignName = self.name
                self.name = idname
            else:
                self.foreignName = soClass.sqlmeta.style.\
                    instanceIDAttrToAttr(self.name)
        else:
            self.foreignName = None

        # if they don't give us a specific database name for
        # the column, we separate the mixedCase into mixed_case
        # and assume that.
        if dbName is None:
            self.dbName = soClass.sqlmeta.style.pythonAttrToDBColumn(self.name)
        else:
            self.dbName = dbName

        # alternateID means that this is a unique column that
        # can be used to identify rows
        self.alternateID = alternateID

        if unique is NoDefault:
            self.unique = alternateID
        else:
            self.unique = unique
        if self.unique and alternateMethodName is None:
            self.alternateMethodName = 'by' + capword(self.name)
        else:
            self.alternateMethodName = alternateMethodName

        _validators = self.createValidators()
        if validator:
            _validators.append(validator)
        if validator2:
            _validators.insert(0, validator2)
        _vlen = len(_validators)
        if _vlen:
            for _validator in _validators:
                _validator.soCol = weakref.proxy(self)
        if _vlen == 0:
            self.validator = None  # Set sef.{from,to}_python
        elif _vlen == 1:
            self.validator = _validators[0]
        elif _vlen > 1:
            self.validator = compound.All.join(
                _validators[0], *_validators[1:])
        self.noCache = noCache
        self.lazy = lazy
        # this is in case of ForeignKey, where we rename the column
        # and append an ID
        self.origName = origName or name
        self.title = title
        self.tags = tags
        self.dbEncoding = dbEncoding

        if extra_vars:
            for name, value in extra_vars.items():
                setattr(self, name, value)

    def _set_validator(self, value):
        self._validator = value
        if self._validator:
            self.to_python = self._validator.to_python
            self.from_python = self._validator.from_python
        else:
            self.to_python = None
            self.from_python = None

    def _get_validator(self):
        return self._validator

    validator = property(_get_validator, _set_validator)

    def createValidators(self):
        """Create a list of validators for the column."""
        return []

    def autoConstraints(self):
        return []

    def _get_default(self):
        # A default can be a callback or a plain value,
        # here we resolve the callback
        if self._default is NoDefault:
            return NoDefault
        elif hasattr(self._default, '__sqlrepr__'):
            return self._default
        elif callable(self._default):
            return self._default()
        else:
            return self._default
    default = property(_get_default, None, None)

    def _get_joinName(self):
        return self.soClass.sqlmeta.style.instanceIDAttrToAttr(self.name)
    joinName = property(_get_joinName, None, None)

    def __repr__(self):
        r = '<%s %s' % (self.__class__.__name__, self.name)
        if self.default is not NoDefault:
            r += ' default=%s' % repr(self.default)
        if self.foreignKey:
            r += ' connected to %s' % self.foreignKey
        if self.alternateID:
            r += ' alternate ID'
        if self.notNone:
            r += ' not null'
        return r + '>'

    def createSQL(self):
        return ' '.join([self._sqlType()] + self._extraSQL())

    def _extraSQL(self):
        result = []
        if self.notNone or self.alternateID:
            result.append('NOT NULL')
        if self.unique or self.alternateID:
            result.append('UNIQUE')
        if self.defaultSQL is not None:
            result.append("DEFAULT %s" % self.defaultSQL)
        return result

    def _sqlType(self):
        if self.customSQLType is None:
            raise ValueError("Col %s (%s) cannot be used for automatic "
                             "schema creation (too abstract)" %
                             (self.name, self.__class__))
        else:
            return self.customSQLType

    def _mysqlType(self):
        return self._sqlType()

    def _postgresType(self):
        return self._sqlType()

    def _sqliteType(self):
        # SQLite is naturally typeless, so as a fallback it uses
        # no type.
        try:
            return self._sqlType()
        except ValueError:
            return ''

    def _sybaseType(self):
        return self._sqlType()

    def _mssqlType(self):
        return self._sqlType()

    def _firebirdType(self):
        return self._sqlType()

    def _maxdbType(self):
        return self._sqlType()

    def mysqlCreateSQL(self, connection=None):
        self.connection = connection
        return ' '.join([self.dbName, self._mysqlType()] + self._extraSQL())

    def postgresCreateSQL(self):
        return ' '.join([self.dbName, self._postgresType()] + self._extraSQL())

    def sqliteCreateSQL(self):
        return ' '.join([self.dbName, self._sqliteType()] + self._extraSQL())

    def sybaseCreateSQL(self):
        return ' '.join([self.dbName, self._sybaseType()] + self._extraSQL())

    def mssqlCreateSQL(self, connection=None):
        self.connection = connection
        return ' '.join([self.dbName, self._mssqlType()] + self._extraSQL())

    def firebirdCreateSQL(self):
        # Ian Sparks pointed out that fb is picky about the order
        # of the NOT NULL clause in a create statement.  So, we handle
        # them differently for Enum columns.
        if not isinstance(self, SOEnumCol):
            return ' '.join(
                [self.dbName, self._firebirdType()] + self._extraSQL())
        else:
            return ' '.join(
                [self.dbName] + [self._firebirdType()[0]] +
                self._extraSQL() + [self._firebirdType()[1]])

    def maxdbCreateSQL(self):
        return ' '.join([self.dbName, self._maxdbType()] + self._extraSQL())

    def __get__(self, obj, type=None):
        if obj is None:
            # class attribute, return the descriptor itself
            return self
        if obj.sqlmeta._obsolete:
            raise RuntimeError('The object <%s %s> is obsolete' % (
                obj.__class__.__name__, obj.id))
        if obj.sqlmeta.cacheColumns:
            columns = obj.sqlmeta._columnCache
            if columns is None:
                obj.sqlmeta.loadValues()
            try:
                return columns[name]  # noqa
            except KeyError:
                return obj.sqlmeta.loadColumn(self)
        else:
            return obj.sqlmeta.loadColumn(self)

    def __set__(self, obj, value):
        if self.immutable:
            raise AttributeError("The column %s.%s is immutable" %
                                 (obj.__class__.__name__,
                                  self.name))
        obj.sqlmeta.setColumn(self, value)

    def __delete__(self, obj):
        raise AttributeError("I can't be deleted from %r" % obj)

    def getDbEncoding(self, state, default='utf-8'):
        if self.dbEncoding:
            return self.dbEncoding
        dbEncoding = state.soObject.sqlmeta.dbEncoding
        if dbEncoding:
            return dbEncoding
        try:
            connection = state.connection or state.soObject._connection
        except AttributeError:
            dbEncoding = None
        else:
            dbEncoding = getattr(connection, "dbEncoding", None)
        if not dbEncoding:
            dbEncoding = default
        return dbEncoding


class Col(object):

    baseClass = SOCol

    def __init__(self, name=None, **kw):
        super(Col, self).__init__()
        self.__dict__['_name'] = name
        self.__dict__['_kw'] = kw
        self.__dict__['creationOrder'] = next(creationOrder)
        self.__dict__['_extra_vars'] = {}

    def _set_name(self, value):
        assert self._name is None or self._name == value, (
            "You cannot change a name after it has already been set "
            "(from %s to %s)" % (self.name, value))
        self.__dict__['_name'] = value

    def _get_name(self):
        return self._name

    name = property(_get_name, _set_name)

    def withClass(self, soClass):
        return self.baseClass(soClass=soClass, name=self._name,
                              creationOrder=self.creationOrder,
                              columnDef=self,
                              extra_vars=self._extra_vars,
                              **self._kw)

    def __setattr__(self, var, value):
        if var == 'name':
            super(Col, self).__setattr__(var, value)
            return
        self._extra_vars[var] = value

    def __repr__(self):
        return '<%s %s %s>' % (
            self.__class__.__name__, hex(abs(id(self)))[2:],
            self._name or '(unnamed)')


class SOValidator(validators.Validator):
    def getDbEncoding(self, state, default='utf-8'):
        try:
            return self.dbEncoding
        except AttributeError:
            return self.soCol.getDbEncoding(state, default=default)


class SOStringLikeCol(SOCol):
    """A common ancestor for SOStringCol and SOUnicodeCol"""
    def __init__(self, **kw):
        self.length = kw.pop('length', None)
        self.varchar = kw.pop('varchar', 'auto')
        self.char_binary = kw.pop('char_binary', None)  # A hack for MySQL
        if not self.length:
            assert self.varchar == 'auto' or not self.varchar, \
                "Without a length strings are treated as TEXT, not varchar"
            self.varchar = False
        elif self.varchar == 'auto':
            self.varchar = True

        super(SOStringLikeCol, self).__init__(**kw)

    def autoConstraints(self):
        constraints = [constrs.isString]
        if self.length is not None:
            constraints += [constrs.MaxLength(self.length)]
        return constraints

    def _sqlType(self):
        if self.customSQLType is not None:
            return self.customSQLType
        if not self.length:
            return 'TEXT'
        elif self.varchar:
            return 'VARCHAR(%i)' % self.length
        else:
            return 'CHAR(%i)' % self.length

    def _check_case_sensitive(self, db):
        if self.char_binary:
            raise ValueError("%s does not support "
                             "binary character columns" % db)

    def _mysqlType(self):
        type = self._sqlType()
        if self.char_binary:
            type += " BINARY"
        return type

    def _postgresType(self):
        self._check_case_sensitive("PostgreSQL")
        return super(SOStringLikeCol, self)._postgresType()

    def _sqliteType(self):
        self._check_case_sensitive("SQLite")
        return super(SOStringLikeCol, self)._sqliteType()

    def _sybaseType(self):
        self._check_case_sensitive("SYBASE")
        type = self._sqlType()
        return type

    def _mssqlType(self):
        if self.customSQLType is not None:
            return self.customSQLType
        if not self.length:
            if self.connection and self.connection.can_use_max_types():
                type = 'VARCHAR(MAX)'
            else:
                type = 'VARCHAR(4000)'
        elif self.varchar:
            type = 'VARCHAR(%i)' % self.length
        else:
            type = 'CHAR(%i)' % self.length
        return type

    def _firebirdType(self):
        self._check_case_sensitive("FireBird")
        if not self.length:
            return 'BLOB SUB_TYPE TEXT'
        else:
            return self._sqlType()

    def _maxdbType(self):
        self._check_case_sensitive("SAP DB/MaxDB")
        if not self.length:
            return 'LONG ASCII'
        else:
            return self._sqlType()


class StringValidator(SOValidator):

    def to_python(self, value, state):
        if value is None:
            return None
        try:
            connection = state.connection or state.soObject._connection
            binaryType = connection._binaryType
            dbName = connection.dbName
        except AttributeError:
            binaryType = type(None)  # Just a simple workaround
        dbEncoding = self.getDbEncoding(state, default='ascii')
        if isinstance(value, unicode_type):
            if PY2:
                return value.encode(dbEncoding)
            return value
        if self.dataType and isinstance(value, self.dataType):
            return value
        if isinstance(value,
                      (str, bytes, buffer_type, binaryType,
                       sqlbuilder.SQLExpression)):
            return value
        if hasattr(value, '__unicode__'):
            return unicode(value).encode(dbEncoding)
        if dbName == 'mysql':
            if isinstance(value, bytearray):
                if PY2:
                    return bytes(value)
                else:
                    return value.decode(dbEncoding, errors='surrogateescape')
            if not PY2 and isinstance(value, bytes):
                return value.decode('ascii', errors='surrogateescape')
        raise validators.Invalid(
            "expected a str in the StringCol '%s', got %s %r instead" % (
                self.name, type(value), value), value, state)

    from_python = to_python


class SOStringCol(SOStringLikeCol):

    def createValidators(self, dataType=None):
        return [StringValidator(name=self.name, dataType=dataType)] + \
            super(SOStringCol, self).createValidators()


class StringCol(Col):
    baseClass = SOStringCol


class NQuoted(sqlbuilder.SQLExpression):
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __sqlrepr__(self, db):
        assert db == 'mssql'
        return "N" + sqlbuilder.sqlrepr(self.value, db)


class UnicodeStringValidator(SOValidator):

    def to_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, (unicode_type, sqlbuilder.SQLExpression)):
            return value
        if isinstance(value, str):
            return value.decode(self.getDbEncoding(state))
        if isinstance(value, array):  # MySQL
            return value.tostring().decode(self.getDbEncoding(state))
        if hasattr(value, '__unicode__'):
            return unicode(value)
        raise validators.Invalid(
            "expected a str or a unicode in the UnicodeCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)

    def from_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, (str, sqlbuilder.SQLExpression)):
            return value
        if isinstance(value, unicode_type):
            try:
                connection = state.connection or state.soObject._connection
            except AttributeError:
                pass
            else:
                if connection.dbName == 'mssql':
                    if PY2:
                        value = value.encode(self.getDbEncoding(state))
                    return NQuoted(value)
            return value.encode(self.getDbEncoding(state))
        if hasattr(value, '__unicode__'):
            return unicode(value).encode(self.getDbEncoding(state))
        raise validators.Invalid(
            "expected a str or a unicode in the UnicodeCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)


class SOUnicodeCol(SOStringLikeCol):
    def _mssqlType(self):
        if self.customSQLType is not None:
            return self.customSQLType
        return 'N' + super(SOUnicodeCol, self)._mssqlType()

    def createValidators(self):
        return [UnicodeStringValidator(name=self.name)] + \
            super(SOUnicodeCol, self).createValidators()


class UnicodeCol(Col):
    baseClass = SOUnicodeCol


class IntValidator(SOValidator):

    def to_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, (int, long, sqlbuilder.SQLExpression)):
            return value
        for converter, attr_name in (int, '__int__'), (long, '__long__'):
            if hasattr(value, attr_name):
                try:
                    return converter(value)
                except Exception:
                    break
        raise validators.Invalid(
            "expected an int in the IntCol '%s', got %s %r instead" % (
                self.name, type(value), value), value, state)

    from_python = to_python


class SOIntCol(SOCol):
    # 3-03 @@: support precision, maybe max and min directly
    def __init__(self, **kw):
        self.length = kw.pop('length', None)
        self.unsigned = bool(kw.pop('unsigned', None))
        self.zerofill = bool(kw.pop('zerofill', None))
        SOCol.__init__(self, **kw)

    def autoConstraints(self):
        return [constrs.isInt]

    def createValidators(self):
        return [IntValidator(name=self.name)] + \
            super(SOIntCol, self).createValidators()

    def addSQLAttrs(self, str):
        _ret = str
        if str is None or len(str) < 1:
            return None

        if self.length and self.length >= 1:
            _ret = "%s(%d)" % (_ret, self.length)
        if self.unsigned:
            _ret = _ret + " UNSIGNED"
        if self.zerofill:
            _ret = _ret + " ZEROFILL"
        return _ret

    def _sqlType(self):
        return self.addSQLAttrs("INT")


class IntCol(Col):
    baseClass = SOIntCol


class SOTinyIntCol(SOIntCol):
    def _sqlType(self):
        return self.addSQLAttrs("TINYINT")


class TinyIntCol(Col):
    baseClass = SOTinyIntCol


class SOSmallIntCol(SOIntCol):
    def _sqlType(self):
        return self.addSQLAttrs("SMALLINT")


class SmallIntCol(Col):
    baseClass = SOSmallIntCol


class SOMediumIntCol(SOIntCol):
    def _sqlType(self):
        return self.addSQLAttrs("MEDIUMINT")


class MediumIntCol(Col):
    baseClass = SOMediumIntCol


class SOBigIntCol(SOIntCol):
    def _sqlType(self):
        return self.addSQLAttrs("BIGINT")


class BigIntCol(Col):
    baseClass = SOBigIntCol


class BoolValidator(SOValidator):

    def to_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, (bool, sqlbuilder.SQLExpression)):
            return value
        if PY2 and hasattr(value, '__nonzero__') \
                or not PY2 and hasattr(value, '__bool__'):
            return bool(value)
        try:
            connection = state.connection or state.soObject._connection
        except AttributeError:
            pass
        else:
            if connection.dbName == 'postgres' and \
                    connection.driver in ('odbc', 'pyodbc', 'pypyodbc') and \
                    isinstance(value, string_type):
                return bool(int(value))
        raise validators.Invalid(
            "expected a bool or an int in the BoolCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)

    from_python = to_python


class SOBoolCol(SOCol):
    def autoConstraints(self):
        return [constrs.isBool]

    def createValidators(self):
        return [BoolValidator(name=self.name)] + \
            super(SOBoolCol, self).createValidators()

    def _postgresType(self):
        return 'BOOL'

    def _mysqlType(self):
        return "BOOL"

    def _sybaseType(self):
        return "BIT"

    def _mssqlType(self):
        return "BIT"

    def _firebirdType(self):
        return 'INT'

    def _maxdbType(self):
        return "BOOLEAN"

    def _sqliteType(self):
        return "BOOLEAN"


class BoolCol(Col):
    baseClass = SOBoolCol


class FloatValidator(SOValidator):

    def to_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, (float, int, long, sqlbuilder.SQLExpression)):
            return value
        for converter, attr_name in (
                (float, '__float__'), (int, '__int__'), (long, '__long__')):
            if hasattr(value, attr_name):
                try:
                    return converter(value)
                except Exception:
                    break
        raise validators.Invalid(
            "expected a float in the FloatCol '%s', got %s %r instead" % (
                self.name, type(value), value), value, state)

    from_python = to_python


class SOFloatCol(SOCol):
    # 3-03 @@: support precision (e.g., DECIMAL)

    def autoConstraints(self):
        return [constrs.isFloat]

    def createValidators(self):
        return [FloatValidator(name=self.name)] + \
            super(SOFloatCol, self).createValidators()

    def _sqlType(self):
        return 'FLOAT'

    def _mysqlType(self):
        return "DOUBLE PRECISION"


class FloatCol(Col):
    baseClass = SOFloatCol


class SOKeyCol(SOCol):
    key_type = {int: "INT", str: "TEXT"}

    # 3-03 @@: this should have a simplified constructor
    # Should provide foreign key information for other DBs.

    def __init__(self, **kw):
        self.refColumn = kw.pop('refColumn', None)
        super(SOKeyCol, self).__init__(**kw)

    def _idType(self):
        return self.soClass.sqlmeta.idType

    def _sqlType(self):
        return self.key_type[self._idType()]

    def _sybaseType(self):
        key_type = {int: "NUMERIC(18,0)", str: "TEXT"}
        return key_type[self._idType()]

    def _mssqlType(self):
        key_type = {int: "INT", str: "TEXT"}
        return key_type[self._idType()]

    def _firebirdType(self):
        key_type = {int: "INT", str: "VARCHAR(255)"}
        return key_type[self._idType()]


class KeyCol(Col):

    baseClass = SOKeyCol


class ForeignKeyValidator(SOValidator):

    def __init__(self, *args, **kw):
        super(ForeignKeyValidator, self).__init__(*args, **kw)
        self.fkIDType = None

    def from_python(self, value, state):
        if value is None:
            return None
        # Avoid importing the main module
        # to get the SQLObject class for isinstance
        if hasattr(value, 'sqlmeta'):
            return value
        if self.fkIDType is None:
            otherTable = findClass(self.soCol.foreignKey,
                                   self.soCol.soClass.sqlmeta.registry)
            self.fkIDType = otherTable.sqlmeta.idType
        try:
            value = self.fkIDType(value)
            return value
        except (ValueError, TypeError):
            pass
        raise validators.Invalid("expected a %r for the ForeignKey '%s', "
                                 "got %s %r instead" %
                                 (self.fkIDType, self.name,
                                  type(value), value), value, state)


class SOForeignKey(SOKeyCol):

    def __init__(self, **kw):
        foreignKey = kw['foreignKey']
        style = kw['soClass'].sqlmeta.style
        if kw.get('name'):
            kw['origName'] = kw['name']
            kw['name'] = style.instanceAttrToIDAttr(kw['name'])
        else:
            kw['name'] = style.instanceAttrToIDAttr(
                style.pythonClassToAttr(foreignKey))
        super(SOForeignKey, self).__init__(**kw)

    def createValidators(self):
        return [ForeignKeyValidator(name=self.name)] + \
            super(SOForeignKey, self).createValidators()

    def _idType(self):
        other = findClass(self.foreignKey, self.soClass.sqlmeta.registry)
        return other.sqlmeta.idType

    def sqliteCreateSQL(self):
        sql = SOKeyCol.sqliteCreateSQL(self)
        other = findClass(self.foreignKey, self.soClass.sqlmeta.registry)
        tName = other.sqlmeta.table
        idName = self.refColumn or other.sqlmeta.idName
        if self.cascade is not None:
            if self.cascade == 'null':
                action = 'ON DELETE SET NULL'
            elif self.cascade:
                action = 'ON DELETE CASCADE'
            else:
                action = 'ON DELETE RESTRICT'
        else:
            action = ''
        constraint = ('CONSTRAINT %(colName)s_exists '
                      # 'FOREIGN KEY(%(colName)s) '
                      'REFERENCES %(tName)s(%(idName)s) '
                      '%(action)s' %
                      {'tName': tName,
                       'colName': self.dbName,
                       'idName': idName,
                       'action': action})
        sql = ' '.join([sql, constraint])
        return sql

    def postgresCreateSQL(self):
        sql = SOKeyCol.postgresCreateSQL(self)
        return sql

    def postgresCreateReferenceConstraint(self):
        sTName = self.soClass.sqlmeta.table
        other = findClass(self.foreignKey, self.soClass.sqlmeta.registry)
        tName = other.sqlmeta.table
        idName = self.refColumn or other.sqlmeta.idName
        if self.cascade is not None:
            if self.cascade == 'null':
                action = 'ON DELETE SET NULL'
            elif self.cascade:
                action = 'ON DELETE CASCADE'
            else:
                action = 'ON DELETE RESTRICT'
        else:
            action = ''
        constraint = ('ALTER TABLE %(sTName)s '
                      'ADD CONSTRAINT %(colName)s_exists '
                      'FOREIGN KEY (%(colName)s) '
                      'REFERENCES %(tName)s (%(idName)s) '
                      '%(action)s' %
                      {'tName': tName,
                       'colName': self.dbName,
                       'idName': idName,
                       'action': action,
                       'sTName': sTName})
        return constraint

    def mysqlCreateReferenceConstraint(self):
        sTName = self.soClass.sqlmeta.table
        sTLocalName = sTName.split('.')[-1]
        other = findClass(self.foreignKey, self.soClass.sqlmeta.registry)
        tName = other.sqlmeta.table
        idName = self.refColumn or other.sqlmeta.idName
        if self.cascade is not None:
            if self.cascade == 'null':
                action = 'ON DELETE SET NULL'
            elif self.cascade:
                action = 'ON DELETE CASCADE'
            else:
                action = 'ON DELETE RESTRICT'
        else:
            action = ''
        constraint = ('ALTER TABLE %(sTName)s '
                      'ADD CONSTRAINT %(sTLocalName)s_%(colName)s_exists '
                      'FOREIGN KEY (%(colName)s) '
                      'REFERENCES %(tName)s (%(idName)s) '
                      '%(action)s' %
                      {'tName': tName,
                       'colName': self.dbName,
                       'idName': idName,
                       'action': action,
                       'sTName': sTName,
                       'sTLocalName': sTLocalName})
        return constraint

    def mysqlCreateSQL(self, connection=None):
        return SOKeyCol.mysqlCreateSQL(self, connection)

    def sybaseCreateSQL(self):
        sql = SOKeyCol.sybaseCreateSQL(self)
        other = findClass(self.foreignKey, self.soClass.sqlmeta.registry)
        tName = other.sqlmeta.table
        idName = self.refColumn or other.sqlmeta.idName
        reference = ('REFERENCES %(tName)s(%(idName)s) ' %
                     {'tName': tName,
                      'idName': idName})
        sql = ' '.join([sql, reference])
        return sql

    def sybaseCreateReferenceConstraint(self):
        # @@: Code from above should be moved here
        return None

    def mssqlCreateSQL(self, connection=None):
        sql = SOKeyCol.mssqlCreateSQL(self, connection)
        other = findClass(self.foreignKey, self.soClass.sqlmeta.registry)
        tName = other.sqlmeta.table
        idName = self.refColumn or other.sqlmeta.idName
        reference = ('REFERENCES %(tName)s(%(idName)s) ' %
                     {'tName': tName,
                      'idName': idName})
        sql = ' '.join([sql, reference])
        return sql

    def mssqlCreateReferenceConstraint(self):
        # @@: Code from above should be moved here
        return None

    def maxdbCreateSQL(self):
        other = findClass(self.foreignKey, self.soClass.sqlmeta.registry)
        fidName = self.dbName
        # I assume that foreign key name is identical
        # to the id of the reference table
        sql = ' '.join([fidName, self._maxdbType()])
        tName = other.sqlmeta.table
        idName = self.refColumn or other.sqlmeta.idName
        sql = sql + ',' + '\n'
        sql = sql + 'FOREIGN KEY (%s) REFERENCES %s(%s)' % (fidName, tName,
                                                            idName)
        return sql

    def maxdbCreateReferenceConstraint(self):
        # @@: Code from above should be moved here
        return None


class ForeignKey(KeyCol):

    baseClass = SOForeignKey

    def __init__(self, foreignKey=None, **kw):
        super(ForeignKey, self).__init__(foreignKey=foreignKey, **kw)


class EnumValidator(SOValidator):

    def to_python(self, value, state):
        if value in self.enumValues:
            # Only encode on python 2 - on python 3, the database driver
            # will handle this
            if isinstance(value, unicode_type) and PY2:
                dbEncoding = self.getDbEncoding(state)
                value = value.encode(dbEncoding)
            return value
        elif not self.notNone and value is None:
            return None
        raise validators.Invalid(
            "expected a member of %r in the EnumCol '%s', got %r instead" % (
                self.enumValues, self.name, value), value, state)

    from_python = to_python


class SOEnumCol(SOCol):

    def __init__(self, **kw):
        self.enumValues = kw.pop('enumValues', None)
        assert self.enumValues is not None, \
            'You must provide an enumValues keyword argument'
        super(SOEnumCol, self).__init__(**kw)

    def autoConstraints(self):
        return [constrs.isString, constrs.InList(self.enumValues)]

    def createValidators(self):
        return [EnumValidator(name=self.name, enumValues=self.enumValues,
                              notNone=self.notNone)] + \
            super(SOEnumCol, self).createValidators()

    def _mysqlType(self):
        # We need to map None in the enum expression to an appropriate
        # condition on NULL
        if None in self.enumValues:
            return "ENUM(%s)" % ', '.join(
                [sqlbuilder.sqlrepr(v, 'mysql') for v in self.enumValues
                    if v is not None])
        else:
            return "ENUM(%s) NOT NULL" % ', '.join(
                [sqlbuilder.sqlrepr(v, 'mysql') for v in self.enumValues])

    def _postgresType(self):
        length = max(map(self._getlength, self.enumValues))
        enumValues = ', '.join(
            [sqlbuilder.sqlrepr(v, 'postgres') for v in self.enumValues])
        checkConstraint = "CHECK (%s in (%s))" % (self.dbName, enumValues)
        return "VARCHAR(%i) %s" % (length, checkConstraint)

    _sqliteType = _postgresType

    def _sybaseType(self):
        return self._postgresType()

    def _mssqlType(self):
        return self._postgresType()

    def _firebirdType(self):
        length = max(map(self._getlength, self.enumValues))
        enumValues = ', '.join(
            [sqlbuilder.sqlrepr(v, 'firebird') for v in self.enumValues])
        checkConstraint = "CHECK (%s in (%s))" % (self.dbName, enumValues)
        # NB. Return a tuple, not a string here
        return "VARCHAR(%i)" % (length), checkConstraint

    def _maxdbType(self):
        raise TypeError("Enum type is not supported on MAX DB")

    def _getlength(self, obj):
        """
        None counts as 0; everything else uses len()
        """
        if obj is None:
            return 0
        else:
            return len(obj)


class EnumCol(Col):
    baseClass = SOEnumCol


class SetValidator(SOValidator):
    """
    Translates Python tuples into SQL comma-delimited SET strings.
    """

    def to_python(self, value, state):
        if isinstance(value, str):
            return tuple(value.split(","))
        raise validators.Invalid(
            "expected a string in the SetCol '%s', got %s %r instead" % (
                self.name, type(value), value), value, state)

    def from_python(self, value, state):
        if isinstance(value, string_type):
            value = (value,)
        try:
            return ",".join(value)
        except Exception:
            raise validators.Invalid(
                "expected a string or a sequence of strings "
                "in the SetCol '%s', got %s %r instead" % (
                    self.name, type(value), value), value, state)


class SOSetCol(SOCol):
    def __init__(self, **kw):
        self.setValues = kw.pop('setValues', None)
        assert self.setValues is not None, \
            'You must provide a setValues keyword argument'
        super(SOSetCol, self).__init__(**kw)

    def autoConstraints(self):
        return [constrs.isString, constrs.InList(self.setValues)]

    def createValidators(self):
        return [SetValidator(name=self.name, setValues=self.setValues)] + \
            super(SOSetCol, self).createValidators()

    def _mysqlType(self):
        return "SET(%s)" % ', '.join(
            [sqlbuilder.sqlrepr(v, 'mysql') for v in self.setValues])


class SetCol(Col):
    baseClass = SOSetCol


class DateTimeValidator(validators.DateValidator):
    def to_python(self, value, state):
        if value is None:
            return None
        if isinstance(value,
                      (datetime.datetime, datetime.date,
                       datetime.time, sqlbuilder.SQLExpression)):
            return value
        if mxdatetime_available:
            if isinstance(value, DateTimeType):
                # convert mxDateTime instance to datetime
                if (self.format.find("%H") >= 0) or \
                   (self.format.find("%T")) >= 0:
                    return datetime.datetime(value.year, value.month,
                                             value.day,
                                             value.hour, value.minute,
                                             int(value.second))
                else:
                    return datetime.date(value.year, value.month, value.day)
            elif isinstance(value, TimeType):
                # convert mxTime instance to time
                if self.format.find("%d") >= 0:
                    return datetime.timedelta(seconds=value.seconds)
                else:
                    return datetime.time(value.hour, value.minute,
                                         int(value.second))
        try:
            if self.format.find(".%f") >= 0:
                if '.' in value:
                    _value = value.split('.')
                    microseconds = _value[-1]
                    _l = len(microseconds)
                    if _l < 6:
                        _value[-1] = microseconds + '0' * (6 - _l)
                    elif _l > 6:
                        _value[-1] = microseconds[:6]
                    if _l != 6:
                        value = '.'.join(_value)
                else:
                    value += '.0'
            return datetime.datetime.strptime(value, self.format)
        except Exception:
            raise validators.Invalid(
                "expected a date/time string of the '%s' format "
                "in the DateTimeCol '%s', got %s %r instead" % (
                    self.format, self.name, type(value), value), value, state)

    def from_python(self, value, state):
        if value is None:
            return None
        if isinstance(value,
                      (datetime.datetime, datetime.date,
                       datetime.time, sqlbuilder.SQLExpression)):
            return value
        if hasattr(value, "strftime"):
            return value.strftime(self.format)
        raise validators.Invalid(
            "expected a datetime in the DateTimeCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)

if mxdatetime_available:
    class MXDateTimeValidator(validators.DateValidator):
        def to_python(self, value, state):
            if value is None:
                return None
            if isinstance(value,
                          (DateTimeType, TimeType, sqlbuilder.SQLExpression)):
                return value
            if isinstance(value, datetime.datetime):
                return DateTime.DateTime(value.year, value.month, value.day,
                                         value.hour, value.minute,
                                         value.second)
            elif isinstance(value, datetime.date):
                return DateTime.Date(value.year, value.month, value.day)
            elif isinstance(value, datetime.time):
                return DateTime.Time(value.hour, value.minute, value.second)
            elif isinstance(value, datetime.timedelta):
                if value.days:
                    raise validators.Invalid(
                        "the value for the TimeCol '%s' must has days=0, "
                        "it has days=%d" % (self.name, value.days),
                        value, state)
                return DateTime.Time(seconds=value.seconds)
            try:
                if self.format.find(".%f") >= 0:
                    if '.' in value:
                        _value = value.split('.')
                        microseconds = _value[-1]
                        _l = len(microseconds)
                        if _l < 6:
                            _value[-1] = microseconds + '0' * (6 - _l)
                        elif _l > 6:
                            _value[-1] = microseconds[:6]
                        if _l != 6:
                            value = '.'.join(_value)
                    else:
                        value += '.0'
                value = datetime.datetime.strptime(value, self.format)
                return DateTime.DateTime(value.year, value.month, value.day,
                                         value.hour, value.minute,
                                         value.second)
            except Exception:
                raise validators.Invalid(
                    "expected a date/time string of the '%s' format "
                    "in the DateTimeCol '%s', got %s %r instead" % (
                        self.format, self.name, type(value), value),
                    value, state)

        def from_python(self, value, state):
            if value is None:
                return None
            if isinstance(value,
                          (DateTimeType, TimeType, sqlbuilder.SQLExpression)):
                return value
            if hasattr(value, "strftime"):
                return value.strftime(self.format)
            raise validators.Invalid(
                "expected a mxDateTime in the DateTimeCol '%s', "
                "got %s %r instead" % (
                    self.name, type(value), value), value, state)


class SODateTimeCol(SOCol):
    datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, **kw):
        datetimeFormat = kw.pop('datetimeFormat', None)
        if datetimeFormat:
            self.datetimeFormat = datetimeFormat
        super(SODateTimeCol, self).__init__(**kw)

    def createValidators(self):
        _validators = super(SODateTimeCol, self).createValidators()
        if default_datetime_implementation == DATETIME_IMPLEMENTATION:
            validatorClass = DateTimeValidator
        elif default_datetime_implementation == MXDATETIME_IMPLEMENTATION:
            validatorClass = MXDateTimeValidator
        if default_datetime_implementation:
            _validators.insert(0, validatorClass(name=self.name,
                                                 format=self.datetimeFormat))
        return _validators

    def _mysqlType(self):
        if self.connection and self.connection.can_use_microseconds():
            return 'DATETIME(6)'
        else:
            return 'DATETIME'

    def _postgresType(self):
        return 'TIMESTAMP'

    def _sybaseType(self):
        return 'DATETIME'

    def _mssqlType(self):
        if self.connection and self.connection.can_use_microseconds():
            return 'DATETIME2(6)'
        else:
            return 'DATETIME'

    def _sqliteType(self):
        return 'TIMESTAMP'

    def _firebirdType(self):
        return 'TIMESTAMP'

    def _maxdbType(self):
        return 'TIMESTAMP'


class DateTimeCol(Col):
    baseClass = SODateTimeCol

    @staticmethod
    def now():
        if default_datetime_implementation == DATETIME_IMPLEMENTATION:
            return datetime.datetime.now()
        elif default_datetime_implementation == MXDATETIME_IMPLEMENTATION:
            return DateTime.now()
        else:
            assert 0, ("No datetime implementation available "
                       "(DATETIME_IMPLEMENTATION=%r)"
                       % DATETIME_IMPLEMENTATION)


class DateValidator(DateTimeValidator):
    def to_python(self, value, state):
        if isinstance(value, datetime.datetime):
            value = value.date()
        if isinstance(value, (datetime.date, sqlbuilder.SQLExpression)):
            return value
        value = super(DateValidator, self).to_python(value, state)
        if isinstance(value, datetime.datetime):
            value = value.date()
        return value

    from_python = to_python


class SODateCol(SOCol):
    dateFormat = '%Y-%m-%d'

    def __init__(self, **kw):
        dateFormat = kw.pop('dateFormat', None)
        if dateFormat:
            self.dateFormat = dateFormat
        super(SODateCol, self).__init__(**kw)

    def createValidators(self):
        """Create a validator for the column.

        Can be overriden in descendants.

        """
        _validators = super(SODateCol, self).createValidators()
        if default_datetime_implementation == DATETIME_IMPLEMENTATION:
            validatorClass = DateValidator
        elif default_datetime_implementation == MXDATETIME_IMPLEMENTATION:
            validatorClass = MXDateTimeValidator
        if default_datetime_implementation:
            _validators.insert(0, validatorClass(name=self.name,
                                                 format=self.dateFormat))
        return _validators

    def _mysqlType(self):
        return 'DATE'

    def _postgresType(self):
        return 'DATE'

    def _sybaseType(self):
        return self._postgresType()

    def _mssqlType(self):
        """
        SQL Server doesn't have  a DATE data type, to emulate we use a vc(10)
        """
        return 'VARCHAR(10)'

    def _firebirdType(self):
        return 'DATE'

    def _maxdbType(self):
        return 'DATE'

    def _sqliteType(self):
        return 'DATE'


class DateCol(Col):
    baseClass = SODateCol


class TimeValidator(DateTimeValidator):
    def to_python(self, value, state):
        if isinstance(value, (datetime.time, sqlbuilder.SQLExpression)):
            return value
        if isinstance(value, datetime.timedelta):
            if value.days:
                raise validators.Invalid(
                    "the value for the TimeCol '%s' must has days=0, "
                    "it has days=%d" % (self.name, value.days), value, state)
            return datetime.time(*time.gmtime(value.seconds)[3:6])
        value = super(TimeValidator, self).to_python(value, state)
        if isinstance(value, datetime.datetime):
            value = value.time()
        return value

    from_python = to_python


class SOTimeCol(SOCol):
    timeFormat = '%H:%M:%S.%f'

    def __init__(self, **kw):
        timeFormat = kw.pop('timeFormat', None)
        if timeFormat:
            self.timeFormat = timeFormat
        super(SOTimeCol, self).__init__(**kw)

    def createValidators(self):
        _validators = super(SOTimeCol, self).createValidators()
        if default_datetime_implementation == DATETIME_IMPLEMENTATION:
            validatorClass = TimeValidator
        elif default_datetime_implementation == MXDATETIME_IMPLEMENTATION:
            validatorClass = MXDateTimeValidator
        if default_datetime_implementation:
            _validators.insert(0, validatorClass(name=self.name,
                                                 format=self.timeFormat))
        return _validators

    def _mysqlType(self):
        if self.connection and self.connection.can_use_microseconds():
            return 'TIME(6)'
        else:
            return 'TIME'

    def _postgresType(self):
        return 'TIME'

    def _sybaseType(self):
        return 'TIME'

    def _mssqlType(self):
        if self.connection and self.connection.can_use_microseconds():
            return 'TIME(6)'
        else:
            return 'TIME'

    def _sqliteType(self):
        return 'TIME'

    def _firebirdType(self):
        return 'TIME'

    def _maxdbType(self):
        return 'TIME'


class TimeCol(Col):
    baseClass = SOTimeCol


class SOTimestampCol(SODateTimeCol):
    """
    Necessary to support MySQL's use of TIMESTAMP versus DATETIME types
    """

    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = None
        SOCol.__init__(self, **kw)

    def _mysqlType(self):
        if self.connection and self.connection.can_use_microseconds():
            return 'TIMESTAMP(6)'
        else:
            return 'TIMESTAMP'


class TimestampCol(Col):
    baseClass = SOTimestampCol


class TimedeltaValidator(SOValidator):
    def to_python(self, value, state):
        return value

    from_python = to_python


class SOTimedeltaCol(SOCol):
    def _postgresType(self):
        return 'INTERVAL'

    def createValidators(self):
        return [TimedeltaValidator(name=self.name)] + \
            super(SOTimedeltaCol, self).createValidators()


class TimedeltaCol(Col):
    baseClass = SOTimedeltaCol


class DecimalValidator(SOValidator):
    def to_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, (int, long, Decimal, sqlbuilder.SQLExpression)):
            return value
        if isinstance(value, float):
            value = str(value)
        try:
            connection = state.connection or state.soObject._connection
        except AttributeError:
            pass
        else:
            if hasattr(connection, "decimalSeparator"):
                value = value.replace(connection.decimalSeparator, ".")
        try:
            return Decimal(value)
        except Exception:
            raise validators.Invalid(
                "expected a Decimal in the DecimalCol '%s', "
                "got %s %r instead" % (
                    self.name, type(value), value), value, state)

    def from_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, float):
            value = str(value)
        if isinstance(value, string_type):
            try:
                connection = state.connection or state.soObject._connection
            except AttributeError:
                pass
            else:
                if hasattr(connection, "decimalSeparator"):
                    value = value.replace(connection.decimalSeparator, ".")
            try:
                return Decimal(value)
            except Exception:
                raise validators.Invalid(
                    "can not parse Decimal value '%s' "
                    "in the DecimalCol from '%s'" % (
                        value, getattr(state, 'soObject', '(unknown)')),
                    value, state)
        if isinstance(value, (int, long, Decimal, sqlbuilder.SQLExpression)):
            return value
        raise validators.Invalid(
            "expected a Decimal in the DecimalCol '%s', got %s %r instead" % (
                self.name, type(value), value), value, state)


class SODecimalCol(SOCol):

    def __init__(self, **kw):
        self.size = kw.pop('size', NoDefault)
        assert self.size is not NoDefault, \
            "You must give a size argument"
        self.precision = kw.pop('precision', NoDefault)
        assert self.precision is not NoDefault, \
            "You must give a precision argument"
        super(SODecimalCol, self).__init__(**kw)

    def _sqlType(self):
        return 'DECIMAL(%i, %i)' % (self.size, self.precision)

    def createValidators(self):
        return [DecimalValidator(name=self.name)] + \
            super(SODecimalCol, self).createValidators()


class DecimalCol(Col):
    baseClass = SODecimalCol


class SOCurrencyCol(SODecimalCol):

    def __init__(self, **kw):
        pushKey(kw, 'size', 10)
        pushKey(kw, 'precision', 2)
        super(SOCurrencyCol, self).__init__(**kw)


class CurrencyCol(DecimalCol):
    baseClass = SOCurrencyCol


class DecimalStringValidator(DecimalValidator):
    def to_python(self, value, state):
        value = super(DecimalStringValidator, self).to_python(value, state)
        if self.precision and isinstance(value, Decimal):
            assert value < self.max, \
                "Value must be less than %s" % int(self.max)
            value = value.quantize(self.precision)
        return value

    def from_python(self, value, state):
        value = super(DecimalStringValidator, self).from_python(value, state)
        if isinstance(value, Decimal):
            if self.precision:
                assert value < self.max, \
                    "Value must be less than %s" % int(self.max)
                value = value.quantize(self.precision)
            value = value.to_eng_string()
        elif isinstance(value, (int, long)):
            value = str(value)
        return value


class SODecimalStringCol(SOStringCol):
    def __init__(self, **kw):
        self.size = kw.pop('size', NoDefault)
        assert (self.size is not NoDefault) and (self.size >= 0), \
            "You must give a size argument as a positive integer"
        self.precision = kw.pop('precision', NoDefault)
        assert (self.precision is not NoDefault) and (self.precision >= 0), \
            "You must give a precision argument as a positive integer"
        kw['length'] = int(self.size) + int(self.precision)
        self.quantize = kw.pop('quantize', False)
        assert isinstance(self.quantize, bool), \
            "quantize argument must be Boolean True/False"
        super(SODecimalStringCol, self).__init__(**kw)

    def createValidators(self):
        if self.quantize:
            v = DecimalStringValidator(
                name=self.name,
                precision=Decimal(10) ** (-1 * int(self.precision)),
                max=Decimal(10) ** (int(self.size) - int(self.precision)))
        else:
            v = DecimalStringValidator(name=self.name, precision=0)
        return [v] + \
            super(SODecimalStringCol, self).createValidators(dataType=Decimal)


class DecimalStringCol(StringCol):
    baseClass = SODecimalStringCol


class BinaryValidator(SOValidator):
    """
    Validator for binary types.

    We're assuming that the per-database modules provide some form
    of wrapper type for binary conversion.
    """

    _cachedValue = None

    def to_python(self, value, state):
        if value is None:
            return None
        try:
            connection = state.connection or state.soObject._connection
        except AttributeError:
            dbName = None
            binaryType = type(None)  # Just a simple workaround
        else:
            dbName = connection.dbName
            binaryType = connection._binaryType
        if isinstance(value, str):
            if not PY2 and dbName == "mysql":
                value = value.encode('ascii', errors='surrogateescape')
            if dbName == "sqlite":
                if not PY2:
                    value = bytes(value, 'ascii')
                value = connection.module.decode(value)
            return value
        if isinstance(value, bytes):
            return value
        if isinstance(value, (buffer_type, binaryType)):
            cachedValue = self._cachedValue
            if cachedValue and cachedValue[1] == value:
                return cachedValue[0]
            if isinstance(value, array):  # MySQL
                return value.tostring()
            if not PY2 and isinstance(value, memoryview):
                return value.tobytes()
            return str(value)  # buffer => string
        raise validators.Invalid(
            "expected a string in the BLOBCol '%s', got %s %r instead" % (
                self.name, type(value), value), value, state)

    def from_python(self, value, state):
        if value is None:
            return None
        connection = state.connection or state.soObject._connection
        binary = connection.createBinary(value)
        if not PY2 and isinstance(binary, memoryview):
            binary = str(binary.tobytes(), 'ascii')
        self._cachedValue = (value, binary)
        return binary


class SOBLOBCol(SOStringCol):
    def __init__(self, **kw):
        # Change the default from 'auto' to False -
        # this is a (mostly) binary column
        if 'varchar' not in kw:
            kw['varchar'] = False
        super(SOBLOBCol, self).__init__(**kw)

    def createValidators(self):
        return [BinaryValidator(name=self.name)] + \
            super(SOBLOBCol, self).createValidators()

    def _mysqlType(self):
        length = self.length
        varchar = self.varchar
        if length:
            if length >= 2 ** 24:
                return varchar and "LONGTEXT" or "LONGBLOB"
            if length >= 2 ** 16:
                return varchar and "MEDIUMTEXT" or "MEDIUMBLOB"
            if length >= 2 ** 8:
                return varchar and "TEXT" or "BLOB"
        return varchar and "TINYTEXT" or "TINYBLOB"

    def _postgresType(self):
        return 'BYTEA'

    def _mssqlType(self):
        if self.connection and self.connection.can_use_max_types():
            return 'VARBINARY(MAX)'
        else:
            return "IMAGE"


class BLOBCol(StringCol):
    baseClass = SOBLOBCol


class PickleValidator(BinaryValidator):
    """
    Validator for pickle types.  A pickle type is simply a binary type
    with hidden pickling, so that we can simply store any kind of
    stuff in a particular column.

    The support for this relies directly on the support for binary for
    your database.
    """

    def to_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, unicode_type):
            dbEncoding = self.getDbEncoding(state, default='ascii')
            if PY2:
                value = value.encode(dbEncoding)
            else:
                value = value.encode(dbEncoding, errors='surrogateescape')
        if isinstance(value, bytes):
            return pickle.loads(value)
        raise validators.Invalid(
            "expected a pickle string in the PickleCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)

    def from_python(self, value, state):
        if value is None:
            return None
        return pickle.dumps(value, self.pickleProtocol)


class SOPickleCol(SOBLOBCol):

    def __init__(self, **kw):
        self.pickleProtocol = kw.pop('pickleProtocol', pickle.HIGHEST_PROTOCOL)
        super(SOPickleCol, self).__init__(**kw)

    def createValidators(self):
        return [PickleValidator(name=self.name,
                pickleProtocol=self.pickleProtocol)] + \
            super(SOPickleCol, self).createValidators()

    def _mysqlType(self):
        length = self.length
        if length:
            if length >= 2 ** 24:
                return "LONGBLOB"
            if length >= 2 ** 16:
                return "MEDIUMBLOB"
        return "BLOB"


class PickleCol(BLOBCol):
    baseClass = SOPickleCol


class UuidValidator(SOValidator):

    def to_python(self, value, state):
        if value is None:
            return None
        if PY2 and isinstance(value, unicode):
            value = value.encode('ascii')
        if isinstance(value, str):
            return UUID(value)
        if isinstance(value, UUID):
            return value
        raise validators.Invalid(
            "expected string in the UuidCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)

    def from_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, UUID):
            return str(value)
        raise validators.Invalid(
            "expected uuid in the UuidCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)


class SOUuidCol(SOCol):
    def createValidators(self):
        return [UuidValidator(name=self.name)] + \
            super(SOUuidCol, self).createValidators()

    def _sqlType(self):
        return 'VARCHAR(36)'

    def _postgresType(self):
        return 'UUID'


class UuidCol(Col):
    baseClass = SOUuidCol


class JsonbValidator(SOValidator):

    def to_python(self, value, state):
        if isinstance(value, string_type):
            return json.loads(value)
        return value

    def from_python(self, value, state):
        if value is None:
            return json.dumps(None)
        if isinstance(value, (dict, list, unicode, int, long, float, bool)):
            return json.dumps(value)
        raise validators.Invalid(
            "expect one of the following types "
            "(dict, list, unicode, int, long, float, bool) for '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)


class SOJsonbCol(SOCol):
    def createValidators(self):
        return [JsonbValidator(name=self.name)] + \
            super(SOJsonbCol, self).createValidators()

    def _postgresType(self):
        return 'JSONB'


class JsonbCol(Col):
    baseClass = SOJsonbCol


class JSONValidator(StringValidator):

    def to_python(self, value, state):
        if value is None:
            return None
        if isinstance(value, string_type):
            return json.loads(value)
        raise validators.Invalid(
            "expected a JSON str in the JSONCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)

    def from_python(self, value, state):
        if value is None:
            return None
        if isinstance(value,
                      (bool, int, float, long, dict, list, string_type)):
            return json.dumps(value)
        raise validators.Invalid(
            "expected an object suitable for JSON in the JSONCol '%s', "
            "got %s %r instead" % (
                self.name, type(value), value), value, state)


class SOJSONCol(SOStringCol):

    def createValidators(self):
        return [JSONValidator(name=self.name)] + \
            super(SOJSONCol, self).createValidators()


class JSONCol(StringCol):
    baseClass = SOJSONCol


def pushKey(kw, name, value):
    if name not in kw:
        kw[name] = value

all = []
# Use copy() to avoid 'dictionary changed' issues on python 3
for key, value in globals().copy().items():
    if isinstance(value, type) and (issubclass(value, (Col, SOCol))):
        all.append(key)
__all__.extend(all)
del all
