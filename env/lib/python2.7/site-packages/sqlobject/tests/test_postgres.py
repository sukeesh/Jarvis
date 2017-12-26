import os
import pytest
from sqlobject import SQLObject, StringCol
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# Test PosgreSQL sslmode
########################################


try:
    connection = getConnection()
except (AttributeError, NameError):
    # The module was imported during documentation building
    pass
else:
    if connection.dbName != "postgres":
        pytestmark = pytest.mark.skip('')


class SOTestSSLMode(SQLObject):
    test = StringCol()


def test_sslmode():
    setupClass(SOTestSSLMode)
    connection = SOTestSSLMode._connection
    if (not connection.module.__name__.startswith('psycopg')) or \
            (os.name == 'nt'):
        pytest.skip("The test requires PostgreSQL, psycopg and ssl mode; "
                    "also it doesn't work on w32")

    connection = getConnection(sslmode='require')
    SOTestSSLMode._connection = connection
    test = SOTestSSLMode(test='test')  # Connect to the DB to test sslmode

    connection.cache.clear()
    test = SOTestSSLMode.select()[0]
    assert test.test == 'test'


########################################
# Test PosgreSQL list{Database,Tables}
########################################


class SOTestSOList(SQLObject):
    pass


def test_list_databases():
    assert connection.db in connection.listDatabases()


def test_list_tables():
    setupClass(SOTestSOList)
    assert SOTestSOList.sqlmeta.table in connection.listTables()
