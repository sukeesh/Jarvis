from utilities.GeneralUtilities import print_say
import requests
import os
import json
import base64


def imgur(self, s):
    # Get the absolute path
    s = os.path.abspath(s)
    if os.path.isfile(s):
        try:
            url = "https://api.imgur.com/3/image"
            headers = {"Authorization": "Client-ID 145b6ea95cf11b4"}
            # Send POST
            resp = requests.post(
                url,
                headers=headers,
                data={
                    'image': base64.b64encode(open(s, 'rb').read()),
                    'type': 'base64'
                }
            )

            objresp = json.loads(resp.text)
            # Treat response
            if objresp.get('success', False):
                print_say('Here is your image: ' +
                          objresp['data']['link'], self)
            else:
                print_say('Error: ' + objresp['data']['error'], self)
        except Exception as e:
            # Print exception as string
            print_say("Error {0}".format(str(e.args[0])).encode("utf-8"), self)
    else:
        print_say("No such file", self)
