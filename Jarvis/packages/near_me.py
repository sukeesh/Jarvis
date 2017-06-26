from utilities.GeneralUtilities import wordIndex
import mapps


def main(data):
    word_list = data.split()
    things = " ".join(word_list[0:wordIndex(data, "|")])
    if " me" in data:
        city = 0
    else:
        word_list = data.split()
        city = " ".join(word_list[wordIndex(data, "|") + 1:])
        print(city)
    mapps.search_near(things, city)
