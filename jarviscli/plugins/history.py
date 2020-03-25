from plugin import plugin, require

@require(network=True)
@plugin('history')
class history:
    """
    Provides you with a random hisotry fact

    Enter 'history' to use
    """

    def __call__(self, jarvis, s):
        jarvis.say(s)
