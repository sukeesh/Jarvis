import requests

from plugin import plugin, require


@require(network=True)
@plugin('geolocation')
def geolocation(jarvis, s):
    """Helps to geolocate an IP address."""
    base_url = "https://api.ip2location.io/"
    payload = {'ip': s, 'format': 'json'}
    jarvis.say(f'Lookup {s} now...')
    api_result = requests.get(base_url, params=payload)
    api_result_json = api_result.json()
    jarvis.say(
        f"It's located at {api_result_json['city_name']}, "
        f"{api_result_json['region_name']}, "
        f"{api_result_json['country_name']}."
    )
    jarvis.say(
        f"Its coordinates are ({api_result_json['latitude']}, "
        f"{api_result_json['longitude']})."
    )
    jarvis.say(
        f"It's owned by {api_result_json['as']} "
        f"with the ASN {api_result_json['asn']}."
    )
