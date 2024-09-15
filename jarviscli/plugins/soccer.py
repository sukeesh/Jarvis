import requests
from datetime import datetime as dt

# API KEY = 0209778eaa6148d8b68b6484ff217a4f

class Soccer:
    BASE_URL = "http://api.football-data.org/v4/"
    API_KEY = '0209778eaa6148d8b68b6484ff217a4f'
    def __call__(self, jarvis, s):
        print('\nFeature powered by football-data.org APIs')
        if self.API_KEY is None:
            self.API_KEY = input('Enter an API key by registering at football-data.org/client/register: ')
            while requests.get(self.BASE_URL + 'competitions/2013/matches', headers = {'X-Auth-Token': self.API_KEY}).status_code == 403:
                self.API_KEY = input('Please enter a valid API key: ')
        self.get_competitions()
        competition_id = input()
        self.get_matches(competition_id)

    def get_competitions(self):
        headers = {
            'X-Auth-Token': self.API_KEY
        }
        response = requests.get(self.BASE_URL + 'competitions', headers=headers)
        if response.status_code == 200:
            payload = response.json()
            competitions = payload['competitions']
            print('\nPlease select a competition ID from the following:\n')
            print(f"{' Competitions ':—^40}")
            for competition in competitions:
                print(f"{competition['name']:<30} (ID: {competition['id']})")
            print()
        else:
            print('Error retrieving API based data - ' + str(response.status_code))


    def get_matches(self, competition_id: str):
        headers = {
            'X-Auth-Token': self.API_KEY
        }
        curr = dt.now()
        year_to = curr.year
        if curr.month == 12:
            year_to += 1
        parameters = {
            'dateFrom'  :   f'{curr.year}-{curr.month}-{curr.day}',
            'dateTo'    :   f'{year_to}-{(curr.month + 1)%12}-{curr.day}'
        }
        URL = f'{self.BASE_URL}competitions/{competition_id}/matches'
        print(parameters['dateTo'] + parameters['dateFrom'])
        print(URL)
        response = requests.get(URL, params=parameters, headers=headers)
        payload = response.json()
        if response.status_code == 200:
            matches = payload['matches']
            if len(matches) == 0:
                print('No match data available in the upcoming month')
                return
            for match in matches:
                home = f'{match["homeTeam"]["shortName"]} ({match["homeTeam"]["tla"]})'
                away = f'{match["awayTeam"]["shortName"]} ({match["awayTeam"]["tla"]})'
                finished = match["status"] == "FINISHED"
                home_goals = match["score"]["fullTime"]["home"]
                away_goals = match["score"]["fullTime"]["away"]
                time = match["utcDate"]
                print(f'{time:—^40}')
                print(f'\033[91m{home:<30} {home_goals} --- {away_goals} \033[0m{away:>30}')
        else:
            print('Error retrieving API based data - ' + str(response.status_code))


def main():
    soccer = Soccer()
    soccer("","")


if __name__ == '__main__':
    main()