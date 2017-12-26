from sqlobject.dbconnection import registerConnection


def builder():
    from . import mssqlconnection
    return mssqlconnection.MSSQLConnection

registerConnection(['mssql'], builder)
