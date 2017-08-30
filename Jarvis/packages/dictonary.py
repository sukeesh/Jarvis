import requests
import xmltodict
import json

# move this to config file
thesaurus = {
    "key": "+0ODhyndgjiW0xpGhMlbU+",
    "url": "http://thesaurus.altervista.org/thesaurus/v1"
}


class Thesaurus(object):
    def __init__(self, word):
        self.word = word
        self.url = thesaurus.get('url')
        self.key = thesaurus.get('key')
        self.lang = 'en_US'

    def find(self):
        url = self.url + "?word=" + self.word + "&key=" + self.key + "&language=" + self.lang
        response = {"response": "failure"}
        try:
            request = requests.get(url)
        except Exception, e:
            print "Exception during request for word: {}".format(e)
        else:
            response = xmltodict.parse(request._content)
        return json.dumps(response)


if __name__ == '__main__':
    th = Thesaurus('Peace')
    print th.find()
