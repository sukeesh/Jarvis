"""
The framework for making database tests.
"""
from __future__ import print_function

import logging
import os
import sys
from pytest import raises, skip
import sqlobject
from sqlobject.col import use_microseconds
import sqlobject.conftest as conftest

if sys.platform[:3] == "win":
    def getcwd():
        return os.getcwd().replace('\\', '/')
else:
    getcwd = os.getcwd

"""
supportsMatrix defines what database backends support what features.
Each feature has a name, if you see a key like '+featureName' then
only the databases listed support the feature.  Conversely,
'-featureName' means all databases *except* the ones listed support
the feature.  The databases are given by their SQLObject string name,
separated by spaces.

The function supports(featureName) returns True or False based on this,
and you can use it like::

    def test_featureX():
        if not supports('featureX'):
            pytest.skip("Doesn't support featureX")
"""
supportsMatrix = {
    '-blobData': 'mssql rdbhost',
    '-decimalColumn': 'mssql',
    '-dropTableCascade': 'sybase mssql mysql',
    '-emptyTable': 'mssql',
    '+exceptions': 'mysql postgres sqlite',
    '-expressionIndex': 'mysql sqlite firebird mssql',
    '-limitSelect': 'mssql',
    '+memorydb': 'sqlite',
    '+rlike': 'mysql postgres sqlite',
    '+schema': 'postgres',
    '-transactions': 'mysql rdbhost',
}


def setupClass(soClasses, force=False):
    """
    Makes sure the classes have a corresponding and correct table.
    This won't recreate the table if it already exists.  It will check
    that the table is properly defined (in case you change your table
    definition).

    You can provide a single class or a list of classes; if a list
    then classes will be created in the order you provide, and
    destroyed in the opposite order.  So if class A depends on class
    B, then do setupClass([B, A]) and B won't be destroyed or cleared
    until after A is destroyed or cleared.

    If force is true, then the database will be recreated no matter
    what.
    """
    global hub
    if not isinstance(soClasses, (list, tuple)):
        soClasses = [soClasses]
    connection = getConnection()
    for soClass in soClasses:
        # This would be an alternate way to register connections:
        # try:
        #    hub
        # except NameError:
        #    hub = sqlobject.dbconnection.ConnectionHub()
        # soClass._connection = hub
        # hub.threadConnection = connection
        # hub.processConnection = connection
        soClass._connection = connection
    installOrClear(soClasses, force=force)
    return soClasses


def speedupSQLiteConnection(connection):
    connection.query("PRAGMA synchronous=OFF")
    connection.query("PRAGMA count_changes=OFF")
    connection.query("PRAGMA journal_mode=MEMORY")
    connection.query("PRAGMA temp_store=MEMORY")

installedDBFilename = os.path.join(getcwd(), 'dbs_data.tmp')

installedDBTracker = sqlobject.connectionForURI(
    'sqlite:///' + installedDBFilename)
speedupSQLiteConnection(installedDBTracker)


def getConnection(**kw):
    name = getConnectionURI()
    conn = sqlobject.connectionForURI(name, **kw)
    if conftest.option.show_sql:
        conn.debug = True
    if conftest.option.show_sql_output:
        conn.debugOutput = True
    if (conn.dbName == 'sqlite') and not conn._memory:
        speedupSQLiteConnection(conn)
    return conn


def getConnectionURI():
    name = conftest.option.Database
    if name in conftest.connectionShortcuts:
        name = conftest.connectionShortcuts[name]
    return name

try:
    connection = getConnection()
except Exception as e:
    # At least this module should be importable...
    # The module was imported during documentation building
    if 'sphinx' not in sys.modules:
        print("Could not open database: %s" % e, file=sys.stderr)
else:
    if (connection.dbName == 'firebird') \
        or (
            (connection.dbName == 'mysql') and
            (
                (os.environ.get('APPVEYOR')) or
                (os.environ.get('TRAVIS'))
            )
    ):
        use_microseconds(False)


