import webbrowser
from plugin import plugin

playerList = ["Youtube", "youtube", "dailymotion", "Dailymotion"]


@plugin("music")
def music(jarvis, s):
    """
    Allow to launch search in YouTube or Dailymotion
    """
    cut_string = s.split(" ")
    if len(cut_string) == 1 and cut_string[0] in playerList:
        player = cut_string[0]
        jarvis.say("What do you want to see?")
        search_term_list = jarvis.input().split(" ")
    elif len(cut_string) == 1:
        jarvis.say("Pick a site (Youtube or Dailymotion)")
        player = jarvis.input()
        if player not in playerList:
            jarvis.say("Pick between Youtube or Dailymotion. Please try again.")
            return
        jarvis.say("What do you want to see?")
        search_term_list = jarvis.input().split(" ")
    else:
        if cut_string[0] not in playerList:
            jarvis.say("Pick between Youtube or Dailymotion. Please try again.")
            return
        else:
            player = cut_string[0]
            search_term_list = cut_string[1:]
    if player in ("youtube", "Youtube"):
        startingURL = "https://www.youtube.com/results?search_query="
        endURL = generateURLYoutube(startingURL, search_term_list)
    else:
        startingURL = "https://www.dailymotion.com/search/"
        endURL = generateURLDailymotion(startingURL, search_term_list)
    webbrowser.open(endURL)


def generateURLYoutube(startingURL, search_term):
    for words in search_term:
        startingURL += "+" + words
    return startingURL


def generateURLDailymotion(startingURL, search_term):
    for words in search_term:
        startingURL += " " + words
    return startingURL + '/videos'
