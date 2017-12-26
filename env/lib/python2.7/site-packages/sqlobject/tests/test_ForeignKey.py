from formencode import validators
from sqlobject import ForeignKey, IntCol, SQLObject, StringCol
from sqlobject.tests.dbtest import getConnection, InstalledTestDatabase, \
    raises, setupClass, setupCyclicClasses


class SOTestComposerKey(SQLObject):
    name = StringCol()
    id2 = IntCol(default=None, unique=True)


class SOTestWorkKey(SQLObject):
    class sqlmeta:
        idName = "work_id"

    composer = ForeignKey('SOTestComposerKey', cascade=True)
    title = StringCol()


class SOTestWorkKey2(SQLObject):
    title = StringCol()


class SOTestOtherColumn(SQLObject):
    key1 = ForeignKey('SOTestComposerKey', default=None)
    key2 = ForeignKey('SOTestComposerKey', refColumn='id2', default=None)


def test1():
    setupClass([SOTestComposerKey, SOTestWorkKey])

    c = SOTestComposerKey(name='Mahler, Gustav')
    w1 = SOTestWorkKey(composer=c, title='Symphony No. 9')
    w2 = SOTestWorkKey(composer=None, title=None)

    # Select by usual way
    s = SOTestWorkKey.selectBy(composerID=c.id, title='Symphony No. 9')
    assert s.count() == 1
    assert s[0] == w1
    # selectBy object.id
    s = SOTestWorkKey.selectBy(composer=c.id, title='Symphony No. 9')
    assert s.count() == 1
    assert s[0] == w1
    # selectBy object
    s = SOTestWorkKey.selectBy(composer=c, title='Symphony No. 9')
    assert s.count() == 1
    assert s[0] == w1
    # selectBy id
    s = SOTestWorkKey.selectBy(id=w1.id)
    assert s.count() == 1
    assert s[0] == w1
    # is None handled correctly?
    s = SOTestWorkKey.selectBy(composer=None, title=None)
    assert s.count() == 1
    assert s[0] == w2

    s = SOTestWorkKey.selectBy()
    assert s.count() == 2

    # select with objects
    s = SOTestWorkKey.select(SOTestWorkKey.q.composerID == c.id)
    assert s.count() == 1
    assert s[0] == w1
    s = SOTestWorkKey.select(SOTestWorkKey.q.composer == c.id)
    assert s.count() == 1
    assert s[0] == w1
    s = SOTestWorkKey.select(SOTestWorkKey.q.composerID == c)
    assert s.count() == 1
    assert s[0] == w1
    s = SOTestWorkKey.select(SOTestWorkKey.q.composer == c)
    assert s.count() == 1
    assert s[0] == w1
    s = SOTestWorkKey.select(
        (SOTestWorkKey.q.composer == c) &
        (SOTestWorkKey.q.title == 'Symphony No. 9'))
    assert s.count() == 1
    assert s[0] == w1


def test2():
    SOTestWorkKey._connection = getConnection()
    InstalledTestDatabase.drop(SOTestWorkKey)
    setupClass([SOTestComposerKey, SOTestWorkKey2], force=True)
    SOTestWorkKey2.sqlmeta.addColumn(ForeignKey('SOTestComposerKey'),
                                     changeSchema=True)


def test_otherColumn():
    setupClass([SOTestComposerKey, SOTestOtherColumn])
    test_composer1 = SOTestComposerKey(name='Test1')
    test_composer2 = SOTestComposerKey(name='Test2', id2=2)
    test_fkey = SOTestOtherColumn(key1=test_composer1)
    test_other = SOTestOtherColumn(key2=test_composer2.id2)
    getConnection().cache.clear()
    assert test_fkey.key1 == test_composer1
    assert test_other.key2 == test_composer2


class SOTestFKValidationA(SQLObject):
    name = StringCol()
    bfk = ForeignKey("SOTestFKValidationB")
    cfk = ForeignKey("SOTestFKValidationC", default=None)


class SOTestFKValidationB(SQLObject):
    name = StringCol()
    afk = ForeignKey("SOTestFKValidationA")


class SOTestFKValidationC(SQLObject):
    class sqlmeta:
        idType = str
    name = StringCol()


def test_foreignkey_validation():
    setupCyclicClasses(SOTestFKValidationA, SOTestFKValidationB,
                       SOTestFKValidationC)
    a = SOTestFKValidationA(name="testa", bfk=None)
    b = SOTestFKValidationB(name="testb", afk=a)
    c = SOTestFKValidationC(id='testc', name="testc")
    a.bfk = b
    a.cfk = c
    assert a.bfk == b
    assert a.cfk == c
    assert b.afk == a

    raises(validators.Invalid,
           SOTestFKValidationA, name="testa", bfk='testb', cfk='testc')

    a = SOTestFKValidationA(name="testa", bfk=1, cfk='testc')
    assert a.bfkID == 1
    assert a.cfkID == 'testc'
