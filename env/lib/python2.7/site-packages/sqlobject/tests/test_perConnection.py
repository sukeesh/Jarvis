from sqlobject import SQLObject, StringCol
from sqlobject.tests.dbtest import getConnection


########################################
# Per-instance connection
########################################


class SOTestPerConnection(SQLObject):
    test = StringCol()


def test_perConnection():
    connection = getConnection()
    SOTestPerConnection.dropTable(connection=connection, ifExists=True)
    SOTestPerConnection.createTable(connection=connection)
    SOTestPerConnection(test='test', connection=connection)
    assert len(list(SOTestPerConnection.select(
        SOTestPerConnection.q.test == 'test', connection=connection))) == 1
