from colorama import Fore
import imdb
from utilities.GeneralUtilities import print_say


def movie_plot(self, movie):
    app = imdb.IMDb()
    results = app.search_movie(movie)
    first = results[0]
    ID = first.movieID
    data = app.get_movie(ID)
    title = data['title']
    plot = ""
    story = data['plot']
    for i in story:
        plot += i
        plot += "\n"
    print_say(str(title), self, Fore.RED)
    print_say(str(plot), self)
