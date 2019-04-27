from plugin import Plugin, PYTHON2, PYTHON3


class PY2(Plugin):
    """Test"""

    def require(self):
        yield ("python", PYTHON2)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class PY3(Plugin):
    """Test"""

    def require(self):
        yield ("python", PYTHON3)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class Both(Plugin):
    """Test"""

    def require(self):
        yield ("python", (PYTHON2, PYTHON3))

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class Bothalt(Plugin):
    """Test"""

    def require(self):
        yield ("python", PYTHON2)
        yield ("python", PYTHON3)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass
