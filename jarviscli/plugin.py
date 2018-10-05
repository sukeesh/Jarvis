from functools import partial
from inspect import cleandoc

import pluginmanager
from requests import ConnectionError


# Constants
# python
PYTHON2 = "PY2"
PYTHON3 = "PY3"
# plattform
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
            plattform: LINUX, MACOS
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
    def get_name(self):
        """
        * Lower case
        * Remove everything after __
        * replace '_' with Space
        """
        return self.__class__.__name__.lower().split("__", 1)[0].replace("_", " ")

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


def plugin(network=None, plattform=None, python=None, native=None):
    """
    The plugin-decorator is an alternative Plugin declaration. This decorator basically
    takes a method and creates a Plugin-class.

    Pass requirements as plugin-parameters
    Doc-String of method will be copied.
    Run-method = function
    To specify complete and alias-method use @require, @complete and @alias

    Example:

    @python(plattform=LINUX, native="ap-hotspot")
    def hotspot_start(jarvis, s):
        system("sudo ap-hotspot start")
    """
    def __plugin(run_method):
        # create class
        plugin_class = type(run_method.__name__, Plugin.__bases__, dict(Plugin.__dict__))

        def __run_method(self, jarvis, s):
            run_method(jarvis, s)

        plugin_class.run = __run_method
        plugin_class.__doc__ = run_method.__doc__

        # parse require
        require = []
        if network is not None:
            require.append(("network", network))
        if plattform is not None:
            require.append(("plattform", plattform))
        if python is not None:
            require.append(("python", python))
        if native is not None:
            require.append(("native", native))

        plugin_class.require = partial(_yield_something, require)

        # complete and alias
        if "complete" in run_method.__dict__:
            complete = run_method.complete
            plugin_class.complete = partial(_yield_something, complete)
        else:
            plugin_class.complete = _return_none

        if "alias" in run_method.__dict__:
            alias = run_method.alias
            plugin_class.alias = partial(_yield_something, alias)
        else:
            plugin_class.alias = _return_none

        return plugin_class
    return __plugin


def complete(*alias):
    def __complete(run_method):
        if "complete" not in run_method.__dict__:
            run_method.complete = []

        run_method.complete.extend(alias)
        return run_method
    return __complete


def alias(*alias):
    def __alias(run_method):
        if "alias" not in run_method.__dict__:
            run_method.alias = []

        run_method.alias.extend(alias)
        return run_method
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