class InstalledTestDatabase(sqlobject.SQLObject):
    """
    This table is set up in SQLite (always, regardless of --Database) and
    tracks what tables have been set up in the 'real' database.  This
    way we don't keep recreating the tables over and over when there
    are multiple tests that use a table.
    """

    _connection = installedDBTracker
    table_name = sqlobject.StringCol(notNull=True)
    createSQL = sqlobject.StringCol(notNull=True)
    connectionURI = sqlobject.StringCol(notNull=True)

    @classmethod
    def installOrClear(cls, soClasses, force=False):
        cls.setup()
        reversed = list(soClasses)[:]
        reversed.reverse()
        # If anything needs to be dropped, they all must be dropped
        # But if we're forcing it, then we'll always drop
        if force:
            any_drops = True
        else:
            any_drops = False
        for soClass in reversed:
            table = soClass.sqlmeta.table
            if not soClass._connection.tableExists(table):
                continue
            items = list(cls.selectBy(
                table_name=table,
                connectionURI=soClass._connection.uri()))
            if items:
                instance = items[0]
                sql = instance.createSQL
            else:
                sql = None
            newSQL, constraints = soClass.createTableSQL()
            if sql != newSQL:
                if sql is not None:
                    instance.destroySelf()
                any_drops = True
                break
        for soClass in reversed:
            if soClass._connection.tableExists(soClass.sqlmeta.table):
                if any_drops:
                    cls.drop(soClass)
                else:
                    cls.clear(soClass)
        for soClass in soClasses:
            table = soClass.sqlmeta.table
            if not soClass._connection.tableExists(table):
                cls.install(soClass)

    @classmethod
    def install(cls, soClass):
        """
        Creates the given table in its database.
        """
        sql = getattr(soClass, soClass._connection.dbName + 'Create',
                      None)
        all_extra = []
        if sql:
            soClass._connection.query(sql)
        else:
            sql, extra_sql = soClass.createTableSQL()
            soClass.createTable(applyConstraints=False)
            all_extra.extend(extra_sql)
        cls(table_name=soClass.sqlmeta.table,
            createSQL=sql,
            connectionURI=soClass._connection.uri())
        for extra_sql in all_extra:
            soClass._connection.query(extra_sql)

    @classmethod
    def drop(cls, soClass):
        """
        Drops a the given table from its database
        """
        sql = getattr(soClass, soClass._connection.dbName + 'Drop', None)
        if sql:
            soClass._connection.query(sql)
        else:
            soClass.dropTable()

    @classmethod
    def clear(cls, soClass):
        """
        Removes all the rows from a table.
        """
        soClass.clearTable()

    @classmethod
    def setup(cls):
        """
        This sets up *this* table.
        """
        if not cls._connection.tableExists(cls.sqlmeta.table):
            cls.createTable()

installOrClear = InstalledTestDatabase.installOrClear


class Dummy(object):

    """
    Used for creating fake objects; a really poor 'mock object'.
    """

    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)


def inserts(cls, data, schema=None):
    """
    Creates a bunch of rows.

    You can use it like::

        inserts(Person, [{'fname': 'blah', 'lname': 'doe'}, ...])

    Or::

        inserts(Person, [('blah', 'doe')], schema=
                ['fname', 'lname'])

    If you give a single string for the `schema` then it'll split
    that string to get the list of column names.
    """
    if schema:
        if isinstance(schema, str):
            schema = schema.split()
        keywordData = []
        for item in data:
            itemDict = {}
            for name, value in zip(schema, item):
                itemDict[name] = value
            keywordData.append(itemDict)
        data = keywordData
    results = []
    for args in data:
        results.append(cls(**args))
    return results


def supports(feature):
    dbName = connection.dbName
    support = supportsMatrix.get('+' + feature, None)
    notSupport = supportsMatrix.get('-' + feature, None)
    if support is not None and dbName in support.split():
        return True
    elif support:
        return False
    if notSupport is not None and dbName in notSupport.split():
        return False
    elif notSupport:
        return True
    assert notSupport is not None or support is not None, (
        "The supportMatrix does not list this feature: %r"
        % feature)


# To avoid name clashes:
_inserts = inserts


def setSQLiteConnectionFactory(TableClass, factory):
    from sqlobject.sqlite.sqliteconnection import SQLiteConnection
    conn = TableClass._connection
    TableClass._connection = SQLiteConnection(
        filename=conn.filename,
        name=conn.name, debug=conn.debug, debugOutput=conn.debugOutput,
        cache=conn.cache, style=conn.style, autoCommit=conn.autoCommit,
        debugThreading=conn.debugThreading, registry=conn.registry,
        factory=factory
    )
    speedupSQLiteConnection(TableClass._connection)
    installOrClear([TableClass])


def deprecated_module():
    sqlobject.main.warnings_level = None
    sqlobject.main.exception_level = None


def setup_module(mod):
    # modules with '_old' test backward compatible methods, so they
    # don't get warnings or errors.
    mod_name = str(mod.__name__)
    if mod_name.endswith('/py'):
        mod_name = mod_name[:-3]
    if mod_name.endswith('_old'):
        sqlobject.main.warnings_level = None
        sqlobject.main.exception_level = None
    else:
        sqlobject.main.warnings_level = None
        sqlobject.main.exception_level = 0


def teardown_module(mod=None):
    sqlobject.main.warnings_level = None
    sqlobject.main.exception_level = 0


def setupLogging():
    fmt = '[%(asctime)s] %(name)s %(levelname)s: %(message)s'
    formatter = logging.Formatter(fmt)
    hdlr = logging.StreamHandler(sys.stderr)
    hdlr.setFormatter(formatter)
    hdlr.setLevel(logging.NOTSET)
    logger = logging.getLogger()
    logger.addHandler(hdlr)


def setupCyclicClasses(*classes):
    if not supports('dropTableCascade'):
        skip("dropTableCascade isn't supported")
    conn = getConnection()
    for soClass in classes:
        soClass.setConnection(conn)
        soClass.dropTable(ifExists=True, cascade=True)

    constraints = []
    for soClass in classes:
        constraints += soClass.createTable(ifNotExists=True,
                                           applyConstraints=False)
    for constraint in constraints:
        conn.query(constraint)


__all__ = ['Dummy', 'deprecated_module', 'getConnection', 'getConnectionURI',
           'inserts', 'raises', 'setupClass', 'setupCyclicClasses',
           'setupLogging', 'setup_module', 'supports', 'teardown_module',
           ]
