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
