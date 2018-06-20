from plugin import Plugin, LINUX, MACOS


class Linux(Plugin):
    """Test"""
    def require(self):
        yield ("plattform", LINUX)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class Macos(Plugin):
    """Test"""
    def require(self):
        yield ("plattform", MACOS)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class Both(Plugin):
    """Test"""
    def require(self):
        yield ("plattform", (LINUX, MACOS))

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass


class Bothalt(Plugin):
    """Test"""
    def require(self):
        yield ("plattform", LINUX)
        yield ("plattform", MACOS)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass
