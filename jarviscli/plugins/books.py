from plugin import plugin, require
from bs4 import BeautifulSoup
import requests


@require(network=True)
@alias("books", "book")
@plugin('book_sugges')
def extract_genre(jarvis, s):
    """
        This method gives jarvis the ability to find a list of books
        based on the user's interest of genres.
    """
    jarvis.say("Hey! Ready to turn some pages? \n")
    jarvis.say("Here are some of the interesting genres: ")
    genres = [
        "romance",
        "fiction",
        "fantasy",
        "science-fiction",
        "non-fiction"
        "",
        "children",
        "history",
        "mystery",
        "horror",
        "historical-fiction",
        "love",
        "biography",
        "thriller",
        "contemporary",
        "classics",
        "novels",
        "series"]
    for gen in genres:
        jarvis.say(gen)
    jarvis.say("Please let me know your genre: ")
    genre = jarvis.input()
    # request sent for the url
    page = requests.get(
        "https://www.goodreads.com/search?&query={}".format(genre))
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all('tr', {'itemtype': "http://schema.org/Book"})
    records = []
    jarvis.say("Searching for books......\n")

    for item in results:  # Searches for books
        try:
            book = item.find('a', class_='bookTitle').span.text.strip()
            author = item.find(
                'div', class_='authorName__container').a.span.text.strip()
            rating = float(
                item.find(
                    'span',
                    class_="minirating").text.strip().split(" ")[0])
            record = (book, author, rating)
        except:
            record = None

        if record is not None:
            # Appends information of the book found as a record
            records.append(record)
    if records:
        sorted_ = sorted(records, key=last, reverse=True)
        jarvis.say("Here are the top 10 books \n")
        for i in range(10):
            # sorts the books based on ratings
            print(sorted_[i][0] + " " + "by " + sorted_[i][1])
    else:
        jarvis.say("Sorry, couldn't find your genre \n")
        jarvis.say(
            "Please choose a valid genre or choose from the below genres list: \n")
        for gen in genres:
            jarvis.say(gen)


def last(n):
    return n[-1]
