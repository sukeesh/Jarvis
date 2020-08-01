from plugin import Platform, feature, plugin, require


@require(native="id")
@require(platform=Platform.SERVER)
@plugin("talk")
def talk(jarvis, s):
    """
    talk    : when s string is an input from server as unidentified command
    """

    jarvis.eval(s)
