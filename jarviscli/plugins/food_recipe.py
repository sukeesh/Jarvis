import requests
from plugin import plugin, require
from colorama import Fore
from bs4 import BeautifulSoup


@require(network=True)
@plugin("food recipe")
def getChoices(jarvis, s):
    """
    function gets the choice of the type of cuisine the user wants.

    user must get an api key from https://spoonacular.com/food-api/docs#Authentication
    THIS WILL NOT WORK WITHOUT THE API KEY.

    user has to input api key everytime they run the plugin
    """

    user_api_key = jarvis.input(
        "Enter spoonacular.com food-api API_KEY (visit https://spoonacular.com/food-api/docs#Authentication) for getting one: ",
        Fore.GREEN)

    print("--------------------------ENTER CUISINE----------------------------")
    print("1. Indian \t\t 7. European \t\t 13. Cajun")
    print("2. Asian \t\t 8. German \t\t 14. Middle Eastern")
    print("3. British \t\t 9. Korean \t\t 15. Latin American")
    print("4. Mexican \t\t 10. Irish \t\t 16. Thai")
    print("5. Italian \t\t 11. American \t\t 17. Vietnamese")
    print("6. Chinese \t\t 12. Mediterranean \t 18. Jewish")

    cuisine_dict = {
        "1": "Indian",
        "2": "Asian",
        "3": "British",
        "4": "Mexican",
        "5": "Italian",
        "6": "Chinese",
        "7": "European",
        "8": "German",
        "9": "Korean",
        "10": "Irish",
        "11": "American",
        "12": "Mediterranean",
        "13": "Cajun",
        "14": "Middle Eastern",
        "15": "Latin American",
        "16": "Thai",
        "17": "Vietnamese",
        "18": "Jewish"
    }

    cuisine_input = jarvis.input("Enter Cuisine (no. of the cuisine): ", Fore.RED)

    # Check if the user's input exists in the dictionary
    if cuisine_input in cuisine_dict:
        cuisine = cuisine_dict[cuisine_input]
        print("Selected cuisine:", cuisine)
    else:
        print("Invalid input. Please enter a valid choice.")

    getAllRecipes(user_api_key, cuisine)


def getAllRecipes(apiKey, cuisine):
    url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={apiKey}&cuisine={cuisine}&includeNutrition=true."

    response = requests.get(url)
    # print(response)

    if response.status_code == 200:
        content = response.json()

        # for debugging purposes, need import json
        # with open("contentFood.json", "w") as f:
        #     json.dump(content, f, indent=2)

        # extracting titles
        titles = []
        for item in content["results"]:
            titles.append(item["title"])

        print("--------------------------FOOD ITEM----------------------------")
        for index, title in enumerate(titles, 1):
            print(f"{index}. {title}")

        # Asking the user to select a title
        while True:
            try:
                selected_index = int(input("Enter the number corresponding to the title you want: ", ))
                print()
                if 1 <= selected_index <= len(titles):
                    break
                else:
                    print("Invalid selection. Please enter a valid number.", Fore.RED)
            except ValueError:
                print("Invalid input. Please enter a number.", Fore.RED)

        # Get the ID number for the selected title
        selectedTitle = titles[selected_index - 1]
        for item in content['results']:
            if item['title'] == selectedTitle:
                selectedId = item['id']
                break

        print(f"Selected Title: {selectedTitle}", Fore.CYAN)
        # print(f"ID Number for Selected Title: {selected_id}")

        # now get the recipe info from the id
        url2 = f"https://api.spoonacular.com/recipes/{selectedId}/information?apiKey={apiKey}&includeNutrition=false"
        responseRecipeInformation = requests.get(url2)

        if responseRecipeInformation.status_code == 200:

            content2 = responseRecipeInformation.json()

            # debugging purposes again
            # with open("recipeInfo.json", "w") as f2:
            #     json.dump(content2, f2, indent=2)

            """
            below code gets the ingredients, summary and description
            uses the beautiful soup module for cutting out the html tags.
            source code has been outputted for reference
            """

            summary_html = content2['summary']

            # Cleaning the summary text from HTML tags (cutting out the html tags)
            soup = BeautifulSoup(summary_html, 'html.parser')
            summary_text = soup.get_text()

            source_url = content2['sourceUrl']
            description = content2['analyzedInstructions'][0]['steps'][0][
                'step']

            print("Summary:")
            print(summary_text)
            print("\nDescription:")
            print(description)

            print("\nSource URL:")
            print(source_url)

            # Extracting the list of ingredients with their corresponding aisle
            ingredients = content2['extendedIngredients']
            print("\nIngredients:")
            for ingredient in ingredients:
                original_value = ingredient['original']
                aisle = ingredient['aisle']
                print(f"- {original_value} (Aisle: {aisle})", Fore.GREEN)

            print("\nHope you enjoy your food!", Fore.BLUE)
        else:
            print("Network down. Please try again later.")
    else:
        print("Network down. Please try again later.")
    return
