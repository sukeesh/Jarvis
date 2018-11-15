from inspect import cleandoc, isclass

import pluginmanager
from requests import ConnectionError


# Constants
# python
PYTHON2 = "PY2"
PYTHON3 = "PY3"
# platform
MACOS = "MACOS"
LINUX = "LINUX"


class Plugin(pluginmanager.IPlugin):
    """
    Class name = Command name
    Docstring = Help displayed when typing "help COMMAND"

    Each plugin MUST implement these methods:

    * require()
        -> Iterator of requirement

        A requirement may be
          * (key: string, value)
          * (key: string, (value0, value1, value2, ...))
        Implemented requirements are:
            python: PYTHON2, PYTHON3
            platform: LINUX, MACOS
            network: True, False
            native: String (any executable in PATH)
        A Plugin is "compabible" if all requirements are fulfilled.
        A requirement is fulfilled if value or one of (value0, value1, value2, ...)
        matches host configuration.
        Non "compabible" plugins will be ignored and not displayed.
        If plugin is not "compaibile" because of native-requirement, an error
        message is show "Please install XXX".
        If plugin requires Network, requests.ConnecitonError is auto-catched
        and jarvis.connection_error() will be called.

    * complete()
        -> Iterator<String>

        CmdInterpreter's complete_XXX method will return these strings.
        Use for two-part commands like "wiki search", "wiki summary" and "wiki content".
        In this case yield "search", "summary" and "content"

    * alias()
        -> Iterator<String>

        Return alternative names for this command.
        TODO: implement

    * run(jarvis, s)
        ->

        Called when plugin is executed. s is the user command.
        jarvis is an instance of CmdInterpreter.JarvisAPI
        e.g. to say text type jarvis.say("TEXT")
        Please refere JarvisAPI documentation for all available methods.
    """
    def init(self, jarvis):
        """Overwrite"""
        pass

    def require(self):
        return self._require

    def complete(self):
        return self._complete

    def alias(self):
        return self._alias

    def get_name(self):
        return self._name

    def get_doc(self):
        if self.__doc__ is None:
            return "Sorry - no description available."
        return cleandoc(self.__doc__)

    def is_composed(self):
        return False

    def _plugin_run_with_network_error(self, run_func, jarvis, s):
        """
        Calls run_func(jarvis, s); try-catch ConnectionError

        This method is auto-used if require() yields ("network", True). Do not
        use manually.
        """
        try:
            run_func(jarvis, s)
        except ConnectionError:
            jarvis.connection_error()


def plugin(name):
    """
    Convert function in Plugin Class

    @python(platform=LINUX, native="ap-hotspot")
    def hotspot_start(jarvis, s):
        system("sudo ap-hotspot start")
    """
    def create_plugin(run):
        if isclass(run):
            # class -> object
            run_instance = run()

            def __run_method(self, jarvis, s):
                run_instance(jarvis, s)
        else:
            def __run_method(self, jarvis, s):
                print("--> {}".format(s))
                run(jarvis, s)

        # create class
        plugin_class = type(run.__name__, Plugin.__bases__, dict(Plugin.__dict__))
        plugin_class.run = __run_method
        plugin_class.__doc__ = run.__doc__

        plugin_class._require = []
        plugin_class._complete = []
        plugin_class._alias = []
        plugin_class._name = name
        plugin_class._backend = run

        return plugin_class
    return create_plugin


def require(network=None, platform=None, python=None, native=None):
    require = []
    if network is not None:
        require.append(('network', network))
    if platform is not None:
        require.append(('platform', platform))
    if python is not None:
        require.append(('python', python))
    if native is not None:
        require.append(('native', native))

    def __require(plugin):
        plugin._require.extend(require)
        return plugin
    return __require


def complete(*complete):
    def __complete(plugin):
        plugin._complete.extend(complete)
        return plugin
    return __complete


def alias(*alias):
    def __alias(plugin):
        plugin._alias.extend(alias)
        return plugin
    return __alias


def _yield_something(values):
    for value in values:
        yield value


def _return_none(*args):
    return None


class PluginComposed(object):
    """
    Problem:
    Take a plugin "check" which supports "check ram" and "check weather".
    ram and weather do not have much in common and being forced to implement
    every "check" command in on plugin is not good (bad modularisation, not
    extensible, bad dependency management, ...).

    Solution:
    Let PluginManager take care of two-word commands!

    To solve the check-problem create two plugins:
    * Check_ram
    * Check_weather
    And that's it!

    PluginManager will recognise _ as space - and create a new PluginComposed
    "check" with "ram" and "weather" as sub-commands.

    * Help command will be composed out of all help docs of sub commands
    * complete() is not necessary nor recommendet for sub-commands since it will
      be ignored! "check" of PluginComposed will yield name of all sub commands
    * If "check" is executed and the command contains "ram", Check_ram.run()
      will be executed. Otherwise - if "weather" in command, Check_weather.run()
      will be executed.
    * It is even possible to create a own Plugin "check". This plugin will be
      added as "default" and executed if no sub command matches. If no "default"
      exists an error message will be print.

    """
    def __init__(self, name):
        self._name = name
        self._command_default = None
        self._command_sub = {}

    def init(self, jarvis):
        if self._command_default is not None:
            if hasattr(self._command_default.__class__, "init") and callable(getattr(self._command_default.__class__, "init")):
                self._command_default.init(jarvis)
        for plugin in self._command_sub.values():
            if hasattr(plugin.__class__, "init") and callable(getattr(plugin.__class__, "init")):
                plugin.init(jarvis)

    def get_name(self):
        return self._name

    def is_composed(self):
        return True

    def try_add_command(self, sub_command, name):
        """Regist new sub command. Return False, if sub command with same name
        allready exists"""
        if name in self._command_sub.keys():
            return False
        else:
            self._command_sub.update({name: sub_command})
            return True

    def try_set_default(self, command):
        """Set default, return False if default allready set"""
        if self._command_default is None:
            self._command_default = command
            return True
        else:
            return False

    def complete(self):
        # return default complete() if possible
        if self._command_default is not None:
            complete = self._command_default.complete()
            if complete is not None:
                for complete in complete:
                    yield complete

        # yield each sub command
        for complete in self._command_sub.keys():
            yield complete

    def get_doc(self):
        doc = ""
        examples = ""
        extended_doc = ""

        # default complete
        if self._command_default is not None:
            default_command_doc = self._command_default.get_doc()
            default_command_doc = default_command_doc.split("-- Example:")
            if len(default_command_doc) > 1:
                examples += default_command_doc[1]
            default_command_doc = default_command_doc[0]

            doc += default_command_doc
            if not doc.endswith("\n"):
                doc += "\n"
            doc += "\nSubcommands:"

        # sub command complete
        for name, sub_command in self._command_sub.items():
            doc += "\n-> {}: ".format(name)

            sub_command_doc = sub_command.get_doc()
            sub_command_doc = sub_command_doc.split("-- Example:")
            if len(sub_command_doc) > 1:
                examples += sub_command_doc[1]
            sub_command_doc = sub_command_doc[0]

            if '\n' not in sub_command_doc:
                doc += sub_command_doc
            else:
                extended_doc += "\n  {}:\n".format(name)
                extended_doc += sub_command_doc
                if not sub_command_doc.endswith("\n"):
                    extended_doc += "\n"

        if extended_doc != "":
            doc += "\n"
            doc += extended_doc

        if examples != "":
            doc += "\n--Examples:"
            doc += examples

        return doc

    def run(self, jarvis, s):
        # run sub command
        for name, sub_command in self._command_sub.items():
            if name in s:
                if s.startswith(name):
                    s = s[len(name):]
                    s = s.lstrip()

                    sub_command.run(jarvis, s)
                    return

        # run default
        if self._command_default is not None:
            self._command_default.run(jarvis, s)
            return

        jarvis.say("Sorry, I don't know what you mean...")
