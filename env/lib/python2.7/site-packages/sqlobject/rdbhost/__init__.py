from sqlobject.dbconnection import registerConnection


def builder():
    from . import rdbhostconnection
    return rdbhostconnection.RdbhostConnection

registerConnection(['rdbhost'], builder)
