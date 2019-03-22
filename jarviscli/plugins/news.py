# !!! This uses the https://newsapi.org/ api. TO comply with the TOU
# !!! we must link back to this site whenever we display results.
import json
import webbrowser
from six.moves import input
from plugin import plugin, require
from colorama import Fore
try:  # python3
    import urllib.request
    import urllib.parse
    import urllib.error
except ImportError:  # python2
    import urllib


@require(network=True)
@plugin('news')
class News:

    def __init__(self, api_key="7488ba8ff8dc43459d36f06e7141c9e5"):
        self.apiKey = api_key
        self.url = "https://newsapi.org/v1/articles?source=google-news&sortBy=top" \
                   "&apiKey="+self.apiKey
        self.possibleFlags = ['configure', 'updateKey', 'help']
        self.is_news_site_configured = False
        self.sources = ['bloomberg', 'financial-times', 'cnbc', 'reuters', 'al-jazeera-english',
                        'the-wall-street-journal', 'the-huffington-post', 'business-insider', 'the-new-york-times',
                        'abc-news', 'fox-news', 'cnn', 'google-news', 'wired']
        self.source_dict = {}

        for source in self.sources:
            self.source_dict[str(self.sources.index(source) + 1)] = source

    def __call__(self, jarvis, s):
        if s == "updatekey":
            key = input("Please enter your NEWS API key (q or Enter go back): ")
            if key.lower() == "q" or key.lower() == "":
                jarvis.say("Could not update the NEWS API key! ", Fore.RED)
            else:
                self.update_api_key(jarvis, key)
                jarvis.say("NEWS API key successfully updated! ", Fore.GREEN)
        elif s == "configure":
            self.configure(jarvis)
        elif s == "remove":
            source_to_remove = input("Please enter the news source you want to remove: ")
            self.remove_source(jarvis, source_to_remove)
        elif s == "help":
            print("news : Finds top headlines")
            print("news updatekey : Updates the news API key of the user")
            print("news configure : Configures the news channel of the user")
            print("news removesource : Removes a source from the news channel of the user")
            print("news [word]: Finds articles related to that word")
        elif s == "" or s == " ":
            self.get_headlines(jarvis)
        else:
            self.get_news(jarvis, s)

    """
        will return either the news_api key of the user, already stored in the memory.json
        file or None in case the user does not have his own api
    """
    @staticmethod
    def get_api_key(jarvis):
        return jarvis.get_data("news-settings")

    """
        the user might have a news api key and they might want to add to memory.json or update an old one
    """
    def update_api_key(self, jarvis, api_key):
        jarvis.update_data("news-settings", api_key)
        return self.get_api_key(jarvis)

    """
        returns a list of all the new sources added to the news channel of the user
    """
    def get_news_sources(self, jarvis):
        sources = jarvis.get_data("news-sources")
        if sources is None:
            sources = []
        return sources

    """
        adds a new source (if it does not exist) to the news channel of the user
    """
    def add_source(self, jarvis, news_source):
        sources = self.get_news_sources(jarvis)
        print(sources)
        if news_source not in sources:
            sources.append(news_source)
            jarvis.update_data("news-sources", sources)
        return self.get_news_sources(jarvis)

    """
        removes a new source from the news channel of the user
    """
    def remove_source(self, jarvis, news_source):
        sources = self.get_news_sources(jarvis)
        if news_source in sources:
            sources.remove(news_source)
            jarvis.update_data("news-sources", sources)
        print(self.get_news_sources(jarvis))
        return self.get_news_sources(jarvis)

    """
        configures the news channel of the user
    """
    def configure(self, jarvis):
        choice = input('Would you like to configure your own news channel(y/n) ')
        if choice == 'y' or choice == 'yes':
            for index in self.source_dict.keys():
                print(str(index) + ": " + self.source_dict.get(index))
            index_list = input("Type the indexes of the sources you would like to add to your channel separated by "
                               "space: ")
            index_list = index_list.split(" ")
            for index in index_list:
                print(self.source_dict[index])
                self.add_source(jarvis, self.source_dict.get(index, index))
            print("Visit https://newsapi.org/sources to add any sources not in the previous list")
        elif choice.lower() == 'n' or choice.lower() == 'no':
            return
        else:
            print("Command not recognized!", Fore.RED)

    """
        gets top headlines for a quick lookup of the world news, based on the news channel of the user (if it exists)
    """
    def get_headlines(self, jarvis):
        sources = self.get_news_sources(jarvis)
        if len(sources) == 0:
            url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=" + self.get_api_key(jarvis)
        else:
            url = "https://newsapi.org/v2/top-headlines?sources="
            for source in sources:
                url += source + ","
            url += "&apiKey=" + self.get_api_key(jarvis)
        return self.parse_articles(url)

    """
        gets top news based on a particular search word , based on the news channel of the user (if it exists)
    """
    def get_news(self, jarvis, search):
        sources = self.get_news_sources(jarvis)

        url = "https://newsapi.org/v2/everything?q=" + search

        if len(sources) != 0:
            url += "&sources="
            for source in sources:
                url += source + ","
        url += "&apiKey=" + self.get_api_key(jarvis)
        return self.parse_articles(url)

    def parse_articles(self, url):
        # check to see if a url was passed
        if url is None:
            url = self.url
        try:
            response = urllib.request.urlopen(url)
        except AttributeError:
            response = urllib.urlopen(url)
        # Load json
        data = json.loads(response.read())
        article_list = {}
        index = 1
        # print articles with their index
        for article in data['articles']:
            # print (Fore.GREEN + str(index) + ": " + article['title'] + Fore.RESET)
            print(str(index) + ": " + article['title'])
            article_list[index] = article
            index += 1

        # Attribution link for News API to comply with TOU
        print("Powered by News API. Type NewsAPI to learn more")
        print("Type index to expand news\n")

        # Check to see if index or NewsAPI was enterd
        idx = input()
        if idx.lower() == "newsapi":
            webbrowser.open('https://newsapi.org/')
            return

        # check if we have a valid index
        try:
            int(idx)
            if int(idx) > index:
                print("Not a valid index")
                return
        except:
            print("Not a valid index")
            return

        # if index valid print article description
        print(article_list[int(idx)]['description'])

        print("Do you want to read more? (yes/no): ")
        i = input()
        # if user wants to read more open browser to article url
        if i.lower() == "yes" or i.lower() == 'y':
            webbrowser.open(article_list[int(idx)]['url'])
            return
        else:
            return

