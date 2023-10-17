import re

import requests
from bs4 import BeautifulSoup
from colorama import Fore
from plugin import plugin, require


class TennisDataFetcher:
    def __init__(self):
        self.headers = {
            "X-RapidAPI-Key": "fd465be687msh3301d6b31b7b572p184e56jsnedc4fcdbd169",
            "X-RapidAPI-Host": "tennisapi1.p.rapidapi.com"
        }

    def fetch_rankings(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch ranking.")
            return

        data = response.json()
        rankings = data.get('rankings')
        if rankings and isinstance(rankings, list):
            for player in rankings:
                print(
                    f"Player: {player.get('rowName')}, Ranking: {player.get('ranking')}, Points: {player.get('points')}")
        else:
            print("No ranking data available.")

    def fetch_grand_slam_winners(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Failed to fetch data.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all('table')[2 if "women" in url else 3]
        rows = table.find_all('tr')[1:]
        hint = "♠ 	Player won the four major tournaments in the same year. \n" \
               "● 	Player won three major tournaments in the same year. \n" \
               "♦ 	Player won two major tournaments in the same year. \n" \
               "§ 	Tournament change of surface. \n" \
               if "women" in url else \
               "♠ 	Player won the four major tournaments in the same year. \n" \
               "● 	Player won three major tournaments in the same year. \n" \
               "♦ 	Player won two major tournaments in the same year. \n" \
               "§ 	Tournament change of surface. \n" \
               "* 	French club members or citizens only, thus not yet a Grand Slam tournament" \
               "(until 1925 when the tournament opened itself to international competitors after merging with the World Hard Court Championships). \n" \
               "† 	Tournaments held during German occupation not recognized by Fédération Française de Tennis. \n" \
               "‡ 	Australian Open held in December from 1977 through 1985, then moved back to January (skipped one calendar year in order to arrange that). \n" \
               "◊ 	2020 French Open held in September ( as the last Grand Slam tournament of the year) due to the COVID-19 pandemic. \n"

        print(hint)

        print("{:<10} {:<20} {:<20} {:<20} {:<20}".format("Year", "Australian Open", "French Open", "Wimbledon",
                                                          "US Open"))
        print("{:<10} {:<20} {:<20} {:<20} {:<20}".format("----", "---------------", "-----------", "---------",
                                                          "-------"))

        for row in rows[-11:-1]:  # Adjust this to print more or less rows
            columns = row.find_all('td')
            year = columns[0].text.strip()
            ao_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[1].text).strip()
            fo_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[2].text).strip()
            wimbledon_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[3].text).strip()
            us_open_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[4].text).strip()

            print("{:<10} {:<20} {:<20} {:<20} {:<20}".format(year, ao_winner, fo_winner, wimbledon_winner,
                                                              us_open_winner))


@require(network=True)
@plugin("tennis")
class TennisPlugin:
    def __call__(self, jarvis, s):
        fetcher = TennisDataFetcher()

        option = str(jarvis.input("Choose one of these options:\n "
                                  "1. Current ATP rankings\n "
                                  "2. Current WTA rankings\n "
                                  "3. Past Grand Slam winners for ATP\n "
                                  "4. Past Grand Slam winners for WTA\n", Fore.BLUE))

        if option == '1':
            fetcher.fetch_rankings("https://tennisapi1.p.rapidapi.com/api/tennis/rankings/atp/live")
        elif option == '2':
            fetcher.fetch_rankings("https://tennisapi1.p.rapidapi.com/api/tennis/rankings/wta/live")
        elif option == '3':
            fetcher.fetch_grand_slam_winners(
                "https://en.wikipedia.org/wiki/List_of_Grand_Slam_men%27s_singles_champions")
        elif option == '4':
            fetcher.fetch_grand_slam_winners(
                "https://en.wikipedia.org/wiki/List_of_Grand_Slam_women%27s_singles_champions")
        else:
            jarvis.say("You should input an option either 1 ~ 4.")
