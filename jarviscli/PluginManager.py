import distutils.spawn
import sys
from functools import partial

import pluginmanager
import six
from requests import ConnectionError

import plugin
from utilities.GeneralUtilities import warning, error


class PluginManager(object):
    """
    Frontend for pluginmanager
    https://github.com/benhoff/pluginmanager
    Also handles plugin.PluginComposed
    """
    def __init__(self):
        self._backend = pluginmanager.PluginInterface()

        self._cache_clean = False
        self._cache_plugins = {}

        # blacklist files
        def __ends_with_py(s):
            return [x for x in s if x.endswith(".py")]
        self._backend.set_file_filters(__ends_with_py)
        self._backend.add_blacklisted_directories("jarviscli/packages/aiml")
        self._backend.add_blacklisted_directories("jarviscli/packages/memory")

    def add_directory(self, path):
        """Add directory to search path for plugins"""
        self._backend.add_plugin_directories(path)

        self._cache_clean = False

    def add_plugin(self, plugin):
        """Add singe plugin-instance"""
        self._backend.add_plugins(plugin)

    def _load(self):
        """lazy load"""
        self._cache_clean = True
        self._cache_plugins = {}

        self._backend.collect_plugins()
        for plugin in self._backend.get_plugins():
            # I really don't know why that check is necessary...
            if not isinstance(plugin, pluginmanager.IPlugin):
                continue
            if plugin.get_name() != "plugin":
                self._load_plugin_handle_alias(plugin)

    def _load_plugin_handle_alias(self, plugin):
        self._load_add_plugin(plugin.get_name(), plugin)

        alias = plugin.alias()
        if alias is not None:
            for name in alias:
                self._load_add_plugin(name.lower(), plugin)

    def _load_add_plugin(self, name, plugin):
        if name not in self._cache_plugins:
            self._cache_plugins.update({name: plugin})
            return

        if self._cache_plugins[name].is_composed():
            success = self._cache_plugins[name].try_set_fallback(plugin)
            if success:
                return

        error("Duplicated plugin {}!".format(name))

    def get_all(self):
        """Returns all loaded plugins as dictionary (key: name, value: plugin instance)"""
        if not self._cache_clean:
            self._load()

        return self._cache_plugins

    def get_by_name(self, name):
        """Returns one plugin with given name or None if not found"""
        if not self._cache_clean:
            self._load()

        name = name.lower()
        if name in self._cache_plugins:
            return self._cache_plugins[name]

        return None
