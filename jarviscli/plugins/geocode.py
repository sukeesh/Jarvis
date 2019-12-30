import json
import re
import requests
import requests.exceptions
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin('geocode')
def geocode(jarvis, s):
    jarvis.say("Welcome to geocoder. I can use geocoding to convert a street address to a geographic latitude and longitude.", Fore.RED)

    # If an address wasn't given when the plugin is launched
    if not s:
        s = jarvis.input("Enter the full street address to geocode: ")
    # Parse the address to remove url-unfriendly characters
    parsed_addr = parse_address(s)

    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={}&benchmark=4&vintage=4&format=json".format(parsed_addr)

    # Make request to geocoding API
    req = make_request(url)

    # Request failed
    if not req:
        jarvis.say("The geocoding service appears to be unavailable. Please try again later.", Fore.RED)
    
    # Request succeeded
    else:
        data = json.loads(req.text)
        matches = data['result']['addressMatches']

        if matches:
            if len(matches) > 1:
                jarvis.say("Multiple address matches were found. Showing best match.", Fore.YELLOW)

            match = data['result']['addressMatches'][0]

            output = {'Address matched': match['matchedAddress'],
                    'Latitude': str(match['coordinates']['y']),
                    'Longitude': str(match['coordinates']['x'])}

            for result in output:
                jarvis.say("{}: {}".format(result, output[result]), Fore.CYAN)

        else:
            jarvis.say('No matching addresses found.', Fore.RED)

def parse_address(s):
    # Remove everything that isn't alphanumeric or whitespace
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all whitespace
    s = re.sub(r"\s+", '+', s)

    return s


# Make a request to a URL. Return the request if success or None if it failed
def make_request(url):
    try:
        req = requests.get(url)
        req.raise_for_status()
        return req
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
        return None
