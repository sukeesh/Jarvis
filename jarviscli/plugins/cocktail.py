from colorama import Fore
from plugin import plugin, require, alias
import requests
import json
import os


@require(network=True)
@alias("cocktails")
@plugin("cocktail cookbook")
class Cocktail:
    def __call__(self, jarvis, s):
        self.jarvis = jarvis
        self.main()

    def __init__(self):
        # get the width of terminal
        self.SCREEN_WIDTH = os.get_terminal_size().columns
        self.RECIPE_WIDTH = 60
        self.MARGIN = round((self.SCREEN_WIDTH - self.RECIPE_WIDTH) / 2) + 1
        self.ingredients = [
            "Rum",
            "Light rum",
            "Dark rum",
            "Spiced rum",
            "Añejo rum",
            "Vodka",
            "Gin",
            "Tequila",
            "Whiskey",
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
        """
        Method demonstrate the functionality of Cocktail cookbook plugin.
        """

        # Continue as the user wants more cocktails
        while True:

            self.display_data(self.ingredients)

            # User chooses an ingredient
            selected_ingredient = self.get_input(
                "Base Ingredient", len(self.ingredients))

            if self.is_exit_input(selected_ingredient):
                break
            # List of cocktails that needs the given ingredient
            retrived_cocktails = self.get_cocktails_by_ingredient(
                selected_ingredient - 1)

            self.display_data(retrived_cocktails)

            chosen_cocktail = self.get_input(
                "Cocktail", len(retrived_cocktails))

            if self.is_exit_input(selected_ingredient):
                break
            # List of all ingredients that a cocktail needs
            retrieved_cocktail_ingredients = self.get_cocktail_ingredients(
                chosen_cocktail - 1, retrived_cocktails)
            cocktail = retrived_cocktails[chosen_cocktail - 1]
            self.display_cocktail_ingredients(
                retrieved_cocktail_ingredients, cocktail)

            retrived_cocktail_instructions = self.get_cocktail_instructions(
                chosen_cocktail - 1, retrived_cocktails)

            self.display_cocktail_instructions(retrived_cocktail_instructions)

            if self.is_end():
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
        # data is a list of str
        for number, d in enumerate(data):
            self.jarvis.say(
                f'{(number + 1):{3}}.  {d}')

    def display_cocktail_ingredients(self, ingredients, cocktail):
        """
        Display Cocktail ingredients to the user
        """

        self.header_msg(f"ALL YOU NEED for {cocktail}")

        self.jarvis.say(f'{"INGREDIENTS":{30}}{"MEASURE":{15}}'.center(
            self.SCREEN_WIDTH), color=Fore.LIGHTGREEN_EX)
        for ingredient in ingredients:
            self.jarvis.say(
                f'{ingredient[0] :{30}}{ingredient[1]:{15}}'.center(self.SCREEN_WIDTH))

    def display_cocktail_instructions(self, instructions: str):
        """
        Display Cocktail ingredients to the user
        """
        self.header_msg("HOW TO MAKE IT")
        instructions = instructions.replace("\r\n", " ")

        for line in range(0, len(instructions), self.RECIPE_WIDTH):
            # skip space in the end of the line
            if instructions[line] == " " and line < len(instructions):
                line += 1
            self.jarvis.say(
                f'{" " * self.MARGIN}{instructions[line : line + self.RECIPE_WIDTH]}')

    def header_msg(self, msg: str):
        self.jarvis.say(
            f'{"-" * self.RECIPE_WIDTH}'.center(self.SCREEN_WIDTH))
        self.jarvis.say(f"{msg}".center(
            self.SCREEN_WIDTH))
        self.jarvis.say(
            f'{"-" * self.RECIPE_WIDTH}'.center(self.SCREEN_WIDTH))

    def get_input(self, input_is: str, upper_bound: int):
        """
        Get user input and validate it.
        Input must be a number that corresponds to an ingredients.
        """
        input_code = None
        # Until country code is valid
        while not input_code:
            try:
                input_code = self.jarvis.input(
                    f"Choose {input_is}: ", color=Fore.GREEN)
                if self.is_valid_input(int(input_code), upper_bound):
                    raise ValueError
            except ValueError:
                if self.is_exit_input(input_code):
                    return 'exit'
                self.jarvis.say(
                    f"Please select a number (1 - {upper_bound})", color=Fore.YELLOW)
                input_code = None
        return int(input_code)

    def is_exit_input(self, input):
        if (type(input) == str and input.lower() == "exit"):
            return True

    def is_valid_input(self, input, upper_bound):
        if type(input) == int and self.is_out_of_range(input, upper_bound):
            return True

    def is_out_of_range(self, x: int, upper_bound) -> bool:
        return (True if (x > upper_bound or x <= 0) else False)

    def is_end(self):
        inp = self.jarvis.input(
            "Do you want to continue? (Y/N) ", color=Fore.RED)
        if inp.lower() == "n" or inp.lower() == "exit":
            return True

    def get_cocktail_ingredients(self, cocktail: int, cocktails):
        """
        Get chosen cocktail's ingredients.
        """
        URL = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={cocktails[cocktail]}"
        json_text = self.get_json(URL)['drinks'][0]
        cocktail_ingredients = []
        for i in range(1, 16):
            ingredient = json_text[f'strIngredient{i}']
            measure = json_text[f'strMeasure{i}']
            if ingredient:
                if not measure:
                    cocktail_ingredients.append([ingredient, "Your pref."])
                else:
                    cocktail_ingredients.append([ingredient, measure])
        return cocktail_ingredients

    def get_cocktail_instructions(self, cocktail: int, cocktails):
        """
        Get chosen cocktail's instructions.
        """
        URL = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={cocktails[cocktail]}"
        json_text = self.get_json(URL)['drinks'][0]["strInstructions"]
        return json_text

    def get_cocktails_by_ingredient(self, ingredients: int):
        """
        Get most popular cocktails with the given ingredients as base one.
        """
        URL = f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={self.ingredients[ingredients]}"
        json_text = self.get_json(URL)["drinks"]
        cocktails = [i["strDrink"] for i in json_text]
        return cocktails
