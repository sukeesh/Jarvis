from sqlobject import SQLObject, StringCol
from sqlobject.tests.dbtest import setupClass


########################################
# sqlmeta.asDict()
########################################


class SOTestAsDict(SQLObject):
    name = StringCol(length=10)
    name2 = StringCol(length=10)


def test_asDict():
    setupClass(SOTestAsDict, force=True)
    t1 = SOTestAsDict(name='one', name2='1')
    assert t1.sqlmeta.asDict() == dict(name='one', name2='1', id=1)
