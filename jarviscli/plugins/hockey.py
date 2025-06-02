import requests
import datetime
from plugin import plugin, require
from colorama import Fore
from packages.memory.memory import Memory

# base url for hockey api
URL = "https://api-hockey.p.rapidapi.com/"

@require(network=True)
@plugin("hockey")
class Hockey:
    """
    hockey plugin for retrieving information about leagues, games, and teams.
    requires an api key from rapidapi: https://rapidapi.com/api-sports/api/api-hockey/
    """

    def __call__(self, jarvis, s):
        # initialize the plugin and get api key
        print("hockey data provided by API-Hockey via RapidAPI\n")
        self.get_api_key(jarvis)
        while True:
            option = self.get_option(jarvis)
            if option is None:
                return
            self.process_chosen_option(option, jarvis)

    def get_headers(self):
        # return required headers for api requests
        return {"x-rapidapi-host": "api-hockey.p.rapidapi.com", "x-rapidapi-key": self.key}

    def fetch_data(self, route):
        # make api request and return json response
        r = requests.get(URL + route, headers=self.get_headers())
        r = r.json()
        if "errorCode" in r.keys():
            return None
        return r

    def get_api_key(self, jarvis):
        # retrieve or prompt for api key
        m = Memory("hockey.json")
        if m.get_data("API_KEY") is None:
            user_api_key = jarvis.input("Enter API-Hockey.com API_KEY: ", Fore.GREEN)
            m.add_data("API_KEY", user_api_key)
            m.save()
            self.key = user_api_key
        else:
            self.key = m.get_data("API_KEY")

    def process_chosen_option(self, option, jarvis):
        # process selected menu option
        if option == "search_team":
            self.search_entity(jarvis, "teams", "Team")
        elif option == "list_leagues":
            self.list_leagues(jarvis)
        elif option == "todays_games":
            self.todays_games(jarvis)
        elif option == "search_league":
            self.search_entity(jarvis, "leagues", "League")
        elif option == "new_key":
            self.update_api_key(jarvis)
        else:
            return

    def update_api_key(self, jarvis):
        # update api key
        user_api_key = jarvis.input("Enter New API-Hockey.com API_KEY: ", Fore.GREEN)
        m = Memory("hockey.json")
        m.update_data("API_KEY", user_api_key)
        m.save()
        self.key = user_api_key

    def list_leagues(self, jarvis):
        # retrieve and display list of leagues
        jarvis.spinner_start('Fetching...')
        response = self.fetch_data("leagues")
        if response is None:
            jarvis.spinner_stop("Error loading data - try again later.", Fore.YELLOW)
            return
        leagues = response["response"]
        jarvis.spinner_stop("Found {} leagues".format(len(leagues)))
        for i, league in enumerate(leagues, start=1):
            print(" {}. {}".format(i, league["name"]))

    def search_entity(self, jarvis, query, entity_name):
        # search for teams or leagues by name
        value = jarvis.input(f"Enter {entity_name} Name: ", Fore.GREEN).strip()
        while len(value) < 3:
            jarvis.say(f"the {entity_name} name must be at least 3 characters long.", Fore.YELLOW)
            value = jarvis.input(f"Enter {entity_name} Name: ", Fore.GREEN).strip()
        jarvis.spinner_start(f'Searching for {entity_name}...')
        response = self.fetch_data(f"{query}?search={value}")
        if response is None:
            jarvis.spinner_stop(f"Error while searching for {entity_name} - try again later.", Fore.YELLOW)
            return
        entities = response["response"]
        if not entities:
            jarvis.spinner_stop(f"No {entity_name} found", Fore.YELLOW)
            return
        jarvis.spinner_stop(f"Found {len(entities)} {entity_name}(s)")
        for i, entity in enumerate(entities, start=1):
            print(f" {i}. {entity['name']}")

    def todays_games(self, jarvis):
        # retrieve and display today's games
        jarvis.spinner_start('Fetching...')
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        response = self.fetch_data(f"games?date={date}")
        if response is None:
            jarvis.spinner_stop("Error loading matches - try again later.", Fore.YELLOW)
            return
        matches = response["response"]
        if not matches:
            jarvis.spinner_stop("No matches today", Fore.YELLOW)
            return
        jarvis.spinner_stop("Found {} matches".format(len(matches)))
        for i, match in enumerate(matches, start=1):
            print(" {}. {} VS {}".format(i, match["teams"]["home"]["name"], match["teams"]["away"]["name"]))

    def get_option(self, jarvis):
        # display menu options
        options = {1: "todays_games", 2: "search_team", 3: "list_leagues", 4: "search_league", 5: "new_key"}

        print()
        jarvis.say("What would you like to do?", Fore.BLUE)
        print("1: list today's games")
        print("2: search team by name")
        print("3: list available leagues")
        print("4: search league by name")
        print("5: enter new api key")
        print("6: exit")
        print()
        choice = self.get_choice(jarvis)
        return options.get(choice)

    def get_choice(self, jarvis):
        # handle menu selection input
        while True:
            try:
                value = int(jarvis.input("Enter your choice: ", Fore.GREEN))
                if value == 6:
                    return None
                elif 1 <= value <= 5:
                    return value
                else:
                    jarvis.say("Invalid input! choose from the options provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say("Invalid input! choose from the options provided.", Fore.YELLOW)
