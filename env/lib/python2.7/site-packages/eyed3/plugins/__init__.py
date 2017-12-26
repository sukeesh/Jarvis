# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
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
import os, sys, types

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from eyed3 import core, utils
from eyed3.utils import guessMimetype
from eyed3.utils.console import printMsg, printError

_PLUGINS = {}

from ..utils.log import getLogger
log = getLogger(__name__)


def load(name=None, reload=False, paths=None):
    '''Returns the eyed3.plugins.Plugin *class* identified by ``name``.
    If ``name`` is ``None`` then the full list of plugins is returned.
    Once a plugin is loaded its class object is cached, and future calls to
    this function will returned the cached version. Use ``reload=True`` to
    refresh the cache.'''
    global _PLUGINS

    if len(list(_PLUGINS.keys())) and not reload:
        # Return from the cache if possible
        try:
            return _PLUGINS[name] if name else _PLUGINS
        except KeyError:
            # It's not in the cache, look again and refresh cash
            _PLUGINS = {}
    else:
        _PLUGINS = {}

    def _isValidModule(f, d):
        '''Determine if file ``f`` is a valid module file name.'''
        # 1) tis a file
        # 2) does not start with '_', or '.'
        # 3) avoid the .pyc dup
        return bool(os.path.isfile(os.path.join(d, f))
                    and f[0] not in ('_', '.')
                    and f.endswith(".py"))

    log.debug("Extra plugin paths: %s" % paths)
    for d in [os.path.dirname(__file__)] + (paths if paths else []):
        log.debug("Searching '%s' for plugins", d)
        if not os.path.isdir(d):
            continue

        if d not in sys.path:
            sys.path.append(d)
        try:
            for f in os.listdir(d):
                if not _isValidModule(f, d):
                    continue

                mod_name = os.path.splitext(f)[0]
                try:
                    mod = __import__(mod_name, globals=globals(),
                                     locals=locals())
                except ImportError as ex:
                    log.warning("Plugin '%s' requires packages that are not "
                                "installed: %s" % ((f, d), ex))
                    continue
                except Exception as ex:
                    log.exception("Bad plugin '%s'", (f, d))
                    continue

                for attr in [getattr(mod, a) for a in dir(mod)]:
                    if (type(attr) == type and issubclass(attr, Plugin)):
                        # This is a eyed3.plugins.Plugin
                        PluginClass = attr
                        if (PluginClass not in list(_PLUGINS.values()) and
                                len(PluginClass.NAMES)):
                            log.debug("loading plugin '%s' from '%s%s%s'",
                                      mod, d, os.path.sep, f)
                            # Setting the main name outside the loop to ensure
                            # there is at least one, otherwise a KeyError is
                            # thrown.
                            main_name = PluginClass.NAMES[0]
                            _PLUGINS[main_name] = PluginClass
                            for alias in PluginClass.NAMES[1:]:
                                # Add alternate names
                                _PLUGINS[alias] = PluginClass

                            # If 'plugin' is found return it immediately
                            if name and name in PluginClass.NAMES:
                                return PluginClass

        finally:
            if d in sys.path:
                sys.path.remove(d)

    log.debug("Plugins loaded: %s", _PLUGINS)
    if name:
        # If a specific plugin was requested and we've not returned yet...
        return None
    return _PLUGINS


class Plugin(utils.FileHandler):
    '''Base class for all eyeD3 plugins'''

    SUMMARY = u"eyeD3 plugin"
    '''One line about the plugin'''

    DESCRIPTION = u""
    '''Detailed info about the plugin'''

    NAMES = []
    '''A list of **at least** one name for invoking the plugin, values [1:]
    are treated as alias'''

    def __init__(self, arg_parser):
        self.arg_parser = arg_parser
        self.arg_group = arg_parser.add_argument_group("Plugin options",
                                                  "%s\n%s" % (self.SUMMARY,
                                                              self.DESCRIPTION))

    def start(self, args, config):
        '''Called after command line parsing but before any paths are
        processed. The ``self.args`` argument (the parsed command line) and
        ``self.config`` (the user config, if any) is set here.'''
        self.args = args
        self.config = config

    def handleFile(self, f):
        pass

    def handleDone(self):
        '''Called after all file/directory processing; before program exit.
        The return value is passed to sys.exit (None results in 0).'''
        pass


class LoaderPlugin(Plugin):
    '''A base class that provides auto loading of audio files'''

    def __init__(self, arg_parser, cache_files=False, track_images=False):
        '''Constructor. If ``cache_files`` is True (off by default) then each
        AudioFile is appended to ``_file_cache`` during ``handleFile`` and
        the list is cleared by ``handleDirectory``.'''
        super(LoaderPlugin, self).__init__(arg_parser)
        self._num_loaded = 0
        self._file_cache = [] if cache_files else None
        self._dir_images = [] if track_images else None

    def handleFile(self, f, *args, **kwargs):
        '''Loads ``f`` and sets ``self.audio_file`` to an instance of
        :class:`eyed3.core.AudioFile` or ``None`` if an error occurred or the
        file is not a recognized type.

        The ``*args`` and ``**kwargs`` are passed to :func:`eyed3.core.load`.
        '''
        self.audio_file = None

        try:
            self.audio_file = core.load(f, *args, **kwargs)
        except NotImplementedError as ex:
            # Frame decryption, for instance...
            printError(str(ex))
            return

        if self.audio_file:
            self._num_loaded += 1
            if self._file_cache is not None:
                self._file_cache.append(self.audio_file)
        elif self._dir_images is not None:
            mt = guessMimetype(f)
            if mt and mt.startswith("image/"):
                self._dir_images.append(f)

    def handleDirectory(self, d, _):
        '''Override to make use of ``self._file_cache``. By default the list
        is cleared, subclasses should consider doing the same otherwise every
        AudioFile will be cached.'''
        if self._file_cache is not None:
            self._file_cache = []

        if self._dir_images is not None:
            self._dir_images = []

    def handleDone(self):
        '''If no audio files were loaded this simply prints "Nothing to do".'''
        if self._num_loaded == 0:
            printMsg("Nothing to do")
