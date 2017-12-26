from sqlobject.dbconnection import registerConnection


def builder():
    from . import sqliteconnection
    return sqliteconnection.SQLiteConnection

registerConnection(['sqlite'], builder)
