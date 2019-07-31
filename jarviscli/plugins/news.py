# !!! This uses the https://newsapi.org/ api. TO comply with the TOU
# !!! we must link back to this site whenever we display results.
import json
import requests
import webbrowser
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin('news')
class News:

    def __init__(self):
        self.sources = [
            'bloomberg',
            'financial-times',
            'cnbc',
            'reuters',
            'al-jazeera-english',
            'the-wall-street-journal',
            'the-huffington-post',
            'business-insider',
            'the-new-york-times',
            'abc-news',
            'fox-news',
            'cnn',
            'google-news',
            'wired']
        self.source_dict = {}

        for source in self.sources:
            self.source_dict[str(self.sources.index(source) + 1)] = source

    def __call__(self, jarvis, s):
        if s == "updatekey":
            key = jarvis.input(
                "Please enter your NEWS API key (q or Enter go back): ")
            if key.lower() == "q" or key.lower() == "":
                jarvis.say("Could not update the NEWS API key! ", Fore.RED)
            else:
                self.update_api_key(jarvis, key)
                jarvis.say("NEWS API key successfully updated! ", Fore.GREEN)
        elif s == "configure":
            self.configure(jarvis)
        elif s == "remove":
            self.remove_source(jarvis)
        elif s == "help":
            jarvis.say("-------------------------------------")
            jarvis.say("Command\t\t | Description")
            jarvis.say("-------------------------------------")
            jarvis.say("news\t\t : Finds top headlines")
            jarvis.say(
                "news updatekey\t : Updates the news API key of the user")
            jarvis.say(
                "news configure\t : Configures the news channel of the user")
            jarvis.say("news sources\t : List the configured news sources")
            jarvis.say(
                "news remove\t : Removes a source from the news channel of the user")
            jarvis.say("news [word]\t : Finds articles related to that word")
        elif s == "sources":
            sources = self.get_news_sources(jarvis)
            if not sources:
                jarvis.say(
                    "No sources configured. Use 'news configure' to add sources.",
                    Fore.RED)
            else:
                dic = {}
                for source in sources:
                    dic[str(sources.index(source) + 1)] = source

                for index in sorted([int(x) for x in dic.keys()]):
                    jarvis.say(str(index) + " : " + dic[str(index)])
        elif self.get_api_key(jarvis) is None:
            jarvis.say("Missing API key", Fore.RED)
            jarvis.say("Visit https://newsapi.org/ to get the key", Fore.RED)
            jarvis.say(
                "Use \'news updatekey\' command to add a key\n",
                Fore.RED)
        elif s == "" or s == " ":
            self.parse_articles(self.get_headlines(jarvis), jarvis)
        else:
            searchlist = s.split(" ")
            if "" in searchlist:
                searchlist.remove("")
            if " " in searchlist:
                searchlist.remove(" ")
            self.parse_articles(self.get_news(jarvis, searchlist), jarvis)

    @staticmethod
    def get_api_key(jarvis):
        """
            will return either the news_api key of the user, already stored in the memory.json
            file or None in case the user does not have his own api
        """
        return jarvis.get_data("news-settings")

    def update_api_key(self, jarvis, api_key):
        """
            the user might have a news api key and they might want to add to memory.json or update an old one
        """
        jarvis.update_data("news-settings", api_key)
        return self.get_api_key(jarvis)

    def get_news_sources(self, jarvis):
        """
            returns a list of all the new sources added to the news channel of the user
        """
        sources = jarvis.get_data("news-sources")
        if sources is None:
            sources = []
        return sources

    def add_source(self, jarvis, news_source):
        """
            adds a new source (if it does not exist) to the news channel of the user
        """
        sources = self.get_news_sources(jarvis)
        if news_source not in sources:
            sources.append(news_source)
            jarvis.update_data("news-sources", sources)
            jarvis.say(
                news_source
                + " has been successfully been added to your sources!",
                Fore.GREEN)
        else:
            jarvis.say(
                news_source
                + " was already included in your sources!",
                Fore.GREEN)
        return self.get_news_sources(jarvis)

    def remove_source(self, jarvis):
        """
            removes a new source from the news channel of the user
        """
        sources = self.get_news_sources(jarvis)

        dic = {}
        for source in sources:
            dic[str(sources.index(source) + 1)] = source

        for index in sorted([int(x) for x in dic.keys()]):
            jarvis.say(str(index) + " : " + dic[str(index)])
        index_list = jarvis.input(
            "Type the indexes of the sources you would like to remove from your channel separated by "
            "space: ")
        index_list = index_list.split(" ")
        if " " in index_list:
            index_list.remove(" ")
        if "" in index_list:
            index_list.remove("")
        for index in index_list:
            if str(index) in dic:
                source = dic[str(index)]
                sources.remove(source)
                jarvis.update_data("news-sources", sources)
                jarvis.say(
                    source
                    + " has been successfully removed from your news channel!",
                    Fore.GREEN)
            else:
                jarvis.say("Index not found!", Fore.RED)
        return self.get_news_sources(jarvis)

    def configure(self, jarvis):
        """
            configures the news channel of the user
        """
        for index in sorted([int(x) for x in self.source_dict.keys()]):
            jarvis.say(str(index) + ": " + self.source_dict.get(str(index)))
        index_list = jarvis.input(
            "Type the indexes of the sources you would like to add to your channel separated by "
            "space: ")
        index_list = index_list.split(" ")
        if " " in index_list:
            index_list.remove(" ")
        if "" in index_list:
            index_list.remove("")
        for index in index_list:
            if index in self.source_dict.keys():
                self.add_source(jarvis, self.source_dict.get(index, index))
            else:
                jarvis.say(index + " is not a valid index", Fore.RED)

    def get_headlines(self, jarvis):
        """
            gets top headlines for a quick lookup of the world news, based on the news channel of the user (if it exists)
        """
        sources = self.get_news_sources(jarvis)

        if len(sources) == 0:
            jarvis.say(
                "You have not configured any source. Getting top headlines\n",
                Fore.GREEN)
            url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=" + \
                self.get_api_key(jarvis)
        else:
            url = "https://newsapi.org/v2/top-headlines?sources="
            for source in sources:
                url += source + ","
            url += "&apiKey=" + self.get_api_key(jarvis)
        return self._get(jarvis, url)

    def get_news(self, jarvis, searchlist):
        """
            gets top news based on a particular search list , based on the news channel of the user (if it exists)
        """
        sources = self.get_news_sources(jarvis)

        url = "https://newsapi.org/v2/everything?q="

        for i in searchlist:
            url += i + "%20"
        if len(sources) != 0:
            url += "&sources="
            for source in sources:
                url += source + ","
        url += "&apiKey=" + self.get_api_key(jarvis)
        return self._get(jarvis, url)

    def _get(self, jarvis, url):
        """fetch a webpage"""
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            return data
        else:
            if response.status_code == 401:
                jarvis.say("API key not valid", Fore.RED)
            else:
                jarvis.say("An error occured: Error code: "
                           + response.raise_for_status(), Fore.RED)
            return None

    def parse_articles(self, data, jarvis):
        article_list = {}
        index = 1
        if data is None:
            jarvis.say("No Articles", Fore.RED)
            return
        # jarvis.say articles with their index
        if not data['articles']:
            jarvis.say("No Articles matching the word(s)", Fore.RED)
            return
        for article in data['articles']:
            jarvis.say(str(index) + ": " + article['title'])
            article_list[index] = article
            index += 1

        # Attribution link for News API to comply with TOU
        jarvis.say("\nPowered by News API. Type NewsAPI to learn more")
        jarvis.say("\nType index to expand news, 0 to return to jarvis prompt\n")

        # Check to see if index or NewsAPI was enterd
        idx = jarvis.input()
        if idx.lower() == "newsapi":
            webbrowser.open('https://newsapi.org/')
            return

        # check if we have a valid index
        try:
            int(idx)
            if int(idx) > (index - 1):
                jarvis.say(str(idx) + " is not a valid index", Fore.RED)
                return
            elif int(idx) == 0:
                return
        except BaseException:
            jarvis.say("Not a valid index", Fore.RED)
            return

        # if index valid jarvis.say article description
        jarvis.say(article_list[int(idx)]['description'])

        jarvis.say("Do you want to read more? (yes/no): ")
        i = jarvis.input()
        # if user wants to read more open browser to article url
        if i.lower() == "yes" or i.lower() == 'y':
            webbrowser.open(article_list[int(idx)]['url'])
        return
