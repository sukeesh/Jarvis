from plugin import Plugin, LINUX, MACOS


class Linux(Plugin):
    """Test"""

    def require(self):
        yield ("platform", LINUX)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class Macos(Plugin):
    """Test"""

    def require(self):
        yield ("platform", MACOS)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class Both(Plugin):
    """Test"""

    def require(self):
        yield ("platform", (LINUX, MACOS))

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class Bothalt(Plugin):
    """Test"""

    def require(self):
        yield ("platform", LINUX)
        yield ("platform", MACOS)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass
