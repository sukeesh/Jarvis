from plugin import plugin


@plugin("helloworld")
def helloworld(jarvis, yourSpeech):
    """Repeats what you type"""
    jarvis.say(yourSpeech)