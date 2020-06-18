import tempfile
from cmd import Cmd
from typing import Dict, Optional

from colorama import Fore

from api import JarvisAPI
from plugin import Plugin
from plugin_manager import PluginManager
from utilities.GeneralUtilities import warning

# register hist path via tempfile
HISTORY_FILENAME = tempfile.TemporaryFile('w+t')


class Jarvis:
    def __init__(self, language_parser, plugin_manager):
        self.jarvis_api = JarvisAPI()
        self.language_parser = language_parser
        self.plugin_manager = plugin_manager

        self.language_parser.train(self.plugin_manager.get_plugins().values())

        self.cache = ''
        self.stdout = self

    def register_io(self, jarvis_io):
        self.jarvis_api.io = jarvis_io
        return self.jarvis_api

    def plugin_info(self):
        plugin_status_formatter = {
            "disabled": len(self.plugin_manager.get_disabled()),
            "enabled": self.plugin_manager.get_number_plugins_loaded(),
            "red": Fore.RED,
            "blue": Fore.BLUE,
            "reset": Fore.RESET
        }

        plugin_status = "{red}{enabled} {blue}plugins loaded"
        if plugin_status_formatter['disabled'] > 0:
            plugin_status += " {red}{disabled} {blue}plugins disabled. More information: {red}status\n"
        plugin_status += Fore.RESET

        return plugin_status.format(**plugin_status_formatter)

    def activate_plugins(self):
        """Generate do_XXX, help_XXX and (optionally) complete_XXX functions"""
        for (plugin_name, plugin) in self.plugin_manager.get_plugins().items():
            yield plugin
            plugin.init(self.jarvis_api)

    def execute_once(self, command: str) -> Optional[bool]:
        # save commands' history
        HISTORY_FILENAME.write(command + '\n')

        plugin = self.language_parser.identify_action(command)

        if command.startswith('help'):
            self.do_help(plugin)
            return True

        if plugin is None:
            return None

        s = self.build_s_string(command, plugin)
        ret = plugin.run(self.jarvis_api, s)

        if ret is False:
            return False
        return True

    def build_s_string(self, data: str, plugin: Plugin):
        features = self._parse_plugin_features(plugin.feature())

        if not features['punctuation']:
            data = data.replace("?", "")
            data = data.replace("!", "")
            data = data.replace(",", "")

        if not features['case_sensitive']:
            data = data.lower()

        data = data.replace(plugin.get_name(), '')
        for alias in plugin.alias():
            data = data.replace(alias, '')
        data = data.strip()
        data = " ".join(data.split())
        return data

    def _parse_plugin_features(self, features_iter):
        plugin_features = {
            "case_sensitive": False,
            "punctuation": True
        }

        if features_iter is None:
            return plugin_features

        for feature in features_iter:
            key = feature[0]
            value = feature[1]

            if not isinstance(value, bool):
                warning("{}={}: No supported requirement".format(key, value))

            if key in plugin_features:
                plugin_features[key] = value
            else:
                warning("{}={}: No supported requirement".format(key, value))

        return plugin_features

    def do_help(self, plugin: Optional[Plugin]):
        if plugin is not None:
            self.jarvis_api.say(plugin.get_doc())
        else:
            self.jarvis_api.say("")
            headerString = "These are valid commands for Jarvis"
            formatString = "Format: command ([aliases for command])"
            self.jarvis_api.say(headerString)
            self.jarvis_api.say(formatString, Fore.BLUE)
            pluginDict = self.plugin_manager.get_plugins()
            uniquePlugins: Dict[str, Plugin] = {}
            for key in pluginDict.keys():
                plugin = pluginDict[key]
                if(plugin not in uniquePlugins.keys()):
                    uniquePlugins[plugin.get_name()] = plugin
            helpOutput = []
            for name in sorted(uniquePlugins.keys()):
                if (name == "help"):
                    continue
                try:
                    aliasString = ", ".join(uniquePlugins[name].alias())
                    if (aliasString != ""):
                        pluginOutput = "* " + name + " (" + aliasString + ")"
                        helpOutput.append(pluginOutput)
                    else:
                        helpOutput.append("* " + name)
                except AttributeError:
                    helpOutput.append("* " + name)

            Cmd.columnize(self, helpOutput, displaywidth=100)

    def write(self, line):
        if line.endswith('\n'):
            self.jarvis_api.say(self.cache + line[:-1])
            self.cache = ''
        else:
            self.cache += line
