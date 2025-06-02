import requests
from plugin import plugin, require

"""
Gives you ideas to do when you are bored from https://bored.api.lewagon.com/
"""


@require(network=True)
@plugin('bored')
class bored_api:
    """
    Tells an activity and its details when you type 'bored'
    """

    def __call__(self, jarvis, s):
        api_url = 'https://bored.api.lewagon.com/api/activity'
        header = {'Accept': 'application/json'}

        try:
            r = requests.get(api_url, headers=header)

            query = r.json()

            activity = query['activity']
            typ =      query['type']
            partic =   query['participants']
            price =    query['price']
            access =   query['accessibility']
            link =     query['link']

            jarvis.say(f'Activity: {activity}')
            jarvis.say(f'Type: {typ}')
            jarvis.say(f'Number of Participants: {partic}')
            jarvis.say(f'Price: {"free" if price == 0 else price}')
            jarvis.say(f'Link: {link if link is None else "none"}')

            jarvis.say(f'Accessibility: {access}')

        except requests.exceptions.RequestException:

            # Is said in case of a connection or parse error
            jarvis.say('Request Exception Occurred')