from plugin import plugin

@plugin()
def helloworld(jarvis, s):
    """Prints \"hello world!\""""
    jarvis.say("Hello World!")


@plugin()
def repeat(jarvis, s):
    """Repeats what you type"""
    jarvis.say(s)
