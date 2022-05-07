from ast import For
from colorama import Fore
from plugin import plugin, require
import requests
import json
import os

@require(network=True)
@plugin("cocktail cookbook")
class Cocktail:
    def __call__(self, jarvis, s):
        self.jarvis = jarvis
        self.main()
    
    def __init__(self):
        self.ingridients = [
            "Rum",
            "Light rum",
            "Dark rum",
            "Spiced rum",
            "Añejo rum",
            "Vodka",
            "Gin",
            "Tequila",
            "Whiskey" ,
            "Blended whiskey",
            "Irish whiskey",
            "Bourbon",
            "Sweet Vermouth",
            "Dry Vermouth",
            "Triple sec",
            "Brandy",
            "Amaretto",
            "Coffee liqueur",
            "Kahlua",
            "Cognac",
            "Ouzo",
            "Irish cream",
            "Sambuca",
            "Creme de Cassis"
            ]
    
    def main(self):
        self.display_data(self.ingridients)
        while True:
            selected_ingridient = self.get_ingridient()
            retrived_cocktails = self.get_cocktails_by_ingridient(selected_ingridient - 1)
            self.display_data(retrived_cocktails)
            chosen_cocktail = self.get_cocktail(retrived_cocktails)
            retrieved_cocktail_ingridients = self.get_cocktail_ingridients(chosen_cocktail - 1, retrived_cocktails)
            self.display_cocktail_ingridients(retrieved_cocktail_ingridients)
            retrived_cocktail_instrucions = self.get_cocktail_instructions(chosen_cocktail - 1, retrived_cocktails)
            self.display_cocktail_instructions(retrived_cocktail_instrucions)
            break
    
    def get_json(self, URL: str):
        """
        Return data from given url in json format
        """
        try:
            request = requests.get(URL)
        except Exception:
            self.jarvis.say(
                "Can not reach URL for the moment.")
        return json.loads(request.text)

    def display_data(self, data):
        """
        Display available data to the user.
        """
        # order in the list
        for number, d in enumerate(data):
            self.jarvis.say(
                f'{(number + 1):{3}}.  {d}')
    
    def display_cocktail_ingridients(self, ingridients):
        """
        Display Cocktail Ingridients to the user
        """
        self.jarvis.say("<------------------Ingridients----------------->".center(os.get_terminal_size().columns), color=Fore.LIGHTCYAN_EX)
        self.jarvis.say(f'{"Ingridient":{24}}  {"Measure":{10}}'.center(os.get_terminal_size().columns), color=Fore.LIGHTMAGENTA_EX)
        for i in ingridients:
            self.jarvis.say(
                f'{i[0] :{21}}      {i[1]:{8}}'.center(os.get_terminal_size().columns), color=Fore.LIGHTCYAN_EX)
    
    def display_cocktail_instructions(self, instructions):
        """
        Display Cocktail Ingridients to the user
        """
        self.jarvis.say("<------------------Instructions----------------->".center(os.get_terminal_size().columns), color=Fore.LIGHTCYAN_EX)
        self.jarvis.say(instructions.center(os.get_terminal_size().columns), color=Fore.LIGHTMAGENTA_EX)

    def get_ingridient(self):
        """
        Get user input and validate it.
        Input must be a number that corresponds to an ingridient.
        """
        try:
            ingridient = int(self.jarvis.input(
                "Select Base Ingridient number: ", color=Fore.GREEN))
        except ValueError:
            self.jervis.say("Please select a number", color=Fore.RED)
        try:
            upper_bound = len(self.ingridients)
            if (ingridient <= 0) or (ingridient >= upper_bound) :
                raise Exception("Number out of range")
        except Exception:
            self.jarvis.say(
                f"Please select a number from 1 to {upper_bound}", color=Fore.RED)
        return ingridient
    
    def get_cocktail(self, cocktails):
        """
        Get user input and validate it.
        Input must be a number that corresponds to an ingridient.
        """
        try:
            cocktail = int(self.jarvis.input(
                "Select Cocktail number: ", color=Fore.GREEN))
        except ValueError:
            self.jervis.say("Please select a number", color=Fore.RED)
        try:
            upper_bound = len(cocktails)
            if (cocktail <= 0) or (cocktail >= upper_bound) :
                raise Exception("Number out of range")
        except Exception:
            self.jarvis.say(
                f"Please select a number from 1 to {upper_bound}", color=Fore.RED)
        return cocktail

    def get_cocktail_ingridients(self, cocktail: int, cocktails):
        """
        Get chosen cocktail's ingridients.
        """
        URL = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={cocktails[cocktail]}"
        json_text = self.get_json(URL)['drinks'][0]
        cocktail_ingridients = []
        for i in range(1,16):
            ingridient = json_text[f'strIngredient{i}']
            measure = json_text[f'strMeasure{i}']
            if ingridient:
                if not measure:
                    cocktail_ingridients.append([ingridient, "Your pref."])
                else:
                    cocktail_ingridients.append([ingridient, measure])
        return cocktail_ingridients

    def get_cocktail_instructions(self, cocktail: int, cocktails):
        """
        Get chosen cocktail's instructions.
        """
        URL = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={cocktails[cocktail]}"
        json_text = self.get_json(URL)['drinks'][0]
        instructions = json_text["strInstructions"]
        return instructions
        

    def get_cocktails_by_ingridient(self, ingridient: int):
        """
        Get most popular cocktails with the given ingridient as base one.
        """
        URL = f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={self.ingridients[ingridient]}"
        json_text = self.get_json(URL)
        cocktails = []
        for i in json_text["drinks"]:
            cocktails.append(i["strDrink"])
        return cocktails
