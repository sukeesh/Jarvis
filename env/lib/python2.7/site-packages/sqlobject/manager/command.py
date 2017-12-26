#!/usr/bin/env python
from __future__ import print_function

import fnmatch
import optparse
import os
import re
import sys
import textwrap
import time
import warnings

try:
    from paste.deploy import appconfig
except ImportError:
    appconfig = None

import sqlobject
from sqlobject import col
from sqlobject.classregistry import findClass
from sqlobject.declarative import DeclarativeMeta
from sqlobject.util import moduleloader
from sqlobject.compat import PY2, with_metaclass, string_type

# It's not very unsafe to use tempnam like we are doing:
warnings.filterwarnings(
    'ignore', 'tempnam is a potential security risk.*',
    RuntimeWarning, '.*command', 28)


if PY2:
    # noqa for flake8 and python 3
    input = raw_input  # noqa


def nowarning_tempnam(*args, **kw):
    return os.tempnam(*args, **kw)


class SQLObjectVersionTable(sqlobject.SQLObject):
    """
    This table is used to store information about the database and
    its version (used with record and update commands).
    """
    class sqlmeta:
        table = 'sqlobject_db_version'
    version = col.StringCol()
    updated = col.DateTimeCol(default=col.DateTimeCol.now)


def db_differences(soClass, conn):
    """
    Returns the differences between a class and the table in a
    connection.  Returns [] if no differences are found.  This
    function does the best it can; it can miss many differences.
    """
    # @@: Repeats a lot from CommandStatus.command, but it's hard
    # to actually factor out the display logic.  Or I'm too lazy
    # to do so.
    diffs = []
    if not conn.tableExists(soClass.sqlmeta.table):
        if soClass.sqlmeta.columns:
            diffs.append('Does not exist in database')
    else:
        try:
            columns = conn.columnsFromSchema(soClass.sqlmeta.table,
                                             soClass)
        except AttributeError:
            # Database does not support reading columns
            pass
        else:
            existing = {}
            for _col in columns:
                _col = _col.withClass(soClass)
                existing[_col.dbName] = _col
            missing = {}
            for _col in soClass.sqlmeta.columnList:
                if _col.dbName in existing:
                    del existing[_col.dbName]
                else:
                    missing[_col.dbName] = _col
            for _col in existing.values():
                diffs.append('Database has extra column: %s' % _col.dbName)
            for _col in missing.values():
                diffs.append('Database missing column: %s' % _col.dbName)
    return diffs


class CommandRunner(object):

    def __init__(self):
        self.commands = {}
        self.command_aliases = {}

    def run(self, argv):
        invoked_as = argv[0]
        args = argv[1:]
        for i in range(len(args)):
            if not args[i].startswith('-'):
                # this must be a command
                command = args[i].lower()
                del args[i]
                break
        else:
            # no command found
            self.invalid('No COMMAND given (try "%s help")'
                         % os.path.basename(invoked_as))
        real_command = self.command_aliases.get(command, command)
        if real_command not in self.commands.keys():
            self.invalid('COMMAND %s unknown' % command)
        runner = self.commands[real_command](
            invoked_as, command, args, self)
        runner.run()

    def register(self, command):
        name = command.name
        self.commands[name] = command
        for alias in command.aliases:
            self.command_aliases[alias] = name

    def invalid(self, msg, code=2):
        print(msg)
        sys.exit(code)

the_runner = CommandRunner()
register = the_runner.register


def standard_parser(connection=True, simulate=True,
                    interactive=False, find_modules=True):
    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose',
                      help='Be verbose (multiple times for more verbosity)',
                      action='count',
                      dest='verbose',
                      default=0)
    if simulate:
        parser.add_option('-n', '--simulate',
                          help="Don't actually do anything (implies -v)",
                          action='store_true',
                          dest='simulate')
    if connection:
        parser.add_option('-c', '--connection',
                          help="The database connection URI",
                          metavar='URI',
                          dest='connection_uri')
    parser.add_option('-f', '--config-file',
                      help="The Paste config file "
                      "that contains the database URI (in the database key)",
                      metavar="FILE",
                      dest="config_file")
    if find_modules:
        parser.add_option('-m', '--module',
                          help="Module in which to find SQLObject classes",
                          action='append',
                          metavar='MODULE',
                          dest='modules',
                          default=[])
        parser.add_option('-p', '--package',
                          help="Package to search for SQLObject classes",
                          action="append",
                          metavar="PACKAGE",
                          dest="packages",
                          default=[])
        parser.add_option('--class',
                          help="Select only named classes (wildcards allowed)",
                          action="append",
                          metavar="NAME",
                          dest="class_matchers",
                          default=[])
    if interactive:
        parser.add_option('-i', '--interactive',
                          help="Ask before doing anything "
                          "(use twice to be more careful)",
                          action="count",
                          dest="interactive",
                          default=0)
    parser.add_option('--egg',
                      help="Select modules from the given Egg, "
                      "using sqlobject.txt",
                      action="append",
                      metavar="EGG_SPEC",
                      dest="eggs",
                      default=[])
    return parser


