"""This module is used by pytest to configure testing"""

try:
    import pkg_resources
except ImportError:
    pass
else:
    pkg_resources.require('SQLObject')

# Override some options (doesn't override command line):
verbose = 0
exitfirst = True

connectionShortcuts = {
    'mysql': 'mysql://test@localhost/test',
    'dbm': 'dbm:///data',
    'postgres': 'postgres:///test',
    'postgresql': 'postgres:///test',
    'rdbhost': 'rdhbost://role:authcode@www.rdbhost.com/',
    'pygresql': 'pygresql://localhost/test',
    'sqlite': 'sqlite:/:memory:',
    'sybase': 'sybase://test:test123@sybase/test?autoCommit=0',
    'firebird':
        'firebird://sysdba:masterkey@localhost/var/lib/firebird/data/test.gdb',
    'mssql': 'mssql://sa:@127.0.0.1/test'
}


def pytest_addoption(parser):
    """Add the SQLObject options"""
    parser.addoption(
        '-D', '--Database',
        action="store", dest="Database", default='sqlite',
        help="The database to run the tests under (default sqlite).  "
        "Can also use an alias from: %s"
        % (', '.join(connectionShortcuts.keys())))
    parser.addoption(
        '-S', '--SQL',
        action="store_true", dest="show_sql", default=False,
        help="Show SQL from statements (when capturing stdout the "
        "SQL is only displayed when a test fails)")
    parser.addoption(
        '-O', '--SQL-output',
        action="store_true", dest="show_sql_output", default=False,
        help="Show output from SQL statements (when capturing "
        "stdout the output is only displayed when a test fails)")
    parser.addoption(
        '-E', '--events',
        action="store_true", dest="debug_events", default=False,
        help="Debug events (print information about events as they are "
        "sent)")

option = None


def pytest_configure(config):
    """Make cmdline arguments available to dbtest"""
    global option
    option = config.option


def setup_tests():
    if option.debug_events:
        from sqlobject import events
        events.debug_events()
