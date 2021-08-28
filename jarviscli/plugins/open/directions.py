import webbrowser

from plugin import alias, plugin, require


def wordIndex(data, word):
    wordList = data.split()
    return wordList.index(word)


def directions(to_city, from_city=0):
    if not from_city:
        from_city = get_location()['city']
    url = "https://www.google.com/maps/dir/{0}/{1}".format(from_city, to_city)
    webbrowser.open(url)


@require(network=True)
@plugin("directions")
def directions(jarvis, s):
    """
    Get directions about a destination you are interested to.
    -- Example:
        directions to the Eiffel Tower
    """
    try:
        word_list = s.split()
        to_index = wordIndex(s, "to")
        if " from " in s:
            from_index = wordIndex(s, "from")
            if from_index > to_index:
                to_city = " ".join(word_list[to_index + 1:from_index])
                from_city = " ".join(word_list[from_index + 1:])
            else:
                from_city = " ".join(word_list[from_index + 1:to_index])
                to_city = " ".join(word_list[to_index + 1:])
        else:
            to_city = " ".join(word_list[to_index + 1:])
            from_city = 0
        directions(to_city, from_city)
    except ValueError:
        print("Please enter destination")
