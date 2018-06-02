from plugin import plugin, alias


@plugin()
@alias("goodbye", "q", "quit")
def exit(jarvis, s):
    """Closing jarvis"""
    jarvis.exit()
