from plugin import Plugin


class Plugin7(Plugin):
    """Test"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        yield "Plugin4"
        yield "Plugin5"
        yield "Plugin6"

    def run(self, jarvis, s):
        pass
