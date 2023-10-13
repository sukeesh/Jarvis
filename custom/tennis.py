import re

import requests
from bs4 import BeautifulSoup
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin("tennis")
def tennis(jarvis, s):
    """Repeats what you type"""
    option = str(jarvis.input("Choose one of these option:\n "
                              "\n1. Current ATP rankings. "
                              "\n2. Current WTA rankings. "
                              "\n3. Past Grand Slam winners for ATP"
                              "\n4. Past Grand Slam winners for WTA\n", Fore.BLUE))

    if option == '1':
        get_current_ATP_rankings()
    elif option == '2':
        get_current_WTA_rankings()
    elif option == '3':
        get_grand_slam_ATP_winners()
    elif option == '4':
        get_grand_slam_WTA_winners()
    else:
        jarvis.say("You should input a option either 1 ~ 4.")


def get_current_ATP_rankings():
    urls = {
        "ATP": "https://tennisapi1.p.rapidapi.com/api/tennis/rankings/atp/live",
    }

    headers = {
        "X-RapidAPI-Key": "fd465be687msh3301d6b31b7b572p184e56jsnedc4fcdbd169",
        "X-RapidAPI-Host": "tennisapi1.p.rapidapi.com"
    }

    for key, url in urls.items():
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            rankings = data.get('rankings')
            if rankings and isinstance(rankings, list):
                for player in rankings:
                    name = player.get('rowName')
                    ranking = player.get('ranking')
                    points = player.get('points')
                    print(f"{key} Player: {name}, Ranking: {ranking}, Points: {points}")
            else:
                print(f"No ranking data available for {key}.")
        else:
            print(f"Failed to fetch {key} ranking.")


def get_current_WTA_rankings():
    urls = {
        "WTA": "https://tennisapi1.p.rapidapi.com/api/tennis/rankings/wta/live"
    }

    headers = {
        "X-RapidAPI-Key": "fd465be687msh3301d6b31b7b572p184e56jsnedc4fcdbd169",
        "X-RapidAPI-Host": "tennisapi1.p.rapidapi.com"
    }

    for key, url in urls.items():
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            rankings = data.get('rankings')
            if rankings and isinstance(rankings, list):
                for player in rankings:
                    name = player.get('rowName')
                    ranking = player.get('ranking')
                    points = player.get('points')
                    print(f"{key} Player: {name}, Ranking: {ranking}, Points: {points}")
            else:
                print(f"No ranking data available for {key}.")
        else:
            print(f"Failed to fetch {key} ranking.")


def get_grand_slam_ATP_winners():
    urls = {
        "Men": "https://en.wikipedia.org/wiki/List_of_Grand_Slam_men%27s_singles_champions"
    }

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
        , 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }

    for key, url in urls.items():
        response = requests.get(url, headers=header)
        # print(response.text)  # Remove this line if you don't want to print the whole HTML content
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # find table
            table = soup.find_all('table')[3]

            # Get all rows in the table
            rows = table.find_all('tr')[1:]  # Skip the header row
            print("Grand Slam ATP Winners for past 5 years.")
            print("♠ 	Player won the four major tournaments in the same year. \n"
                  "● 	Player won three major tournaments in the same year. \n"
                  "♦ 	Player won two major tournaments in the same year. \n"
                  "§ 	Tournament change of surface. \n")

            print("{:<10} {:<20} {:<20} {:<20} {:<20}".format("Year", "Australian Open", "French Open", "Wimbledon",
                                                              "US Open"))
            print("{:<10} {:<20} {:<20} {:<20} {:<20}".format("----", "---------------", "-----------", "---------",
                                                              "-------"))

            # Print the winners for each year (assuming the order of tournaments in the table is fixed)
            for row in rows[-6:-1]:  # Adjust this to print more or less rows
                columns = row.find_all('td')
                year = columns[0].text.strip()
                ao_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[1].text).strip()
                fo_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[2].text).strip()
                wimbledon_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[3].text).strip()
                us_open_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[4].text).strip()

                print("{:<10} {:<20} {:<20} {:<20} {:<20}".format(year, ao_winner, fo_winner, wimbledon_winner, us_open_winner))



def get_grand_slam_WTA_winners():
    urls = {
        "Women": "https://en.wikipedia.org/wiki/List_of_Grand_Slam_women%27s_singles_champions"
    }

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
        , 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }

    for key, url in urls.items():
        response = requests.get(url, headers=header)
        # print(response.text)  # Remove this line if you don't want to print the whole HTML content
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # find table
            table = soup.find_all('table')[2]

            # Get all rows in the table
            rows = table.find_all('tr')[1:]  # Skip the header row
            print("Grand Slam WTA Winners for past 5 years. \n")
            print("♠ 	Player won the four major tournaments in the same year. \n"
                  "● 	Player won three major tournaments in the same year. \n"
                  "♦ 	Player won two major tournaments in the same year. \n"
                  "§ 	Tournament change of surface. \n"
                  "* 	French club members or citizens only, thus not yet a Grand Slam tournament"
                  "(until 1925 when the tournament opened itself to international competitors after merging with the World Hard Court Championships). \n"
                  "† 	Tournaments held during German occupation not recognized by Fédération Française de Tennis. \n"
                  "‡ 	Australian Open held in December from 1977 through 1985, then moved back to January (skipped one calendar year in order to arrange that). \n"
                  "◊ 	2020 French Open held in September ( as the last Grand Slam tournament of the year) due to the COVID-19 pandemic. \n")

            print("{:<10} {:<20} {:<20} {:<20} {:<20}".format("Year", "Australian Open", "French Open", "Wimbledon",
                                                              "US Open"))
            print("{:<10} {:<20} {:<20} {:<20} {:<20}".format("----", "---------------", "-----------", "---------",
                                                              "-------"))

            # Print the winners for each year (assuming the order of tournaments in the table is fixed)
            for row in rows[-6:-1]:  # Adjust this to print more or less rows
                columns = row.find_all('td')
                year = columns[0].text.strip()
                ao_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[1].text).strip()
                fo_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[2].text).strip()
                wimbledon_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[3].text).strip()
                us_open_winner = re.sub(r'\[.*\]|\(.*\)', '', columns[4].text).strip()

                print("{:<10} {:<20} {:<20} {:<20} {:<20}".format(year, ao_winner, fo_winner, wimbledon_winner, us_open_winner))

