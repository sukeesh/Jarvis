import codecs
import pytest
from sqlobject import BoolCol, ForeignKey, IntCol, KeyCol, SQLObject, \
    StringCol, connectionForURI, sqlhub
from sqlobject.tests.dbtest import inserts, raises, setupClass, supports


class SOTestSO1(SQLObject):

    name = StringCol(length=50, dbName='name_col')
    name.title = 'Your Name'
    name.foobar = 1
    passwd = StringCol(length=10)

    class sqlmeta:
        cacheValues = False

    def _set_passwd(self, passwd):
        self._SO_set_passwd(codecs.encode(passwd, 'rot13'))


def setupGetters(cls):
    setupClass(cls)
    inserts(cls, [('bob', 'god'), ('sally', 'sordid'),
                  ('dave', 'dremel'), ('fred', 'forgo')],
            'name passwd')


def test_case1():
    setupGetters(SOTestSO1)
    bob = SOTestSO1.selectBy(name='bob')[0]
    assert bob.name == 'bob'
    assert bob.passwd == codecs.encode('god', 'rot13')
    bobs = SOTestSO1.selectBy(name='bob')[:10]
    assert len(list(bobs)) == 1


def test_newline():
    setupGetters(SOTestSO1)
    bob = SOTestSO1.selectBy(name='bob')[0]
    testString = 'hey\nyou\\can\'t you see me?\t'
    bob.name = testString
    bob.expire()
    assert bob.name == testString


def test_count():
    setupGetters(SOTestSO1)
    assert SOTestSO1.selectBy(name=None).count() == 0
    assert SOTestSO1.selectBy(name='bob').count() == 1
    assert SOTestSO1.select(SOTestSO1.q.name == 'bob').count() == 1
    assert SOTestSO1.select().count() == len(list(SOTestSO1.select()))


def test_getset():
    setupGetters(SOTestSO1)
    bob = SOTestSO1.selectBy(name='bob')[0]
    assert bob.name == 'bob'
    bob.name = 'joe'
    assert bob.name == 'joe'
    bob.set(name='joebob', passwd='testtest')
    assert bob.name == 'joebob'


def test_extra_vars():
    setupGetters(SOTestSO1)
    col = SOTestSO1.sqlmeta.columns['name']
    assert col.title == 'Your Name'
    assert col.foobar == 1
    assert getattr(SOTestSO1.sqlmeta.columns['passwd'], 'title', None) is None


class SOTestSO2(SQLObject):
    name = StringCol(length=50, dbName='name_col')
    passwd = StringCol(length=10)

    def _set_passwd(self, passwd):
        self._SO_set_passwd(codecs.encode(passwd, 'rot13'))


def test_case2():
    setupGetters(SOTestSO2)
    bob = SOTestSO2.selectBy(name='bob')[0]
    assert bob.name == 'bob'
    assert bob.passwd == codecs.encode('god', 'rot13')


class Student(SQLObject):
    is_smart = BoolCol()


def test_boolCol():
    setupClass(Student)
    student = Student(is_smart=False)
    assert not student.is_smart
    student2 = Student(is_smart=1)
    assert student2.is_smart


class SOTestSO3(SQLObject):
    name = StringCol(length=10, dbName='name_col')
    other = ForeignKey('SOTestSO4', default=None)
    other2 = KeyCol(foreignKey='SOTestSO4', default=None)


class SOTestSO4(SQLObject):
    me = StringCol(length=10)


def test_foreignKey():
    setupClass([SOTestSO4, SOTestSO3])
    test3_order = [col.name for col in SOTestSO3.sqlmeta.columnList]
    assert test3_order == ['name', 'otherID', 'other2ID']
    tc3 = SOTestSO3(name='a')
    assert tc3.other is None
    assert tc3.other2 is None
    assert tc3.otherID is None
    assert tc3.other2ID is None
    tc4a = SOTestSO4(me='1')
    tc3.other = tc4a
    assert tc3.other == tc4a
    assert tc3.otherID == tc4a.id
    tc4b = SOTestSO4(me='2')
    tc3.other = tc4b.id
    assert tc3.other == tc4b
    assert tc3.otherID == tc4b.id
    tc4c = SOTestSO4(me='3')
    tc3.other2 = tc4c
    assert tc3.other2 == tc4c
    assert tc3.other2ID == tc4c.id
    tc4d = SOTestSO4(me='4')
    tc3.other2 = tc4d.id
    assert tc3.other2 == tc4d
    assert tc3.other2ID == tc4d.id
    tcc = SOTestSO3(name='b', other=tc4a)
    assert tcc.other == tc4a
    tcc2 = SOTestSO3(name='c', other=tc4a.id)
    assert tcc2.other == tc4a


