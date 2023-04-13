from plugin import plugin
from plugin import complete
import requests


@complete("fruit")
@plugin("fruit")
def fruit(jarvis, s: str) -> None:
    """
    Retrieves information about a specific fruit from the Fruityvice API and outputs it to the user.

    Parameters:
    jarvis (obj): Jarvis assistant object
    s (str): Fruit name entered by the user

    Returns:
    None

    Example Usage:
    fruit apple
    """
    API_URL_SINGLE_FRUIT = "https://fruityvice.com/api/fruit/"

    try:
        # Validate user input
        if not s:
            jarvis.say("Please input a fruit. Usage: fruit [fruit]")
            return

        # Rename and format user input
        s = s.strip().lower()

        # Query the API for the requested fruit
        response = requests.get(API_URL_SINGLE_FRUIT + s)

        # Handle invalid or nonexistent fruit names
        if response.status_code == 404:
            jarvis.say("Invalid fruit name. Please enter a valid fruit name.")
            return
        response.raise_for_status()

        # Parse JSON response
        fruit = response.json()

        # Output fruit information to the user
        jarvis.say(f"{fruit['name']}\n")
        jarvis.say("Nutritional Facts Per 100 grams")
        for fact, value in fruit["nutritions"].items():
            jarvis.say(f"{fact}: {value}")
        jarvis.say("\nSpecies Classifications")
        jarvis.say(f"Order: {fruit['order']}")
        jarvis.say(f"Family: {fruit['family']}")
        jarvis.say(f"Genus: {fruit['genus']}")

    # Handle errors
    except (requests.exceptions.RequestException, KeyError, ValueError):
        jarvis.say("Error occurred while fetching the fruit information. Please try again.")
