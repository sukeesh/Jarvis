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
