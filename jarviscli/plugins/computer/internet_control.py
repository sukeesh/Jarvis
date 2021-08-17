from plugin import plugin
import sys
import os
import socket



@plugin("internet")
def internet(jarvis, s):
    connected = jarvis.online_status.get_online_status

    if connected:
        if sys.platform == "win32":
            os.system("netsh interface set interface \"Wi-Fi\" DISABLED")

        elif sys.platform == "linux":
            os.system("nmcli radio wifi off")

        elif sys.platform == "darwin":
            os.system("networksetup -setairportpower en0 off")

    else:
        if sys.platform == "win32":
            os.system("netsh interface set interface \"Wi-Fi\" ENABLED")

        elif sys.platform == "linux":
            os.system("nmcli radio wifi on")

        elif sys.platform == "darwin":
            os.system("networksetup -setairportpower en0 on")
