from utilities.GeneralUtilities import wordIndex
from . import mapps


def main(data):
    word_list = data.split()
    to_index = wordIndex(data, "to")
    if " from " in data:
        from_index = wordIndex(data, "from")
        if from_index > to_index:
            to_city = " ".join(word_list[to_index + 1:from_index])
            from_city = " ".join(word_list[from_index + 1:])
        else:
            from_city = " ".join(word_list[from_index + 1:to_index])
            to_city = " ".join(word_list[to_index + 1:])
    else:
        to_city = " ".join(word_list[to_index + 1:])
        from_city = 0
    mapps.directions(to_city, from_city)
