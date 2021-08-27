from plugin import plugin, require
import requests
from bs4 import BeautifulSoup

valid_genres = [
        "comedy", "sci-fi", "horror", 
        "romance", "action", "thriller", 
        "drama", "mystery", "crime", 
        "animation", "adventure", "fantasy", 
        "comedy,romance", "action,comedy", 
        "superhero"
        ]


@require(network=True)
@plugin("topmovies")
def top_250_movies(jarvis, genre):
    # Taking care of accidental capitalisations when entering the genre.
    genre = genre.lower()

    if genre in valid_genres:
        # Each page on IMDB contains 50 movies. So, start = 1 implies movies ranked 1-50.
        for start in [1,51,101,151,201]:
            url = ("https://www.imdb.com/search/title/?genres="
                   + genre
                   + "&start="
                   + str(start)
                   + "&explore=title_type,genres&title_type=movie")
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            table = soup.find("div", attrs = {"class":"lister-list"}) 
            i = 0
            for row2 in table.findAll("h3", attrs = {"class":"lister-item-header"}):
                #Printing rank and name of the movie.
                jarvis.say(str(start + i) + ". " + row2.a.text)    # The a tag has the name of the movie
                i += 1
    else:
        jarvis.say("The genre you have entered is not valid.\nPlease try again with one of the following genres:")
        for genre in valid_genres:
            jarvis.say(genre)