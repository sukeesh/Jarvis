from sqlobject import SQLObject, StringCol, sqlmeta
from sqlobject.tests.dbtest import setupClass


########################################
# String ID test
########################################


class SOStringID(SQLObject):

    class sqlmeta(sqlmeta):
        table = 'so_string_id'
        idType = str
    val = StringCol(alternateID=True)

    mysqlCreate = """
    CREATE TABLE IF NOT EXISTS so_string_id (
      id VARCHAR(50) PRIMARY KEY,
      val TEXT
    )
    """

    postgresCreate = """
    CREATE TABLE so_string_id (
      id VARCHAR(50) PRIMARY KEY,
      val TEXT
    )
    """

    sybaseCreate = """
    CREATE TABLE so_string_id (
      id VARCHAR(50) UNIQUE,
      val VARCHAR(50) NULL
    )
    """

    firebirdCreate = """
    CREATE TABLE so_string_id (
      id VARCHAR(50) NOT NULL PRIMARY KEY,
      val BLOB SUB_TYPE TEXT
    )
    """

    mssqlCreate = """
    CREATE TABLE so_string_id (
      id VARCHAR(50) PRIMARY KEY,
      val varchar(4000)
    )
    """

    sqliteCreate = postgresCreate

    mysqlDrop = """
    DROP TABLE IF EXISTS so_string_id
    """

    postgresDrop = """
    DROP TABLE so_string_id
    """

    sqliteDrop = postgresDrop
    firebirdDrop = postgresDrop
    mssqlDrop = postgresDrop


def test_stringID():
    setupClass(SOStringID)
    t1 = SOStringID(id='hey', val='whatever')
    t2 = SOStringID.byVal('whatever')
    assert t1 == t2
    assert t1.val == t2.val
    assert t1.val == 'whatever'

    t1 = SOStringID(id='you', val='nowhere')
    t2 = SOStringID.get('you')
    assert t1 == t2
    assert t1.val == t2.val
    assert t1.val == 'nowhere'
