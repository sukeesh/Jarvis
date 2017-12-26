from sqlobject import SQLObject, StringCol
from sqlobject.tests.dbtest import setupClass


########################################
# Expiring, syncing
########################################


class SyncTest(SQLObject):
    name = StringCol(length=50, alternateID=True, dbName='name_col')


def test_expire():
    setupClass(SyncTest)
    SyncTest(name='bob')
    SyncTest(name='tim')

    conn = SyncTest._connection
    b = SyncTest.byName('bob')
    conn.query("UPDATE sync_test SET name_col = 'robert' WHERE id = %i"
               % b.id)
    assert b.name == 'bob'
    b.expire()
    assert b.name == 'robert'
    conn.query("UPDATE sync_test SET name_col = 'bobby' WHERE id = %i"
               % b.id)
    b.sync()
    assert b.name == 'bobby'
