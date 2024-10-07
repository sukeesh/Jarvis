from plugin import plugin
import requests
from colorama import Fore
def ExceptionHandling(type_of_input):
    jarvis.say(f"Your input for {type_of_input} was not in correct format.", Fore.RED)
    return
@plugin('boardgames')
def boardgames(jarvis, s):
    """
    Suggest board games
    """
    categories = {
    0: 'ALL',
    1: 'Strategy Games',
    2: 'Thematic Games',
    3: 'Wargames',
    4: 'Family Games',
    5: 'Customizable Games',
    6: 'Abstract Games',
    7: 'Party Games',
    8: "Children's Games"
    }

    jarvis.say("Select a category: ")
    for i in categories.keys():
        print(f'{i}: {categories[i]}')
    category_index = jarvis.input()
    try:
        category = categories[category_index]
    except KeyError:
        ExceptionHandling("category")
    age = jarvis.input("Type the age of youngest player. ")
    try:
        age = int(age)
    except ValueError:
        ExceptionHandling("age")
    players = jarvis.input("Type the number of players. ")
    try:
        players = int(players)
    except ValueError:
        ExceptionHandling("player count")
    rate = jarvis.input("Type minimum rating for the board game you want between 0-10. If you don't want to set a minimum rating, type 0.")
    try:
        rate = float(rate)
    except ValueError:
        ExceptionHandling("rating")
    r = requests.get(f'https://boardgames.pythonanywhere.com/search?category={category}&playerCount={players}&age={age}&rating={rate}')
    data = r.json()
    counter = 0
    jarvis.say('Here are the games I found: ')
    for game in data:
        counter += 1
        jarvis.say(f"""Game {counter}
        Name: {game['Name']}
        Year Published: {game['YearPublished']}
        Players: {game['MinPlayers']} to {game['MaxPlayers']}
        Rating: {game['RatingAverage']}
        Categories: {game['Domains']}
        """)
