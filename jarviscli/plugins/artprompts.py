from plugin import plugin
import random
from colorama import Fore
import json
import os
import requests
import time
import webbrowser

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


@plugin("prompt")
class art_promps():
    template = "@templates@"

    def __call__(self, jarvis, s):
        jarvis.say("Do you want to receive a prompt to draw?", Fore.RED)
        answer = jarvis.input("(y/n): ", Fore.GREEN)
        if answer == "y":
            while True:

                jarvis.say(self.convert(self.template, self.getData()),
                           Fore.LIGHTGREEN_EX)
                jarvis.say("Do you want to see another prompt?", Fore.RED)
                answer = jarvis.input("(y/n): ", Fore.GREEN)
                if answer == "y":
                    continue
                else:
                    break
        else:
            jarvis.say("Do you want create an Ai image using a prompt you give?", Fore.RED)
            answer = jarvis.input("(y/n): ", Fore.GREEN)
            if answer == "y":
                while True:

                    print(self.accessApi(jarvis))
                    jarvis.say("Do you want to give another prompt?", Fore.RED)
                    answer = jarvis.input("(y/n): ", Fore.GREEN)
                    if answer == "y":
                        continue
                    else:
                        break
            else:
                jarvis.say("Exiting art prompts program...")




    def searchString(self, html, tag, lists):
        for line in html.splitlines():
            if tag in line:
                string = line.split(tag)[1]
                item = self.selectItem(string, lists)
                return html.replace(tag + string + tag, item, 1)

    def selectItem(self, listName, lists):
        return random.choice(lists[listName])

    def changeA(self, html):
        htmlList = html.split()
        aIndex = 0
        i = 0
        length = len(htmlList)
        while i < length:
            if "<a>" == htmlList[i]:
                aIndex = i
                break
            i += 1

        # check first letter of string to see if vowel
        if length > 1:
            if htmlList[aIndex + 1][0] in "aeiou":
                htmlList[aIndex] = "an"
            else:
                htmlList[aIndex] = "a"
        else:
            htmlList[aIndex] = "a"

        return " ".join(htmlList)

    def convert(self, html, lists):
        newHtml = html
        while True:
            if self.searchString(newHtml, "@", lists) is None:
                break
            newHtml = self.searchString(newHtml, "@", lists)
        while True:

            aChange = self.changeA(newHtml)
            if aChange == newHtml:
                break
            else:
                newHtml = aChange
        return newHtml

    def getData(self):

        with open(os.path.join(FILE_PATH, '../data/prompts.json')) as json_file:
            data = json.load(json_file)
        return data

    # get a list from a its name in a string


    ##Use api key to create images using ai Horde. https://github.com/Haidra-Org

        # ask user for prompt to give ai
    def aiPrompt(self, jarvis):
        user_prompt = jarvis.input("Enter prompt to create Ai image: ", Fore.GREEN)
        self.prompt = user_prompt
    #
    # #use api key to access api
    def accessApi(self, jarvis):
        self.aiPrompt(jarvis)
        GENERATE_URL = "https://aihorde.net/api/v2/generate/async"
        CHECK_URL = "https://aihorde.net/api/v2/generate/check/"
        STATUS_URL = "https://aihorde.net/api/v2/generate/status/"
        data = {
            "prompt": self.prompt,
            "params": {
                "cfg_scale": 7,
                "seed": "42",
                "sampler_name": "k_euler",
                "height": 512,
                "width": 512,
                "steps": 20,
                "tiling": False,
                "karras": False,
                "clip_skip": 1,
                "n": 1,
                "max_kudos": 5
            },
            "nsfw": False,
            # "censor_nsfw": False,
            "trusted_workers": True,
            "models": ["Deliberate"],
            # "r2": True,
            # "replacement_filter": True,
            # "shared": False,
            # "slow_workers": False,
            # "dry_run": False
        }

        headers = {
            "apikey": "0000000000" #free anonymous key, has some cons
        }

        response = requests.post(GENERATE_URL, headers=headers, json=data).json()

        print(response)

        _id = response["id"]

        while True:
            response = requests.get(CHECK_URL + _id, headers=headers).json()
            print(response)
            if response["finished"] == data["params"]["n"]:
                break
            time.sleep(2)

        response = requests.get(STATUS_URL + _id, headers=headers).json()

        # print(response)

        # Extract the image URL
        try:
            image_url = response['generations'][0]['img']
            webbrowser.open(image_url)
            return f"Here is your image: {image_url}"
        except (KeyError, IndexError):
            return "Error: Image URL not found in the response."