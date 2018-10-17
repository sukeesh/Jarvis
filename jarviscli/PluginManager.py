import distutils.spawn

import sys
from functools import partial

import pluginmanager
import six
from requests import ConnectionError

import plugin
from utilities.GeneralUtilities import warning, error, executable_exists

if six.PY2:
    from funcsigs import signature as signature
else:
    from inspect import signature as signature


class PluginManager(object):
    """
    Frontend for pluginmanager
    https://github.com/benhoff/pluginmanager
    Also handles plugin.PluginComposed
    """
    def __init__(self):
        self._backend = pluginmanager.PluginInterface()
        self._plugin_dependency = PluginDependency()

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
            if self._plugin_validate(plugin):
                self._load_plugin_handle_alias(plugin)

    def _plugin_validate(self, plugin):
        # I really don't know why that check is necessary...
        if not isinstance(plugin, pluginmanager.IPlugin):
            return False

        if plugin.get_name() == "plugin":
            return False

        # has doc, run, alias, require and complete?
        if not self._plugin_has_method(plugin, "run", 2):
            print("Warning! Plugin \"{}\" has no method \"run\"! Will be disabled!".format(plugin.get_name()))
            return False

        if not self._plugin_has_method(plugin, "alias", 0):
            print("Warning! Plugin \"{}\" has no method \"alias\"!".format(plugin.get_name()))
            plugin.alias = lambda: None

        if not self._plugin_has_method(plugin, "require", 0):
            print("Warning! Plugin \"{}\" has no method \"require\"!".format(plugin.get_name()))
            plugin.require = lambda: None

        if not self._plugin_has_method(plugin, "complete", 0):
            print("Warning! Plugin \"{}\" has no method \"complete\"!".format(plugin.get_name()))
            plugin.complete = lambda: None

        # dependency check
        if not self._plugin_dependency.check(plugin):
            return False

        return True

    def _plugin_has_method(self, plugin, method, param_len):
        if not hasattr(plugin.__class__, method) or not callable(getattr(plugin.__class__, method)):
            return False

        params = signature(getattr(plugin, method)).parameters
        params = [param for param in params if param != 'args']
        if param_len != len(params):
            print("Warning! Wrong parameter number: \"{}\" of \"{}\" ({}, epxected: {})".
                  format(method, plugin.get_name(), len(params), param_len))
            return False

        return True

    def _load_plugin_handle_alias(self, plugin):
        self._load_add_plugin(plugin.get_name(), plugin)

        alias = plugin.alias()
        if alias is not None:
            for name in alias:
                self._load_add_plugin(name.lower(), plugin)

    def _load_add_plugin(self, name, plugin):
        if ' ' in name:
            name_split = name.split(' ')
            self._load_add_composed_plugin(name_split[0], name_split[1], plugin)
        else:
            self._load_add_regular_plugin(name, plugin)

    def _load_add_composed_plugin(self, name_first, name_second, plugin_sub):
        if name_first in self._cache_plugins:
            plugin_composed = self._cache_plugins[name_first]
            if not plugin_composed.is_composed():
                plugin_composed = self._load_convert_into_composed(name_first, plugin_composed)
        else:
            # create new PluginComposed
            plugin_composed = plugin.PluginComposed(name_first)
            self._cache_plugins[name_first] = plugin_composed

        allready_exists = not plugin_composed.try_add_command(plugin_sub, name_second)
        if allready_exists:
            error("Duplicated plugin {} {}".format(name_first, name_second))

    def _load_convert_into_composed(self, name, plugin_default):
        plugin_composed = plugin.PluginComposed(name)
        plugin_composed.try_set_default(plugin_default)
        self._cache_plugins[name] = plugin_composed
        return plugin_composed

    def _load_add_regular_plugin(self, name, plugin):
        if name not in self._cache_plugins:
            self._cache_plugins.update({name: plugin})
            return

        if self._cache_plugins[name].is_composed():
            success = self._cache_plugins[name].try_set_default(plugin)
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


class PluginDependency(object):
    """
    Plugins may have requirement - specified by require().
    Please refere plugin-doku.

    This module checks if dependencies are fulfilled.
    """

    def __init__(self):
        # plugin shoud match these requirements
        self._requirement_has_network = True
        if six.PY2:
            self._requirement_python = plugin.PYTHON2
        else:
            self._requirement_python = plugin.PYTHON3
        if sys.platform == "darwin":
            self._requirement_platform = plugin.MACOS
        else:
            self._requirement_platform = plugin.LINUX

    def _plugin_get_requirements(self, requirements_iter):
        plugin_requirements = {
            "plattform": [],
            "python": [],
            "network": [],
            "native": []
        }

        # parse requirements
        for requirement in requirements_iter:
            key = requirement[0]
            values = requirement[1]

            if isinstance(values, str) or isinstance(values, bool):
                values = [values]

            if key in plugin_requirements:
                plugin_requirements[key].extend(values)
            else:
                warning("{}={}: No supportet requirement".format(key, values))

        return plugin_requirements

    def check(self, plugin):
        """
        Parses plugin.require(). Plase refere plugin.Plugin-documentation
        """
        requirements_iter = plugin.require()
        if requirements_iter is None:
            return True

        plugin_requirements = self._plugin_get_requirements(requirements_iter)

        if not self._check_plattform(plugin_requirements["plattform"]):
            return False

        if not self._check_python(plugin_requirements["python"]):
            return False

        if not self._check_network(plugin_requirements["network"], plugin):
            return False

        if not self._check_native(plugin_requirements["native"], plugin):
            return False

        return True

    def _check_plattform(self, values):
        if len(values) == 0:
            return True

        return self._requirement_platform in values

    def _check_python(self, values):
        if len(values) == 0:
            return True

        return self._requirement_python in values

    def _check_network(self, values, plugin):
        if True in values:
            if not self._requirement_has_network:
                return False
            else:
                self._plugin_patch_network_error_message(plugin)
                return True

        return True

    def _check_native(self, values, plugin):
        missing = ""
        for native in values:
            if not executable_exists(native):
                missing += native
                missing += " "

        if len(missing) == 0:
            return True
        else:
            warning("Disabeling {} - missing native executables {}".format(plugin.get_name(), missing))

    def _plugin_patch_network_error_message(self, plugin):
        if "plugin._network_error_patched" not in plugin.__dict__:
            plugin.run = partial(plugin._plugin_run_with_network_error, plugin.run)
