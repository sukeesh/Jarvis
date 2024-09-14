import requests


BASE_URL = "http://api.football-data.org/v4/"
API_KEY = "0209778eaa6148d8b68b6484ff217a4f"

class Soccer():
    def get_competitions(self):
        headers = {
            'X-Auth-Token': API_KEY
        }
        response = requests.get(BASE_URL + 'competitions', headers=headers)
        if response.status_code == 200:
            payload = response.json()
            competitions = payload['competitions']
            for competition in competitions:
                print(f"{competition['name']:<30} (ID: {competition['id']})")


if __name__ == '__main__':
    main()