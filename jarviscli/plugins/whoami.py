import os
import re

from plugin import Platform, feature, plugin, require


@require(native="id")
@require(platform=Platform.LINUX)
@plugin("whoami")
def whoami(jarvis, s):
    """
    Tells you the current user name
    whoami:          says the current effective user ID's name
    whoami -options: passes the options to the linux
    command "id" and returns the response
    """

    def check(s) -> bool:
        """
        Ensure that the string is not damaging
        """

        options = [
            "--context",
            "--group",
            "--groups",
            "--name",
            "--real",
            "--user",
            "--zero",
            "--help",
            "--version"
        ]

        for i in s.split(" "):
            if (
                # valid POSIX user names or UIDs
                not re.match("(^[a-z][a-z0-9-]*$)|(^[0-9]+$)", i)
                and
                # possible short options
                not re.match("^-[agnruzGZ]+$", i)
                and
                # possible long options
                i not in options
            ):
                return False

        return True

    if s == "":
        os.system("id -un")
        return

    if not check(s):
        jarvis.say("There seems to be some awkward stuff ...?")
        return

    os.system("id " + str(s))


@feature(case_sensitive=True)
@require(native="id")
@require(platform=Platform.MACOS)
@plugin("whoami")
def whoami(jarvis, s):
    """
    Tells you the current user name
    whoami:          says the current effective user ID's name
    whoami -options: passes the options to the linux
    command "id" and returns the response
    """

    def check(s) -> bool:
        """
        Ensure that the string is not damaging
        """

        for i in s.split(" "):
            if (
                # valid POSIX user names or UIDs
                not re.match("(^[a-z][a-z0-9-]*$)|(^[0-9]+$)", i)
                and
                # possible short options:
                not re.match("-[AFGMPagpunr]+$", i)
            ):
                return False

        return True

    if s == "":
        os.system("id -un")
        return

    if not check(s):
        jarvis.say("There seems to be some awkward stuff ...?")
        return

    os.system("id " + str(s))
