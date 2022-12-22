from plugin import Platform, plugin, require, quality, QualityLevel
from dependency import KEY_DISABLED


@plugin("plugin disable")
def jarvis_disable(jarvis, s):
    s = jarvis.input("Plugin name: ")
    if s not in jarvis.plugins:
        jarvis.say('No plugin {} exists'.format(s))
        return

    disabled = jarvis.get_data(KEY_DISABLED)
    disabled[s] = True
    jarvis.update_data(KEY_DISABLED, disabled)

    jarvis.say('Changes will be applied on next start.')


@plugin("plugin enable")
def javis_enable(jarvis, s):
    s = jarvis.input("Plugin name: ")
    disabled = jarvis.get_data(KEY_DISABLED)
    if s not in disabled:
        jarvis.say('No plugin {} disabled'.format(s))
        return

    del disabled[s]
    jarvis.update_data(KEY_DISABLED, disabled)

    jarvis.say('Changes will be applied on next start.')
