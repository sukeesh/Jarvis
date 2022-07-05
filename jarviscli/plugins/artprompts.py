from plugin import plugin
import random
from colorama import Fore
import json
from packages.memory.memory import Memory
import os

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


@plugin("prompt")
class art_promps():
    template = "@templates@"

    def __call__(self, jarvis, s):
        while True:

            jarvis.say(self.convert(self.template, self.getData()),
                       Fore.LIGHTGREEN_EX)
            jarvis.say("Do you want to see another prompt?", Fore.RED)
            answer = jarvis.input("(y/n): ", Fore.GREEN)
            if answer == "y":
                continue
            else:
                break

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
