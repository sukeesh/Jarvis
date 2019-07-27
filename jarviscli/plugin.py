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
WINDOWS = "WINDOWS"
# Shortcut for MACOS + LINUX
UNIX = "UNIX"


def plugin(name):
    """
    Convert function in Plugin Class

    @python(platform=LINUX, native="ap-hotspot")
    def hotspot_start(jarvis, s):
        system("sudo ap-hotspot start")
    """
    def create_plugin(run):
        plugin_class = type(
            run.__name__, Plugin.__bases__, dict(
                Plugin.__dict__))
        plugin_class.__doc__ = run.__doc__

        if isclass(run):
            # class -> object
            run = run()

        # create class
        plugin_class._require = []
        plugin_class._complete = []
        plugin_class._alias = []
        plugin_class._name = name
        plugin_class._backend = (run,)
        plugin_class._backend_instance = run

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


class PluginStorage(object):
    def __init__(self):
        self._sub_plugins = {}

    def add_plugin(self, name, plugin_to_add):
        self._sub_plugins[name] = plugin_to_add

    def get_plugins(self, name=None):
        if name is None:
            return self._sub_plugins
        if name in self._sub_plugins:
            return self._sub_plugins[name]
        return None


class Plugin(pluginmanager.IPlugin, PluginStorage):
    """
    """
    _backend = None

    def __init__(self):
        super(pluginmanager.IPlugin, self).__init__()
        self._sub_plugins = {}

    def init(self, jarvis_api):
        """
        Called before Jarvis starts;
        Passes jarvis_api object for plugins to do initialization.
        (would not be possible with __init__)
        """
        if self.is_callable_plugin():
            if hasattr(
                self._backend[0].__class__,
                "init") and callable(
                getattr(
                    self._backend[0].__class__,
                    "init")):
                self._backend[0].init(jarvis_api)
        for plugin in self.get_plugins().values():
            plugin.init(jarvis_api)

    def is_callable_plugin(self):
        """
        Return True, if this plugin has a executable implementation (e.g. news)
        Return False, if this instance is only used for calling other plugins
        (e.g. movie in 'movie search' and 'movie plot')
        """
        return self._backend is not None

    def get_name(self):
        """Set with @plugin(name)"""
        return self._name

    def require(self):
        """Set with @require"""
        return self._require

    def alias(self):
        """Set with @alias"""
        return self._alias

    def complete(self):
        """Set with @complete"""
        # return default complete() if possible
        if self.is_callable_plugin():
            for complete in self._complete:
                yield complete

        # yield each sub command
        for complete in self.get_plugins().keys():
            yield complete

    def get_doc(self):
        """Parses plugin doc string"""
        doc = ""
        examples = ""
        extended_doc = ""

        # default complete
        if self.__doc__ is not None:
            default_command_doc = cleandoc(self.__doc__)
            default_command_doc = default_command_doc.split("-- Example:")
            if len(default_command_doc) > 1:
                examples += default_command_doc[1]
            default_command_doc = default_command_doc[0]

            doc += default_command_doc
            if not doc.endswith("\n"):
                doc += "\n"
            doc += "\nSubcommands:"

        # sub command complete
        for name, sub_command in self.get_plugins().items():
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
        """Entry point if this plugin is called"""
        sub_command = jarvis.find_action(s, self.get_plugins().keys())

        if sub_command is "None":
            # run default
            if self.is_callable_plugin():
                self._backend[0](jarvis.get_api(), s)
            else:
                jarvis.get_api().say("Sorry, I could not recognise your command. Did you mean:")
                for sub_command in self._sub_plugins.keys():
                    jarvis.get_api().say("    * {} {}".format(self.get_name(), sub_command))
        else:
            command = sub_command.split()[0]
            new_s = " ".join(sub_command.split()[1:])
            self.get_plugins(command).run(jarvis, new_s)

    def _plugin_run_with_network_error(self, run_func, jarvis, s):
        """
        Calls run_func(jarvis, s); try-catch ConnectionError

        This method is auto-used if require() yields ("network", True). Do not
        use m
        """
        try:
            run_func(jarvis, s)
        except ConnectionError:
            jarvis.get_api().connection_error()
