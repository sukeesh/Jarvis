import requests
from colorama import Fore

from plugin import plugin, require
from tabulate import tabulate

API_KEY = '1ebd3b92bf5041249f8c1e7a540ce98c'
url = 'https://api.football-data.org/v2'
headers = {'X-Auth-Token': API_KEY}


def fetch(route):
    r = requests.get(url + route, headers=headers)
    r = r.json()
    if "errorCode" in r.keys():
        return None
    return r


@require(network=True)
@plugin('football')
class Football():
    """
    Provides football competition information (tournament/league standings) and daily match info.

    Enter 'football' to use.
    """

    def __call__(self, jarvis, s):
        # Attribution to the football-data.org API
        print("Football data provided by the Football-Data.org API\n")
        # Ask for user option (competition or match info)
        option = self.get_option(jarvis)
        if option is None:
            return
        # Present the list of competitions
        # (common step for both choices)
        compId = self.get_competition(jarvis)
        # Proceed according to option
        if compId is None:
            return
        if option == 'competitions':
            self.competition(jarvis, compId)
        elif option == 'matches':
            self.matches(jarvis, compId)
        print()

    def get_option(self, jarvis):
        """
        Get user input for choosing between
        match info or competition info
        """
        options = {1: 'competitions', 2: 'matches'}
        # Ask for the option
        jarvis.say("What information do you want:", Fore.BLUE)
        print()
        print("1: Competition/league standings")
        print("2: Today's matches")
        print("3: Exit")
        print()
        while True:
            try:
                option = int(jarvis.input("Enter your choice: ", Fore.GREEN))
                if option == 3:
                    return
                elif option == 1 or option == 2:
                    return options[option]
                else:
                    jarvis.say(
                        "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            print()

    def get_competition(self, jarvis):
        """
        Takes input from user for selecting a competition
        """
        # Fetch top-tier competitions
        jarvis.spinner_start('Fetching ')
        r = fetch("/competitions?plan=TIER_ONE")
        if r is None:
            jarvis.spinner_stop("Error in fetching data - try again later.", Fore.YELLOW)
            return
        comps = r["competitions"]
        jarvis.spinner_stop("Pick a competition:", Fore.BLUE)
        # Print the list of competitions
        print()
        for i in range(r["count"]):
            print("{}: {}, {}".format(
                i + 1, comps[i]["name"], comps[i]["area"]["name"]))
        print("0: Exit")
        print()
        # Take input option
        while True:
            try:
                option = int(jarvis.input("Enter your choice: ", Fore.BLUE))
                if option == 0:
                    return None
                elif option in range(1, r["count"] + 1):
                    return comps[option - 1]["id"]
                else:
                    jarvis.say(
                        "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            print()

    def competition(self, jarvis, compId):
        """
        Fetches details of a competition and outputs
        the competition's current standings
        """
        # Fetch competition info)
        jarvis.spinner_start('Fetching ')
        r = fetch("/competitions/{}/standings".format(compId))
        if r is None:
            jarvis.spinner_stop("Error in fetching data - try again later.", Fore.YELLOW)
            return

        jarvis.spinner_stop('')
        print()
        self.printStandings(jarvis, r["standings"])

    def printStandings(self, jarvis, tables):
        """
        Helper function for validating, formatting
        and printing the standings table
        """
        if len(tables) == 0:
            # No standings available
            jarvis.say("No standings found for this competition.", Fore.BLUE)
            return
        if tables[0]["group"] is None:
            # League table - print top three
            jarvis.say("First position:  {}".format(
                tables[0]["table"][0]["team"]["name"]))
            jarvis.say("Second position: {}".format(
                tables[0]["table"][1]["team"]["name"]))
            jarvis.say("Third position:  {}".format(
                tables[0]["table"][2]["team"]["name"]))
            print()
        # General case
        jarvis.say("Here are the full standings: ", Fore.BLUE)
        print()
        for table in tables:
            # Loop through all standing tables
            if table["type"] != "TOTAL":
                # Do not print HOME and AWAY tables
                continue
            if table["group"] is not None:
                # Group table - print the group name
                print(Fore.BLUE + "GROUP " + table["group"][6] + Fore.RESET)
                print()
            stList = []
            for team in table["table"]:
                # Set "team" property to only team name
                team["team"] = team["team"]["name"]
                stList.append([team[k] for k in team])
            # Print the standings table
            print(tabulate(stList, headers=[
                "#", "Team", "P", "W", "D", "L", "Points", "GF", "GA", "GD"]))
            print()

    def matches(self, jarvis, compId):
        """
        Fetches today's matches in given competition
        and prints the match info
        """
        print()
        jarvis.spinner_start('Fetching ')
        r = fetch("/matches?competitions={}".format(compId))
        if r is None:
            jarvis.spinner_stop("Error in fetching data - try again later.", Fore.YELLOW)
            return

        jarvis.spinner_stop('')
        if r["count"] == 0:
            jarvis.say("No matches found for today.", Fore.BLUE)
            return
        else:
            # Print each match info
            for match in r["matches"]:
                matchInfo = self.formatMatchInfo(match)
                length = len(matchInfo)
                jarvis.say(matchInfo[0], Fore.BLUE)
                for i in range(1, length):
                    print(matchInfo[i])
                print()

    def formatMatchInfo(self, match):
        """
        Helper function for formatting
        and printing match info
        """
        lines = []
        # Get home and away team names
        homeTeam = match["homeTeam"]["name"].upper()
        awayTeam = match["awayTeam"]["name"].upper()
        lines.append("{} vs {}".format(homeTeam, awayTeam))
        # Get type and status of match
        group = match["group"]
        status = match["status"]
        lines.append("Group:  {}".format(group))
        lines.append("Status: {}".format(status.capitalize()))
        # Get the scores
        if status != "SCHEDULED":
            # Get the score after 90 mins ordinary time
            scores = match["score"]
            homeScore = scores["fullTime"]["homeTeam"]
            awayScore = scores["fullTime"]["awayTeam"]
            lines.append("SCORE: {} - {}".format(homeScore, awayScore))
            if scores["extraTime"]["homeTeam"] is not None:
                # Match went on to extra time
                homeExtra = scores["extraTime"]["homeTeam"]
                awayExtra = scores["extraTime"]["awayTeam"]
                lines.append(
                    "Extra time: {} - {}".format(homeExtra, awayExtra))
            if scores["penalties"]["homeTeam"] is not None:
                # Match went on to penalties
                homePen = scores["penalties"]["homeTeam"]
                awayPen = scores["penalties"]["awayTeam"]
                lines.append("Penalties: {} - {}".format(homePen, awayPen))
        # Return list of lines
        return lines
