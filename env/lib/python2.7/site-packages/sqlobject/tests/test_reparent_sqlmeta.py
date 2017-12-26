from sqlobject import SQLObject, StringCol, sqlmeta
from sqlobject.tests.dbtest import setupClass

real_sqlmeta = sqlmeta


class Reparented1(SQLObject):

    class sqlmeta:
        table = 'reparented1'

    dummy = StringCol()


class Reparented2(SQLObject):
    class sqlmeta(object):
        @classmethod
        def setClass(cls, soClass):
            # Well, it's pretty hard to call the superclass method
            # when it's a classmethod and it's not actually your
            # *current* superclass.  Sigh
            real_sqlmeta.setClass.__func__(cls, soClass)
            cls.worked = True

    dummy = StringCol()


def test_reparented():
    setupClass([Reparented1, Reparented2])
    assert Reparented1.sqlmeta.table == 'reparented1'
    assert issubclass(Reparented1.sqlmeta, real_sqlmeta)
    assert issubclass(Reparented2.sqlmeta, real_sqlmeta)
    assert Reparented2.sqlmeta.worked
