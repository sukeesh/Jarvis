import requests
from plugin import plugin, alias, require
from colorama import Fore

@require(network=True)
@alias("soccer")
@plugin("soccer scores")
class SoccerScores:
    """The user can request the latest soccer scores, and the API from TheSportsDB will be used to make a GET request and
    fetch data. Then, the user can see the latest scores from major soccer games."""

    def __call__(self, jarvis: "JarvisAPI", s: str) -> None:
        self.print_latest_scores(jarvis)

    def print_latest_scores(self, jarvis: "JarvisAPI"):
        jarvis.say("Fetching the latest soccer scores...")
        try:
            response = requests.get('https://www.thesportsdb.com/api/v1/json/3/latestsoccer.php')
            response.raise_for_status()
            data = response.json()
            
            if 'games' in data:
                for game in data['games']:
                    jarvis.say(f"Match: {game['strEvent']}", color=Fore.BLUE)
                    jarvis.say(f"Date: {game['dateEvent']}")
                    jarvis.say(f"Score: {game['intHomeScore']} - {game['intAwayScore']}", color=Fore.GREEN)
                    jarvis.say(f"Status: {game['strStatus']}\n")
            else:
                jarvis.say("No recent games data found.", color=Fore.RED)
        except requests.RequestException as e:
            jarvis.say(f"An error occurred while fetching data: {e}", color=Fore.RED)