class Command(with_metaclass(DeclarativeMeta, object)):

    min_args = 0
    min_args_error = 'You must provide at least %(min_args)s arguments'
    max_args = 0
    max_args_error = 'You must provide no more than %(max_args)s arguments'
    aliases = ()
    required_args = []
    description = None

    help = ''

    def orderClassesByDependencyLevel(self, classes):
        """
        Return classes ordered by their depth in the class dependency
        tree (this is *not* the inheritance tree), from the
        top level (independant) classes to the deepest level.
        The dependency tree is defined by the foreign key relations.
        """
        # @@: written as a self-contained function for now, to prevent
        # having to modify any core SQLObject component and namespace
        # contamination.
        # yemartin - 2006-08-08

        class SQLObjectCircularReferenceError(Exception):
            pass

        def findReverseDependencies(cls):
            """
            Return a list of classes that cls depends on. Note that
            "depends on" here mean "has a foreign key pointing to".
            """
            depended = []
            for _col in cls.sqlmeta.columnList:
                if _col.foreignKey:
                    other = findClass(_col.foreignKey,
                                      _col.soClass.sqlmeta.registry)
                    if (other is not cls) and (other not in depended):
                        depended.append(other)
            return depended

        # Cache to save already calculated dependency levels.
        dependency_levels = {}

        def calculateDependencyLevel(cls, dependency_stack=[]):
            """
            Recursively calculate the dependency level of cls, while
            using the dependency_stack to detect any circular reference.
            """
            # Return value from the cache if already calculated
            if cls in dependency_levels:
                return dependency_levels[cls]
            # Check for circular references
            if cls in dependency_stack:
                dependency_stack.append(cls)
                raise SQLObjectCircularReferenceError(
                    "Found a circular reference: %s " %
                    (' --> '.join([x.__name__ for x in dependency_stack])))
            dependency_stack.append(cls)
            # Recursively inspect dependent classes.
            depended = findReverseDependencies(cls)
            if depended:
                level = max([calculateDependencyLevel(x, dependency_stack)
                             for x in depended]) + 1
            else:
                level = 0
            dependency_levels[cls] = level
            return level

        # Now simply calculate and sort by dependency levels:
        try:
            sorter = []
            for cls in classes:
                level = calculateDependencyLevel(cls)
                sorter.append((level, cls))
            sorter.sort(key=lambda x: x[0])
            ordered_classes = [cls for _, cls in sorter]
        except SQLObjectCircularReferenceError as msg:
            # Failsafe: return the classes as-is if a circular reference
            # prevented the dependency levels to be calculated.
            print("Warning: a circular reference was detected in the "
                  "model. Unable to sort the classes by dependency: they "
                  "will be treated in alphabetic order. This may or may "
                  "not work depending on your database backend. "
                  "The error was:\n%s" % msg)
            return classes
        return ordered_classes

    def __classinit__(cls, new_args):
        if cls.__bases__ == (object,):
            # This abstract base class
            return
        register(cls)

    def __init__(self, invoked_as, command_name, args, runner):
        self.invoked_as = invoked_as
        self.command_name = command_name
        self.raw_args = args
        self.runner = runner

    def run(self):
        self.parser.usage = "%%prog [options]\n%s" % self.summary
        if self.help:
            help = textwrap.fill(
                self.help, int(os.environ.get('COLUMNS', 80)) - 4)
            self.parser.usage += '\n' + help
        self.parser.prog = '%s %s' % (
            os.path.basename(self.invoked_as),
            self.command_name)
        if self.description:
            self.parser.description = self.description
        self.options, self.args = self.parser.parse_args(self.raw_args)
        if (getattr(self.options, 'simulate', False) and
                not self.options.verbose):
            self.options.verbose = 1
        if self.min_args is not None and len(self.args) < self.min_args:
            self.runner.invalid(
                self.min_args_error % {'min_args': self.min_args,
                                       'actual_args': len(self.args)})
        if self.max_args is not None and len(self.args) > self.max_args:
            self.runner.invalid(
                self.max_args_error % {'max_args': self.max_args,
                                       'actual_args': len(self.args)})
        for var_name, option_name in self.required_args:
            if not getattr(self.options, var_name, None):
                self.runner.invalid(
                    'You must provide the option %s' % option_name)
        conf = self.config()
        if conf and conf.get('sys_path'):
            update_sys_path(conf['sys_path'], self.options.verbose)
        if conf and conf.get('database'):
            conn = sqlobject.connectionForURI(conf['database'])
            sqlobject.sqlhub.processConnection = conn
        for egg_spec in getattr(self.options, 'eggs', []):
            self.load_options_from_egg(egg_spec)
        self.command()

    def classes(self, require_connection=True,
                require_some=False):
        all = []
        for module_name in self.options.modules:
            all.extend(self.classes_from_module(
                moduleloader.load_module(module_name)))
        for package_name in self.options.packages:
            all.extend(self.classes_from_package(package_name))
        for egg_spec in self.options.eggs:
            all.extend(self.classes_from_egg(egg_spec))
        if self.options.class_matchers:
            filtered = []
            for soClass in all:
                name = soClass.__name__
                for matcher in self.options.class_matchers:
                    if fnmatch.fnmatch(name, matcher):
                        filtered.append(soClass)
                        break
            all = filtered
        conn = self.connection()
        if conn:
            for soClass in all:
                soClass._connection = conn
        else:
            missing = []
            for soClass in all:
                try:
                    if not soClass._connection:
                        missing.append(soClass)
                except AttributeError:
                    missing.append(soClass)
            if missing and require_connection:
                self.runner.invalid(
                    'These classes do not have connections set:\n  * %s\n'
                    'You must indicate --connection=URI'
                    % '\n  * '.join([soClass.__name__
                                     for soClass in missing]))
        if require_some and not all:
            print('No classes found!')
            if self.options.modules:
                print('Looked in modules: %s' %
                      ', '.join(self.options.modules))
            else:
                print('No modules specified')
            if self.options.packages:
                print('Looked in packages: %s' %
                      ', '.join(self.options.packages))
            else:
                print('No packages specified')
            if self.options.class_matchers:
                print('Matching class pattern: %s' %
                      self.options.class_matches)
            if self.options.eggs:
                print('Looked in eggs: %s' % ', '.join(self.options.eggs))
            else:
                print('No eggs specified')
            sys.exit(1)
        return self.orderClassesByDependencyLevel(all)

    def classes_from_module(self, module):
        all = []
        if hasattr(module, 'soClasses'):
            for name_or_class in module.soClasses:
                if isinstance(name_or_class, str):
                    name_or_class = getattr(module, name_or_class)
                all.append(name_or_class)
        else:
            for name in dir(module):
                value = getattr(module, name)
                if (isinstance(value, type) and
                        issubclass(value, sqlobject.SQLObject) and
                        value.__module__ == module.__name__):
                    all.append(value)
        return all

    def connection(self):
        config = self.config()
        if config is not None:
            assert config.get('database'), (
                "No database variable found in config file %s"
                % self.options.config_file)
            return sqlobject.connectionForURI(config['database'])
        elif getattr(self.options, 'connection_uri', None):
            return sqlobject.connectionForURI(self.options.connection_uri)
        else:
            return None

    def config(self):
        if not getattr(self.options, 'config_file', None):
            return None
        config_file = self.options.config_file
        if appconfig:
            if (not config_file.startswith('egg:') and
                    not config_file.startswith('config:')):
                config_file = 'config:' + config_file
            return appconfig(config_file,
                             relative_to=os.getcwd())
        else:
            return self.ini_config(config_file)

    def ini_config(self, conf_fn):
        conf_section = 'main'
        if '#' in conf_fn:
            conf_fn, conf_section = conf_fn.split('#', 1)

        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        p = ConfigParser()
        # Case-sensitive:
        p.optionxform = str
        if not os.path.exists(conf_fn):
            # Stupid RawConfigParser doesn't give an error for
            # non-existant files:
            raise OSError(
                "Config file %s does not exist" % self.options.config_file)
        p.read([conf_fn])
        p._defaults.setdefault(
            'here', os.path.dirname(os.path.abspath(conf_fn)))

        possible_sections = []
        for section in p.sections():
            name = section.strip().lower()
            if (conf_section == name or
                (conf_section == name.split(':')[-1] and
                    name.split(':')[0] in ('app', 'application'))):
                possible_sections.append(section)

        if not possible_sections:
            raise OSError(
                "Config file %s does not have a section [%s] or [*:%s]"
                % (conf_fn, conf_section, conf_section))
        if len(possible_sections) > 1:
            raise OSError(
                "Config file %s has multiple sections matching %s: %s"
                % (conf_fn, conf_section, ', '.join(possible_sections)))

        config = {}
        for op in p.options(possible_sections[0]):
            config[op] = p.get(possible_sections[0], op)
        return config

    def classes_from_package(self, package_name):
        all = []
        package = moduleloader.load_module(package_name)
        package_dir = os.path.dirname(package.__file__)

        def find_classes_in_file(arg, dir_name, filenames):
            if dir_name.startswith('.svn'):
                return
            filenames = filter(
                lambda fname: fname.endswith('.py') and fname != '__init__.py',
                filenames)
            for fname in filenames:
                module_name = os.path.join(dir_name, fname)
                module_name = module_name[module_name.find(package_name):]
                module_name = module_name.replace(os.path.sep, '.')[:-3]
                try:
                    module = moduleloader.load_module(module_name)
                except ImportError as err:
                    if self.options.verbose:
                        print('Could not import module "%s". '
                              'Error was : "%s"' % (module_name, err))
                    continue
                except Exception as exc:
                    if self.options.verbose:
                        print('Unknown exception while processing module '
                              '"%s" : "%s"' % (module_name, exc))
                    continue
                classes = self.classes_from_module(module)
                all.extend(classes)

        for dirpath, dirnames, filenames in os.walk(package_dir):
            find_classes_in_file(None, dirpath, dirnames + filenames)
        return all

    def classes_from_egg(self, egg_spec):
        modules = []
        dist, conf = self.config_from_egg(egg_spec, warn_no_sqlobject=True)
        for mod in conf.get('db_module', '').split(','):
            mod = mod.strip()
            if not mod:
                continue
            if self.options.verbose:
                print('Looking in module %s' % mod)
            modules.extend(self.classes_from_module(
                moduleloader.load_module(mod)))
        return modules

    def load_options_from_egg(self, egg_spec):
        dist, conf = self.config_from_egg(egg_spec)
        if (hasattr(self.options, 'output_dir') and
                not self.options.output_dir and conf.get('history_dir')):
            dir = conf['history_dir']
            dir = dir.replace('$base', dist.location)
            self.options.output_dir = dir

    def config_from_egg(self, egg_spec, warn_no_sqlobject=True):
        import pkg_resources
        dist = pkg_resources.get_distribution(egg_spec)
        if not dist.has_metadata('sqlobject.txt'):
            if warn_no_sqlobject:
                print('No sqlobject.txt in %s egg info' % egg_spec)
            return None, {}
        result = {}
        for line in dist.get_metadata_lines('sqlobject.txt'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            name, value = line.split('=', 1)
            name = name.strip().lower()
            if name in result:
                print('Warning: %s appears more than once '
                      'in sqlobject.txt' % name)
            result[name.strip().lower()] = value.strip()
        return dist, result

    def command(self):
        raise NotImplementedError

    def _get_prog_name(self):
        return os.path.basename(self.invoked_as)
    prog_name = property(_get_prog_name)

    def ask(self, prompt, safe=False, default=True):
        if self.options.interactive >= 2:
            default = safe
        if default:
            prompt += ' [Y/n]? '
        else:
            prompt += ' [y/N]? '
        while 1:
            response = input(prompt).strip()
            if not response.strip():
                return default
            if response and response[0].lower() in ('y', 'n'):
                return response[0].lower() == 'y'
            print('Y or N please')

    def shorten_filename(self, fn):
        """
        Shortens a filename to make it relative to the current
        directory (if it can).  For display purposes.
        """
        if fn.startswith(os.getcwd() + '/'):
            fn = fn[len(os.getcwd()) + 1:]
        return fn

    def open_editor(self, pretext, breaker=None, extension='.txt'):
        """
        Open an editor with the given text.  Return the new text,
        or None if no edits were made.  If given, everything after
        `breaker` will be ignored.
        """
        fn = nowarning_tempnam() + extension
        f = open(fn, 'w')
        f.write(pretext)
        f.close()
        print('$EDITOR %s' % fn)
        os.system('$EDITOR %s' % fn)
        f = open(fn, 'r')
        content = f.read()
        f.close()
        if breaker:
            content = content.split(breaker)[0]
            pretext = pretext.split(breaker)[0]
        if content == pretext or not content.strip():
            return None
        return content


class CommandSQL(Command):

    name = 'sql'
    summary = 'Show SQL CREATE statements'

    parser = standard_parser(simulate=False)

    def command(self):
        classes = self.classes()
        allConstraints = []
        for cls in classes:
            if self.options.verbose >= 1:
                print('-- %s from %s' % (
                      cls.__name__, cls.__module__))
            createSql, constraints = cls.createTableSQL()
            print(createSql.strip() + ';\n')
            allConstraints.append(constraints)
        for constraints in allConstraints:
            if constraints:
                for constraint in constraints:
                    if constraint:
                        print(constraint.strip() + ';\n')


class CommandList(Command):

    name = 'list'
    summary = 'Show all SQLObject classes found'

    parser = standard_parser(simulate=False, connection=False)

    def command(self):
        if self.options.verbose >= 1:
            print('Classes found:')
        classes = self.classes(require_connection=False)
        for soClass in classes:
            print('%s.%s' % (soClass.__module__, soClass.__name__))
            if self.options.verbose >= 1:
                print('  Table: %s' % soClass.sqlmeta.table)


class CommandCreate(Command):

    name = 'create'
    summary = 'Create tables'

    parser = standard_parser(interactive=True)
    parser.add_option('--create-db',
                      action='store_true',
                      dest='create_db',
                      help="Create the database")

    def command(self):
        v = self.options.verbose
        created = 0
        existing = 0
        dbs_created = []
        constraints = {}
        for soClass in self.classes(require_some=True):
            if (self.options.create_db and
                    soClass._connection not in dbs_created):
                if not self.options.simulate:
                    try:
                        soClass._connection.createEmptyDatabase()
                    except soClass._connection.module.ProgrammingError as e:
                        if str(e).find('already exists') != -1:
                            print('Database already exists')
                        else:
                            raise
                else:
                    print('(simulating; cannot create database)')
                dbs_created.append(soClass._connection)
            if soClass._connection not in constraints.keys():
                constraints[soClass._connection] = []
            exists = soClass._connection.tableExists(soClass.sqlmeta.table)
            if v >= 1:
                if exists:
                    existing += 1
                    print('%s already exists.' % soClass.__name__)
                else:
                    print('Creating %s' % soClass.__name__)
            if v >= 2:
                sql, extra = soClass.createTableSQL()
                print(sql)
            if (not self.options.simulate and not exists):
                if self.options.interactive:
                    if self.ask('Create %s' % soClass.__name__):
                        created += 1
                        tableConstraints = soClass.createTable(
                            applyConstraints=False)
                        if tableConstraints:
                            constraints[soClass._connection].append(
                                tableConstraints)
                    else:
                        print('Cancelled')
                else:
                    created += 1
                    tableConstraints = soClass.createTable(
                        applyConstraints=False)
                    if tableConstraints:
                        constraints[soClass._connection].append(
                            tableConstraints)
        for connection in constraints.keys():
            if v >= 2:
                print('Creating constraints')
            for constraintList in constraints[connection]:
                for constraint in constraintList:
                    if constraint:
                        connection.query(constraint)
        if v >= 1:
            print('%i tables created (%i already exist)' % (
                  created, existing))


class CommandDrop(Command):

    name = 'drop'
    summary = 'Drop tables'

    parser = standard_parser(interactive=True)

    def command(self):
        v = self.options.verbose
        dropped = 0
        not_existing = 0
        for soClass in reversed(self.classes()):
            exists = soClass._connection.tableExists(soClass.sqlmeta.table)
            if v >= 1:
                if exists:
                    print('Dropping %s' % soClass.__name__)
                else:
                    not_existing += 1
                    print('%s does not exist.' % soClass.__name__)
            if (not self.options.simulate and exists):
                if self.options.interactive:
                    if self.ask('Drop %s' % soClass.__name__):
                        dropped += 1
                        soClass.dropTable()
                    else:
                        print('Cancelled')
                else:
                    dropped += 1
                    soClass.dropTable()
        if v >= 1:
            print('%i tables dropped (%i didn\'t exist)' % (
                  dropped, not_existing))


class CommandStatus(Command):

    name = 'status'
    summary = 'Show status of classes vs. database'
    help = ('This command checks the SQLObject definition and checks if '
            'the tables in the database match.  It can always test for '
            'missing tables, and on some databases can test for the '
            'existance of other tables.  Column types are not currently '
            'checked.')

    parser = standard_parser(simulate=False)

    def print_class(self, soClass):
        if self.printed:
            return
        self.printed = True
        print('Checking %s...' % soClass.__name__)

    def command(self):
        good = 0
        bad = 0
        missing_tables = 0
        columnsFromSchema_warning = False
        for soClass in self.classes(require_some=True):
            conn = soClass._connection
            self.printed = False
            if self.options.verbose:
                self.print_class(soClass)
            if not conn.tableExists(soClass.sqlmeta.table):
                self.print_class(soClass)
                print('  Does not exist in database')
                missing_tables += 1
                continue
            try:
                columns = conn.columnsFromSchema(soClass.sqlmeta.table,
                                                 soClass)
            except AttributeError:
                if not columnsFromSchema_warning:
                    print('Database does not support reading columns')
                    columnsFromSchema_warning = True
                good += 1
                continue
            except AssertionError as e:
                print('Cannot read db table %s: %s' % (
                    soClass.sqlmeta.table, e))
                continue
            existing = {}
            for _col in columns:
                _col = _col.withClass(soClass)
                existing[_col.dbName] = _col
            missing = {}
            for _col in soClass.sqlmeta.columnList:
                if _col.dbName in existing:
                    del existing[_col.dbName]
                else:
                    missing[_col.dbName] = _col
            if existing:
                self.print_class(soClass)
                for _col in existing.values():
                    print('  Database has extra column: %s' % _col.dbName)
            if missing:
                self.print_class(soClass)
                for _col in missing.values():
                    print('  Database missing column: %s' % _col.dbName)
            if existing or missing:
                bad += 1
            else:
                good += 1
        if self.options.verbose:
            print('%i in sync; %i out of sync; %i not in database' % (
                  good, bad, missing_tables))


class CommandHelp(Command):

    name = 'help'
    summary = 'Show help'

    parser = optparse.OptionParser()

    max_args = 1

    def command(self):
        if self.args:
            the_runner.run([self.invoked_as, self.args[0], '-h'])
        else:
            print('Available commands:')
            print('  (use "%s help COMMAND" or "%s COMMAND -h" ' % (
                  self.prog_name, self.prog_name))
            print('  for more information)')
            items = sorted(the_runner.commands.items())
            max_len = max([len(cn) for cn, c in items])
            for command_name, command in items:
                print('%s:%s %s' % (command_name,
                                    ' ' * (max_len - len(command_name)),
                                    command.summary))
                if command.aliases:
                    print('%s (Aliases: %s)' % (
                        ' ' * max_len, ', '.join(command.aliases)))


class CommandExecute(Command):

    name = 'execute'
    summary = 'Execute SQL statements'
    help = ('Runs SQL statements directly in the database, with no '
            'intervention.  Useful when used with a configuration file.  '
            'Each argument is executed as an individual statement.')

    parser = standard_parser(find_modules=False)
    parser.add_option('--stdin',
                      help="Read SQL from stdin "
                      "(normally takes SQL from the command line)",
                      dest="use_stdin",
                      action="store_true")

    max_args = None

    def command(self):
        args = self.args
        if self.options.use_stdin:
            if self.options.verbose:
                print("Reading additional SQL from stdin "
                      "(Ctrl-D or Ctrl-Z to finish)...")
            args.append(sys.stdin.read())
        self.conn = self.connection().getConnection()
        self.cursor = self.conn.cursor()
        for sql in args:
            self.execute_sql(sql)

    def execute_sql(self, sql):
        if self.options.verbose:
            print(sql)
        try:
            self.cursor.execute(sql)
        except Exception as e:
            if not self.options.verbose:
                print(sql)
            print("****Error:")
            print('    ', e)
            return
        desc = self.cursor.description
        rows = self.cursor.fetchall()
        if self.options.verbose:
            if not self.cursor.rowcount:
                print("No rows accessed")
            else:
                print("%i rows accessed" % self.cursor.rowcount)
        if desc:
            for (name, type_code, display_size, internal_size,
                    precision, scale, null_ok) in desc:
                sys.stdout.write("%s\t" % name)
            sys.stdout.write("\n")
        for row in rows:
            for _col in row:
                sys.stdout.write("%r\t" % _col)
            sys.stdout.write("\n")
        print()


class CommandRecord(Command):

    name = 'record'
    summary = 'Record historical information about the database status'
    help = ('Record state of table definitions.  The state of each '
            'table is written out to a separate file in a directory, '
            'and that directory forms a "version".  A table is also '
            'added to your database (%s) that reflects the version the '
            'database is currently at.  Use the upgrade command to '
            'sync databases with code.'
            % SQLObjectVersionTable.sqlmeta.table)

    parser = standard_parser()
    parser.add_option('--output-dir',
                      help="Base directory for recorded definitions",
                      dest="output_dir",
                      metavar="DIR",
                      default=None)
    parser.add_option('--no-db-record',
                      help="Don't record version to database",
                      dest="db_record",
                      action="store_false",
                      default=True)
    parser.add_option('--force-create',
                      help="Create a new version even if appears to be "
                      "identical to the last version",
                      action="store_true",
                      dest="force_create")
    parser.add_option('--name',
                      help="The name to append to the version.  The "
                      "version should sort after previous versions (so "
                      "any versions from the same day should come "
                      "alphabetically before this version).",
                      dest="version_name",
                      metavar="NAME")
    parser.add_option('--force-db-version',
                      help="Update the database version, and include no "
                      "database information.  This is for databases that "
                      "were developed without any interaction with "
                      "this tool, to create a 'beginning' revision.",
                      metavar="VERSION_NAME",
                      dest="force_db_version")
    parser.add_option('--edit',
                      help="Open an editor for the upgrader in the last "
                      "version (using $EDITOR).",
                      action="store_true",
                      dest="open_editor")

    version_regex = re.compile(r'^\d\d\d\d-\d\d-\d\d')

    def command(self):
        if self.options.force_db_version:
            self.command_force_db_version()
            return

        v = self.options.verbose
        sim = self.options.simulate
        classes = self.classes()
        if not classes:
            print("No classes found!")
            return

        output_dir = self.find_output_dir()
        version = os.path.basename(output_dir)
        print("Creating version %s" % version)
        conns = []
        files = {}
        for cls in self.classes():
            dbName = cls._connection.dbName
            if cls._connection not in conns:
                conns.append(cls._connection)
            fn = os.path.join(cls.__name__ + '_' + dbName + '.sql')
            if sim:
                continue
            create, constraints = cls.createTableSQL()
            if constraints:
                constraints = '\n-- Constraints:\n%s\n' % (
                    '\n'.join(constraints))
            else:
                constraints = ''
            files[fn] = ''.join([
                '-- Exported definition from %s\n'
                % time.strftime('%Y-%m-%dT%H:%M:%S'),
                '-- Class %s.%s\n'
                % (cls.__module__, cls.__name__),
                '-- Database: %s\n'
                % dbName,
                create.strip(),
                '\n',
                constraints])
        last_version_dir = self.find_last_version()
        if last_version_dir and not self.options.force_create:
            if v > 1:
                print("Checking %s to see if it is current" % last_version_dir)
            files_copy = files.copy()
            for fn in os.listdir(last_version_dir):
                if not fn.endswith('.sql'):
                    continue
                if fn not in files_copy:
                    if v > 1:
                        print("Missing file %s" % fn)
                    break
                f = open(os.path.join(last_version_dir, fn), 'r')
                content = f.read()
                f.close()
                if (self.strip_comments(files_copy[fn]) !=
                        self.strip_comments(content)):
                    if v > 1:
                        print("Content does not match: %s" % fn)
                    break
                del files_copy[fn]
            else:
                # No differences so far
                if not files_copy:
                    # Used up all files
                    print("Current status matches version %s"
                          % os.path.basename(last_version_dir))
                    return
                if v > 1:
                    print("Extra files: %s" % ', '.join(files_copy.keys()))
            if v:
                print("Current state does not match %s"
                      % os.path.basename(last_version_dir))
        if v > 1 and not last_version_dir:
            print("No last version to check")
        if not sim:
            os.mkdir(output_dir)
        if v:
            print('Making directory %s' % self.shorten_filename(output_dir))
        files = sorted(files.items())
        for fn, content in files:
            if v:
                print('  Writing %s' % self.shorten_filename(fn))
            if not sim:
                f = open(os.path.join(output_dir, fn), 'w')
                f.write(content)
                f.close()
        if self.options.db_record:
            all_diffs = []
            for cls in self.classes():
                for conn in conns:
                    diffs = db_differences(cls, conn)
                    for diff in diffs:
                        if len(conns) > 1:
                            diff = '  (%s).%s: %s' % (
                                conn.uri(), cls.sqlmeta.table, diff)
                        else:
                            diff = '  %s: %s' % (cls.sqlmeta.table, diff)
                        all_diffs.append(diff)
            if all_diffs:
                print('Database does not match schema:')
                print('\n'.join(all_diffs))
                for conn in conns:
                    self.update_db(version, conn)
        else:
            all_diffs = []
        if self.options.open_editor:
            if not last_version_dir:
                print("Cannot edit upgrader because there is no "
                      "previous version")
            else:
                breaker = ('-' * 20 + ' lines below this will be ignored ' +
                           '-' * 20)
                pre_text = breaker + '\n' + '\n'.join(all_diffs)
                text = self.open_editor('\n\n' + pre_text, breaker=breaker,
                                        extension='.sql')
                if text is not None:
                    fn = os.path.join(last_version_dir,
                                      'upgrade_%s_%s.sql' %
                                      (dbName, version))
                    f = open(fn, 'w')
                    f.write(text)
                    f.close()
                    print('Wrote to %s' % fn)

    def update_db(self, version, conn):
        v = self.options.verbose
        if not conn.tableExists(SQLObjectVersionTable.sqlmeta.table):
            if v:
                print('Creating table %s'
                      % SQLObjectVersionTable.sqlmeta.table)
            sql = SQLObjectVersionTable.createTableSQL(connection=conn)
            if v > 1:
                print(sql)
            if not self.options.simulate:
                SQLObjectVersionTable.createTable(connection=conn)
        if not self.options.simulate:
            SQLObjectVersionTable.clearTable(connection=conn)
            SQLObjectVersionTable(
                version=version,
                connection=conn)

    def strip_comments(self, sql):
        lines = [l for l in sql.splitlines()
                 if not l.strip().startswith('--')]
        return '\n'.join(lines)

    def base_dir(self):
        base = self.options.output_dir
        if base is None:
            config = self.config()
            if config is not None:
                base = config.get('sqlobject_history_dir', '.')
            else:
                base = '.'
        if not os.path.exists(base):
            print('Creating history directory %s' %
                  self.shorten_filename(base))
            if not self.options.simulate:
                os.makedirs(base)
        return base

    def find_output_dir(self):
        today = time.strftime('%Y-%m-%d', time.localtime())
        if self.options.version_name:
            dir = os.path.join(self.base_dir(), today + '-' +
                               self.options.version_name)
            if os.path.exists(dir):
                print("Error, directory already exists: %s"
                      % dir)
                sys.exit(1)
            return dir
        extra = ''
        while 1:
            dir = os.path.join(self.base_dir(), today + extra)
            if not os.path.exists(dir):
                return dir
            if not extra:
                extra = 'a'
            else:
                extra = chr(ord(extra) + 1)

    def find_last_version(self):
        names = []
        for fn in os.listdir(self.base_dir()):
            if not self.version_regex.search(fn):
                continue
            names.append(fn)
        if not names:
            return None
        names.sort()
        return os.path.join(self.base_dir(), names[-1])

    def command_force_db_version(self):
        v = self.options.verbose
        sim = self.options.simulate
        version = self.options.force_db_version
        if not self.version_regex.search(version):
            print("Versions must be in the format YYYY-MM-DD...")
            print("You version %s does not fit this" % version)
            return
        version_dir = os.path.join(self.base_dir(), version)
        if not os.path.exists(version_dir):
            if v:
                print('Creating %s' % self.shorten_filename(version_dir))
            if not sim:
                os.mkdir(version_dir)
        elif v:
            print('Directory %s exists'
                  % self.shorten_filename(version_dir))
        if self.options.db_record:
            self.update_db(version, self.connection())


class CommandUpgrade(CommandRecord):

    name = 'upgrade'
    summary = 'Update the database to a new version (as created by record)'
    help = ('This command runs scripts (that you write by hand) to '
            'upgrade a database.  The database\'s current version is in '
            'the sqlobject_version table (use record --force-db-version '
            'if a database does not have a sqlobject_version table), '
            'and upgrade scripts are in the version directory you are '
            'upgrading FROM, named upgrade_DBNAME_VERSION.sql, like '
            '"upgrade_mysql_2004-12-01b.sql".')

    parser = standard_parser(find_modules=False)
    parser.add_option('--upgrade-to',
                      help="Upgrade to the given version "
                      "(default: newest version)",
                      dest="upgrade_to",
                      metavar="VERSION")
    parser.add_option('--output-dir',
                      help="Base directory for recorded definitions",
                      dest="output_dir",
                      metavar="DIR",
                      default=None)

    upgrade_regex = re.compile(r'^upgrade_([a-z]*)_([^.]*)\.sql$', re.I)

    def command(self):
        v = self.options.verbose
        sim = self.options.simulate
        if self.options.upgrade_to:
            version_to = self.options.upgrade_to
        else:
            fname = self.find_last_version()
            if fname is None:
                print("No version exists, use 'record' command to create one")
                return
            version_to = os.path.basename(fname)
        current = self.current_version()
        if v:
            print('Current version: %s' % current)
        version_list = self.make_plan(current, version_to)
        if not version_list:
            print('Database up to date')
            return
        if v:
            print('Plan:')
            for next_version, upgrader in version_list:
                print('  Use %s to upgrade to %s' % (
                      self.shorten_filename(upgrader), next_version))
        conn = self.connection()
        for next_version, upgrader in version_list:
            f = open(upgrader)
            sql = f.read()
            f.close()
            if v:
                print("Running:")
                print(sql)
                print('-' * 60)
            if not sim:
                try:
                    conn.query(sql)
                except Exception:
                    print("Error in script: %s" % upgrader)
                    raise
            self.update_db(next_version, conn)
        print('Done.')

    def current_version(self):
        conn = self.connection()
        if not conn.tableExists(SQLObjectVersionTable.sqlmeta.table):
            print('No sqlobject_version table!')
            sys.exit(1)
        versions = list(SQLObjectVersionTable.select(connection=conn))
        if not versions:
            print('No rows in sqlobject_version!')
            sys.exit(1)
        if len(versions) > 1:
            print('Ambiguous sqlobject_version_table')
            sys.exit(1)
        return versions[0].version

    def make_plan(self, current, dest):
        if current == dest:
            return []
        dbname = self.connection().dbName
        next_version, upgrader = self.best_upgrade(current, dest, dbname)
        if not upgrader:
            print('No way to upgrade from %s to %s' % (current, dest))
            print('(you need a %s/upgrade_%s_%s.sql script)'
                  % (current, dbname, dest))
            sys.exit(1)
        plan = [(next_version, upgrader)]
        if next_version == dest:
            return plan
        else:
            return plan + self.make_plan(next_version, dest)

    def best_upgrade(self, current, dest, target_dbname):
        current_dir = os.path.join(self.base_dir(), current)
        if self.options.verbose > 1:
            print('Looking in %s for upgraders'
                  % self.shorten_filename(current_dir))
        upgraders = []
        for fn in os.listdir(current_dir):
            match = self.upgrade_regex.search(fn)
            if not match:
                if self.options.verbose > 1:
                    print('Not an upgrade script: %s' % fn)
                continue
            dbname = match.group(1)
            version = match.group(2)
            if dbname != target_dbname:
                if self.options.verbose > 1:
                    print('Not for this database: %s (want %s)' % (
                          dbname, target_dbname))
                continue
            if version > dest:
                if self.options.verbose > 1:
                    print('Version too new: %s (only want %s)' % (
                          version, dest))
            upgraders.append((version, os.path.join(current_dir, fn)))
        if not upgraders:
            if self.options.verbose > 1:
                print('No upgraders found in %s' % current_dir)
            return None, None
        upgraders.sort()
        return upgraders[-1]


def update_sys_path(paths, verbose):
    if isinstance(paths, string_type):
        paths = [paths]
    for path in paths:
        path = os.path.abspath(path)
        if path not in sys.path:
            if verbose > 1:
                print('Adding %s to path' % path)
            sys.path.insert(0, path)

if __name__ == '__main__':
    the_runner.run(sys.argv)
