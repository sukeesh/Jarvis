import wikipedia

def search(query, count=10, suggestion=False):
    items = wikipedia.search(query, count, suggestion)
    if isinstance(items, list) and len(items) > 0:
        return items
    return "No articles with that name, try another item."

def suggest(query):
    item = wikipedia.suggest(query)
    if item:
        return item
    return "No article with that name, try another item."

def summary(query, sentences=0, chars=0):
    try:
        return wikipedia.summary(query, sentences, chars)
    except wikipedia.exceptions.PageError:
        return "No page matches, try another item."
    except wikipedia.exceptions.DisambiguationError as error:
        return error.options[:5]

def page(title=None, pageid=None, auto_suggest=True, redirect=True, preload=False):
    try:
        page = wikipedia.page(title)

        print("Select page options (1-7):\n")
        print("1: Categories")
        print("2: Content")
        print("3: HTML")
        print("4: Images")
        print("5: Links")
        print("6: References")
        print("7: Summary\n")

        number = int(input())
        while number not in range(1,8):
            print("Please select an option from (1-7):\n")
            number = int(input())

        if number == 1:
            return page.categories
        elif number == 2:
            return page.content
        elif number == 3:
            return page.html()
        elif number == 4:
            return page.images
        elif number == 5:
            return page.links
        elif number == 6:
            return page.references
        elif number == 7:
            return page.summary
    except wikipedia.exceptions.PageError:
        return "No page matches, try another item."
    except wikipedia.exceptions.DisambiguationError as error:
        return error.options[:5]

def random(pages=1):
    return wikipedia.random(pages)

def donate():
    wikipedia.donate()
