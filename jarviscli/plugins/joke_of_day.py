import requests
from colorama import Fore

from plugin import plugin, require


@require(network=True)
@plugin('joke daily')
class joke_of_day:
    """
    Provides you with a joke of day to help you laugh amidst the
    daily boring schedule

    Enter 'joke daily' to use

    """

    def __call__(self, jarvis, s):
        jarvis.say("Welcome To The Plugin Joke Of Day!", Fore.CYAN)
        jarvis.say("Jokes provided by jokes.one API", Fore.CYAN, False)
        print()
        joke_fetch = self.get_joke(jarvis)
        if joke_fetch is not None:
            self.joke(jarvis, joke_fetch)

    def get_joke(self, jarvis):
        while True:
            url = "https://api.jokes.one/jod"
            jarvis.spinner_start('Fetching')
            r = requests.get(url)
            if r is None:
                jarvis.spinner.stop()
                jarvis.say(
                    "Error in fetching joke - try again! later", Fore.RED)
            jarvis.spinner_stop()
            return r.json()

    def joke(self, jarvis, joke_fetch):
        title = joke_fetch["contents"]["jokes"][0]["joke"]["title"]
        joke = joke_fetch["contents"]["jokes"][0]["joke"]["text"]
        print()
        jarvis.say("Title: " + title, Fore.BLUE)
        print()
        jarvis.say(joke, Fore.YELLOW)
