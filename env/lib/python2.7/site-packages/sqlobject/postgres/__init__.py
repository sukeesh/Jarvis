from sqlobject.dbconnection import registerConnection


def builder():
    from . import pgconnection
    return pgconnection.PostgresConnection

registerConnection(['postgres', 'postgresql', 'psycopg'], builder)
