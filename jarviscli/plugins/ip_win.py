import socket

from jarviscli import entrypoint


@entrypoint
def ip_WIN32(jarvis, s):
    """
    Returns information about IP for windows
    """

    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    jarvis.say("IP address: " + str(IP))
