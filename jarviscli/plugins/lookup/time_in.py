import datetime
import time

import pytz
from colorama import Fore

from plugin import alias, plugin, require
from utilities.get_location import get_location


@require(network=True, api_key='google')
@plugin('check time')
def check_time(jarvis, s, google=None):
    """
    checks the current time in any part of the globe.
    -- Examples:
        check time in Manchester (UK)
    """
    # Trims input s to be just the city/region name
    s = s.replace('time ', '').replace('in ', '')
    loc = getLocation(google, s)

    if loc is None:
        return

    timestamp = time.time()
    # Gets current date and time using Google API
    api_response = requests.get(
        'https://maps.googleapis.com/maps/api/timezone/json?location={0},{1}&timestamp={2}&key={3}'.format(loc[0], loc[1], time.time(), google))
    api_response_dict = api_response.json()

    if api_response_dict['status'] == 'OK':
        timezone = api_response_dict['timeZoneName']
        tz = pytz.timezone(timezone)
        now = datetime.datetime.now(tz).strftime("%H:%m")

        jarvis.say("The current date and time in {LOC} is: {TIME}".
                   format(LOC=timezone, TIME=now),
                   color=Fore.MAGENTA)
