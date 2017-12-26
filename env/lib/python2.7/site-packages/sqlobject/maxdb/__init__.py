from sqlobject.dbconnection import registerConnection


def builder():
    from . import maxdbconnection
    return maxdbconnection.MaxdbConnection

registerConnection(['maxdb', 'sapdb'], builder)
