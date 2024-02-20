import requests
from jarviscli import entrypoint

"""
Gives you ideas to do when you are bored from https://www.boredapi.com/
"""


@entrypoint
def bored(jarvis, s):
    """
    Tells an activity and its details when you type 'bored'
    """

    api_url = 'https://www.boredapi.com/api/activity/'
    header = {'Accept': 'application/json'}
    r = requests.get(api_url, headers=header)

    query = r.json()

    activity = query['activity']
    typ = query['type']
    partic = query['participants']
    price = query['price']
    access = query['accessibility']

    jarvis.say(f'Activity: {activity}')
    jarvis.say(f'Type: {typ}')
    jarvis.say(f'Number of Participants: {partic}')
    jarvis.say(f'Price: {"free" if price==0 else price}')
    jarvis.say(f'Accessibility: {access}')
