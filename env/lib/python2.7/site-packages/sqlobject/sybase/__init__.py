from sqlobject.dbconnection import registerConnection


def builder():
    from . import sybaseconnection
    return sybaseconnection.SybaseConnection

registerConnection(['sybase'], builder)
