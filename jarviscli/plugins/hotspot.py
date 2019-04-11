from os import system
from plugin import plugin, require, LINUX


@require(network=True, platform=LINUX, native=["ap-hotspot", "sudo"])
@plugin('hotspot start')
def hotspot_start(jarvis, string):
    """
    Jarvis will set up your own hotspot.
    """
    system("sudo ap-hotspot start")


@require(network=True, platform=LINUX, native=["ap-hotspot", "sudo"])
@plugin('hotspot stop')
def hotspot_stop(jarvis, string):
    """
    Jarvis will stop your hotspot.
    """
    system("sudo ap-hotspot stop")
