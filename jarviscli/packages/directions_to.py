from utilities.GeneralUtilities import wordIndex
import mapps


def main(data):
    wordList = data.split()
    to_index = wordIndex(data, "to")
    if " from " in data:
        from_index = wordIndex(data, "from")
        if from_index > to_index:
            toCity = " ".join(wordList[to_index + 1:from_index])
            fromCity = " ".join(wordList[from_index + 1:])
        else:
            fromCity = " ".join(wordList[from_index + 1:to_index])
            toCity = " ".join(wordList[to_index + 1:])
    else:
        toCity = " ".join(wordList[to_index + 1:])
        fromCity = 0
    mapps.directions(toCity, fromCity)
