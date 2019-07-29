import imdb
import six
from colorama import Fore, Style
from plugin import plugin, require

app = imdb.IMDb()


def main(jarvis, movie):
    movie_id = search_movie(jarvis, movie)

    if movie_id is None:
        return None
    return get_movie_by_id(movie_id)


def search_movie(jarvis, movie, all_results=False):
    if movie == '':
        jarvis.say("Please add movie name!", Fore.RED)
        return None
    results = app.search_movie(movie, results=10)
    if not results:
        jarvis.say("Error: Did not find movie!", Fore.RED)
        return None
    if not all_results:
        first = results[0]
        return first.movieID

    return results


def get_movie_by_id(movie_id):
    return app.get_movie(movie_id)


# cache: Python3 only
if six.PY3:
    from functools import lru_cache

    # equals @functools.lru_cache(maxsize=50, typed=False)
    search_movie = lru_cache(maxsize=50, typed=False)(search_movie)
    get_movie_by_id = lru_cache(maxsize=20, typed=False)(get_movie_by_id)


@require(network=True)
@plugin('movie cast')
def movie_cast(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['cast']:
            jarvis.say(d['name'])


@require(network=True)
@plugin('movie director')
def movie_director(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['director']:
            jarvis.say(d['name'])


@require(network=True)
@plugin('movie plot')
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


@require(network=True)
@plugin('movie producer')
def movie_producer(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['producers']:
            jarvis.say(d['name'])


@require(network=True)
@plugin('movie rating')
def movie_rating(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        jarvis.say(str(data['rating']))


@require(network=True)
@plugin('movie year')
def movie_year(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        jarvis.say(str(data['year']))


@require(network=True)
@plugin('movie runtime')
def movie_runtime(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        if 'runtimes' in data:
            jarvis.say(str(data['runtimes'][0]) + ' minutes')
        else:
            jarvis.say("No runtime data present")


@require(network=True)
@plugin('movie countries')
def movie_countries(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['countries']:
            jarvis.say(str(d))


@require(network=True)
@plugin('movie genres')
def movie_genres(jarvis, movie):
    """"""
    data = main(jarvis, movie)
    if data is not None:
        for d in data['genres']:
            jarvis.say(d)


@require(network=True)
@plugin('movie info')
def movie_info(jarvis, movie):
    """
    Display table with various information
    """
    data = main(jarvis, movie)

    if data is not None:
        get_movie_info(jarvis, data)


@require(network=True)
@plugin('movie search')
def movie_search(jarvis, movie):
    """ search for a movie on IMDB"""
    results = search_movie(jarvis, movie, all_results=True)

    # if results is None or empty
    if not results:
        return None

    # get only movies from the results, filtering out TV series, etc
    movie_results = []
    for item in results:
        if item['kind'] == 'movie':
            movie_results.append(item)

    if len(movie_results) > 5:
        count = 5
    else:
        count = len(movie_results)

    jarvis.say('')
    space = ' '
    text = 'ID'
    text += space * 3 + 'Movie title'
    jarvis.say(text, Fore.GREEN)

    for i in range(count):
        item = movie_results[i]
        text = Fore.GREEN + str(i + 1) + space * 4
        text += Fore.RESET + item['smart long imdb canonical title']
        jarvis.say(text)

    jarvis.say('')
    jarvis.say('Please enter ID to know more(q - quit):')

    input_id = jarvis.input()

    # If nothing is entered, just return
    if input_id is '':
        return None
    if len(input_id) != 1:
        return jarvis.say(Fore.RED + 'Please enter valid value')
    elif input_id in '123456789':
        input_id = int(input_id)
    elif input_id == 'q':
        return None

    # if entered input is out of the given list of ID's
    if (int(input_id) > count) or (int(input_id) < 1):
        return jarvis.say(Fore.RED + 'Please enter id from the given list')

    movie_id = movie_results[input_id - 1].movieID
    data = get_movie_by_id(movie_id)
    get_movie_info(jarvis, data)


def colorized_output(key, value):
    """
    pretty print key value pair
    """
    green_text = Fore.GREEN + "{:<14}".format(key)
    normal_text = Style.RESET_ALL + ": " + str(value)
    return green_text + normal_text


def get_movie_info(jarvis, data):
    """
    Takes a movie attributes as input and prints them accordingly
    """
    jarvis.say('')
    jarvis.say(
        'What type of information do you want: cast, producers, genres, etc.?')
    jarvis.say('Write one after another separated by space, please:')

    movie_attributes = jarvis.input()
    movie_attributes = movie_attributes.split()
    jarvis.say('')

    for attribute in movie_attributes:
        if attribute in data:
            value = data[attribute]

            if attribute == 'genres':
                value = ', '.join(value)

            if attribute == 'cast':
                lst = [person['name'] for person in value]
                value = ', '.join(lst[0:3])

            if isinstance(value, list):
                value = value[0]

            jarvis.say(colorized_output(attribute.capitalize(), str(value)))
        else:
            jarvis.say(
                colorized_output(
                    attribute.capitalize(),
                    'no information retrieved'))

    # print IMDB url of the movie

    movie_url = app.urls['movie_base'] + 'tt' + data.movieID
    jarvis.say(colorized_output('IMDB url', movie_url))
    jarvis.say('')
