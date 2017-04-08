from utilities.GeneralUtilities import wordIndex
import mapps


def main(data):
    wordList = data.split()
    things = " ".join(wordList[0:wordIndex(data, "near")])
    if " me" in data:
        city = 0
    else:
        wordList = data.split()
        city = " ".join(wordList[wordIndex(data, "near") + 1:])
        print city
    mapps.searchNear(things, city)
