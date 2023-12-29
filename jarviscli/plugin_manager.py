import sys
from functools import partial

import pluginmanager

import plugin
from dependency import QualityLevel
from plugin import Platform
from utilities.GeneralUtilities import error, executable_exists, warning


class PluginManager(object):
    """
    Frontend for pluginmanager
    https://github.com/benhoff/pluginmanager
    Also handles plugin.PluginComposed
    """

    def __init__(self):
        import pluginmanager.module_manager
        self._backend = pluginmanager.PluginInterface()

        # patch to ignore import exception
        _load_source = pluginmanager.module_manager.load_source

        def patched_load_source(*args):
            try:
                return _load_source(*args)
            except ImportError as e:
                print(e)
            import sys
            return sys
        pluginmanager.module_manager.load_source = patched_load_source

        # blacklist files
        def __ends_with_py(s):
            return [x for x in s if x.endswith(".py")]
        self._backend.set_file_filters(__ends_with_py)
        self._backend.add_blacklisted_directories("jarviscli/packages/aiml")
        self._backend.add_blacklisted_directories("jarviscli/packages/memory")
        self._backend.add_blacklisted_directories("jarviscli/frontend")
        self._backend.add_blacklisted_plugins(plugin.Platform)
        self._backend.add_blacklisted_plugins(QualityLevel)

    def add_directory(self, path):
        """Add directory to search path for plugins"""
        self._backend.add_plugin_directories(path)
        self._cache = None
        return self

    def add_plugin(self, plugin):
        """Add singe plugin-instance"""
        self._backend.add_plugins(plugin)
        return self

    def load(self, dependency):
        def is_plugin(plugin_to_validate):
            if not isinstance(plugin_to_validate, pluginmanager.IPlugin):
                return False

            if plugin_to_validate.get_name() == "plugin":
                return False

            return True

        self._backend.collect_plugins()
        plugins = [plugin for plugin in self._backend.get_plugins() if is_plugin(plugin)]
        dependency_result = dependency.check(plugins)

        plugins_dict = {}
        for plugin_to_add in dependency_result.enabled:
            for name in [plugin_to_add.get_name()] + plugin_to_add.alias():
                if name in plugins_dict:
                    error("Duplicated plugin {}!".format(name))
                    continue
                if name in dependency_result.disabled:
                    del dependency_result.disabled[name]

                plugins_dict[name] = plugin_to_add

        return dependency_result, plugins_dict

    def _load_plugin_witch_aliases(plugin_to_add):
        self.add_plugin(
            plugin_to_add.get_name().split(' '),
            plugin_to_add,
            plugin_storage)

        for name in plugin_to_add.alias():
            self.add_plugin(
                name.lower().split(' '),
                plugin_to_add,
                plugin_storage)

    def add(self, plugin):
        self._backend.add_plugins(plugin)

    def dump_android(self):
        self._load()
        imports = []
        plugins = []

        for _plugin in self._backend.get_instances():
            require = _plugin.require()
            platforms = []
            for key, value in require:
                if key == 'platform':
                    if isinstance(value, plugin.Platform):
                        platforms.append(value)
                    else:
                        platforms.extend(value)

            if plugin.Platform.ANDROID in platforms:
                origin = _plugin._origin.replace('jarviscli.', '')
                imports += [origin]
                plugins += [origin + '.' + _plugin.__class__.__name__]

        imports = sorted(list(set(imports)))
        plugins = sorted(plugins)

        return """\
###############################
#    AUTO-GENERATED FILE      #
#      DO NOT MODIFY          #
###############################

import {}

from plugin_manager import PluginManager


def build_plugin_manager():
    plugin_manager = PluginManager()
    plugin_manager.add({}())

    return plugin_manager
""".format('\nimport '.join(imports),
           '())\nplugin_manager.add('.join(plugins))
