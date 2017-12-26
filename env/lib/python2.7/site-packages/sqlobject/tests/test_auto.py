from datetime import datetime
from pytest import raises

from sqlobject import KeyCol, MultipleJoin, SQLObject, StringCol, \
    classregistry, sqlmeta
from sqlobject.col import use_microseconds
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# Dynamic column tests
########################################


now = datetime.now


class Person(SQLObject):

    class sqlmeta:
        defaultOrder = 'name'
    name = StringCol(length=100, dbName='name_col')


class Phone(SQLObject):

    class sqlmeta:
        defaultOrder = 'phone'
    phone = StringCol(length=12)


class TestPeople:

    def setup_method(self, meth):
        setupClass(Person)
        setupClass(Phone)
        for n in ['jane', 'tim', 'bob', 'jake']:
            Person(name=n)
        for p in ['555-555-5555', '555-394-2930',
                  '444-382-4854']:
            Phone(phone=p)

    def test_defaultOrder(self):
        assert list(Person.select('all')) == list(
            Person.select('all', orderBy=Person.sqlmeta.defaultOrder))

    def test_dynamicColumn(self):
        nickname = StringCol('nickname', length=10)
        Person.sqlmeta.addColumn(nickname, changeSchema=True)
        Person(name='robert', nickname='bob')
        assert ([p.name for p in Person.select('all')] ==
                ['bob', 'jake', 'jane', 'robert', 'tim'])
        Person.sqlmeta.delColumn(nickname, changeSchema=True)

    def test_dynamicJoin(self):
        col = KeyCol('person', foreignKey='Person')
        Phone.sqlmeta.addColumn(col, changeSchema=True)
        join = MultipleJoin('Phone')
        Person.sqlmeta.addJoin(join)
        for phone in Phone.select('all'):
            if phone.phone.startswith('555'):
                phone.person = Person.selectBy(name='tim')[0]
            else:
                phone.person = Person.selectBy(name='bob')[0]
        _l = [p.phone for p in Person.selectBy(name='tim')[0].phones]
        _l.sort()
        assert _l == ['555-394-2930', '555-555-5555']
        Phone.sqlmeta.delColumn(col, changeSchema=True)
        Person.sqlmeta.delJoin(join)

    def _test_collidingName(self):
        class CollidingName(SQLObject):
            expire = StringCol()

    def test_collidingName(self):
        raises(AssertionError, Person.sqlmeta.addColumn,
               StringCol(name="name"))
        raises(AssertionError, Person.sqlmeta.addColumn,
               StringCol(name="_init"))
        raises(AssertionError, Person.sqlmeta.addColumn,
               StringCol(name="expire"))
        raises(AssertionError, Person.sqlmeta.addColumn,
               StringCol(name="set"))
        raises(AssertionError, self._test_collidingName)


########################################
# Auto class generation
########################################


class TestAuto:

    mysqlCreate = """
    CREATE TABLE IF NOT EXISTS auto_test (
      auto_id INT AUTO_INCREMENT PRIMARY KEY,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT NULL,
      created DATETIME NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
      wannahavefun TINYINT DEFAULT 0 NOT NULL
    )
    """

    postgresCreate = """
    CREATE TABLE auto_test (
      auto_id SERIAL PRIMARY KEY,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created TIMESTAMP NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
      wannahavefun BOOL DEFAULT FALSE NOT NULL
    )
    """

    rdbhostCreate = """
    CREATE TABLE auto_test (
      auto_id SERIAL PRIMARY KEY,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created VARCHAR(40) NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
      wannahavefun BOOL DEFAULT FALSE NOT NULL
    )
    """

    sqliteCreate = """
    CREATE TABLE auto_test (
      auto_id INTEGER PRIMARY KEY AUTOINCREMENT ,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT NULL,
      created DATETIME NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
      wannahavefun INT DEFAULT 0 NOT NULL
    )
    """

    sybaseCreate = """
    CREATE TABLE auto_test (
      auto_id integer,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created DATETIME NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
      wannahavefun BIT default(0) NOT NULL
    )
    """

    mssqlCreate = """
    CREATE TABLE auto_test (
      auto_id int identity(1,1),
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created DATETIME NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
      wannahavefun BIT default(0) NOT NULL
    )
    """

    mysqlDrop = """
    DROP TABLE IF EXISTS auto_test
    """

    postgresDrop = """
    DROP TABLE auto_test
    """

    sqliteDrop = sybaseDrop = mssqlDrop = rdbhostDrop = postgresDrop

    def setup_method(self, meth):
        conn = getConnection()
        dbName = conn.dbName
        creator = getattr(self, dbName + 'Create', None)
        if creator:
            conn.query(creator)

    def teardown_method(self, meth):
        conn = getConnection()
        dbName = conn.dbName
        dropper = getattr(self, dbName + 'Drop', None)
        if dropper:
            try:
                conn.query(dropper)
            except Exception:  # Perhaps we don't have DROP permission
                pass

    def test_classCreate(self):
        class AutoTest(SQLObject):
            _connection = getConnection()

            class sqlmeta(sqlmeta):
                idName = 'auto_id'
                fromDatabase = True
        if AutoTest._connection.dbName == 'mssql':
            use_microseconds(False)
        john = AutoTest(firstName='john',
                        lastName='doe',
                        age=10,
                        created=now(),
                        wannahavefun=False,
                        longField='x' * 1000)
        jane = AutoTest(firstName='jane',
                        lastName='doe',
                        happy='N',
                        created=now(),
                        wannahavefun=True,
                        longField='x' * 1000)
        assert not john.wannahavefun
        assert jane.wannahavefun
        assert john.longField == 'x' * 1000
        assert jane.longField == 'x' * 1000
        del classregistry.registry(
            AutoTest.sqlmeta.registry).classes['AutoTest']

        columns = AutoTest.sqlmeta.columns
        assert columns["lastName"].dbName == "last_name"
        assert columns["wannahavefun"].dbName == "wannahavefun"
        if AutoTest._connection.dbName == 'mssql':
            use_microseconds(True)
