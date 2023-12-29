import enum
import json

import requests


class LocationFields(enum.Enum):
    IP = 0
    CONTINENT = 1
    COUNTRY = 2
    CAPITAL = 3
    REGION = 4
    CITY = 5
    LATITUDE = 6
    LONGITUDE = 7
    TIMEZONE = 8
    CURRENCY = 9


class LocationProvider:
    def update(self, jarvis, force=False):
        assert False, "Overwrite"

    def get(self, key):
        assert False, "Overwrite"


class LocationProvider_IPWHOIS(LocationProvider):
    SEND_URL = 'http://ipwhois.app/json/'
    KEY = 'LOCATION_IPWHOISP'

    def __init__(self, jarvis):
        self.data = jarvis.get_data(self.KEY)

    def update(self, jarvis, force=False):
        if self.data is None or force is True:
            r = requests.get(self.SEND_URL)
            self.data = json.loads(r.text)
            jarvis.update_data(self.KEY, self.data)
            print("DEBUG {}".format(self.data))

    def get(self, key):
        key = key.name.lower()
        if key in self.data:
            return self.data[key]
        return None


class Location:
    PROVIDERS = {
        "ipwhois.io": LocationProvider_IPWHOIS
    }
    KEY = 'LOCATION_PROVIDERS'
    MESSAGE = 'Hi! I can receive basic information about you (location, timezone, ...). Please tell me what providers I should use.'

    def __init__(self, dependency):
        pass

    def init(self, jarvis):
        providers_list = jarvis.get_data(self.KEY)
        if providers_list is None:
            self.update_providers(jarvis)
        else:
            self._build_providers(jarvis, providers_list)

    def update_providers(self, jarvis):
        chooses = [x for x in self.PROVIDERS.keys()]
        providers_list = jarvis.choose((self.MESSAGE,  chooses))
        jarvis.say('You can always update your choice with "update providers"')
        self._build_providers(jarvis, providers_list)
        jarvis.update_data(self.KEY, providers_list)

    def _build_providers(self, jarvis, providers_list):
        self.providers = [self.PROVIDERS[key](jarvis) for key in providers_list]
        self.update(jarvis)

    def update(self, jarvis, force=False):
        for provider in self.providers:
            provider.update(jarvis, force)

    def _key_field(self, field):
        return self.KEY + '-' + field.name

    def get(self, field, jarvis):
        known_value = jarvis.get_data(self._key_field(field))
        if known_value is not None:
            return known_value
        for provider in self.providers:
            value = provider.get(field)
            if value is not None:
                return value
        value = self.ask_input_value(field, jarvis)
        jarvis.update_value(self._key_field(field), value)
        return value

    def ask_choose_value(self, field, jarvis):
        options = set([provider.get(field) for provider in self.providers] + ['other'])
        value = jarvis.choose(('Choose value for {}'.format(field.name.lower()), options))
        if value == 'other':
            value = self.ask_input_value(field, jarvis)
        jarvis.update_value(self._key_field(field), value)
        return value

    def ask_input_value(self, field, jarvis):
        return jarvis.input('Value of {}: '.format(field.name.lower()))
