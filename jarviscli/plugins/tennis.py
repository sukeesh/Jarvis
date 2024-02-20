import requests
from colorama import Fore
from jarviscli import entrypoint, get_api_key

URL = "https://api.sportradar.com/tennis/trial/v3/en/rankings"
KEY = get_api_key(sportradar)


@entrypoint
def run(jarvis, s):
    Tennis()(jarvis, s)


class Tennis():
    """
    Tennis Plugin for getting information about ATP and
    !!! needs api.sportradar.com/tennis API_KEY for usage
    """

    def __call__(self, jarvis, s):
        print("\nTennis data provided by the sportradar.com")
        while True:
            option = self.get_option(jarvis)
            if option is None:
                return
            self.process_option(jarvis, option)

    def process_option(self, jarvis, option):
        """
        Processes the users input option and performs required action,
        either getting and printing ATP rankings,
        getting and printing WTA rankings, or resetting API key
        """
        data = self.fetch_data(f'?api_key={KEY}')
        if data is None:
            jarvis.spinner_stop("Error While Loading Data - "
                                "Try Again Later.", Fore.YELLOW)
            return
        if option == 'atp':
            self.get_atp_top10(data)
        if option == 'wta':
            self.get_wta_top10(data)

    def get_atp_top10(self, data):
        """
        Makes API call to get ATP rankings, prints out top 10 players
        """
        atp_rankings = data['rankings'][0]['competitor_rankings']
        atp_names = [obj['competitor']['name'] for obj in atp_rankings]
        i = 1
        print('\nCurrent ATP Rankings\n')
        for name in atp_names[:10]:
            print(f'{i}. {name}')
            i += 1

    def get_wta_top10(self, data):
        """
        Makes API call to get WTA rankings, prints out top 10 players
        """
        wta_rankings = data['rankings'][1]['competitor_rankings']
        wta_names = [obj['competitor']['name'] for obj in wta_rankings]
        i = 1
        print('\nCurrent WTA Rankings:\n')
        for name in wta_names[:10]:
            print(f'{i}. {name}')
            i += 1

    def get_headers(self):
        """
        Gets headers required for all HTTP requests made by this plugin
        """
        return {"accept": "application/json"}

    def fetch_data(self, route):
        """
        Makes API call for given route
        """
        r = requests.get(URL + route, headers=self.get_headers())
        r = r.json()
        if "errorCode" in r.keys():
            return None
        return r

    def get_option(self, jarvis):
        """
        Prompts user for what feature of the tennis plugin they'd like
        to use and takes in and returns the user's choice
        """
        options = {1: "atp", 2: "wta", 3: "new_key"}

        print()
        jarvis.say("How Can I Help You?", Fore.BLUE)
        print()
        print("1: Get ATP (mens) tennis rankings")
        print("2: Get WTA (womens) tennis rankings")
        print("4: exit")
        print()
        choice = self.get_choice(jarvis)
        if choice == -1:
            return
        else:
            return options[choice]

    def get_choice(self, jarvis):
        """
        Prompts user for integer choice indicating what part of the
        tennis plugin they want to use, returns this choice
        """
        while True:
            try:
                inserted_value = int(jarvis.input("Enter your "
                                                  "choice: ", Fore.GREEN))
                if inserted_value == 4:
                    return -1
                elif inserted_value in [1, 2, 3]:
                    return inserted_value
                else:
                    jarvis.say(
                        "Invalid input! Enter a number "
                        "from the choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say(
                    "Invalid input! Enter a number "
                    "from the choices provided.", Fore.YELLOW)
            print()
