from plugin import alias, plugin


@plugin()
@alias("bye", "goodbye", "q", "quit")
def exit(jarvis, s):
    """Closing jarvis"""
    jarvis.exit()
