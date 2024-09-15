import requests
from numpy.distutils.conv_template import header


# API KEY = 0209778eaa6148d8b68b6484ff217a4f

class Soccer():
    BASE_URL = "http://api.football-data.org/v4/"
    API_KEY = None
    def __call__(self, jarvis, s):
        print('\nFeature powered by football-data.org APIs')
        if self.API_KEY is None:
            self.API_KEY = input('Enter an API key by registering at football-data.org/client/register: ')
            while requests.get(self.BASE_URL + 'competitions/2013/matches', headers = {'X-Auth-Token': self.API_KEY}).status_code == 403:
                self.API_KEY = input('Please enter a valid API key: ')
            self.get_competitions()


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



    def get_matches(self, competition_id: str):
        headers = {
            'X-Auth-Token': self.API_KEY
        }
        response = requests.get(f'{self.BASE_URL}competitions/{competition_id}/matches', headers=headers)
        if response.status_code == 200:


def main():
    soccer = Soccer()
    soccer("","")


if __name__ == '__main__':
    main()