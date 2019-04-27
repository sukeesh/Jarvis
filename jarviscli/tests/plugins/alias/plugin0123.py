from plugin import Plugin


class Plugin0(Plugin):
    """Test"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        yield "Plugin1"
        yield "Plugin2"

    def run(self, jarvis, s):
        pass


class Plugin3(Plugin):
    """Test"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass
