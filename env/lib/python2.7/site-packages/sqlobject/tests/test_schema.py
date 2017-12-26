import pytest
from sqlobject import SQLObject, UnicodeCol
from sqlobject.tests.dbtest import getConnection, setupClass, supports


########################################
# Schema per connection
########################################


class SOTestSchema(SQLObject):
    foo = UnicodeCol(length=200)


def test_connection_schema():
    if not supports('schema'):
        pytest.skip("schemas aren't supported")
    conn = getConnection()
    conn.schema = None
    conn.query('CREATE SCHEMA test')
    conn.schema = 'test'
    conn.query('SET search_path TO test')
    setupClass(SOTestSchema)
    assert SOTestSchema._connection is conn
    SOTestSchema(foo='bar')
    assert conn.queryAll("SELECT * FROM test.so_test_schema")
    conn.schema = None
    conn.query('SET search_path TO public')
