from plugin import alias, plugin


@alias("bye", "goodbye", "q", "quit")
@plugin
def exit(jarvis, s):
    """Closing jarvis"""
    jarvis.exit()
