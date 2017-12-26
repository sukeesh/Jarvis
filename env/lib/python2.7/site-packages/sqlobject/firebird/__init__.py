from sqlobject.dbconnection import registerConnection


def builder():
    from . import firebirdconnection
    return firebirdconnection.FirebirdConnection

registerConnection(['firebird', 'interbase'], builder)
