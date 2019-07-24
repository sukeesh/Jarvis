from plugin import Plugin


class NativeTrue(Plugin):
    """Test"""

    def require(self):
        # ls should really be available on every system
        yield ("native", "ls")

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class NativeFalse(Plugin):
    """Test"""

    def require(self):
        yield ("native", "sdfsdefaerfsdfg")

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class NativeFalseAlt(Plugin):
    """Test"""

    def require(self):
        yield ("native", ("sdfsdefaerfsdfg", "ls"))

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass
