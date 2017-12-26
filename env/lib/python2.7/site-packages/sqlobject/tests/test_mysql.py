import pytest
from sqlobject import SQLObject
from sqlobject.tests.dbtest import getConnection, setupClass


try:
    connection = getConnection()
except (AttributeError, NameError):
    # The module was imported during documentation building
    pass
else:
    if connection.dbName != "mysql":
        pytestmark = pytest.mark.skip('')


class SOTestSOListMySQL(SQLObject):
    pass


def test_list_databases():
    assert connection.db in connection.listDatabases()


def test_list_tables():
    setupClass(SOTestSOListMySQL)
    assert SOTestSOListMySQL.sqlmeta.table in connection.listTables()
