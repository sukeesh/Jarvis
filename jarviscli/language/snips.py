import re

from snips_nlu import SnipsNLUEngine


class LanguageParser:
    """
      interface to parse input text
    """

    def __init__(self):
        self._plugins = {}
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
            intent_name = '_'.join(re.findall(r"[\w']+", plugin.get_name()))
            self._pre_train_json['intents'][intent_name] = intent
            self._plugins[intent_name] = plugin

            # handle sub commands (recursive)
            self._generate_pre_train_json(plugin.get_plugins().values())

    def identify_action(self, action):
        parsed_action = self.nlu_engine.parse(action)
        # print(parsed_action)
        intent_name = parsed_action['intent']['intentName']
        if intent_name not in self._plugins:
            return None
        return self._plugins[intent_name]
