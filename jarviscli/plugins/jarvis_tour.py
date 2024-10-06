from plugin import plugin

# Dictionary containing categories, subcategories, plugins, and their descriptions
plugin_data = {
    "Entertainment": {
        "Games": {
            "plugins": ["akinator", "asteroids_neows", "blackjack", "coin_flip", "connect_four", "dice", "guess_number_game", "hangman", "magic_8_ball", "rockpaperscissors", "roulette", "spinthewheel", "tic_tac_toe", "trivia", "wordgame", "wordle"],
            "descriptions": {
                "akinator": "Play the Akinator guessing game.",
                "asteroids_neows": "Get information about near Earth objects.",
                "blackjack": "Play a game of Blackjack.",
                "coin_flip": "Simulate a coin flip.",
                "connect_four": "Play Connect Four against the computer.",
                "dice": "Roll virtual dice.",
                "guess_number_game": "Play a number guessing game.",
                "hangman": "Play the classic Hangman word game.",
                "magic_8_ball": "Ask the Magic 8 Ball a question.",
                "rockpaperscissors": "Play Rock, Paper, Scissors.",
                "roulette": "Play a game of Roulette.",
                "spinthewheel": "Spin a virtual wheel for random selection.",
                "tic_tac_toe": "Play Tic-Tac-Toe against the computer.",
                "trivia": "Answer trivia questions on various topics.",
                "wordgame": "Play a word guessing game.",
                "wordle": "Play the popular Wordle game."
            }
        },
        "Media": {
            "plugins": ["artprompts", "cat_fact", "chuck", "dad_jokes", "goodreads", "joke_of_day", "lyrics", "mood_music", "movies", "music_recognition", "picshow", "quote", "random_fact", "taste_dive", "top_media"],
            "descriptions": {
                "artprompts": "Get random art prompts for inspiration.",
                "cat_fact": "Learn interesting facts about cats.",
                "chuck": "Get Chuck Norris jokes.",
                "dad_jokes": "Hear some classic dad jokes.",
                "goodreads": "Get book recommendations and reviews.",
                "joke_of_day": "Hear the joke of the day.",
                "lyrics": "Find and display song lyrics.",
                "mood_music": "Get music recommendations based on your mood.",
                "movies": "Get movie recommendations and information.",
                "music_recognition": "Identify songs playing around you.",
                "picshow": "Display random images or create slideshows.",
                "quote": "Get inspirational or famous quotes.",
                "random_fact": "Learn random interesting facts.",
                "taste_dive": "Get recommendations for movies, TV shows, books, and more.",
                "top_media": "See top trending media content."
            }
        }
    },
    "Productivity": {
        "Task Management": {
            "plugins": ["create_plugin", "notes", "reminder", "routine", "tasks", "write_agenda"],
            "descriptions": {
                "create_plugin": "Create a new Jarvis plugin.",
                "notes": "Take and manage notes.",
                "reminder": "Set reminders for important tasks or events.",
                "routine": "Set up and manage daily routines.",
                "tasks": "Manage your to-do list.",
                "write_agenda": "Create and manage meeting agendas."
            }
        },
        "Time Management": {
            "plugins": ["clock", "event_timer", "timeconv", "typing_test"],
            "descriptions": {
                "clock": "Display the current time and date.",
                "event_timer": "Set timers for events or tasks.",
                "timeconv": "Convert time between different time zones.",
                "typing_test": "Test and improve your typing speed."
            }
        }
    },
    "Fitness & Health": {
        "Health Metrics": {
            "plugins": ["bmi", "bmr", "calories_macros"],
            "descriptions": {
                "bmi": "Calculate your Body Mass Index (BMI).",
                "bmr": "Calculate your Basal Metabolic Rate (BMR).",
                "calories_macros": "Track calories and macronutrients."
            }
        },
        "Fitness": {
            "plugins": ["workout"],
            "descriptions": {
                "workout": "Get workout suggestions and routines."
            }
        }
    },
    "Information & Reference": {
        "General Knowledge": {
            "plugins": ["dictionary", "element", "wiki", "numbers_api"],
            "descriptions": {
                "dictionary": "Look up word definitions.",
                "element": "Get information about chemical elements.",
                "wiki": "Search Wikipedia for information.",
                "numbers_api": "Get interesting facts about numbers."
            }
        },
        "News & Current Events": {
            "plugins": ["hackernews", "news", "corona"],
            "descriptions": {
                "hackernews": "Get top stories from Hacker News.",
                "news": "Get the latest news headlines.",
                "corona": "Get updates on COVID-19 statistics."
            }
        },
        "Geography & Location": {
            "plugins": ["countryinfo", "geocode", "location", "stateinfo"],
            "descriptions": {
                "countryinfo": "Get information about countries.",
                "geocode": "Convert addresses to geographic coordinates and vice versa.",
                "location": "Get your current location information.",
                "stateinfo": "Get information about U.S. states."
            }
        }
    },
    "Utilities": {
        "Conversion Tools": {
            "plugins": ["caesar_cipher", "currency_conv", "length_conv", "mass_conv", "morse_code", "speed_conv", "temp_conv", "binary", "hex", "mips_conv", "string_converter"],
            "descriptions": {
                "caesar_cipher": "Encode or decode messages using Caesar cipher.",
                "currency_conv": "Convert between different currencies.",
                "length_conv": "Convert between different units of length.",
                "mass_conv": "Convert between different units of mass.",
                "morse_code": "Translate text to and from Morse code.",
                "speed_conv": "Convert between different units of speed.",
                "temp_conv": "Convert between different temperature scales.",
                "binary": "Convert between binary and decimal.",
                "hex": "Convert between hexadecimal and decimal.",
                "mips_conv": "Convert MIPS assembly to machine code.",
                "string_converter": "Convert strings to various formats."
            }
        },
        "System Tools": {
            "plugins": ["battery", "clear", "file_manager", "file_organise", "scan_network", "screen_capture", "shutdown", "system_options", "system_update", "change_mac", "hotspot", "wifi_password_getter"],
            "descriptions": {
                "battery": "Check your device's battery status.",
                "clear": "Clear the console screen.",
                "file_manager": "Manage files and directories.",
                "file_organise": "Organize files in a directory.",
                "scan_network": "Scan your local network for devices.",
                "screen_capture": "Take screenshots or record your screen.",
                "shutdown": "Shutdown or restart your computer.",
                "system_options": "Manage system settings and options.",
                "system_update": "Check for and install system updates.",
                "change_mac": "Change your device's MAC address.",
                "hotspot": "Create a Wi-Fi hotspot.",
                "wifi_password_getter": "Retrieve saved Wi-Fi passwords."
            }
        },
        "Web Tools": {
            "plugins": ["curl", "dns_lookup", "get_host_info", "ip", "visit_website", "website_status"],
            "descriptions": {
                "curl": "Make HTTP requests from the command line.",
                "dns_lookup": "Perform DNS lookups.",
                "get_host_info": "Get information about a host or domain.",
                "ip": "Get your public IP address.",
                "visit_website": "Open a website in your default browser.",
                "website_status": "Check the status of a website."
            }
        },
        "File Operations": {
            "plugins": ["bulkresize", "htmltopdf", "imgcompressor", "imgtopdf", "pdftoimg", "readpdf"],
            "descriptions": {
                "bulkresize": "Resize multiple images at once.",
                "htmltopdf": "Convert HTML files to PDF.",
                "imgcompressor": "Compress image files.",
                "imgtopdf": "Convert images to PDF.",
                "pdftoimg": "Convert PDF files to images.",
                "readpdf": "Read the contents of a PDF file."
            }
        }
    },
    "Math & Calculation": {
        "Basic Math": {
            "plugins": ["evaluator", "expression_checker", "factor", "matrix_add"],
            "descriptions": {
                "evaluator": "Evaluate mathematical expressions.",
                "expression_checker": "Check the validity of mathematical expressions.",
                "factor": "Find factors of a number.",
                "matrix_add": "Perform matrix addition."
            }
        },
        "Advanced Math": {
            "plugins": ["armstrong_numbers", "kaprekar", "pi", "project_euler"],
            "descriptions": {
                "armstrong_numbers": "Find Armstrong numbers.",
                "kaprekar": "Find Kaprekar numbers.",
                "pi": "Calculate pi to a specified number of digits.",
                "project_euler": "Solve Project Euler problems."
            }
        }
    },
    "Personal Information": {
        "Personal Data": {
            "plugins": ["age", "agify", "myinfo", "name_day", "nationalize"],
            "descriptions": {
                "age": "Calculate age based on birthdate.",
                "agify": "Predict age based on name.",
                "myinfo": "Store and retrieve personal information.",
                "name_day": "Find the name day for a given name.",
                "nationalize": "Predict nationality based on name."
            }
        },
        "Personal Assistant": {
            "plugins": ["activity", "advice_giver", "motivate", "personality"],
            "descriptions": {
                "activity": "Get suggestions for activities.",
                "advice_giver": "Get advice on various topics.",
                "motivate": "Get motivational quotes and messages.",
                "personality": "Take a personality test."
            }
        }
    },
    "Communication": {
        "Social Media": {
            "plugins": ["imgur", "twitter_trends"],
            "descriptions": {
                "imgur": "Upload images to Imgur.",
                "twitter_trends": "See current Twitter trends."
            }
        },
        "Messaging": {
            "plugins": ["gmail", "natoalphabet"],
            "descriptions": {
                "gmail": "Check and send Gmail emails.",
                "natoalphabet": "Convert text to NATO phonetic alphabet."
            }
        },
        "Voice & Audio": {
            "plugins": ["voice", "voice_control"],
            "descriptions": {
                "voice": "Convert text to speech.",
                "voice_control": "Control Jarvis using voice commands."
            }
        }
    },
    "Travel & Transportation": {
        "Travel Information": {
            "plugins": ["distance", "flightradar", "moon_phase", "weather_report"],
            "descriptions": {
                "distance": "Calculate distance between two locations.",
                "flightradar": "Track flights in real-time.",
                "moon_phase": "Get current moon phase information.",
                "weather_report": "Get weather forecasts for a location."
            }
        },
        "Space": {
            "plugins": ["mars_weather"],
            "descriptions": {
                "mars_weather": "Get weather information for Mars."
            }
        }
    },
    "Sports & Games": {
        "Sports Information": {
            "plugins": ["basketball", "cricket", "football", "tennis", "world_cup"],
            "descriptions": {
                "basketball": "Get basketball-related information.",
                "cricket": "Get cricket match scores and information.",
                "football": "Get football (soccer) match information.",
                "tennis": "Get tennis match information.",
                "world_cup": "Get World Cup tournament information."
            }
        },
        "Game Tools": {
            "plugins": ["check_if_game_runs_on_linux", "game"],
            "descriptions": {
                "check_if_game_runs_on_linux": "Check if a game can run on Linux.",
                "game": "Launch or manage games."
            }
        }
    },
    "Miscellaneous": {
        "Random Generators": {
            "plugins": ["random_list", "random_number", "random_password", "random_repo"],
            "descriptions": {
                "random_list": "Generate a random list of items.",
                "random_number": "Generate random numbers.",
                "random_password": "Generate secure random passwords.",
                "random_repo": "Get a random GitHub repository."
            }
        },
        "Other Tools": {
            "plugins": ["balut", "boredAPI", "buy", "camera", "cat_history", "cocktail", "detect_language", "dial_code", "drink", "exit", "food_recipe", "fruit", "fruit_nutrition", "get_joke", "google", "hackathon", "hash", "history", "leap_year", "memory", "newyear", "open", "performance", "qr_generator", "search", "speed_test", "stock", "switchingwin", "translate", "upside_down", "volume", "voter_info", "weekday", "whoami", "yeelight"],
            "descriptions": {
                "balut": "Information about the Filipino dish Balut.",
                "boredAPI": "Get suggestions for activities when you're bored.",
                "buy": "Get product recommendations or shopping information.",
                "camera": "Access and control device camera.",
                "cat_history": "Learn about the history of cats.",
                "cocktail": "Get cocktail recipes and information.",
                "detect_language": "Detect the language of a given text.",
                "dial_code": "Get country dial codes.",
                "drink": "Get information about various drinks.",
                "exit": "Exit the Jarvis application.",
                "food_recipe": "Get recipes for various dishes.",
                "fruit": "Get information about different fruits.",
                "fruit_nutrition": "Get nutritional information about fruits.",
                "get_joke": "Get a random joke.",
                "google": "Perform a Google search.",
                "hackathon": "Get information about hackathons.",
                "hash": "Generate hash values for strings.",
                "history": "Get historical events for a specific date.",
                "leap_year": "Check if a year is a leap year.",
                "memory": "Check system memory usage.",
                "newyear": "New Year related functions or information.",
                "open": "Open files or applications.",
                "performance": "Check system performance metrics.",
                "qr_generator": "Generate QR codes.",
                "search": "Perform web searches.",
                "speed_test": "Test internet connection speed.",
                "stock": "Get stock market information.",
                "switchingwin": "Switch between windows.",
                "translate": "Translate text between languages.",
                "upside_down": "Convert text to upside-down Unicode characters.",
                "volume": "Control system volume.",
                "voter_info": "Get voter information.",
                "weekday": "Find the day of the week for a given date.",
                "whoami": "Display current user information.",
                "yeelight": "Control Yeelight smart bulbs."
            }
        }
    }
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

    while True:
        category_input = jarvis.input("Please select a category by number (or 'q' to quit): ")
        if category_input.lower() == 'q':
            jarvis.say("Thank you for using the Jarvis Tour!")
            return

        if category_input.isdigit() and 1 <= int(category_input) <= len(categories):
            selected_category = categories[int(category_input) - 1]
            show_subcategories(jarvis, selected_category)
            break
        else:
            jarvis.say("Invalid input. Please try again.")


def show_subcategories(jarvis, category):
    """
    Show subcategories in the selected category.
    """
    subcategories = list(plugin_data[category].keys())
    jarvis.say(f"Subcategories in {category}:")
    for idx, subcategory in enumerate(subcategories, 1):
        jarvis.say(f"{idx}. {subcategory}")

    while True:
        subcategory_input = jarvis.input("Select a subcategory by number (or 'b' to go back): ")
        if subcategory_input.lower() == 'b':
            show_categories(jarvis)
            return

        if subcategory_input.isdigit() and 1 <= int(subcategory_input) <= len(subcategories):
            selected_subcategory = subcategories[int(subcategory_input) - 1]
            show_plugins_in_subcategory(jarvis, category, selected_subcategory)
            break
        else:
            jarvis.say("Invalid input. Please try again.")


def show_plugins_in_subcategory(jarvis, category, subcategory):
    """
    Show plugins in the selected subcategory.
    """
    plugins = plugin_data[category][subcategory]["plugins"]
    descriptions = plugin_data[category][subcategory]["descriptions"]

    jarvis.say(f"Here are the plugins in {subcategory}:")
    for idx, plugin in enumerate(plugins, 1):
        jarvis.say(f"{idx}. {plugin} - {descriptions[plugin]}")

    while True:
        plugin_input = jarvis.input("Select a plugin to get more info or run a demo by number (or 'b' to go back): ")
        if plugin_input.lower() == 'b':
            show_subcategories(jarvis, category)
            return

        if plugin_input.isdigit() and 1 <= int(plugin_input) <= len(plugins):
            selected_plugin = plugins[int(plugin_input) - 1]
            jarvis.say(f"You selected {selected_plugin}.")
            # jarvis.say(f"Type 'help {selected_plugin}' for additional information.")

            action = jarvis.input(
                "Type 'back' to select another plugin, or 'main' to return to main menu: ")
            if action.lower() == 'back':
                continue
            elif action.lower() == 'main':
                show_categories(jarvis)
                return
            else:
                jarvis.say("Invalid input. Returning to plugin selection.")
        else:
            jarvis.say("Invalid input. Please try again.")