import unittest
from unittest import mock
import requests
from tests import PluginTest
from plugins.cocktail import Cocktail
import random


class CocktailTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(Cocktail)
        self.test.jarvis = self.jarvis_api
    
    def test_available_cocktail_ingridients(self):
        available_ingridients = self.test.ingridients
        for i in available_ingridients:
            response = requests.get(
                f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={i}")
            self.assertTrue(response.ok)

    def test_sample_cocktails_by_ingridient(self):
        # Test  Random Ingridient's Cocktails
        available_ingridients = self.test.ingridients
        random_base_ingridient = random.randint(0,len(available_ingridients) - 1)
        cocktails = self.test.get_cocktails_by_ingridient(random_base_ingridient)
        for c in cocktails:
            response = requests.get(
                f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={c}")
            self.assertTrue(response.ok)

    def test_is_out_of_range_true(self):
        with self.assertRaises(Exception):
            self.queue_input("700")
            selected_ingridient = self.test.get_ingridient(self.jarvis_api)
        with self.assertRaises(Exception):
            self.queue_input("-10")
            selected_ingridient = self.test.get_ingridient(self.jarvis_api)

    def test_is_out_of_range_false(self):
        available_ingridients = self.test.ingridients
        self.queue_input("10")
        selected_ingridient = self.test.get_ingridient()
        self.assertEqual(available_ingridients[selected_ingridient],available_ingridients[10])
        self.queue_input("3")
        selected_ingridient = self.test.get_ingridient()
        self.assertEqual(selected_ingridient, 3)

if __name__ == '__main__':
    unittest.main()