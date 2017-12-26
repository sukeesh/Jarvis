from sqlobject.dbconnection import registerConnection


def builder():
    from . import mysqlconnection
    return mysqlconnection.MySQLConnection

registerConnection(['mysql'], builder)
