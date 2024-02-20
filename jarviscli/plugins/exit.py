from jarviscli import entrypoint


@entrypoint
def exit(jarvis, s):
    """Closing jarvis"""
    jarvis.exit()
