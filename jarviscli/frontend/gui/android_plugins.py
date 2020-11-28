###############################
#    AUTO-GENERATED FILE      #
#      DO NOT MODIFY          #
###############################

import plugins.dice

from plugin_manager import PluginManager


def build_plugin_manager():
    plugin_manager = PluginManager()
    plugin_manager.add(plugins.dice.Roll())

    return plugin_manager
