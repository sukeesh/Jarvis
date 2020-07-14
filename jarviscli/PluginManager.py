import sys
from functools import partial

import pluginmanager

import plugin
from utilities.GeneralUtilities import warning, error, executable_exists


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

        self._plugin_dependency = PluginDependency()

        self._cache = None
        self._plugins_loaded = 0
        self._cache_disabled = []

        # blacklist files
        def __ends_with_py(s):
            return [x for x in s if x.endswith(".py")]
        self._backend.set_file_filters(__ends_with_py)
        self._backend.add_blacklisted_directories("jarviscli/packages/aiml")
        self._backend.add_blacklisted_directories("jarviscli/packages/memory")

    def add_directory(self, path):
        """Add directory to search path for plugins"""
        self._backend.add_plugin_directories(path)
        self._cache = None

    def add_plugin(self, plugin):
        """Add singe plugin-instance"""
        self._backend.add_plugins(plugin)

    def _load(self):
        """lazy load"""
        if self._cache is not None:
            # cache clean!
            return

        self._cache = plugin.PluginStorage()
        self._backend.collect_plugins()
        (enabled, disabled) = self._validate_plugins(self._backend.get_plugins())

        for plugin_to_add in enabled:
            self._load_plugin(plugin_to_add, self._cache)

        self._cache_disabled = self._filter_duplicated_disabled(
            enabled, disabled)
        self._plugins_loaded = len(enabled)

    def _validate_plugins(self, plugins):
        def partition(plugins):
            plugins_valid = []
            plugins_incompatible = []

            for plugin_to_validate in plugins:
                if not is_plugin(plugin_to_validate):
                    continue

                compability_check_result = self._plugin_dependency.check(
                    plugin_to_validate)
                if compability_check_result is True:
                    plugins_valid.append(plugin_to_validate)
                else:
                    item = (
                        plugin_to_validate.get_name(),
                        compability_check_result)
                    plugins_incompatible.append(item)

            return (plugins_valid, plugins_incompatible)

        def is_plugin(plugin_to_validate):
            if not isinstance(plugin_to_validate, pluginmanager.IPlugin):
                return False

            if plugin_to_validate.get_name() == "plugin":
                return False

            return True

        return partition(plugins)

    def _load_plugin(self, plugin_to_add, plugin_storage):
        def handle_aliases(plugin_to_add):
            add_plugin(
                plugin_to_add.get_name().split(' '),
                plugin_to_add,
                plugin_storage)

            for name in plugin_to_add.alias():
                add_plugin(
                    name.lower().split(' '),
                    plugin_to_add,
                    plugin_storage)

        def add_plugin(name, plugin_to_add, parent):
            if len(name) == 1:
                add_plugin_single(name[0], plugin_to_add, parent)
            else:
                add_plugin_compose(name[0], name[1:], plugin_to_add, parent)

        def add_plugin_single(name, plugin_to_add, parent):
            plugin_existing = parent.get_plugins(name)
            if plugin_existing is None:
                parent.add_plugin(name, plugin_to_add)
            else:
                if not plugin_existing.is_callable_plugin():
                    plugin_existing.change_with(plugin_to_add)
                    parent.add_plugin(name, plugin_to_add)
                else:
                    error("Duplicated plugin {}!".format(name))

        def add_plugin_compose(
                name_first,
                name_remaining,
                plugin_to_add,
                parent):
            plugin_existing = parent.get_plugins(name_first)

            if plugin_existing is None:
                plugin_existing = plugin.Plugin()
                plugin_existing._name = name_first
                plugin_existing.__doc__ = ''
                parent.add_plugin(name_first, plugin_existing)

            add_plugin(name_remaining, plugin_to_add, plugin_existing)

        return handle_aliases(plugin_to_add)

    def _filter_duplicated_disabled(self, enabled_list, disabled_list):
        enabled_names = []
        for plugin_enabled in enabled_list:
            enabled_names.append(plugin_enabled.get_name())
            enabled_names.extend(plugin_enabled.alias())

        disabled_unique = {}
        for plugin_name, disable_reason in disabled_list:
            if plugin_name in enabled_names:
                continue

            if plugin_name in disabled_unique:
                disabled_unique[plugin_name].append(disable_reason)
            else:
                disabled_unique[plugin_name] = [disable_reason]

        return disabled_unique

    def get_plugins(self):
        """
        Returns all loaded plugins as dictionary
        Key: name
        Value: plugin instance)
        """
        self._load()
        return self._cache.get_plugins()

    def get_disabled(self):
        """
        Returns all disabled plugins names as dictionary
        Key: name
        Value: List of reasons why disabled
        """
        self._load()
        return self._cache_disabled

    def get_number_plugins_loaded(self):
        self._load()
        return self._plugins_loaded


class PluginDependency(object):
    """
    Plugins may have requirement - specified by require().
    Please refere plugin-doku.

    This module checks if dependencies are fulfilled.
    """

    def __init__(self):
        # plugin shoud match these requirements
        self._requirement_has_network = True
        if sys.platform == "darwin":
            self._requirement_platform = plugin.MACOS
        elif sys.platform == "win32":
            self._requirement_platform = plugin.WINDOWS
        elif sys.platform.startswith("linux"):
            self._requirement_platform = plugin.LINUX
        else:
            self._requirement_platform = None
            warning("Unsupported platform {}".format(sys.platform))

    def _plugin_get_requirements(self, requirements_iter):
        plugin_requirements = {
            "platform": [],
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
                warning("{}={}: No supported requirement".format(key, values))

        return plugin_requirements

    def check(self, plugin):
        """
        Parses plugin.require(). Plase refere plugin.Plugin-documentation
        """
        plugin_requirements = self._plugin_get_requirements(plugin.require())

        if not self._check_platform(plugin_requirements["platform"]):
            required_platform = ", ".join(plugin_requirements["platform"])
            return "Requires os {}".format(required_platform)

        if not self._check_network(plugin_requirements["network"], plugin):
            return "Requires networking"

        natives_ok = self._check_native(plugin_requirements["native"], plugin)
        if natives_ok is not True:
            return natives_ok

        return True

    def _check_platform(self, values):
        if not values:
            return True

        if plugin.UNIX in values:
            values += [plugin.LINUX, plugin.MACOS]

        return self._requirement_platform in values

    def _check_network(self, values, plugin):
        if True in values:
            if not self._requirement_has_network:
                return False
            self._plugin_patch_network_error_message(plugin)
            return True

        return True

    def _check_native(self, values, plugin):
        missing = ""
        for native in values:
            if native.startswith('!'):
                # native should not exist
                requirement_ok = not executable_exists(native[1:])
            else:
                requirement_ok = executable_exists(native)

            if not requirement_ok:
                missing += native
                missing += " "

        if not missing:
            return True

        message = "Missing native executables {}"
        return message.format(missing)

    def _plugin_patch_network_error_message(self, plugin):
        if "plugin._network_error_patched" not in plugin.__dict__:
            plugin.run = partial(
                plugin._plugin_run_with_network_error, plugin.run)
