# All plugins should inherite from this library
import requests, json
from colorama import Fore
from plugin import alias, plugin, require
# This is the standard form of a plugin for jarvis

# Anytime you make a change REMEMBER TO RESTART Jarvis

# You can run it through jarvis by the name
# in the @plugin tag.


class ProtonCompatibleGame:

    def getAppIdFromTitle(self,jarvis):
        jarvis.say("Warning: This option may not find the game or find an incorrect game. "
                   + "Find the game's AppId from Steam for accurate results!"
                   ,color=Fore.RED)
        title=jarvis.input("Enter Game Title: ",color=Fore.GREEN).strip();
        games = requests.get("https://protondb.max-p.me/games").text
        games = json.loads(games) 
        for game in games:
            if (game["title"]==title):
                return game["appId"]
        return -1

    def getRating(self,jarvis,appid):
        try:
            jarvis.say("Game appId: "+str(appid),Fore.YELLOW)
            url="https://www.protondb.com/api/v1/reports/summaries/"+str(appid)+".json"
            rating=requests.get(url).json()
            jarvis.say("ProtonDB Rating: "+rating["tier"],Fore.YELLOW)
        except:
            jarvis.say("Invalid AppId or there are no ratings for this game",color=Fore.RED)

    def run(self,jarvis):
        jarvis.say("1. Give Steam game AppId",color=Fore.YELLOW)
        jarvis.say("2. Give Steam game Title",color=Fore.YELLOW)
        jarvis.say("3. Close.",color=Fore.YELLOW)
        choice=jarvis.input("Enter your choice: ",color=Fore.GREEN).strip();
        while (choice<"1" or choice>"3"):
            jarvis.say("Invalid choice!",color=Fore.RED)
            choice=jarvis.input("Enter your choice: ",color=Fore.GREEN).strip();
        if (choice =="1"):
            id=jarvis.input("Enter Game AppId: ",color=Fore.GREEN).strip();
            self.getRating(jarvis,id)
        elif (choice == "2"):
            appid=self.getAppIdFromTitle(jarvis)
            if (appid!=-1):
                self.getRating(jarvis,appid)
            else:
                jarvis.say(
                    "This game does not exist or there are no ratings for this game",
                    color=Fore.RED
                )

@alias('Proton compatible game')
@require(network=True)
@plugin('Proton game')

def my_plugin(jarvis, s):
    ProtonCompatibleGame().run(jarvis)

