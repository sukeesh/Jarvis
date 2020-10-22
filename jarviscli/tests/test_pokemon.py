import unittest

from mock import patch
import requests

from tests import PluginTest
from plugins import pokemon


class PokemonTest(PluginTest):

    def setUp(self):
        self.test = self.load_plugin(pokemon.pokemon)

    def test_pokemon(self):
        with patch.object(requests, 'get') as req_get_mock:
            self.test.run('Charmander')
            req_get_mock.assert_called_with("https://pokeapi.co/api/v2/pokemon-species/charmander/")

    def test_pokemon_no_input(self):
        self.test.run('')

        self.assertEqual(self.history_say().last_text(), 'Tell me the name of the pokemon you want to know more about :)')


if __name__ == '__main__':
    unittest.main()
