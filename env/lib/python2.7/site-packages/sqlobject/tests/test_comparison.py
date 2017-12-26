from sqlobject import SQLObject
from sqlobject.tests.dbtest import setupClass


class SOTestComparison(SQLObject):
    pass


def test_eq():
    setupClass(SOTestComparison, force=True)
    t1 = SOTestComparison()
    t2 = SOTestComparison()

    SOTestComparison._connection.cache.clear()
    t3 = SOTestComparison.get(1)
    t4 = SOTestComparison.get(2)

    assert t1.id == t3.id
    assert t2.id == t4.id
    assert t1 is not t3
    assert t2 is not t4
    assert t1 == t3
    assert t2 == t4
    assert t1 != t2
