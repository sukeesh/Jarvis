import imdb
from plugin import plugin
from colorama import Fore, Style
import six


app = imdb.IMDb()


def main(jarvis, movie):
    movie_id = search_movie(jarvis, movie)
    if movie_id is None:
        return None
    return get_movie_by_id(movie_id)


def search_movie(jarvis, movie):
    if movie == '':
        jarvis.say("Please add movie name!", Fore.RED)
        return None
    results = app.search_movie(movie)
    if not results:
        jarvis.say("Error: Did not find movie!", Fore.RED)
        return None
    first = results[0]
    return first.movieID


def get_movie_by_id(movie_id):
    return app.get_movie(movie_id)


# cache: Python3 only
if six.PY3:
    from functools import lru_cache

    # equals @functools.lru_cache(maxsize=50, typed=False)
    search_movie = lru_cache(maxsize=50, typed=False)(search_movie)
    get_movie_by_id = lru_cache(maxsize=20, typed=False)(get_movie_by_id)


@plugin(network=True)
def movie_cast(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['cast']:
            jarvis.say(d['name'])


@plugin(network=True)
def movie_director(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['director']:
            jarvis.say(d['name'])


@plugin(network=True)
def movie_plot(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        if 'plot outline' in data:
            jarvis.say('Plot outline:', Fore.GREEN)
            jarvis.say(data['plot outline'])
            jarvis.say('')
        if 'plot' in data:
            jarvis.say('Plot:', Fore.GREEN)
            for d in data['plot']:
                jarvis.say(d)


@plugin(network=True)
def movie_producer(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['producers']:
            jarvis.say(d['name'])


@plugin(network=True)
def movie_rating(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        jarvis.say(str(data['rating']))


@plugin(network=True)
def movie_year(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        jarvis.say(str(data['year']))


@plugin(network=True)
def movie_runtime(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        if 'runtimes' in data:
            jarvis.say(str(data['runtimes'][0]) + ' minutes')
        else:
            jarvis.say("No runtime data present")


@plugin(network=True)
def movie_countries(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['countries']:
            jarvis.say(str(d))


@plugin(network=True)
def movie_genres(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['genres']:
            jarvis.say(d)


@plugin(network=True)
def movie_info(jarvis, movie):
    """
    Display table with various information
    """
    data = main(jarvis, movie)

    movie_attributes = [
        'title', 'year', 'genres', 'director',
        'writer', 'cast', 'color info', 'rating',
        'aspect ratio', 'sound mix', 'runtimes',
        'plot outline'
    ]

    def pretty_list(lst):
        """
        Takes a list as input and returns a string with coma separated values
        :param lst:
        :return string:
        """
        line = lst[0]
        for i in lst[1:]:
            line += ', ' + i
        return line

    def get_movie_info(key):
        """
        Takes a movie attribute as input and prints them accordingly
        :param key:
        :return:
        """
        value = data[key]
        if isinstance(value, list):
            if key in ['cast', 'genres']:
                if key == 'genres':
                    value = pretty_list(value)
                if key == 'cast':
                    lst = [d['name'] for d in value]
                    value = pretty_list(lst[0:3])
            else:
                value = value[0]
        jarvis.say(Fore.GREEN + "{:<14}".format(key.capitalize())
                   + Style.RESET_ALL + ": " + str(value))

    if data is not None:
        for attribute in movie_attributes:
            if attribute in data:
                get_movie_info(attribute)

    # print IMDB url of the movie
    jarvis.say(Fore.GREEN + "{:<14}".format('IMDB url')
               + Style.RESET_ALL + ": " 
               + str(app.urls['movie_base'] + 'tt' + data.movieID))
