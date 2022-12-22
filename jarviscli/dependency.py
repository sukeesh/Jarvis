"""
Central Requirements Manager

May check for following requirements:
    * Operating System (Linux, Mac, Windows)
    * Natives (Executable in Path)
    * imports (Python package imports)
    * Network (Offline / Online)
    * API Key (stored in packages/memory/key_vault)
    * User enabled or disabled TODO

Usage:

1. Tag plugins wich @require

    -------------------------
    @require(platform=Platform.Linux, natives=['foo', 'bar'])
    class ExamplePlugin:
        pass
    --------------------------

2. Create Requirements Class and pass list of plugin-instances

    ---------------------------
    require = Requirements()
    requirement_status = require.check([ExamplePlugin()])
    ---------------------------

3. Result is an instance of DependencyStatus

    ---------------------------
    print(requirement_status.print_count())
    print(requirement_status.print_disabled())
    print(requirement_status.enabled)
    ---------------------------
"""

import enum
import sys

from colorama import Fore

from utilities.GeneralUtilities import error, executable_exists, warning


KEY_DISABLED = 'DISABLED_PLUGINS'


class QualityLevel(enum.Enum):
    BROKEN = 0
    DEFAULT = 1

    FULLY_TESTED = 5
    CORE = 6


def quality(quality_level: QualityLevel = QualityLevel.DEFAULT):
    def _quality(plugin):
        plugin.QUALITY = quality_level
        return plugin
    return _quality


def require(network=None, platform=None, native=None, api_key=None, imports=None):
    def _require(plugin):
        require = get_require(plugin)
        if network is not None:
            require.require_network(network)
        if platform is not None:
            require.require_platform(platform)
        if native is not None:
            require.require_native(native)
        if api_key is not None:
            require.require_api_key(api_key)
        if imports is not None:
            require.require_imports(imports)
        return plugin
    return _require


class Platform(enum.Enum):
    MACOS = 0
    LINUX = 1
    WINDOWS = 2
    ANDROID = 3
    # Shortcut for MACOS + LINUX
    UNIX = -1
    # Shortcut for MACOS + LINUX + WINDOW
    DESKTOP = -2
    # there are some plugins that should only be working on a server
    # or when the server is enabled
    SERVER = 4


def get_require(plugin):
    if not hasattr(plugin, '_require'):
        plugin._require = Requirements()
    return plugin._require


class DependencyStatus:
    def __init__(self):
        self.enabled = []
        self.enabled_offline = []
        self.enabled_online = []
        self.disabled = {}
        self.active_disabled = []

    def print_count(self):
        plugin_status_formatter = {
            "disabled": len(self.disabled),
            "enabled": len(self.enabled),
            "red": Fore.RED,
            "blue": Fore.BLUE,
            "reset": Fore.RESET
        }

        plugin_status = "{red}{enabled} {blue}plugins loaded"
        if plugin_status_formatter['disabled'] > 0:
            plugin_status += " {red}{disabled} {blue}plugins disabled.\n"
        plugin_status += "{reset}"

        return plugin_status.format(**plugin_status_formatter)

    def print_disabled(self):
        status = ''
        for disabled, reason in self.disabled.items():
            if len(reason) == 0:
                continue
            status += "{:<20}: {}\n".format(disabled, " OR ".join(reason))
        return status


class Requirements:
    def __init__(self):
        self.platforms = []
        self.natives = []
        self.api_keys = []
        self.imports = []
        self.network = False

    def _require(self, collection, new_elements):
        if isinstance(new_elements, list):
            for element in new_elements:
                self._require(collection, element)
        else:
            element = new_elements
            if element not in collection:
                collection.append(element)

    def require_platform(self, platform):
        self._require(self.platforms, platform)

    def require_native(self, native):
        self._require(self.natives, native)

    def require_api_key(self, api_key):
        self._require(self.api_keys, api_key)

    def require_imports(self, imports):
        self._require(self.imports, imports)

    def require_network(self, network_status):
        if network_status is True:
            self.network = True


