import wikipedia
from plugin import plugin, complete, require


@require(network=True)
@complete("search", "sumary", "content")
@plugin('wiki')
class Wiki():
    """
    Jarvis has now wiki feature
    enter wiki search for searching related topics
    enter wiki summary for getting summary of the topic
    wiki content for full page article of topic
    """

    def __call__(self, jarvis, s):
        k = s.split(' ', 1)
        if len(k) == 1:
            jarvis.say(
                "Do you mean:\n1. wiki search <subject>\n2. wiki summary <subject>\n3. wiki content <subject>")
        else:
            data = None
            if k[0] == "search":
                data = self.search(" ".join(k[1:]))
            elif k[0] == "summary":
                data = self.summary(" ".join(k[1:]))
            elif k[0] == "content":
                data = self.content(" ".join(k[1:]))
            else:
                jarvis.say("I don't know what you mean")
                return

            if isinstance(data, list):
                print("\nDid you mean one of these pages?\n")
                for d in range(len(data)):
                    print(str(d + 1) + ": " + data[d])
            else:
                print("\n" + data)

    def search(self, query, count=10, suggestion=False):
        """Do a Wikipedia search for a query, returns a list of 10 related items."""
        items = wikipedia.search(query, count, suggestion)
        if isinstance(items, list) and items:
            return items
        return "No articles with that name, try another item."

    def summary(self, query, sentences=0, chars=0):
        """Returns a plain text summary from the query's page."""
        try:
            return wikipedia.summary(query, sentences, chars)
        except wikipedia.exceptions.PageError:
            return "No page matches, try another item."
        except wikipedia.exceptions.DisambiguationError as error:
            return error.options[:5]

    def content(
            self,
            title=None,
            pageid=None,
            auto_suggest=True,
            redirect=True,
            preload=False):
        """Returns plain text content of query's page, excluding images, tables and other data."""
        try:
            page = wikipedia.page(title)
            return page.content
        except wikipedia.exceptions.PageError:
            return "No page matches, try another item."
        except wikipedia.exceptions.DisambiguationError as error:
            return error.options[:5]
