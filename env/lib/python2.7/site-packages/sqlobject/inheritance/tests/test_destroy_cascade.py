from sqlobject import ForeignKey, IntCol, SQLObject
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.tests.dbtest import setupClass


class SOTestCascade1(InheritableSQLObject):
    dummy = IntCol()


class SOTestCascade2(SOTestCascade1):
    c = ForeignKey('SOTestCascade3', cascade='null')


class SOTestCascade3(SQLObject):
    dummy = IntCol()


def test_destroySelf():
    setupClass([SOTestCascade1, SOTestCascade3, SOTestCascade2])

    c = SOTestCascade3(dummy=1)
    SOTestCascade2(cID=c.id, dummy=1)
    c.destroySelf()
