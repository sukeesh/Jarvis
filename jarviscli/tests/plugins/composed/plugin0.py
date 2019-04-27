from plugin import Plugin


class Plugin0_Sub0(Plugin):
    """Doc"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        jarvis.say("++sub0++ " + s)


class Plugin3(Plugin):
    """Docu Plugin 3"""

    def require(self):
        pass

    def complete(self):
        yield "test"

    def alias(self):
        yield "Plugin0 Sub0"

    def run(self, jarvis, s):
        jarvis.say("sub0_wrong")


class Plugin0_Sub1__test(Plugin):
    """Doc"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        yield "Plugin1"
        yield "Plugin0 sub2"

    def run(self, jarvis, s):
        jarvis.say("++sub1++ " + s)


class Plugin2(Plugin):
    """Doc"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        yield "Plugin0"

    def run(self, jarvis, s):
        jarvis.say("master")


class Plugin3_Sub0(Plugin):
    """Docu Sub0"""

    def require(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        pass
