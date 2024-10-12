from plugin import plugin

# Dictionary containing categories, subcategories, plugins, and their descriptions
plugin_data = {
    "Entertainment & Games": {
        "Entertainment": {
            "plugins": ["check_if_game_runs_on_linux", "movie", "buy"],
            "descriptions": {
                "check_if_game_runs_on_linux": "Retrieves ProtonDB compatibility ratings for a Steam game.",
                "movie": "Look up movie information on IMDB.",
                "buy": "Search for products on Amazon or eBay"
            },
            "tutorials": {
                "check_if_game_runs_on_linux": "",
                "movie": "",
                "buy": ""
            }
        },
        "Games": {
            "plugins": ["balut", "blackjack", "coin_flip", "connect_four", "guess_number_game", "hangman",
                        "magic_8_ball", "memory", "rockpaperscissors", "roulette", "spinthewheel", "tic_tac_toe",
                        "wordgame", "wordle"],
            "descriptions": {
                "balut": "A strategic multi-player dice game.",
                "blackjack": "Play a game of Blackjack, following standard casino rules.",
                "coin_flip": "Simulate a coin flip.",
                "connect_four": "Play Connect Four against the computer.",
                "guess_number_game": "This plugin initiates a number guessing game where the user selects between two modes (Hard or Normal) and tries to guess a number between 1 and 100, with feedback on whether the guess is higher or lower.",
                "hangman": "This plugin plays a game of Hangman where the player guesses letters to reveal a hidden word.",
                "magic_8_ball": "Ask the Magic 8 Ball a question.",
                "memory": "Train your short-term memory with increasing difficulty.",
                "rockpaperscissors": "Play Rock-Paper-Scissors against Jarvis with score tracking and up to 100 rounds.",
                "roulette": "Play a simple roulette game where you place bets and spin the wheel to win or lose virtual cash.",
                "spinthewheel": "Spin a virtual wheel for random selection.",
                "tic_tac_toe": "Play Tic-Tac-Toe against the computer.",
                "wordgame": "Play a word guessing game.",
                "wordle": "Play the popular Wordle game."
            },
            "tutorials": {
                "balut": "",
                "blackjack": "",
                "coin_flip": "",
                "connect_four": "",
                "guess_number_game": "",
                "hangman": "",
                "magic_8_ball": "",
                "memory": "",
                "rockpaperscissors": "",
                "roulette": "",
                "spinthewheel": "",
                "tic_tac_toe": "",
                "wordgame": "",
                "wordle": ""
            }
        },
        "Media": {
            "plugins": ["mood_music"],
            "descriptions": {
                "mood_music": "Get music recommendations based on your mood."
            },
            "tutorials": {
                "mood_music": ""
            }
        }
    },
    "Fitness & Health": {
        "Fitness": {
            "plugins": ["workout"],
            "descriptions": {
                "workout": "Customized push-up and pull-up workout plans based on user's fitness level."
            },
            "tutorials": {
                "workout": ""
            }
        },
        "Health": {
            "plugins": ["bmi", "bmr", "calories_macros"],
            "descriptions": {
                "bmi": "Calculate your Body Mass Index (BMI).",
                "bmr": "Calculate your Basal Metabolic Rate (BMR).",
                "calories_macros": "Calculate personalized daily calorie and macronutrient recommendations for weight management goals."
            },
            "tutorials": {
                "bmi": "",
                "bmr": "",
                "calories_macros": ""
            }
        }
    },
    "Food & Drink": {
        "Recipe": {
            "plugins": ["drink"],
            "descriptions": {
                "drink": "Fetch details about a specific cocktail, including ingredients and preparation instructions, from an external API."
            },
            "tutorials": {
                "drink": ""
            }
        }
    },
    "Information & Facts": {
        "Facts": {
            "plugins": ["stateinfo"],
            "descriptions": {
                "stateinfo": "Get information about U.S. states."
            },
            "tutorials": {
                "stateinfo": ""
            }
        },
        "Information": {
            "plugins": ["dial_code", "google", "history", "name_day", "weekday"],
            "descriptions": {
                "dial_code": "Lookup or retrieve a country's dialing code, or find the country associated with a given dialing code.",
                "google": "This plugin performs a Google search using a provided query, retrieves the first answer from Google's default result snippets, and returns it.",
                "history": "Get historical events for a specific date.",
                "name_day": "Find the name day for a given name.",
                "weekday": "Tells what day of the week any date falls on."
            },
            "tutorials": {
                "dial_code": "",
                "google": "",
                "history": "",
                "name_day": "",
                "weekday": ""
            }
        },
        "Investment": {
            "plugins": ["cryptotracker"],
            "descriptions": {
                "cryptotracker": "Track the price and 24-hour price change of cryptocurrency pairs, or check a default list of favorite pairs."
            },
            "tutorials": {
                "cryptotracker": ""
            }
        },
        "Language": {
            "plugins": ["dictionary"],
            "descriptions": {
                "dictionary": "Look up the meaning, synonyms, and antonyms of any word, and provide additional details if needed."
            },
            "tutorials": {
                "dictionary": ""
            }
        }
    },
    "Media": {
        "": {
            "plugins": ["voice", "voice_control"],
            "descriptions": {
                "voice": "Enable or disable Jarvis's voice and control speech speed.",
                "voice_control": "Activates voice mode for commands and listens for 'stop' to deactivate."
            },
            "tutorials": {
                "voice": "",
                "voice_control": ""
            }
        }
    },
    "Programming & Math": {
        "Encryption": {
            "plugins": ["caesar_cipher"],
            "descriptions": {
                "caesar_cipher": "Encode or decode messages using Caesar cipher."
            },
            "tutorials": {
                "caesar_cipher": ""
            }
        },
        "Math": {
            "plugins": ["binary", "evaluator", "factor", "kaprekar", "matrix_add"],
            "descriptions": {
                "binary": "Convert between binary and decimal.",
                "evaluator": "This plugin performs various mathematical operations such as solving equations, calculating expressions, factoring, plotting graphs, and analyzing limits, derivatives, and integrals.",
                "factor": "This plugin calculates the prime factors of a given number and prints them in a factorized form.",
                "kaprekar": "Checks if a number is a Kaprekar number.",
                "matrix_add": "Perform matrix addition."
            },
            "tutorials": {
                "binary": "",
                "evaluator": "",
                "factor": "",
                "kaprekar": "",
                "matrix_add": ""
            }
        },
        "Utilities": {
            "plugins": ["bulkresize", "create_plugin"],
            "descriptions": {
                "bulkresize": "Resize and optionally renames all images in a directory, tailored for deep learning data preparation.",
                "create_plugin": "Create a plugin for Jarvis."
            },
            "tutorials": {
                "bulkresize": "",
                "create_plugin": ""
            }
        }
    },
    "System": {
        "Command Line Utilities": {
            "plugins": ["battery", "cat_history", "clear", "volume", "whoami"],
            "descriptions": {
                "battery": "Check your device's battery status.",
                "cat_history": "Print the history of commands",
                "clear": "Clear the terminal screen, supporting both Unix and Windows platforms.",
                "volume": "Increases, decreases, or mutes the speaker volume on Linux or macOS systems.",
                "whoami": "Display current user information."
            },
            "tutorials": {
                "battery":
                    """
                    Battery Plugin Tutorial
                    
                    1. Start the Plugin
                       Run the command:
                       battery [option]
                    
                       Available options:
                       - status: Displays battery state, percentage, and time to full/empty.
                       - vendor: Displays the battery vendor information.
                       - energy: Displays energy information.
                       - technology: Displays battery technology type.
                       - remaining: Displays remaining time to empty.
                    
                    2. Example Usage on Windows
                       battery status
                       Output: 
                       Battery is charging: 80%
                       or
                       charge = 50%, time left = 2:15:30
                    
                    3. Example Usage on Linux (with upower)
                       battery vendor
                       Output: 
                       vendor: XYZ Corporation
                    
                    4. Linux Fallback (without upower)
                       If upower is not available, the plugin will fetch battery info from system files.
                    
                       Example:
                       battery status
                       Output:
                       Status: Discharging
                       Charge: 75%
                    """,
                "cat_history":
                    """
                    Cat History Plugin Tutorial
                    
                    1. Start the Plugin
                       Type:
                       cat his
                    
                    2. Usage
                       This plugin prints the history of commands.
                    
                    3. Functionality
                       - Reads the command history from a file
                       - Displays the history in blue text
                    
                    4. Example
                       cat his
                       Output: Displays a list of previously executed commands in blue
                    
                    5. Notes
                       - No additional parameters required
                       - History is read from a predefined file (HISTORY_FILENAME)""",
                "clear":
                    """Clear Plugin Tutorial
                    
                    1. Usage
                       Type:
                       clear
                    
                    2. Function
                       Clears the terminal screen
                    
                    3. Platform Support
                       - Unix/Linux/MacOS/BSD: Uses 'clear' command
                       - Windows: Uses 'cls' command
                    
                    4. No Additional Parameters
                       This plugin doesn't require any additional parameters
                    
                    5. Example
                       clear
                       Output: Clears the terminal screen""",
                "volume":
                    """1. Start the Plugin
                       Use the following commands based on your platform:
                       - increase volume
                       - decrease volume
                       - mute
                       - max volume (for MacOS only)
                    
                    2. Volume Control
                       Adjust the speaker volume by increasing or decreasing the sound by a percentage.
                    
                    3. Mute/Unmute
                       Use the mute command to silence or unmute your speaker.
                    
                    4. Exit
                       After adjusting the volume or muting, the plugin will terminate automatically.
                    """
                ,
                "whoami":
                    """1. Start the Plugin
                       Run the command:
                       whoami
                    
                    2. Get Current User Name
                       The plugin will display the current effective user ID's name.
                    
                    3. Use Options (Optional)
                       You can pass additional Linux "id" command options:
                       Example: whoami --groups
                       This will show the group memberships of the current user.
                       
                    4. Exit
                       Once you receive the information, the plugin will terminate automatically.
                    """
            }
        },
        "File Management": {
            "plugins": ["file_organise"],
            "descriptions": {
                "file_organise": "Organize files in a directory."
            },
            "tutorials": {
                "file_organise":
                    """File Organise Plugin Tutorial
                    
                    1. Start the Plugin
                       Type:
                       file organise
                    
                    2. Usage Steps
                       1. Enter directory name to clean
                       2. Choose directory from search results
                       3. Review folders before cleaning
                       4. Plugin organizes files by extension
                       5. Review folders after cleaning
                    
                    3. Example
                       file organise
                       Enter the name of directory you want to clear: Downloads
                       [Search results displayed]
                       Enter the option number: 1
                    
                    4. Features
                       - Searches for directory across file system
                       - Creates new folder structure based on file extensions
                       - Moves files to appropriate folders
                       - Handles files without extensions
                    
                    5. Tips
                       - Ensure you have necessary permissions for target directory
                       - Be cautious when organizing system directories"""
            }
        },
        "Networking": {
            "plugins": ["change_mac", "curl", "dns_lookup", "get_host_info", "ip", "wifi_password_getter"],
            "descriptions": {
                "change_mac": "View and change the MAC address of any network device connected to your Linux system.",
                "curl": "Generate a curl request by specifying the HTTP method, content type, data, and endpoint, while ensuring the input parameters are valid.",
                "dns_lookup": "Look up an IP address from a hostname or a hostname from an IP address using DNS forward and reverse queries.",
                "get_host_info": "Get information about a host.",
                "ip": "Displays local and public IP addresses for UNIX and Windows systems.",
                "wifi_password_getter": "Retrieve saved Wi-Fi passwords."
            },
            "tutorials": {
                "change_mac":
                    """MAC Manager Plugin Tutorial
                    
                    1. Start the Plugin
                       Type:
                       mac
                    
                    2. View Connected Devices
                       - The plugin will display a list of connected internet devices
                       - Each device is shown with its name and current MAC address
                    
                    3. Select a Device
                       - Enter the number corresponding to the device you want to modify
                       - To exit, select the last option (Exit)
                    
                    4. Enter New MAC Address
                       - Input a new MAC address in the format XX:XX:XX:XX:XX:XX
                       - Use lowercase letters and numbers
                    
                    5. Confirm Changes
                       - The plugin will display the device name and new MAC address
                       - Changes are applied automatically
                    
                    6. Verify New MAC Address
                       - The plugin will show the updated MAC address for the selected device
                    
                    Note: This plugin requires sudo privileges to modify network settings.""",
                "curl":
                    """Generate Curl Plugin Tutorial
                    
                    1. Start the Plugin
                       Run the command:
                       generate curl
                    
                    2. Enter HTTP Method
                       Input a valid HTTP method (GET, POST, PUT, PATCH, DELETE):
                       HTTP Method: POST
                    
                    3. Select Content Type
                       Choose the content type:
                       1. JSON
                       2. No Data
                       Enter your choice: 1
                    
                    4. Provide Data (Optional)
                       Input the data for the request, or press Enter if not applicable:
                       Enter / copy the data: {"name": "test"}
                    
                    5. Specify Endpoint
                       Input the HTTP endpoint (e.g., https://api.example.com/resource):
                       Specify the HTTP endpoint: https://api.example.com/resource
                    
                    6. View Generated Curl Command
                       The curl request is generated and displayed:
                       curl -XPOST -H "Content-type: application/json" -d '{"name": "test"}' 'https://api.example.com/resource'
                    """,
                "dns_lookup":
                    """DNS Plugin Tutorial
                    
                    1. Forward DNS Lookup (Hostname to IP)
                       To find the IP address of a hostname, run the command:
                       dns forward
                    
                    2. Enter Hostname
                       Input the desired hostname (e.g., example.com):
                       Please input a hostname: example.com
                    
                    3. Output IP Address
                       The IP address will be displayed:
                       The IP address for that hostname is: 93.184.216.34
                    
                    4. Reverse DNS Lookup (IP to Hostname)
                       To find the hostname from an IP address, run the command:
                       dns reverse
                    
                    5. Enter IP Address
                       Input the desired IP address (e.g., 93.184.216.34):
                       Please input an ip: 93.184.216.34
                    
                    6. Output Hostname
                       The hostname will be displayed:
                       The hostname for that IP address is: example.com
                    
                    7. Invalid Input Handling
                       If an invalid input is provided, you will be asked to try again or exit.
                       Example invalid input:
                       Please input a valid ip
                       Do you want to try again (y/n): y
                    """,
                "get_host_info":
                    """Host Info Plugin Tutorial
                    
                    1. Start the Plugin
                       Run the command:
                       hostinfo
                    
                    2. Input Domain or IP
                       You will be prompted to:
                       Enter Domain Name or IP Address: 
                       - Type a valid domain or IP address to retrieve information.
                       - Type 'q' or 'quit' to exit.
                    
                    3. Display Information
                       - **nslookup**: Performs an nslookup query to retrieve DNS information.
                       - **whois**: Shows whois information for the provided domain or IP.
                       - **ping**: Pings the domain or IP to check connectivity.
                    
                    4. Example Flow
                       - After entering a domain like "example.com", the plugin will display:
                         - nslookup information.
                         - whois data (if available).
                         - ping results.
                    
                    5. Exiting the Plugin
                       - Type 'q' or 'quit' at any prompt to exit the plugin.
                    """,
                "ip":
                    """IP Plugin Tutorial
                    
                    1. Display Local and Public IP Address
                       Run the command:
                       ip
                    
                    2. Local IP Addresses
                       The command will display a list of local IP addresses.
                    
                    3. Public IPv4 Address
                       The command will retrieve and display the public IPv4 address.
                    
                    4. Public IPv6 Address
                       The command will also retrieve and display the public IPv6 address.
                    
                    5. Windows IP Information
                       On Windows, the command will return the IP address of the host machine.
                    """,
                "wifi_password_getter":
                    """1. Start the Plugin
                       Run the command:
                       wifi
                    
                    2. View Available WiFi Profiles
                       A list of previously connected WiFi profiles will be displayed. 
                       Select a number to view the password.
                    
                    3. Get WiFi Password
                       After selecting a profile, the WiFi name and password will be shown. 
                       For example:
                       Wifi Name: YourWiFi
                       Password: yourpassword
                    
                    4. Exit
                       Type the number associated with 'Exit' to quit the plugin.
                    """
            }
        },
        "Tools": {
            "plugins": ["clock", "system_update"],
            "descriptions": {
                "clock": "Display the current time, run a stopwatch, and set a timer with customizable durations.",
                "system_update": "Check for and install system updates."
            },
            "tutorials": {
                "clock":
                    """Time Plugins Tutorial
                    
                    1. Clock Plugin
                       Display current date and time:
                       clock
                    
                    2. Stopwatch Plugin
                       Start a stopwatch:
                       stopwatch
                    
                       Controls:
                       L     - Lap
                       R     - Reset
                       SPACE - Pause
                       Q     - Quit
                    
                    3. Timer Plugin
                       Set a countdown timer:
                       timer [duration]
                    
                       Examples:
                       timer 10
                       timer 1h5m30s
                    
                       Controls:
                       R     - Reset
                       SPACE - Pause
                       Q     - Quit
                    
                       Note: Specify duration in seconds or use format: XhYmZs
                       (X hours, Y minutes, Z seconds)""",
                "system_update":
                    """Update System Plugin Tutorial
                    
                    1. Start the Update System Plugin
                       Command: update system
                    
                    2. MacOS System Update
                       On macOS, this command will:
                       - Upgrade all installed Homebrew packages.
                       - Update the Homebrew package list.
                    
                    3. Linux System Update
                       On supported Linux distributions, this command will:
                       - Ubuntu/Linux Mint: Run `apt-get update` and `apt-get upgrade`.
                       - Fedora: Run `dnf upgrade` and `dnf system-upgrade`.
                       - Arch Linux: Run `pacman -Syu`.
                       - openSUSE: Run `zypper update`.
                    
                    Note:
                    - Make sure you have the appropriate permissions (may require `sudo`).
                    - Only supported on macOS and Linux."""
            }
        }
    },
    "Utilities": {
        "Conversion Tools": {
            "plugins": ["hash", "hex", "length_conv", "massconv", "mips", "morse_code", "natoalphabet", "qr_generator",
                        "speed_conv", "temp_conv"],
            "descriptions": {
                "hash": "This plugin allows the user to hash a string or a file using a specified hash function like `md5`, `sha1`, or `sha256`.",
                "hex": "This plugin converts a given integer to its hexadecimal representation and prints it.",
                "length_conv": "Converts between different length measurement units.",
                "massconv": "Convert between different units of mass.",
                "mips": "Conversion between MIPS and machine code.",
                "morse_code": "Translate text to and from Morse code.",
                "natoalphabet": "Convert text to NATO phonetic alphabet.",
                "qr_generator": "Generate QR codes.",
                "speed_conv": "Convert speed between m/s km/h ft/s mi/h and knots.",
                "temp_conv": "Convert between different temperature scales."
            },
            "tutorials": {
                "hash": "",
                "hex": "",
                "length_conv": "",
                "massconv": "",
                "mips": "",
                "morse_code": "",
                "natoalphabet": "",
                "qr_generator": "",
                "speed_conv": "",
                "temp_conv": ""
            }
        },
        "File Operations": {
            "plugins": ["imgcompressor", "imgtopdf"],
            "descriptions": {
                "imgcompressor": "Compress image files.",
                "imgtopdf": "Converts single or multiple images into a PDF file."
            },
            "tutorials": {
                "imgcompressor": "",
                "imgtopdf": ""
            }
        },
        "Random Generator": {
            "plugins": ["random_password"],
            "descriptions": {
                "random_password": "Generate secure random passwords."
            },
            "tutorials": {
                "random_password": ""
            }
        },
        "Reminder": {
            "plugins": ["reminder"],
            "descriptions": {
                "reminder": "Set reminders for important tasks or events."
            },
            "tutorials": {
                "reminder": ""
            }
        },
        "Tools": {
            "plugins": ["tasks", "timeconv", "website_status", "write_agenda"],
            "descriptions": {
                "tasks": "Manage your to-do list.",
                "timeconv": "Convert time between different time zones.",
                "website_status": "Checks the status of a website by requesting its URL.",
                "write_agenda": "Create and manage meeting agendas."
            },
            "tutorials": {
                "tasks": "",
                "timeconv": "",
                "website_status": "",
                "write_agenda": ""
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
    tutorials = plugin_data[category][subcategory]["tutorials"]

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
            jarvis.say(f"Tutorial: {tutorials[selected_plugin]}")  # Displaying tutorial when selected

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
