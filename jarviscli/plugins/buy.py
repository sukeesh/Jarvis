from plugin import plugin
import os
import subprocess
import sys
import webbrowser


@plugin("buy")
def buy(jarvis, s):
    """
    Searches the string you provide on amazon or ebay.
    Generates Url and opens browser.
    Uses: a) "buy <shop> <search term>" (One line command)
          b) "buy", Asks for shop,"<shop>", Asks for search term, "<search term>"
    """

    # Checks if one line command
    cut_string = s.split(" ")
    if len(cut_string) > 1:
        endURL = oneLineCommand(cut_string[0], cut_string[1:])
        if len(endURL) < 1:
            jarvis.say("Wrong input. Try again or try with just 'buy'.")
            return None

    else:
        jarvis.say("Pick a site (Amazon or Ebay)")
        shop_input = jarvis.input()
        startingURL = shop(shop_input)
        if len(startingURL) < 1:
            jarvis.say("Pick between Amazon or Ebay. Please try again.")
            return None
        jarvis.say("What you need to buy?")
        search_term = jarvis.input()

        endURL = generateURL(startingURL, search_term, False)
        if len(endURL) < 1:
            jarvis.say("Empty search term. Please try again.")
            return None

    webbrowser.open(endURL)


# Check is shop is supported and creates the url for searching on that shop
def shop(shopName):
    startingURL = ""
    if shopName in ('amazon', 'Amazon'):
        startingURL = "https://www.amazon.com/s?k="
    elif shopName in ('ebay', 'Ebay', 'eBay', 'e-bay'):
        startingURL = "https://www.ebay.com/sch/i.html?_nkw="
    return startingURL


# Gets the first part of search url and adds the search term to generate the full url
def generateURL(startingURL, searchTerm, splitted):
    if(splitted):
        splittedTerm = searchTerm
    else:
        splittedTerm = searchTerm.split(" ")
    counter = 0
    for word in splittedTerm:
        if len(word) > 0:
            if counter == 0:
                startingURL += word
                counter += 1
            else:
                startingURL += '+' + word
                counter += 1
    return startingURL


# Call if one line command is uses
def oneLineCommand(shop_input, search_term):
    endURL = ""
    startingURL = shop(shop_input)
    if len(startingURL) > 0:
        endURL = generateURL(startingURL, search_term, True)
    return endURL
