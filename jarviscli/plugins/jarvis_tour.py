from plugin import plugin

# Dictionary containing categories, subcategories, plugins, and their descriptions
plugin_data = {
    "Entertainment": {
        "Games": {
            "plugins": ["blackjack", "connect_four", "tic_tac_toe", "wordgame"],
            "descriptions": {
                "blackjack": "A simple blackjack game.",
                "connect_four": "Play a game of Connect Four.",
                "tic_tac_toe": "Classic tic-tac-toe game.",
                "wordgame": "A fun word-guessing game."
            }
        },
        "Media": {
            "plugins": ["mood_music", "movies", "lyrics"],
            "descriptions": {
                "mood_music": "Plays music based on your mood.",
                "movies": "Recommends movies to watch.",
                "lyrics": "Displays song lyrics."
            }
        }
    },
    "Fitness & Health": {
        "Health Metrics": {
            "plugins": ["bmi", "bmr", "calories_macros"],
            "descriptions": {
                "bmi": "Calculates your Body Mass Index (BMI).",
                "bmr": "Calculates your Basal Metabolic Rate (BMR).",
                "calories_macros": "Tracks calories and macronutrients."
            }
        },
        "Workouts": {
            "plugins": ["workout"],
            "descriptions": {
                "workout": "Suggests workout routines."
            }
        }
    },
    # Add more categories, subcategories, and plugins here
}

@plugin("jarvis tour")
def start_tour(jarvis, s):
    """
    Start the Jarvis tour, guiding the user through plugin categories,
    subcategories, and demonstrating how to use selected plugins.
    """
    jarvis.say("Welcome to the Jarvis Tour!")
    show_categories(jarvis)


def show_categories(jarvis):
    """
    Show available plugin categories to the user.
    """
    categories = list(plugin_data.keys())
    jarvis.say("Here are the available categories:")
    for idx, category in enumerate(categories, 1):
        jarvis.say(f"{idx}. {category}")

    category_input = jarvis.input("Please select a category by number: ")

    if category_input.isdigit() and 1 <= int(category_input) <= len(categories):
        selected_category = categories[int(category_input) - 1]
        show_subcategories(jarvis, selected_category)
    else:
        jarvis.say("Invalid input. Please try again.")
        show_categories(jarvis)


def show_subcategories(jarvis, category):
    """
    Show subcategories in the selected category.
    """
    subcategories = list(plugin_data[category].keys())
    jarvis.say(f"Subcategories in {category}:")
    for idx, subcategory in enumerate(subcategories, 1):
        jarvis.say(f"{idx}. {subcategory}")

    subcategory_input = jarvis.input("Select a subcategory by number: ")

    if subcategory_input.isdigit() and 1 <= int(subcategory_input) <= len(subcategories):
        selected_subcategory = subcategories[int(subcategory_input) - 1]
        show_plugins_in_subcategory(jarvis, category, selected_subcategory)
    else:
        jarvis.say("Invalid input. Please try again.")
        show_subcategories(jarvis, category)


def show_plugins_in_subcategory(jarvis, category, subcategory):
    """
    Show plugins in the selected subcategory.
    """
    plugins = plugin_data[category][subcategory]["plugins"]
    descriptions = plugin_data[category][subcategory]["descriptions"]

    jarvis.say(f"Here are the plugins in {subcategory}:")
    for idx, plugin in enumerate(plugins, 1):
        jarvis.say(f"{idx}. {plugin} - {descriptions[plugin]}")

    plugin_input = jarvis.input("Select a plugin to get more info or run a demo by number: ")

    if plugin_input.isdigit() and 1 <= int(plugin_input) <= len(plugins):
        selected_plugin = plugins[int(plugin_input) - 1]
        jarvis.say(f"You selected {selected_plugin}.")
        jarvis.say(f"Type `help {selected_plugin}` for additional information.")
        # You can also directly run the plugin if you want
        # jarvis.run(selected_plugin)
    else:
        jarvis.say("Invalid input. Returning to subcategory menu.")
        show_subcategories(jarvis, category)
