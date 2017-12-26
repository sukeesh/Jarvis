from sqlobject import BLOBCol, DateTimeCol, IntCol, SQLObject, StringCol, \
    sqlmeta
from sqlobject.tests.dbtest import getConnection


class SOTestCreateDrop(SQLObject):
    class sqlmeta(sqlmeta):
        idName = 'test_id_here'
        table = 'test_create_drop_table'
    name = StringCol()
    number = IntCol()
    so_time = DateTimeCol()
    short = StringCol(length=10)
    blobcol = BLOBCol()


def test_create_drop():
    conn = getConnection()
    SOTestCreateDrop.setConnection(conn)
    SOTestCreateDrop.dropTable(ifExists=True)
    assert not conn.tableExists(SOTestCreateDrop.sqlmeta.table)
    SOTestCreateDrop.createTable(ifNotExists=True)
    assert conn.tableExists(SOTestCreateDrop.sqlmeta.table)
    SOTestCreateDrop.createTable(ifNotExists=True)
    assert conn.tableExists(SOTestCreateDrop.sqlmeta.table)
    SOTestCreateDrop.dropTable(ifExists=True)
    assert not conn.tableExists(SOTestCreateDrop.sqlmeta.table)
    SOTestCreateDrop.dropTable(ifExists=True)
    assert not conn.tableExists(SOTestCreateDrop.sqlmeta.table)
