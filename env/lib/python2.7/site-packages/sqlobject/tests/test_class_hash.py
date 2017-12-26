from sqlobject import SQLObject, StringCol
from sqlobject.tests.dbtest import setupClass


########################################
# Test hashing a column instance
########################################


class ClassHashTest(SQLObject):
    name = StringCol(length=50, alternateID=True, dbName='name_col')


def test_class_hash():
    setupClass(ClassHashTest)
    ClassHashTest(name='bob')

    b = ClassHashTest.byName('bob')
    hashed = hash(b)
    b.expire()
    b = ClassHashTest.byName('bob')
    assert hash(b) == hashed
