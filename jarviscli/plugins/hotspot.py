from plugin import plugin, LINUX
from os import system


@plugin(network=True, plattform=LINUX, native=["ap-hotspot", "sudo"])
def hotspot_start(jarvis, string):
    """
    Jarvis will set up your own hotspot.
    """
    system("sudo ap-hotspot start")


@plugin(network=True, plattform=LINUX, native=["ap-hotspot", "sudo"])
def hotspot_stop(jarvis, string):
    """
    Jarvis will stop your hotspot.
    """
    system("sudo ap-hotspot stop")