def test_selectBy():
    setupClass([SOTestSO4, SOTestSO3])
    tc4 = SOTestSO4(me='another')
    tc3 = SOTestSO3(name='sel', other=tc4)
    SOTestSO3(name='not joined')
    assert tc3.other == tc4
    assert list(SOTestSO3.selectBy(other=tc4)) == [tc3]
    assert list(SOTestSO3.selectBy(otherID=tc4.id)) == [tc3]
    assert SOTestSO3.selectBy(otherID=tc4.id)[0] == tc3
    assert list(SOTestSO3.selectBy(otherID=tc4.id)[:10]) == [tc3]
    assert list(SOTestSO3.selectBy(other=tc4)[:10]) == [tc3]


class SOTestSO5(SQLObject):
    name = StringCol(length=10, dbName='name_col')
    other = ForeignKey('SOTestSO6', default=None, cascade=True)
    another = ForeignKey('SOTestSO7', default=None, cascade=True)


class SOTestSO6(SQLObject):
    name = StringCol(length=10, dbName='name_col')
    other = ForeignKey('SOTestSO7', default=None, cascade=True)


class SOTestSO7(SQLObject):
    name = StringCol(length=10, dbName='name_col')


def test_foreignKeyDestroySelfCascade():
    setupClass([SOTestSO7, SOTestSO6, SOTestSO5])

    tc5 = SOTestSO5(name='a')
    tc6a = SOTestSO6(name='1')
    tc5.other = tc6a
    tc7a = SOTestSO7(name='2')
    tc6a.other = tc7a
    tc5.another = tc7a
    assert tc5.other == tc6a
    assert tc5.otherID == tc6a.id
    assert tc6a.other == tc7a
    assert tc6a.otherID == tc7a.id
    assert tc5.other.other == tc7a
    assert tc5.other.otherID == tc7a.id
    assert tc5.another == tc7a
    assert tc5.anotherID == tc7a.id
    assert tc5.other.other == tc5.another
    assert SOTestSO5.select().count() == 1
    assert SOTestSO6.select().count() == 1
    assert SOTestSO7.select().count() == 1
    tc6b = SOTestSO6(name='3')
    tc6c = SOTestSO6(name='4')
    tc7b = SOTestSO7(name='5')
    tc6b.other = tc7b
    tc6c.other = tc7b
    assert SOTestSO5.select().count() == 1
    assert SOTestSO6.select().count() == 3
    assert SOTestSO7.select().count() == 2
    tc6b.destroySelf()
    assert SOTestSO5.select().count() == 1
    assert SOTestSO6.select().count() == 2
    assert SOTestSO7.select().count() == 2
    tc7b.destroySelf()
    assert SOTestSO5.select().count() == 1
    assert SOTestSO6.select().count() == 1
    assert SOTestSO7.select().count() == 1
    tc7a.destroySelf()
    assert SOTestSO5.select().count() == 0
    assert SOTestSO6.select().count() == 0
    assert SOTestSO7.select().count() == 0


