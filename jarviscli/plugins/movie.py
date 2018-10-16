import imdb
from plugin import plugin
from colorama import Fore
import six


app = imdb.IMDb()


def main(jarvis, movie):
    movieId = search_movie(jarvis, movie)
    if movieId is None:
        return None
    return get_movie_by_id(search_movie(jarvis, movie))


def search_movie(jarvis, movie):
    if movie == '':
        jarvis.say("Please add movie name!", Fore.RED)
        return None
    results = app.search_movie(movie)
    if not results:
        jarvis.say("Error: Did not found movie!", Fore.RED)
        return None
    first = results[0]
    return first.movieID


def get_movie_by_id(movieID):
    return app.get_movie(movieID)


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
        jarvis.say(data['plot outline'])
        jarvis.say('')
        jarvis.say('')
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
        jarvis.say(str(data['runtimes']))


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

    def p(key):
        value = data[key]
        if isinstance(value, list):
            value = value[0]
        jarvis.say("{:<14}: {}".format(key, str(value)))

    if data is not None:
        p('title')
        p('year')
        p('director')
        p('writer')
        p('color info')
        p('rating')
        p('aspect ratio')
        p('sound mix')
        p('runtimes')
