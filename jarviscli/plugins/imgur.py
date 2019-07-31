from plugin import plugin, require
from utilities.GeneralUtilities import IS_WIN
import os
import sys
import requests
import json
import base64
import glob
if IS_WIN:
    from pyreadline import Readline
    readline = Readline()
else:
    import readline


def complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


@require(network=True)
@plugin('imgur')
def imgur(jarvis, s):
    """
    Uploads an image to imgur
    """

    # Autocomplete filename
    jarvis.say("What's the image name?: ")
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    r = readline.get_completer()
    readline.set_completer(complete)
    file = jarvis.input('')
    # Get the absolute path
    file = os.path.abspath(file)
    file = os.path.expanduser(file)
    if os.path.isfile(file):
        try:
            url = "https://api.imgur.com/3/image"
            headers = {"Authorization": "Client-ID 145b6ea95cf11b4"}
            # Send POST
            resp = requests.post(
                url,
                headers=headers,
                data={
                    'image': base64.b64encode(open(file, 'rb').read()),
                    'type': 'base64'
                }
            )

            objresp = json.loads(resp.text)
            # Treat response
            if objresp.get('success', False):
                jarvis.say('Here is your image: '
                           + str(objresp['data']['link']))
            else:
                jarvis.say('Error: ' + str(objresp['data']['error']))
        except Exception as e:
            # Print exception as string
            jarvis.say("Error {0}".format(str(e.args[0])).encode("utf-8"))
    else:
        jarvis.say("No such file")

    readline.set_completer(r)
