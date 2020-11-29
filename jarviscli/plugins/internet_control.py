from plugin import plugin
import sys
import os
import socket


def has_internet():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        socket.setdefaulttimeout(3)
        sock.connect(('8.8.8.8', 8000))

        return True
    
    except socket.timeout:
        return False


@plugin("internet")
def internet(jarvis, s):
    connected = has_internet()

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