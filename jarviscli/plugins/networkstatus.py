from plugin import LINUX, PYTHON3, plugin, require
import os

@require(python=PYTHON3, platform=LINUX)
@plugin('networkstatus')
def networkstatus(jarvis, s):
    """Check status of IIT Mandi network: ping the gateway (10.8.0.1) and
    check the response. Check the DNS using nslookup. Return "IIT Mandi
    network is up" or "down" based on your tests"""
    hostname = "10.8.0.1"
    response = os.system("ping -c 1 " + hostname)
    os.system("nslookup gateway.iitmandi.ac.in")
    if response == 0:
        jarvis.say ("IIT Mandi network is up")
    else:
        jarvis.say ('IIT Mandi network is down!')
