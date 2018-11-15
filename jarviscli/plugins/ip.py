from os import system

from colorama import Fore

from plugin import plugin


@plugin('ip')
class IP():
    """
    Display local and public ip address
    """
    def __init__(self):
        self._local_ip = """ifconfig | grep -Eo 'inet (addr:)?([0-9]*\\.){3}[0-9]*' |
                    grep -Eo '([0-9]*\\.){3}[0-9]*' | grep -v '127.0.0.1'"""

        self._public_ip_v4 = "curl -4 ifconfig.co --connect-timeout 10"  # 10 second time out if not connected to internet
        self._public_ip_v6 = "curl -6 ifconfig.co --connect-timeout 10"  # 10 second time out if not connected to internet

    def __call__(self, jarvis, s):
        self._get_local_ip(jarvis)
        jarvis.say("")
        self._get_public_ip(jarvis)

    def _get_local_ip(self, jarvis):
        jarvis.say("List of local ip addresses :", Fore.BLUE)
        system(self._local_ip)

    def _get_public_ip(self, jarvis):
        jarvis.say("Public ip v4 address :", Fore.BLUE)
        system(self._public_ip_v4)
        jarvis.say("Public ip v6 address :", Fore.BLUE)
        system(self._public_ip_v6)
