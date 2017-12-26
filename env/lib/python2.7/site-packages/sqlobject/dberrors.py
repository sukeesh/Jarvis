"""dberrors: database exception classes for SQLObject.

   These classes are dictated by the DB API v2.0, see:
   https://wiki.python.org/moin/DatabaseProgramming
"""

from sqlobject.compat import PY2

if not PY2:
    StandardError = Exception


class Error(StandardError):
    pass


class Warning(StandardError):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class InternalError(DatabaseError):
    pass


class OperationalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class DataError(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass


class DuplicateEntryError(IntegrityError):
    pass
