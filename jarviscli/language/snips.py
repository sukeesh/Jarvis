
import re
import pluginmanager

from snips_nlu import SnipsNLUEngine
from jarviscli.plugin import PluginStorage


class LanguageParser(pluginmanager.IPlugin, PluginStorage):
    """
      interface to parse input text
    """

    def __init__(self):
        super(pluginmanager.IPlugin, self).__init__()
        self._sub_plugins = {}
        self._pre_train_json = dict()
        self._pre_train_json['intents'] = {}
        self._pre_train_json['entities'] = {}
        self._pre_train_json['language'] = 'en'
        self.nlu_engine = SnipsNLUEngine()

    def train(self, plugins):
        self._generate_pre_train_json(plugins)
        self.nlu_engine.fit(self._pre_train_json)

    def _generate_pre_train_json(self, plugins):
        for plugin in plugins:
            intent = dict()
            intent['utterances'] = list()
            _data = list()
            _data.append(dict({'text': plugin.get_name()}))
            intent['utterances'].append(dict({"data": _data}))
            self._pre_train_json['intents']['_'.join(
                re.findall(r"[\w']+", plugin.get_name()))] = intent

    def identify_action(self, action):
        parsed_action = self.nlu_engine.parse(action)
        print(parsed_action)
        return parsed_action['intent']['intentName']