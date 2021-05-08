import CmdInterpreter
from . import mapps


def main(data):
    """
    Extracts from the given argument, the things and the area to be
    searched, which can be either a specific area or the user's
    location.

    Parameters
    ----------
    data: str
        A variable that contains the things and the area to be
        searched.
    """
    word_list = data.split()
    try:
        things = " ".join(word_list[0:word_list.index("|")])
    except ValueError:
        cmd = CmdInterpreter.CmdInterpreter("", "")
        cmd.help_near()
        return

    if "me" in word_list:
        city = 0
    else:
        word_list = data.split()
        city = " ".join(word_list[word_list.index("|") + 1:])
    mapps.search_near(things, city)
