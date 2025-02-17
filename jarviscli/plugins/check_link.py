from plugin import plugin

import requests
import urllib.parse

API = "https://api.redirect-checker.net/?url="
APISettings = "&timeout=5&maxhops=10&meta-refresh=1&format=json"

@plugin('check link')
def check_link(jarvis, s):

    """Prints any redirects in the given link"""
    url = jarvis.input("Enter URL: ")
    encoded_url = urllib.parse.quote(url, safe="")
    full_api_url = API + encoded_url + APISettings

    # Check for redirects
    try:
        response = requests.get(full_api_url, timeout=10)
        json_data = response.json()

        # Print the redirect chain
        if "data" in json_data and json_data["data"]:
            print(f"\n[Redirect Chain for {url}]")
            for i, entry in enumerate(json_data["data"], start=1):
                print(f" - [{i}] {entry['request']['info']['url']}")
            print(f"Final Destination: {json_data['data'][-1]['request']['info']['url']}")
        else:
            print(f"[No Redirect] {url} remains the same.")
    
    except requests.exceptions.RequestException as e:
        print(f"\n[Error] Failed to check {url}: {e}")
