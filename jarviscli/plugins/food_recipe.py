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


def get_recipe_titles(content):
    """Extract recipe titles from API response"""
    titles = []
    for item in content["results"]:
        titles.append(item["title"])
    return titles

def print_titles(titles):
    """Display numbered list of recipe titles"""
    print("--------------------------FOOD ITEM----------------------------")
    for index, title in enumerate(titles, 1):
        print(f"{index}. {title}")

def get_user_selection(titles):
    """Get valid title selection from user"""
    while True:
        try:
            selected_index = int(input("Enter the number corresponding to the title you want: "))
            print()
            if 1 <= selected_index <= len(titles):
                return selected_index
            print("Invalid selection. Please enter a valid number.", Fore.RED)
        except ValueError:
            print("Invalid input. Please enter a number.", Fore.RED)

def get_recipe_id(content, selected_title):
    """Get recipe ID for selected title"""
    for item in content['results']:
        if item['title'] == selected_title:
            return item['id']
    return None

def print_recipe_details(content2):
    """Print recipe summary, description, URL and ingredients"""
    soup = BeautifulSoup(content2['summary'], 'html.parser')
    summary_text = soup.get_text()
    
    print("Summary:")
    print(summary_text)
    print("\nDescription:")
    print(content2['analyzedInstructions'][0]['steps'][0]['step'])
    print("\nSource URL:")
    print(content2['sourceUrl'])
    
    print("\nIngredients:")
    for ingredient in content2['extendedIngredients']:
        print(f"- {ingredient['original']} (Aisle: {ingredient['aisle']})", Fore.GREEN)
    
    print("\nHope you enjoy your food!", Fore.BLUE)

def getAllRecipes(apiKey, cuisine):
    url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={apiKey}&cuisine={cuisine}&includeNutrition=true."
    response = requests.get(url)

    if response.status_code != 200:
        print("Network down. Please try again later.")
        return

    content = response.json()
    titles = get_recipe_titles(content)
    print_titles(titles)
    
    selected_index = get_user_selection(titles)
    selected_title = titles[selected_index - 1]
    selected_id = get_recipe_id(content, selected_title)
    
    print(f"Selected Title: {selected_title}", Fore.CYAN)
    
    url2 = f"https://api.spoonacular.com/recipes/{selected_id}/information?apiKey={apiKey}&includeNutrition=false"
    response_recipe = requests.get(url2)
    
    if response_recipe.status_code != 200:
        print("Network down. Please try again later.")
        return
        
    print_recipe_details(response_recipe.json())
