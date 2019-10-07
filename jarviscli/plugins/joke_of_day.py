from plugin import plugin, require
import requests
from colorama import Fore
from plugins.animations import SpinnerThread


@require(network=True)
@plugin('jokeofday')
class joke_of_day:
    """
    Provides you with a joke of day to help you laugh amidst the
    daily boring schedule

    Enter 'jokeofday' to use

    """

    def __call__(self, jarvis, s):
        jarvis.say("Welcome To The Plugin Joke Of Day!", Fore.CYAN)
        print()
        joke_fetch = self.get_joke(jarvis)
        if joke_fetch is not None:
            self.joke(jarvis, joke_fetch)

    def get_joke(self, jarvis):
        spinner = SpinnerThread('Fetching ', 0.15)
        while True:
            joke = jarvis.input(
                "Select your choice \n 1: Get Joke Of Day \n 2: Exit\n", Fore.GREEN)
            print()
            if joke == '1':
                url = "https://api.jokes.one/jod"
                spinner.start()
                r = requests.get(url)
                if r is None:
                    spinner.stop()
                    jarvis.say(
                        "Error in fetching joke - try again! later", Fore.RED)
                spinner.stop()
                return r.json()
            elif joke == '2':
                return
            else:
                jarvis.say("Please enter a valid choice!")

    def joke(self, jarvis, joke_fetch):
        title = joke_fetch["contents"]["jokes"][0]["joke"]["title"]
        joke = joke_fetch["contents"]["jokes"][0]["joke"]["text"]
        print()
        jarvis.say("Title: " + title, Fore.BLUE)
        print()
        jarvis.say(joke, Fore.YELLOW)
