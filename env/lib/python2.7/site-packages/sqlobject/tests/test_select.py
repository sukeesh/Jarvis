import pytest
from sqlobject import IntCol, LIKE, RLIKE, SQLObject, \
    SQLObjectIntegrityError, SQLObjectNotFound, StringCol
from sqlobject.sqlbuilder import func
from .dbtest import raises, setupClass, supports, setSQLiteConnectionFactory


class IterTest(SQLObject):
    name = StringCol(dbName='name_col', length=200)


names = ('a', 'b', 'c')


def setupIter():
    setupClass(IterTest)
    for n in names:
        IterTest(name=n)


def test_00_normal():
    setupIter()
    count = 0
    for test in IterTest.select():
        count += 1
    assert count == len(names)


def test_00b_lazy():
    setupIter()
    count = 0
    for test in IterTest.select(lazyColumns=True):
        count += 1
    assert count == len(names)


def test_01_turn_to_list():
    count = 0
    for test in list(IterTest.select()):
        count += 1
    assert count == len(names)


def test_02_generator():
    all = IterTest.select()
    count = 0
    for i, test in enumerate(all):
        count += 1
    assert count == len(names)


def test_03_ranged_indexed():
    all = IterTest.select()
    count = 0
    for i in range(all.count()):
        all[i]  # test it's there
        count += 1
    assert count == len(names)


def test_04_indexed_ended_by_exception():
    if not supports('limitSelect'):
        pytest.skip("limitSelect isn't supported")
    all = IterTest.select()
    count = 0
    try:
        while 1:
            all[count]
            count = count + 1
            # Stop the test if it's gone on too long
            if count > len(names):
                break
    except IndexError:
        pass
    assert count == len(names)


def test_05_select_limit():
    setupIter()
    assert len(list(IterTest.select(limit=2))) == 2
    raises(AssertionError, IterTest.select(limit=2).count)


def test_06_contains():
    setupIter()
    assert len(list(IterTest.select(IterTest.q.name.startswith('a')))) == 1
    assert len(list(IterTest.select(IterTest.q.name.contains('a')))) == 1
    assert len(list(IterTest.select(
        IterTest.q.name.contains(func.lower('A'))))) == 1
    assert len(list(IterTest.select(IterTest.q.name.contains("a'b")))) == 0
    assert len(list(IterTest.select(IterTest.q.name.endswith('a')))) == 1


def test_07_contains_special():
    setupClass(IterTest)
    a = IterTest(name='\\test')
    b = IterTest(name='100%')
    c = IterTest(name='test_')
    assert list(IterTest.select(IterTest.q.name.startswith('\\'))) == [a]
    assert list(IterTest.select(IterTest.q.name.contains('%'))) == [b]
    assert list(IterTest.select(IterTest.q.name.endswith('_'))) == [c]


def test_select_getOne():
    setupClass(IterTest)
    a = IterTest(name='a')
    b = IterTest(name='b')
    assert IterTest.selectBy(name='a').getOne() == a
    assert IterTest.select(IterTest.q.name == 'b').getOne() == b
    assert IterTest.selectBy(name='c').getOne(None) is None
    raises(SQLObjectNotFound, 'IterTest.selectBy(name="c").getOne()')
    IterTest(name='b')
    raises(SQLObjectIntegrityError, 'IterTest.selectBy(name="b").getOne()')
    raises(SQLObjectIntegrityError, 'IterTest.selectBy(name="b").getOne(None)')


def test_selectBy():
    setupClass(IterTest)
    IterTest(name='a')
    IterTest(name='b')
    assert IterTest.selectBy().count() == 2


def test_selectBy_kwargs():
    setupClass(IterTest)
    raises(TypeError, IterTest, nonexistant='b')


class UniqTest(SQLObject):
    name = StringCol(dbName='name_col', unique=True, length=100)


def test_by_uniq():
    setupClass(UniqTest)
    a = UniqTest(name='a')
    b = UniqTest(name='b')
    assert UniqTest.byName('a') is a
    assert UniqTest.byName('b') is b


class Counter2(SQLObject):

    n1 = IntCol(notNull=True)
    n2 = IntCol(notNull=True)


class TestSelect:

    def setup_method(self, meth):
        setupClass(Counter2)
        for i in range(10):
            for j in range(10):
                Counter2(n1=i, n2=j)

    def counterEqual(self, counters, value):
        assert [(c.n1, c.n2) for c in counters] == value

    def accumulateEqual(self, func, counters, value):
        assert func([c.n1 for c in counters]) == value

    def test_1(self):
        self.accumulateEqual(sum, Counter2.select(orderBy='n1'),
                             sum(range(10)) * 10)

    def test_2(self):
        self.accumulateEqual(len, Counter2.select('all'), 100)


def test_select_LIKE():
    setupClass(IterTest)
    IterTest(name='sqlobject')
    IterTest(name='sqlbuilder')
    assert IterTest.select(LIKE(IterTest.q.name, "sql%")).count() == 2
    assert IterTest.select(LIKE(IterTest.q.name, "sqlb%")).count() == 1
    assert IterTest.select(LIKE(IterTest.q.name, "sqlb%")).count() == 1
    assert IterTest.select(LIKE(IterTest.q.name, "sqlx%")).count() == 0


def test_select_RLIKE():
    if not supports('rlike'):
        pytest.skip("rlike isn't supported")

    setupClass(IterTest)

    if IterTest._connection.dbName == "sqlite":
        if not IterTest._connection.using_sqlite2:
            pytest.skip("These tests require SQLite v2+")

        # Implement regexp() function for SQLite; only works with PySQLite2
        import re

        def regexp(regexp, test):
            return bool(re.search(regexp, test))

        def SQLiteConnectionFactory(sqlite):
            class MyConnection(sqlite.Connection):
                def __init__(self, *args, **kwargs):
                    super(MyConnection, self).__init__(*args, **kwargs)
                    self.create_function("regexp", 2, regexp)
            return MyConnection

        setSQLiteConnectionFactory(IterTest, SQLiteConnectionFactory)

    IterTest(name='sqlobject')
    IterTest(name='sqlbuilder')
    assert IterTest.select(RLIKE(IterTest.q.name, "^sql.*$")).count() == 2
    assert IterTest.select(RLIKE(IterTest.q.name, "^sqlb.*$")).count() == 1
    assert IterTest.select(RLIKE(IterTest.q.name, "^sqlb.*$")).count() == 1
    assert IterTest.select(RLIKE(IterTest.q.name, "^sqlx.*$")).count() == 0


def test_select_sqlbuilder():
    setupClass(IterTest)
    IterTest(name='sqlobject')
    IterTest.select(IterTest.q.name == u'sqlobject')


def test_select_perConnection():
    setupClass(IterTest)
    IterTest(name='a')
    assert not IterTest.select().getOne().sqlmeta._perConnection