def testForeignKeyDropTableCascade():
    if not supports('dropTableCascade'):
        pytest.skip("dropTableCascade isn't supported")
    setupClass(SOTestSO7)
    setupClass(SOTestSO6)
    setupClass(SOTestSO5)

    tc5a = SOTestSO5(name='a')
    tc6a = SOTestSO6(name='1')
    tc5a.other = tc6a
    tc7a = SOTestSO7(name='2')
    tc6a.other = tc7a
    tc5a.another = tc7a
    tc5b = SOTestSO5(name='b')
    tc5c = SOTestSO5(name='c')
    tc6b = SOTestSO6(name='3')
    tc5c.other = tc6b
    assert SOTestSO5.select().count() == 3
    assert SOTestSO6.select().count() == 2
    assert SOTestSO7.select().count() == 1
    SOTestSO7.dropTable(cascade=True)
    assert SOTestSO5.select().count() == 3
    assert SOTestSO6.select().count() == 2
    tc6a.destroySelf()
    assert SOTestSO5.select().count() == 2
    assert SOTestSO6.select().count() == 1
    tc6b.destroySelf()
    assert SOTestSO5.select().count() == 1
    assert SOTestSO6.select().count() == 0
    assert next(iter(SOTestSO5.select())) == tc5b
    tc6c = SOTestSO6(name='3')
    tc5b.other = tc6c
    assert SOTestSO5.select().count() == 1
    assert SOTestSO6.select().count() == 1
    tc6c.destroySelf()
    assert SOTestSO5.select().count() == 0
    assert SOTestSO6.select().count() == 0


class SOTestSO8(SQLObject):
    name = StringCol(length=10, dbName='name_col')
    other = ForeignKey('SOTestSO9', default=None, cascade=False)


class SOTestSO9(SQLObject):
    name = StringCol(length=10, dbName='name_col')


def testForeignKeyDestroySelfRestrict():
    setupClass([SOTestSO9, SOTestSO8])

    tc8a = SOTestSO8(name='a')
    tc9a = SOTestSO9(name='1')
    tc8a.other = tc9a
    tc8b = SOTestSO8(name='b')
    tc9b = SOTestSO9(name='2')
    assert tc8a.other == tc9a
    assert tc8a.otherID == tc9a.id
    assert SOTestSO8.select().count() == 2
    assert SOTestSO9.select().count() == 2
    raises(Exception, tc9a.destroySelf)
    tc9b.destroySelf()
    assert SOTestSO8.select().count() == 2
    assert SOTestSO9.select().count() == 1
    tc8a.destroySelf()
    tc8b.destroySelf()
    tc9a.destroySelf()
    assert SOTestSO8.select().count() == 0
    assert SOTestSO9.select().count() == 0


class SOTestSO10(SQLObject):
    name = StringCol()


class SOTestSO11(SQLObject):
    name = StringCol()
    other = ForeignKey('SOTestSO10', default=None, cascade='null')


def testForeignKeySetNull():
    setupClass([SOTestSO10, SOTestSO11])
    obj1 = SOTestSO10(name='foo')
    obj2 = SOTestSO10(name='bar')
    dep1 = SOTestSO11(name='xxx', other=obj1)
    dep2 = SOTestSO11(name='yyy', other=obj1)
    dep3 = SOTestSO11(name='zzz', other=obj2)
    for name in 'xxx', 'yyy', 'zzz':
        assert len(list(SOTestSO11.selectBy(name=name))) == 1
    obj1.destroySelf()
    for name in 'xxx', 'yyy', 'zzz':
        assert len(list(SOTestSO11.selectBy(name=name))) == 1
    assert dep1.other is None
    assert dep2.other is None
    assert dep3.other is obj2


def testAsDict():
    setupGetters(SOTestSO1)
    bob = SOTestSO1.selectBy(name='bob')[0]
    assert bob.sqlmeta.asDict() == {
        'passwd': 'tbq', 'name': 'bob', 'id': bob.id}


def test_nonexisting_attr():
    setupClass(Student)
    raises(AttributeError, getattr, Student.q, 'nonexisting')


class SOTestSO12(SQLObject):
    name = StringCol()
    so_value = IntCol(defaultSQL='1')


def test_defaultSQL():
    setupClass(SOTestSO12)
    test = SOTestSO12(name="test")
    assert test.so_value == 1


def test_connection_override():
    sqlhub.processConnection = connectionForURI('sqlite:///db1')

    class SOTestSO13(SQLObject):
        _connection = connectionForURI('sqlite:///db2')

    assert SOTestSO13._connection.uri() == 'sqlite:///db2'
    del sqlhub.processConnection
