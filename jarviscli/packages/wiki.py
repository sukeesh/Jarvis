import wikipedia


def search(query, count=10, suggestion=False):
    """Do a Wikipedia search for a query, returns a list of 10 related items."""
    items = wikipedia.search(query, count, suggestion)
    if isinstance(items, list) and len(items) > 0:
        return items
    return "No articles with that name, try another item."


def summary(query, sentences=0, chars=0):
    """Returns a plain text summary from the query's page."""
    try:
        return wikipedia.summary(query, sentences, chars)
    except wikipedia.exceptions.PageError:
        return "No page matches, try another item."
    except wikipedia.exceptions.DisambiguationError as error:
        return error.options[:5]


def content(title=None, pageid=None, auto_suggest=True, redirect=True, preload=False):
    """Returns plain text content of query's page, excluding images, tables and other data."""
    try:
        page = wikipedia.page(title)
        return page.content
    except wikipedia.exceptions.PageError:
        return "No page matches, try another item."
    except wikipedia.exceptions.DisambiguationError as error:
        return error.options[:5]