class Dependency:
    """
    Plugins may have requirement - specified by require().
    Please refere plugin-doku.

    This module checks if dependencies are fulfilled.
    """

    def __init__(self, key_vault, quality_level, jarvis):
        self.key_vault = key_vault
        self.quality_level = quality_level
        self.disabled = jarvis.get_data(KEY_DISABLED)
        if self.disabled is None:
            self.disabled = {}
            jarvis.update_data(KEY_DISABLED, {})

        # plugin shoud match these requirements
        self._requirement_has_network = True
        if sys.platform == "darwin":
            self._requirement_platform = Platform.MACOS
        elif sys.platform == "win32":
            self._requirement_platform = Platform.WINDOWS
        elif sys.platform.startswith("linux"):
            self._requirement_platform = Platform.LINUX
        else:
            self._requirement_platform = None
            warning("Unsupported platform {}".format(sys.platform))

    def check(self, plugin_list):
        status = DependencyStatus()
        for plugin in plugin_list:
            plugin_status = self._check_plugin(plugin)
            if plugin_status is True:
                status.enabled.append(plugin)
                if get_require(plugin).network:
                    status.enabled_online.append(plugin)
                else:
                    status.enabled_offline.append(plugin)
            else:
                plugin_name = plugin.get_name()
                if plugin_name not in status.disabled:
                    status.disabled[plugin_name] = []
                if plugin_status is False:
                    status.active_disabled.append(plugin_name)
                else:
                    status.disabled[plugin_name].append(plugin_status)

        return status

    def _check_plugin(self, plugin):
        """
        Parses plugin.require(). Plase refere plugin.Plugin-documentation
        """
        requirements = get_require(plugin)

        disabled_ok = self._check_disabled(plugin)
        if disabled_ok is not True:
            return disabled_ok

        quality_level_ok = self._check_quality_level(plugin)
        if quality_level_ok is not True:
            return quality_level_ok

        platform_ok = self._check_platform(requirements.platforms)
        if platform_ok is not True:
            return platform_ok

        natives_ok = self._check_native(requirements.natives)
        if natives_ok is not True:
            return natives_ok

        api_key_ok = self._check_api_keys(requirements.api_keys)
        if api_key_ok is not True:
            return api_key_ok

        imports_ok = self._check_imports(requirements.imports)
        if imports_ok is not True:
            return imports_ok

        return True

    def _check_disabled(self, plugin):
        # to be implemented
        return plugin.get_name() not in self.disabled

    def _check_platform(self, values):
        if not values:
            return True

        if Platform.UNIX in values:
            values += [Platform.LINUX, Platform.MACOS]
        if Platform.DESKTOP in values:
            values += [Platform.LINUX, Platform.WINDOWS, Platform.MACOS]

        if self._requirement_platform in values:
            return True

        # Failed!
        required_platform = ", ".join([x.name for x in values])
        return "Requires os {}".format(required_platform)

    def _check_native(self, values):
        missing = ""
        for native in values:
            if native.startswith('!'):
                # native should not exist
                requirement_ok = not executable_exists(native[1:])
            else:
                requirement_ok = executable_exists(native)

            if not requirement_ok:
                missing += " " + native

        if not missing:
            return True

        message = "Missing native executables{}"
        return message.format(missing)

    def _check_api_keys(self, values):
        missing = ""
        for apikey in values:
            if self.key_vault is None:
                requirement_ok = False
            else:
                self.key_vault.add_valid_api_key_name(apikey)
                requirement_ok = self.key_vault.get_user_pass(apikey)[1] is not None

            if not requirement_ok:
                missing += " " + apikey

        if not missing:
            return True

        message = "Missing api key{}. Add with 'apikey add'"
        return message.format(missing)

    def _check_imports(self, values):
        missing = ""
        for imp in values:
            try:
                __import__(imp)
            except ModuleNotFoundError:
                missing += imp

        if not missing:
            return True

        message = "Missing python import. Install in Jarvis virtualenv (source env/bin/activate && pip install ...)"
        return message.format(missing)

    def _check_quality_level(self, plugin):
        target = QualityLevel.DEFAULT
        if hasattr(plugin, 'QUALITY'):
            target = plugin.QUALITY
        if hasattr(target, 'value'):
            target = target.value
        return target >= self.quality_level
