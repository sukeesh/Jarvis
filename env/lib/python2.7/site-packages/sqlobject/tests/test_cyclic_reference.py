import pytest
from sqlobject import BLOBCol, DateTimeCol, ForeignKey, IntCol, SQLObject, \
    StringCol, sqlmeta
from sqlobject.tests.dbtest import getConnection, supports


class SOTestCyclicRefA(SQLObject):
    class sqlmeta(sqlmeta):
        idName = 'test_id_here'
        table = 'test_cyclic_ref_a_table'
    name = StringCol()
    number = IntCol()
    so_time = DateTimeCol()
    short = StringCol(length=10)
    blobcol = BLOBCol()
    fkeyb = ForeignKey('SOTestCyclicRefB')


class SOTestCyclicRefB(SQLObject):
    class sqlmeta(sqlmeta):
        idName = 'test_id_here'
        table = 'test_cyclic_ref_b_table'
    name = StringCol()
    number = IntCol()
    so_time = DateTimeCol()
    short = StringCol(length=10)
    blobcol = BLOBCol()
    fkeya = ForeignKey('SOTestCyclicRefA')


def test_cyclic_reference():
    if not supports('dropTableCascade'):
        pytest.skip("dropTableCascade isn't supported")
    conn = getConnection()
    SOTestCyclicRefA.setConnection(conn)
    SOTestCyclicRefB.setConnection(conn)
    SOTestCyclicRefA.dropTable(ifExists=True, cascade=True)
    assert not conn.tableExists(SOTestCyclicRefA.sqlmeta.table)
    SOTestCyclicRefB.dropTable(ifExists=True, cascade=True)
    assert not conn.tableExists(SOTestCyclicRefB.sqlmeta.table)

    constraints = SOTestCyclicRefA.createTable(ifNotExists=True,
                                               applyConstraints=False)
    assert conn.tableExists(SOTestCyclicRefA.sqlmeta.table)
    constraints += SOTestCyclicRefB.createTable(ifNotExists=True,
                                                applyConstraints=False)
    assert conn.tableExists(SOTestCyclicRefB.sqlmeta.table)

    for constraint in constraints:
        conn.query(constraint)

    SOTestCyclicRefA.dropTable(ifExists=True, cascade=True)
    assert not conn.tableExists(SOTestCyclicRefA.sqlmeta.table)
    SOTestCyclicRefB.dropTable(ifExists=True, cascade=True)
    assert not conn.tableExists(SOTestCyclicRefB.sqlmeta.table)
