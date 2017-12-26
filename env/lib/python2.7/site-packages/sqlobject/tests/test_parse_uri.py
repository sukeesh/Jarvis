import os
from sqlobject.dbconnection import DBConnection
from sqlobject.sqlite.sqliteconnection import SQLiteConnection


########################################
# Test _parseURI
########################################


def test_parse():
    _parseURI = DBConnection._parseURI

    user, password, host, port, path, args = _parseURI("mysql://host/database")
    assert user is None
    assert password is None
    assert host == "host"
    assert port is None
    assert path == "/database"
    assert args == {}

    user, password, host, port, path, args = _parseURI(
        "mysql://user:pass%20word@host/database?unix_socket=/var/mysql/socket")
    assert user == "user"
    assert password == "pass word"
    assert host == "host"
    assert port is None
    assert path == "/database"
    assert args == {"unix_socket": "/var/mysql/socket"}

    user, password, host, port, path, args = \
        _parseURI("postgres://user@host/database")
    assert user == "user"
    assert password is None
    assert host == "host"
    assert port is None
    assert path == "/database"
    assert args == {}

    user, password, host, port, path, args = \
        _parseURI("postgres://host:5432/database")
    assert user is None
    assert password is None
    assert host == "host"
    assert port == 5432
    assert path == "/database"
    assert args == {}

    user, password, host, port, path, args = \
        _parseURI("postgres:///full/path/to/socket/database")
    assert user is None
    assert password is None
    assert host is None
    assert port is None
    assert path == "/full/path/to/socket/database"
    assert args == {}

    user, password, host, port, path, args = \
        _parseURI("postgres://us%3Aer:p%40ssword@host/database")
    assert user == "us:er"
    assert password == "p@ssword"
    assert host == "host"
    assert port is None
    assert path == "/database"
    assert args == {}

    user, password, host, port, path, args = \
        _parseURI("sqlite:///full/path/to/database")
    assert user is None
    assert password is None
    assert host is None
    assert port is None
    assert path == "/full/path/to/database"
    assert args == {}

    user, password, host, port, path, args = _parseURI("sqlite:/:memory:")
    assert user is None
    assert password is None
    assert host is None
    assert port is None
    assert path == "/:memory:"
    assert args == {}

    if os.name == 'nt':
        user, password, host, port, path, args = \
            _parseURI("sqlite:/C|/full/path/to/database")
        assert user is None
        assert password is None
        assert host is None
        assert port is None
        assert path == "C:/full/path/to/database"
        assert args == {}

        user, password, host, port, path, args = \
            _parseURI("sqlite:///C:/full/path/to/database")
        assert user is None
        assert password is None
        assert host is None
        assert port is None
        assert path == "C:/full/path/to/database"
        assert args == {}


def test_uri():
    connection = DBConnection()
    connection.close = lambda: None

    connection.dbName, connection.host, connection.port, \
        connection.user, connection.password, connection.db = \
        'mysql', 'host', None, None, None, 'database'
    assert connection.uri() == "mysql://host/database"

    connection.dbName, connection.host, connection.port, \
        connection.user, connection.password, connection.db = \
        'mysql', 'host', None, 'user', 'pass word', 'database'
    assert connection.uri() == "mysql://user:pass%20word@host/database"

    connection.dbName, connection.host, connection.port, \
        connection.user, connection.password, connection.db = \
        'postgres', 'host', None, 'user', None, 'database'
    assert connection.uri() == "postgres://user@host/database"

    connection.dbName, connection.host, connection.port, \
        connection.user, connection.password, connection.db = \
        'postgres', 'host', 5432, None, None, 'database'
    assert connection.uri() == "postgres://host:5432/database"

    connection.dbName, connection.host, connection.port, \
        connection.user, connection.password, connection.db = \
        'postgres', None, None, None, None, '/full/path/to/socket/database'
    assert connection.uri() == "postgres:///full/path/to/socket/database"

    connection.dbName, connection.host, connection.port, \
        connection.user, connection.password, connection.db = \
        'postgres', 'host', None, 'us:er', 'p@ssword', 'database'
    assert connection.uri() == "postgres://us%3Aer:p%40ssword@host/database"

    connection = SQLiteConnection(None)
    connection.filename = '/full/path/to/database'
    assert connection.uri() == "sqlite:///full/path/to/database"

    connection.filename = ':memory:'
    assert connection.uri() == "sqlite:/:memory:"

    if os.name == 'nt':
        connection.filename = 'C:/full/path/to/database'
        assert connection.uri() == "sqlite:///C%3A/full/path/to/database"
