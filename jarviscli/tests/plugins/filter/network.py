from plugin import Plugin
from requests import ConnectionError


class Network(Plugin):
    """Test"""

    def require(self):
        yield ("network", True)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        raise ConnectionError()


class NoNetwork(Plugin):
    """Test"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class NoNetworkAlt(Plugin):
    """Test"""

    def require(self):
        yield ("network", False)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass
