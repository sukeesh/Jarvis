# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2009-2012  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from __future__ import print_function
import os
import sys
import textwrap
import warnings

import eyed3
import eyed3.utils
import eyed3.utils.console
import eyed3.plugins
import eyed3.info
from eyed3.compat import ConfigParser, ConfigParserError, StringIO

from eyed3.utils.log import initLogging
initLogging()

DEFAULT_PLUGIN = "classic"
DEFAULT_CONFIG = eyed3.info.USER_CONFIG


def main(args, config):
    if args.list_plugins:
        _listPlugins(config)
        return 0

    args.plugin.start(args, config)

    # Process paths (files/directories)
    for p in args.paths:
        eyed3.utils.walk(args.plugin, p, excludes=args.excludes,
                         fs_encoding=args.fs_encoding)

    retval = args.plugin.handleDone()

    return retval or 0


def _listPlugins(config):
    from eyed3.utils.console import Fore, Style

    print("")

    def header(name):
        is_default = name == DEFAULT_PLUGIN
        return (Style.BRIGHT + (Fore.GREEN if is_default else '') + "* " +
                name + Style.RESET_ALL)

    all_plugins = eyed3.plugins.load(reload=True, paths=_getPluginPath(config))
    # Create a new dict for sorted display
    plugin_names = []
    for plugin in set(all_plugins.values()):
        plugin_names.append(plugin.NAMES[0])

    print("Type 'eyeD3 --plugin=<name> --help' for more help")
    print("")

    plugin_names.sort()
    for name in plugin_names:
        plugin = all_plugins[name]

        alt_names = plugin.NAMES[1:]
        alt_names = " (%s)" % ", ".join(alt_names) if alt_names else ""

        print("%s %s:" % (header(name), alt_names))
        for l in textwrap.wrap(plugin.SUMMARY,
                               initial_indent=' ' * 2,
                               subsequent_indent=' ' * 2):
            print(Style.BRIGHT + Fore.GREY + l + Style.RESET_ALL)
        print("")


def _loadConfig(args):
    import os

    config = None
    config_file = None

    if args.config:
        config_file = os.path.abspath(config_file)
    elif args.no_config is False:
        config_file = DEFAULT_CONFIG

    if not config_file:
        return None

    if os.path.isfile(config_file):
        try:
            config = ConfigParser()
            config.read(config_file)
        except ConfigParserError as ex:
            eyed3.log.warning("User config error: " + str(ex))
            return None
    elif config_file != DEFAULT_CONFIG:
        raise IOError("User config not found: %s" % config_file)

    return config


def _getPluginPath(config):
    plugin_path = [eyed3.info.USER_PLUGINS_DIR]

    if config and config.has_option("default", "plugin_path"):
        val = config.get("default", "plugin_path")
        plugin_path += [os.path.expanduser(os.path.expandvars(d)) for d
                            in val.split(':') if val]
    return plugin_path


def profileMain(args, config):  # pragma: no cover
    '''This is the main function for profiling
    http://code.google.com/appengine/kb/commontasks.html#profiling
    '''
    import cProfile
    import pstats

    eyed3.log.debug("driver profileMain")
    prof = cProfile.Profile()
    prof = prof.runctx("main(args)", globals(), locals())

    stream = StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(100)  # 80 = how many to print

    # The rest is optional.
    stats.print_callees()
    stats.print_callers()
    sys.stderr.write("Profile data:\n%s\n" % stream.getvalue())

    return 0


def makeCmdLineParser(subparser=None):
    from eyed3.utils import ArgumentParser

    p = (ArgumentParser(prog=eyed3.info.NAME, add_help=True)
            if not subparser else subparser)

    p.add_argument("paths", metavar="PATH", nargs="*",
                   help="Files or directory paths")
    p.add_argument("--exclude", action="append", metavar="PATTERN",
                   dest="excludes",
                   help="A regular expression for path exclusion. May be "
                        "specified multiple times.")
    p.add_argument("-L", "--plugins", action="store_true", default=False,
                   dest="list_plugins", help="List all available plugins")
    p.add_argument("-P", "--plugin", action="store", dest="plugin",
                   default=None, metavar="NAME",
                   help="Specify which plugin to use. The default is '%s'" %
                        DEFAULT_PLUGIN)
    p.add_argument("-C", "--config", action="store", dest="config",
                   default=None, metavar="FILE",
                   help="Supply a configuration file. The default is "
                        "'%s', although even that is optional." %
                        DEFAULT_CONFIG)
    p.add_argument("--backup", action="store_true", dest="backup",
                   help="Plugins should honor this option such that "
                        "a backup is made of any file modified. The backup "
                        "is made in same directory with a '.orig' "
                        "extension added.")
    p.add_argument("-Q", "--quiet", action="store_true", dest="quiet",
                   default=False, help="A hint to plugins to output less.")
    p.add_argument("--fs-encoding", action="store",
                   dest="fs_encoding", default=eyed3.LOCAL_FS_ENCODING,
                   metavar="ENCODING",
                   help="Use the specified file system encoding for "
                        "filenames.  Default as it was detected is '%s' "
                        "but this option is still useful when reading "
                        "from mounted file systems." %
                        eyed3.LOCAL_FS_ENCODING)
    p.add_argument("--no-config", action="store_true", dest="no_config",
                   help="Do not load the default user config '%s'. "
                        "The -c/--config options are still honored if "
                        "present." % DEFAULT_CONFIG)
    p.add_argument("--no-color", action="store_true", dest="no_color",
                   help="Suppress color codes in console output. "
                        "This will happen automatically if the output is "
                        "not a TTY (e.g. when redirecting to a file)")

    # Debugging options
    group = p.debug_arg_group
    group.add_argument("--profile", action="store_true", default=False,
                       dest="debug_profile",
                       help="Run using python profiler.")
    group.add_argument("--pdb", action="store_true", dest="debug_pdb",
                       help="Drop into 'pdb' when errors occur.")
    return p


def parseCommandLine(cmd_line_args=None):

    cmd_line_args = list(cmd_line_args) if cmd_line_args else list(sys.argv[1:])

    # Remove any options not related to plugin/config for first parse. These
    # determine the parser for the next stage.
    stage_one_args = []
    idx, auto_append = 0, False
    while idx < len(cmd_line_args):
        opt = cmd_line_args[idx]
        if auto_append:
            stage_one_args.append(opt)
            auto_append = False

        if opt in ("-C", "--config", "-P", "--plugin", "--no-config"):
            stage_one_args.append(opt)
            if opt != "--no-config":
                auto_append = True
        elif (opt.startswith("-C=") or opt.startswith("--config=") or
                opt.startswith("-P=") or opt.startswith("--plugin=")):
            stage_one_args.append(opt)
        idx += 1

    parser = makeCmdLineParser()
    args = parser.parse_args(stage_one_args)

    config = _loadConfig(args)

    if args.plugin:
        # Plugin on the command line takes precedence over config.
        plugin_name = args.plugin
    elif config and config.has_option("default", "plugin"):
        # Get default plugin from config or use DEFAULT_CONFIG
        plugin_name = config.get("default", "plugin")
        if not plugin_name:
            plugin_name = DEFAULT_PLUGIN
    else:
        plugin_name = DEFAULT_PLUGIN
    assert(plugin_name)

    PluginClass = eyed3.plugins.load(plugin_name, paths=_getPluginPath(config))
    if PluginClass is None:
        eyed3.utils.console.printError("Plugin not found: %s" % plugin_name)
        parser.exit(1)
    plugin = PluginClass(parser)

    if config and config.has_option("default", "options"):
        cmd_line_args.extend(config.get("default", "options").split())
    if config and config.has_option(plugin_name, "options"):
        cmd_line_args.extend(config.get(plugin_name, "options").split())

    # Reparse the command line including options from the config.
    args = parser.parse_args(args=cmd_line_args)

    args.plugin = plugin
    eyed3.log.debug("command line args: %s", args)
    eyed3.log.debug("plugin is: %s", plugin)

    return args, parser, config


if __name__ == "__main__":  # pragma: no cover
    retval = 1

    # We should run against the same install
    eyed3.require(eyed3.info.VERSION)

    try:
        args, _, config = parseCommandLine()

        eyed3.utils.console.AnsiCodes.init(not args.no_color)

        mainFunc = main if args.debug_profile is False else profileMain
        retval = mainFunc(args, config)
    except KeyboardInterrupt:
        retval = 0
    except (StopIteration, IOError) as ex:
        eyed3.utils.console.printError(unicode(ex))
        retval = 1
    except Exception as ex:
        eyed3.utils.console.printError("Uncaught exception: %s\n" % str(ex))
        eyed3.log.exception(ex)

        if args.debug_pdb:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", PendingDeprecationWarning)
                    # Must delay the import of ipdb as say as possible because
                    # of https://github.com/gotcha/ipdb/issues/48
                    import ipdb as pdb
            except ImportError:
                import pdb

            e, m, tb = sys.exc_info()
            pdb.post_mortem(tb)
    finally:
        sys.exit(retval)

# vim: set ft=python:
