import imdb


def main(movie):
    app = imdb.IMDb()
    results = app.search_movie(movie)
    if not results:
        return "error 404"
    first = results[0]
    ID = first.movieID
    data = app.get_movie(ID)
    return data


def cast(movie):
    data = main(movie)
    if data == "error 404":
        return data
    return data['cast']


def director(movie):
    data = main(movie)
    if data == "error 404":
        return data
    return data['director']


def plot(movie):
    data = main(movie)
    if data == "error 404":
        return data
    return data['plot outline']


def producer(movie):
    data = main(movie)
    if data == "error 404":
        return data
    return data['producer']


def rating(movie):
    data = main(movie)
    if data == "error 404":
        return data
    return data['rating']


def year(movie):
    data = main(movie)
    if data == "error 404":
        return data
    return data['year']
