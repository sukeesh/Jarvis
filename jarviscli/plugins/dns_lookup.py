import socket

from colorama import Fore

from plugin import plugin


def ip_lookup(hostname):
    return str(socket.gethostbyname(hostname))


def hostname_lookup(ip):
    return str(socket.gethostbyaddr(ip)[0])


def dns_lookup(jarvis, s, txt, func):
    while True:
        request = str(jarvis.input("Please input a " + txt + ": "))
        try:
            if txt == 'ip':
                jarvis.say("The hostname for that IP address is: " +
                           func(request), Fore.CYAN)
                return
            else:
                jarvis.say("The IP address for that hostname is: " +
                           func(request), Fore.CYAN)
                return
        except Exception as e:
            jarvis.say(str(e), Fore.RED)
            jarvis.say("Please make sure you are inputing a valid " + txt)
            try_again = jarvis.input("Do you want to try again (y/n): ")
            try_again = try_again.lower()
            if try_again != 'y':
                return


@plugin("dns forward")
def ip_lookup1(jarvis, s):
    dns_lookup(jarvis, s, "hostname", ip_lookup)


@plugin("dns reverse")
def hostname_lookup1(jarvis, s):
    dns_lookup(jarvis, s, "ip", hostname_lookup)
