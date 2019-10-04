from plugin import plugin, alias
import socket
from colorama import Fore


# a reverse DNS lookup or reverse DNS resolution (rDNS)
# is the querying technique of the Domain Name System (DNS)
# to determine the domain name associated with an IP address
@alias('hostname lookup', 'hostname for')
@plugin("dns reverse")
def hostname_lookup(jarvis, s):
    while True:
        # asks for an IP address
        ip = str(jarvis.input("Please input an IP address: "))
        try:
            # tries to find the hostname for given IP address
            jarvis.say("The hostname for that IP address is: " +
                       str(socket.gethostbyaddr(ip)[0]), Fore.BLUE)
            break
        except Exception as e:
            # prints error and asks if want to try again
            jarvis.say(str(e), Fore.RED)
            jarvis.say("Please make sure you are inputing a valid IP address")
            try_again = jarvis.input("Do you want to try again (y/n): ")
            try_again = try_again.lower()
            if try_again == 'y':
                continue
            else:
                break

# a "forward" DNS lookup is a lookup of an IP address from a domain name.


@alias('ip lookup', 'ip for')
@plugin("dns forward")
def ip_lookup(jarvis, s):
    while True:
        hostname = str(jarvis.input("Please input a hostname: "))
        try:
            # tries to find the hostname for given hostname
            jarvis.say("The IP address for that hostname is: " +
                       str(socket.gethostbyname(hostname)), Fore.BLUE)
            break
        except Exception as e:
            # prints error and asks if want to try again
            jarvis.say(str(e), Fore.RED)
            jarvis.say("Please make sure you are inputing a valid IP address")
            try_again = jarvis.input("Do you want to try again (y/n): ")
            try_again = try_again.lower()
            if try_again == 'y':
                continue
            else:
                break
