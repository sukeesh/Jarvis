from sqlobject import IntCol, SQLObject
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# Identity (MS SQL)
########################################


class SOTestIdentity(SQLObject):
    n = IntCol()


def test_identity():
    # (re)create table
    SOTestIdentity.dropTable(connection=getConnection(), ifExists=True)
    setupClass(SOTestIdentity)

    # insert without giving identity
    SOTestIdentity(n=100)  # i1
    # verify result
    i1get = SOTestIdentity.get(1)
    assert(i1get.n == 100)

    # insert while giving identity
    SOTestIdentity(id=2, n=200)  # i2
    # verify result
    i2get = SOTestIdentity.get(2)
    assert(i2get.n == 200)
