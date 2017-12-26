from sqlobject import IntCol, SQLObject, StringCol
from sqlobject.sqlbuilder import Select, func
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# groupBy
########################################


class GroupbyTest(SQLObject):
    name = StringCol()
    so_value = IntCol()


def test_groupBy():
    setupClass(GroupbyTest)
    GroupbyTest(name='a', so_value=1)
    GroupbyTest(name='a', so_value=2)
    GroupbyTest(name='b', so_value=1)

    connection = getConnection()
    select = Select(
        [GroupbyTest.q.name, func.COUNT(GroupbyTest.q.so_value)],
        groupBy=GroupbyTest.q.name,
        orderBy=GroupbyTest.q.name)
    sql = connection.sqlrepr(select)
    rows = list(connection.queryAll(sql))
    assert [tuple(t) for t in rows] == [('a', 2), ('b', 1)]


def test_groupBy_list():
    setupClass(GroupbyTest)
    GroupbyTest(name='a', so_value=1)
    GroupbyTest(name='a', so_value=2)
    GroupbyTest(name='b', so_value=1)

    connection = getConnection()
    select = Select(
        [GroupbyTest.q.name, GroupbyTest.q.so_value],
        groupBy=[GroupbyTest.q.name, GroupbyTest.q.so_value],
        orderBy=[GroupbyTest.q.name, GroupbyTest.q.so_value])
    sql = connection.sqlrepr(select)
    rows = list(connection.queryAll(sql))
    assert [tuple(t) for t in rows] == [('a', 1), ('a', 2), ('b', 1)]
