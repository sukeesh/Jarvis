import requests
from plugin import plugin

BASE_URL = "https://www.fruityvice.com/api/fruit/"

@plugin("fruit nutrition")
def fruit_nutrition(jarvis, s):
    """Fetches the nutrition facts for the given fruit name from the Fruityvice API and prints them."""

    fruit_name = s.strip()  # delete spaces

    if not fruit_name:
        jarvis.say("Please provide a fruit name.")
        return

    try:
        response = requests.get(BASE_URL + fruit_name)
        response.raise_for_status()  # raise HTTPError if status code is not 200

        data = response.json()

        if 'nutritions' not in data:
            jarvis.say("Error fetching the nutrition facts. Please try again.")
            return

        nutritions = data['nutritions']

        jarvis.say(f"The nutrition of {data['name']} is:")
        for key, value in nutritions.items():
            jarvis.say(f"{key}: {value}")

        # Ask user for personal details
        age = int(jarvis.input("Please enter your age: "))
        height = int(jarvis.input("Please enter your height in cm: "))
        weight = int(jarvis.input("Please enter your weight in kg: "))

        # Calculate BMR using Harris-Benedict equation for males (you can add for females too)
        BMR = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        daily_calories = BMR * 1.55  # assuming moderate activity level

        # Calculate recommended fruit intake based on calories
        fruit_calories_per_100g = nutritions['calories']
        recommended_grams = (0.1 * daily_calories) / (fruit_calories_per_100g / 100)

        # Check nutrition limits
        max_sugar = 50  # assuming a max intake of 50g of sugar per day
        sugar_from_fruit = (recommended_grams / 100) * nutritions['sugar']
        if sugar_from_fruit > max_sugar:
            recommended_grams = (max_sugar / nutritions['sugar']) * 100

        # You can add more nutrition limits as needed

        jarvis.say(f"Based on your details, it's recommended to consume approximately {recommended_grams:.2f} grams of {data['name']} per day.")

    except requests.HTTPError:
        jarvis.say("Error fetching the nutrition facts. Please try again.")
    except requests.ConnectionError:
        jarvis.say("Failed to connect to the Fruityvice API. Please check your internet connection.")
    except ValueError:
        jarvis.say("Please enter valid numeric values for age, height, and weight.")
    except KeyError:
        jarvis.say("Invalid data format received from the API.")