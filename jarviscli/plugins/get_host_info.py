from whois import query, exceptions
from pprint import pprint
from os import popen
from re import findall
from plugin import plugin, require, UNIX


# https://pypi.org/project/nslookup/
def ns_lookup(host):
    ping_str = 'nslookup ' + host
    stream = popen(ping_str)
    output = stream.read()
    return output


def whois_lookup(host):
    try:
        domain = query(host)
        return domain
    except exceptions.UnknownTld:
        return None


def ping(host):
    ping_str = 'ping ' + host + ' -c1'
    stream = popen(ping_str)
    output = stream.read()
    return output


# cutom regex to extract (sub)domain from string and prevents cmd injection
def sanitize_host(host, jarvis, s):
    try:
        domain_regex = (r'([a-z,A-Z,0-9,.]+[.][a-z,A-Z]{1,9})')
        host = findall(domain_regex, host)[0]
    except IndexError:
        try:
            ip_regex = (r'\b(?:'
                        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
            host = findall(ip_regex, host)[0]
        except IndexError:
            jarvis.say('\nInvalid Hostname or IP')
            get_host_info(jarvis, s)
            return None
    return host


def get_host_info(jarvis, s):
    green = "\x1b[1;32m"
    white = "\x1b[1;37m"

    host = input(white + 'Enter Domain Name or IP Address: ')
    if host is not None:
        if host.lower() == "q" or host.lower() == "quit":
            return None

    host = sanitize_host(host, jarvis, s)
    if host is None:
        return None

    # nslookup
    jarvis.say("\n" + green + "nslookup on " + host + ":" + white)
    response = ns_lookup(host)
    jarvis.say(response)

    # whois lookup
    jarvis.say(green + "whois Lookup on " + host + ":" + white)
    response = whois_lookup(host)
    if response:
        pprint(response.__dict__)
    else:
        jarvis.say("Could not run whois lookup on host " + host)

    # ping host
    jarvis.say("\n" + green + "ping " + host + ":" + white)
    response = ping(host)
    jarvis.say(response)

    return None


@require(platform=UNIX, network=True, native=['whois', 'nslookup', 'ping'])
@plugin("hostinfo")
def main(jarvis, s):
    get_host_info(jarvis, s)
