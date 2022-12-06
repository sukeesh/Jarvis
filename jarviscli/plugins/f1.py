import requests
from colorama import Fore

from plugin import plugin, require
from tabulate import tabulate

def fetch(route):
    
    url = 'http://ergast.com/api/f1/'
    r = requests.get(url + route + ".json")
    r = r.json()
    if "errorCode" in r.keys():
        return None
    return r

@require(network=True)
@plugin('f1')
class F1():
    """
    Provides f1 seasons information

    Enter 'f1' to use.
    """

    def __call__(self, jarvis, s):
        # Attribution to the rugby-data.org API
        print("F1 data provided by the ergast.com API\n")
        # Ask for user option (competition or match info)
        option = self.get_option(jarvis)
        if option is None:
            return
        # Present the list of competitions
        # (common step for both choices)
        year = self.get_year(jarvis)
        # Proceed according to option
        if year is None:
            return
        self.standings(jarvis, option, year)
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
        print("1: Driver Standings")
        print("2: Constructor Standings")
        print("3: Exit")
        print()
        while True:
            try:
                option = int(jarvis.input("Enter your choice: ", Fore.GREEN))
                if option == 3:
                    return
                elif option == 1 or option == 2:
                    return option
                else:
                    jarvis.say(
                        "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            print()

    def get_year(self, jarvis):
        """
        Takes input from user for selecting a year
        """
        # Ask for the year
        
        jarvis.say("Give a year from 1950 to today's year :", Fore.BLUE)
        print()
        while True:
            year = str(jarvis.input("Enter your choice: ", Fore.GREEN))
            return year

    def standings(self, jarvis, option, year):
        """
        Fetches details of a competition and outputs
        the competition's current standings
        """
        # Fetch competition info)
        jarvis.spinner_start('Fetching ')
        if option==1:
        	r = fetch(str(year)+"/driverStandings")
        	jarvis.spinner_stop('')
        
        	self.printStandingsDriver(jarvis, r["MRData"]['StandingsTable']["StandingsLists"][0]["DriverStandings"])
        else:
        	r = fetch(str(year)+"/constructorStandings")
        	jarvis.spinner_stop('')
        
        	self.printStandingsConstructor(jarvis, r["MRData"]['StandingsTable']["StandingsLists"][0]["ConstructorStandings"])
            
    

    def printStandingsDriver(self, jarvis, tables):
        """
        Helper function for validating, formatting
        and printing the standings table
        """
        if len(tables) == 0:
            # No standings available
            jarvis.say("No standings found for this competition.", Fore.BLUE)
            return
            
        jarvis.say("Here are the full standings: ", Fore.BLUE)
        print()
   
        stList = []
        for team in tables:
        
            # Set "team" property to only team name
            stList.append([team['positionText'], team["Driver"]["givenName"]+" "+team["Driver"]["familyName"], team["Constructors"][0]["name"], team["points"], team["wins"]])
        # Print the standings table
        print(tabulate(stList, headers=[
            "#", "Name", "Constructor", "Points", "Wins"]))
        print()
        
        
        
        
        
    def printStandingsConstructor(self, jarvis, tables):
        """
        Helper function for validating, formatting
        and printing the standings table
        """
        if len(tables) == 0:
            # No standings available
            jarvis.say("No standings found for this competition.", Fore.BLUE)
            return
            
        jarvis.say("Here are the full standings: ", Fore.BLUE)
        print()
   
        stList = []
        for team in tables:
        
            # Set "team" property to only team name
            stList.append([team['positionText'], team["Constructor"]["name"], team["points"], team["wins"]])
        # Print the standings table
        print(tabulate(stList, headers=[
            "#", "Name", "Points", "Wins"]))
        print()
        
        
