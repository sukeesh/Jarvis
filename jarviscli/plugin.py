from inspect import cleandoc, isclass

import pluginmanager
from requests import ConnectionError


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


def require(network=None, platform=None, native=None):
    """Decorator to specify requirements for a plugin."""
    requirements = []
    if network is not None:
        requirements.append(('network', network))
    if platform is not None:
        requirements.append(('platform', platform))
    if native is not None:
        requirements.append(('native', native))

    def __require(plugin_instance):
        plugin_instance._require.extend(requirements)
        return plugin_instance

    return __require


def complete(*complete_args):
    """Decorator to specify completion options for a plugin."""
    def __complete(plugin_instance):
        plugin_instance._complete.extend(complete_args)
        return plugin_instance
    return __complete


def alias(*alias_args):
    """Decorator to specify aliases for a plugin."""
    def __alias(plugin_instance):
        plugin_instance._alias.extend(alias_args)
        return plugin_instance
    return __alias


def _yield_something(values):
    yield from values


class PluginStorage():
    """ A storage class for managing sub-plugins."""

    def __init__(self):
        self._sub_plugins = {}

    def add_plugin(self, name, plugin_to_add):
        """
        Adds a sub-plugin to the storage.

        Args:
            name: The name of the sub-plugin.
            plugin_to_add: The sub-plugin to add.
        """

        self._sub_plugins[name] = plugin_to_add

    def get_plugins(self, name=None):
        """
        Retrieves sub-plugins from the storage.

        Args:
            name: The name of the sub-plugin to retrieve. If None, all sub-plugins are returned.

        Returns:
            All sub-plugins if name is None, otherwise the specified sub-plugin or None if not found
        """

        if name is None:
            return self._sub_plugins
        if name in self._sub_plugins:
            return self._sub_plugins[name]
        return None

    def change_with(self, plugin_new):
        """
        Replaces the sub-plugins of another PluginStorage instance with the current sub-plugins.

        Args:
            plugin_new: The PluginStorage instance whose sub-plugins will be replaced.
        """

        plugin_new._sub_plugins = self._sub_plugins


class Plugin(pluginmanager.IPlugin, PluginStorage):
    """
    Base class for all plugins.

    This class inherits from both IPlugin and PluginStorage, providing a structure
    for plugins to be managed and initialized within the Jarvis framework.
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
        for sub_plugin in self.get_plugins().values():
            sub_plugin.init(jarvis_api)

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
            yield from self._complete

        # yield each sub command
        yield from self.get_plugins().keys()

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
            doc += f"\n-> {name}: "

            sub_command_doc = sub_command.get_doc()
            sub_command_doc = sub_command_doc.split("-- Example:")
            if len(sub_command_doc) > 1:
                examples += sub_command_doc[1]
            sub_command_doc = sub_command_doc[0]

            if '\n' not in sub_command_doc:
                doc += sub_command_doc
            else:
                extended_doc += f"\n  {name}:\n"
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

        if sub_command == "None":
            # run default
            if self.is_callable_plugin():
                self._backend[0](jarvis.get_api(), s)
            else:
                jarvis.get_api().say("Sorry, I could not recognise your command. Did you mean:")
                for sub_command in self._sub_plugins:
                    jarvis.get_api().say(f"    * {self.get_name()} {sub_command}")
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
