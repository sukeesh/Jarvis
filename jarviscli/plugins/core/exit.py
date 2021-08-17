from plugin import alias, plugin


@alias("bye", "goodbye", "q", "quit")
@plugin('exit')
def exit(jarvis, s):
    """Closing jarvis"""
    jarvis.exit()
