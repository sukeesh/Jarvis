import json

import requests


def get_location(api_key, s):
    send_url = (
        "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(s, api_key))
    # https://developers.google.com/maps/documentation/geocoding/start?hl=en_US
    # https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY
    r = requests.get(send_url)
    j = json.loads(r.text)
    try:
        lat = j['results'][0]['geometry']['location']['lat']    # Latitude
        lng = j['results'][0]['geometry']['location']['lng']    # Longitude
        # Returns both latitude and longitude as a tuple
        return lat, lng
    except IndexError:
        # Error handled after try except
        pass
    raise Exception(r.text)
