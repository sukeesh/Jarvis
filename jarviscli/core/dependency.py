"""
Central Requirements Manager

May check for following requirements:
    * Operating System (Linux, Mac, Windows)
    * Natives (Executable in Path)
    * imports (Python package imports)
    * Network (Offline / Online)
    * API Key (stored in packages/memory/key_vault)

USAGE:
require = Dependency()
requirement_status = require.check([Manifest()])
print(requirement_status.print_count())
print(requirement_status.print_disabled())
print(requirement_status.enabled)
"""

import distutils
import os
import sys

from colorama import Fore


def executable_exists(name):
    binary_path = distutils.spawn.find_executable(name)
    return binary_path is not None and os.access(binary_path, os.X_OK)


class DependencyStatus:
    def __init__(self):
        self.enabled = []
        self.disabled = {}

    def clean(self):
        _enabled_names = [plug['name'] for plug in self.enabled]
        self.disabled = {key: value
                         for key, value in self.disabled.items()
                         if key not in _enabled_names
                         }

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


class Dependency:
    """
    Plugins may have requirement - specified by require().
    Please refere plugin-doku.

    This module checks if dependencies are fulfilled.
    """

    def __init__(self, quality_level='legacy', require_offline_only=False):
        self.quality_level = quality_level

        # plugin should match these requirements
        self._requirement_offline_only = require_offline_only
        if sys.platform == "darwin":
            self._requirement_platform = 'macos'
        elif sys.platform == "win32":
            self._requirement_platform = 'windows'
        elif sys.platform.startswith("linux"):
            self._requirement_platform = 'linux'
        else:
            self._requirement_platform = None
            print("Unsupported platform {}".format(sys.platform))

    def check(self, plugin_list):
        status = DependencyStatus()
        for plugin in plugin_list:
            plugin_status = self._check_plugin(plugin)
            if plugin_status is True:
                status.enabled.append(plugin)
            else:
                plugin_name = plugin['name']
                if plugin_name not in status.disabled:
                    status.disabled[plugin_name] = [str(plugin_status)]
                else:
                    status.disabled[plugin_name].append(str(plugin_status))

        status.clean()
        return status

    def _check_plugin(self, plugin):
        """
        Parses plugin.require(). Plase refere plugin.Plugin-documentation
        """
        if self._requirement_offline_only:
            if plugin['online']:
                return 'online'

        quality_level_ok = self._check_quality_level(plugin['quality'])
        if quality_level_ok is not True:
            return quality_level_ok

        platform_ok = self._check_platform(plugin['requirements']['os'])
        if platform_ok is not True:
            return platform_ok

        natives_ok = self._check_native(plugin['requirements']['native'])
        if natives_ok is not True:
            return natives_ok

        api_key_ok = self._check_api_keys(plugin['requirements']['apikey'])
        if api_key_ok is not True:
            return api_key_ok

        return True

    def _check_platform(self, values):
        if not values:
            return True

        if self._requirement_platform in values:
            return True

        # Failed!
        required_platform = ", ".join(values)
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
        # TODO API KEY MANAGEMENT
        return True
        missing = ""
        for apikey in values:
            if self.key_vault is None:
                requirement_ok = False
            else:
                self.key_vault.add_valid_api_key_name(apikey)
                requirement_ok = self.key_vault.get_user_pass(apikey)[
                    1] is not None

            if not requirement_ok:
                missing += " " + apikey

        if not missing:
            return True

        message = "Missing api key{}. Add with 'apikey add'"
        return message.format(missing)

    def _check_quality_level(self, level):
        from manifest import VALID_QUALITY
        quality_required = VALID_QUALITY.index(self.quality_level)
        quality_plugin = VALID_QUALITY.index(level)
        if quality_plugin < quality_required:
            return 'Quality {} (but required {})'.format(level, self.quality_level)
        else:
            return True
