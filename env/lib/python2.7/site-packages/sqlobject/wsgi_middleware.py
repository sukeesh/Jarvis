import sys
import sqlobject
from sqlobject.compat import string_type

# The module was imported during documentation building
if 'sphinx' not in sys.modules:
    from paste.deploy.converters import asbool
    from paste.wsgilib import catch_errors
    from paste.util import import_string


def make_middleware(app, global_conf, database=None, use_transaction=False,
                    hub=None):
    """
    WSGI middleware that sets the connection for the request (using
    the database URI or connection object) and the given hub (or
    ``sqlobject.sqlhub`` if not given).

    If ``use_transaction`` is true, then the request will be run in a
    transaction.

    Applications can use the keys (which are all no-argument functions):

    ``sqlobject.get_connection()``:
      Returns the connection object

    ``sqlobject.abort()``:
      Aborts the transaction.  Does not raise an error, but at the *end*
      of the request there will be a rollback.

    ``sqlobject.begin()``:
      Starts a transaction.  First commits (or rolls back if aborted) if
      this is run in a transaction.

    ``sqlobject.in_transaction()``:
      Returns true or false, depending if we are currently in a
      transaction.
    """
    use_transaction = asbool(use_transaction)
    if database is None:
        database = global_conf.get('database')
    if not database:
        raise ValueError(
            "You must provide a 'database' configuration value")
    if isinstance(hub, string_type):
        hub = import_string.eval_import(hub)
    if not hub:
        hub = sqlobject.sqlhub
    if isinstance(database, string_type):
        database = sqlobject.connectionForURI(database)
    return SQLObjectMiddleware(app, database, use_transaction, hub)


class SQLObjectMiddleware(object):

    def __init__(self, app, conn, use_transaction, hub):
        self.app = app
        self.conn = conn
        self.use_transaction = use_transaction
        self.hub = hub

    def __call__(self, environ, start_response):
        conn = [self.conn]
        if self.use_transaction:
            conn[0] = conn[0].transaction()
        any_errors = []
        use_transaction = [self.use_transaction]
        self.hub.threadConnection = conn[0]

        def abort():
            assert use_transaction[0], (
                "You cannot abort, because a transaction is not being used")
            any_errors.append(None)

        def begin():
            if use_transaction[0]:
                if any_errors:
                    conn[0].rollback()
                else:
                    conn[0].commit()
            any_errors[:] = []
            use_transaction[0] = True
            conn[0] = self.conn.transaction()
            self.hub.threadConnection = conn[0]

        def error(exc_info=None):
            any_errors.append(None)
            ok()

        def ok():
            if use_transaction[0]:
                if any_errors:
                    conn[0].rollback()
                else:
                    conn[0].commit(close=True)
            self.hub.threadConnection = None

        def in_transaction():
            return use_transaction[0]

        def get_connection():
            return conn[0]

        environ['sqlobject.get_connection'] = get_connection
        environ['sqlobject.abort'] = abort
        environ['sqlobject.begin'] = begin
        environ['sqlobject.in_transaction'] = in_transaction
        return catch_errors(self.app, environ, start_response,
                            error_callback=error, ok_callback=ok)
