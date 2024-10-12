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
                "check_if_game_runs_on_linux":
                    """
                    Proton Compatible Game Plugin Tutorial
                    
                    1. Start the Plugin
                       Type:
                       Proton game
                    
                    2. Usage Options
                       Choose from:
                       1 - Provide Steam game AppId
                       2 - Provide Steam game Title
                       3 - Close
                    
                    3. Using AppId (Option 1)
                       - Enter the Steam game AppId when prompted
                       - Get the ProtonDB rating for the game
                    
                    4. Using Game Title (Option 2)
                       - Enter the Steam game title when prompted
                       - Plugin searches for the game and retrieves its AppId
                       - Get the ProtonDB rating for the game
                    
                    5. Notes
                       - Option 2 may not find the game or find an incorrect game
                       - For accurate results, use Option 1 with the correct AppId from Steam
                       - If the game is not found or has no ratings, you'll receive an error message
                    
                    6. Example
                       Proton game
                       Enter your choice: 1
                       Enter Game AppId: 570
                       Output: Displays ProtonDB rating for the game (e.g., AppId 570 is Dota 2)
                    
                    7. Closing the Plugin
                       Choose option 3 to exit
                                        """
                ,
                "movie":
                    """
                    Movie Plugin Tutorial
                    
                    1. Search for a movie:
                       movie search <movie name>
                    
                    2. Get movie information:
                       movie info <movie name>
                    
                    3. View specific movie details:
                       movie cast <movie name>
                       movie director <movie name>
                       movie plot <movie name>
                       movie producer <movie name>
                       movie rating <movie name>
                       movie year <movie name>
                       movie runtime <movie name>
                       movie countries <movie name>
                       movie genres <movie name>
                    
                    Example:
                    movie search Inception
                    movie info Inception
                    movie cast Inception
                    """,
                "buy":
                    """
                    Buy Plugin Tutorial
                    
                    1. Start the Plugin
                       Type:
                       buy [shop] [search term]
                    
                    2. Example One-Line Command
                       - Search directly on Amazon or eBay by specifying the shop and search term:
                       buy amazon laptop
                       Output: Opens the Amazon search page for "laptop"
                    
                    3. Step-by-Step Usage
                       - If no shop and search term are provided, the plugin will guide you through the steps:
                         1. Choose a shop: "Amazon" or "eBay"
                         2. Provide a search term: e.g., "smartphone"
                    
                    4. Example Step-by-Step
                       buy
                       Pick a site (Amazon or Ebay): amazon
                       What you need to buy? laptop
                       Output: Opens the Amazon search page for "laptop"
                    
                    5. Supported Shops
                       - Amazon
                       - eBay
                    """
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
                "balut":
                    """
                    Balut Plugin Tutorial
                    
                    1. Start the Game
                       Run the command:
                       balut
                    
                    2. Enter Number of Players
                       Input the number of players (e.g., 2):
                       Number of players: 2
                    
                    3. Enter Player Names
                       Provide a username for each player:
                       Player 1 username: Alice
                       Player 2 username: Bob
                    
                    4. Roll Dice
                       Dice will be rolled automatically. Example output:
                       Alice you have rolled:
                       Dice 1: 4, Dice 2: 6, Dice 3: 5, Dice 4: 2, Dice 5: 3
                    
                    5. Re-roll (Optional)
                       Reroll specific dice by typing numbers:
                       Select dice to reroll (e.g., 2 4 5) or press Enter to keep:
                    
                    6. Settle Score
                       Choose a category to settle the score (1-7):
                       Select category (1-7): 3
                    
                    7. Rounds & Results
                       Play continues for 28 rounds. After the final round, total points are displayed, and the winner is announced.
                    """
                ,
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
                "workout":
                """
                1. Start Workout
                Run the command:
                workout

                2. Choose an Exercise
                Select between pushups or pullups:
                Write 'push' for pushups, 'pull' for pullups, or 'q' to quit

                3. Enter Your Maximum Reps
                Input how many times you can do the chosen exercise:
                Enter an integer (e.g., 15)

                4. Follow the Program
                Jarvis will generate a personalized workout routine and guide you through sets with rest intervals.
                
                5. Completion
                After finishing all sets, you will see your total reps and a motivational message.
                """
            }
        },
        "Health": {
            "plugins": ["bmi", "bmr", "calories_macros","drink"],
            "descriptions": {
                "bmi": "Calculate your Body Mass Index (BMI).",
                "bmr": "Calculate your Basal Metabolic Rate (BMR).",
                "calories_macros": "Calculate personalized daily calorie and macronutrient recommendations for weight management goals.",
                "drink": "Fetch details about a specific cocktail, including ingredients and preparation instructions, from an external API."
            },
            "tutorials": {
                "bmi":
                """
                BMI Plugin Tutorial

                1. Start the Plugin
                Type:
                bmi

                2. Choose Measurement System
                - 1: Metric system (cm for height, kg for weight)
                - 2: Imperial system (ft and inches for height, lbs for weight)
                - Default is Metric system

                3. Enter Measurements
                - For Metric: Enter height in cm and weight in kg.
                - For Imperial: Enter height in ft and inches, then weight in lbs.

                4. Example Metric Input
                bmi
                Your choice: 1
                Please insert your height in cm: 170
                Please insert your weight in kg: 70
                Output: BMI: 24.2 (Healthy)

                5. Example Imperial Input
                bmi
                Your choice: 2
                Please insert your height in ft: 5
                Please insert your height in inches: 9
                Please insert your weight in lbs: 160
                Output: BMI: 23.6 (Healthy)

                6. Body State
                - Severe thinness: BMI < 16
                - Mild thinness: BMI 16-18.5
                - Healthy: BMI 18.5-24.9
                - Pre-obese: BMI 25-29.9
                - Obese: BMI ≥ 30
                """,

                "bmr":
                """
                BMR Plugin Tutorial

                1. Start the Plugin
                Type:
                bmr

                2. Choose to Proceed
                - 1: Start calculating BMR.
                - 2: Learn what BMR is before calculating.

                3. Enter Personal Information
                - Gender (M/F)
                - Height (cm)
                - Weight (kg)
                - Age (years)

                4. Example Input
                bmr
                Gender: M
                Height: 180
                Weight: 75
                Age: 25
                Output: BMR: 1700.5

                5. Calculate AMR (Optional)
                After calculating BMR, you can calculate your AMR based on activity level:
                - 1: Low (no or little exercise)
                - 2: Average (light exercise)
                - 3: High (moderate exercise)
                - 4: Every Day (intense exercise)
                - 5: Athletic (very intense exercise)

                6. Example AMR Input
                Would you like to calculate your AMR? (Y/N): Y
                Activity level: 3
                Output: AMR: 2635.7
                """,

                "calories_macros":
                """
                Calories Macros Plugin Tutorial

                1. Start the Plugin
                Type:
                calories

                2. Example Command
                - Calculate daily calorie intake and macros for weight maintenance:
                calories

                3. Step-by-Step Usage
                - Follow prompts to provide:
                    1. Gender (M/F)
                    2. Age (in years)
                    3. Height (cm)
                    4. Weight (kg)
                    5. Activity level (1-4)
                    6. Goal (1-3 for Lose, Maintain, Gain)

                4. Default Macronutrient Ratios
                - Proteins: 20%
                - Carbs: 50%
                - Fats: 30%

                5. Custom Macronutrient Ratios
                - If not using default, specify custom ratios for each macro ensuring the total equals 1.
                """
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
                
                "drink":
                """
                Drink Plugin Tutorial

                1. Start the Plugin
                Run the command:
                drink

                2. Enter a Drink Name
                Input the name of the drink you want information about (e.g., Mojito):
                Enter a drink: Mojito

                3. View Ingredients
                The plugin will display the ingredients used for the drink, example output:
                -----
                Mojito
                -----
                Ingredients: 
                White Rum
                Sugar
                Lime Juice
                Soda Water
                Mint
                -----

                4. View Instructions
                Instructions for preparing the drink will be displayed after the ingredients, example output:
                "Muddle mint leaves with sugar and lime juice. Add a splash of soda water and fill the glass with ice. Pour the rum and top with soda water. Garnish with mint leaves."

                5. Error Handling
                If the drink is not found, the plugin will show:
                Drink not found. Please try again.
                """
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
                "stateinfo":

                """
                State Info Plugin Tutorial

                1. Start the State Info Plugin
                Command: stateinfo [state]
                Alias: state
                        state capital
                        state abbreviation

                2. Enter State Name
                Example usage:
                stateinfo california
                state capital new york
                state abbreviation texas

                3. Get State Information
                The plugin will provide:
                - The capital of the specified U.S. state.
                - The postal abbreviation for the specified U.S. state.

                Example output:
                The capital of California is Sacramento
                The postal abbreviation is CA

                4. Invalid Input
                If an invalid state is provided, the plugin will prompt:
                Please enter a valid U.S. state
                """
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
                "dial_code":

                """
                Dial Code Plugin Tutorial

                1. Get Dial Code by Country
                Use the command to get the dial code of a specific country:
                dial code of <COUNTRY NAME/ COUNTRY CODE>
                Example:
                dial code of United States

                2. Display All Available Countries (Optional)
                If no code is found, the plugin will ask:
                Print available countries? (y/N)
                Choose 'y' to print all countries or press Enter to skip.

                3. Get Country by Dial Code
                To get a country name by its dial code, use the following:
                country with dial code <DIAL CODE>
                Example:
                country with dial code +1

                4. Multiple Country Codes
                If a code is shared by multiple countries, they will all be listed together, separated by semicolons.
                """,

                "google":
                """
                Google Scraper Plugin Tutorial

                1. Perform a Google Search
                Run the command:
                google [your query]
                Example:
                google What is the Large Hadron Collider?

                2. View the Result
                The result will be displayed in the console. If a direct answer is available, it will be returned. Otherwise, you'll see a message like "No Answers Found."

                3. Supported Queries
                You can ask questions related to general knowledge or specific topics. Google will try to provide the best possible answer from its default answers section.
                """,

                "history":
                """
                History Plugin Tutorial

                1. Fetch a Historical Fact
                Run the command:
                history

                2. Get a Random Event
                Get a random historical event for a specific day and month:
                history <event> <day> <month>
                Example:
                history events 10 june

                3. Use Keywords
                You can use the following keywords to specify the date:
                * yesterday
                * today
                * tomorrow
                Example:
                history today

                4. Specify Event Type
                Choose a specific type of historical event:
                * births
                * deaths
                * events
                Example:
                history births today

                5. Random Day or Month
                If you don't provide a specific day or month, a random one will be used.
                Example:
                history deaths 5
                """,

                "name_day":
                """
                Name Day Plugin Tutorial

                1. Start the Plugin
                Run the command:
                name day

                2. Main Menu
                You will be presented with the following options:
                1 See Today's name days
                2 See Tomorrow's name days
                3 Choose specific date
                4 Choose specific name
                5 Choose another country
                6 Exit

                3. Selecting an Option
                - To see name days for today or tomorrow, select options 1 or 2.
                - To check name days for a specific date, select option 3 and enter the date in "day/month" format.
                - To search for a name day by a specific name, select option 4 and provide the name.
                - To change the country for name days, select option 5 and pick a country from the list.
                - Select option 6 to exit the plugin.

                4. Example Flow
                - Choose option 1 to see today's name days for your current location.
                - Choose option 4 to enter a name and find name days related to that name.

                5. Continue or Exit
                After each action, the plugin will ask if you want to continue. Type 'Y' to continue or 'N' to exit.
                """,

                "weekday":
                """
                1. Start the Plugin
                Run the command:
                day of the week or weekday

                2. Enter a Date
                Provide a date in the dd/mm/yyyy format:
                Example: 21/09/2021

                3. View Weekday
                The plugin will display which weekday the provided date falls on.

                4. Exit
                After displaying the weekday, the plugin will terminate automatically.
                """
            }
        },
        "Investment": {
            "plugins": ["cryptotracker"],
            "descriptions": {
                "cryptotracker": "Track the price and 24-hour price change of cryptocurrency pairs, or check a default list of favorite pairs."
            },
            "tutorials": {
                "cryptotracker":

                """
                CryptoTracker Plugin Tutorial

                1. Start the Plugin
                Run the command:
                cryptotracker

                2. Check Prices for Specific Pair
                Enter a specific crypto pair (e.g., BTC/USDT):
                cryptotracker BTC/USDT

                3. Check Prices for Default Favorites
                To view prices and changes for default favorite pairs, simply run:
                cryptotracker

                4. View Results
                After running the command, you will see the price and percentage change:
                Example output:
                BTC/USDT
                Price: 34000.25
                Change: +2.5%

                5. Handle Errors
                If you enter an invalid pair, you'll see:
                Example:
                Wrong pair BTC/USD! Please use USDT for USD prices.
                """
            }
        },
        "Language": {
            "plugins": ["dictionary"],
            "descriptions": {
                "dictionary": "Look up the meaning, synonyms, and antonyms of any word, and provide additional details if needed."
            },
            "tutorials": {
                "dictionary":
                """
                Dictionary Plugin Tutorial

                1. Start the Plugin
                Run the command:
                dictionary

                2. Input Word
                If no word is provided, the plugin will prompt:
                Enter word: example

                3. Display Meanings
                The plugin will list possible meanings of the word:
                1. A representative form or pattern
                2. Something to be imitated

                4. Display Synonyms and Antonyms
                Synonyms and antonyms of the word are displayed:
                Synonyms: instance, illustration
                Antonyms: non-example

                5. Choose Meaning for Details (Optional)
                Select a meaning for more details (1-N):
                Details of meaning (1-2): 1

                6. View Detailed Meaning
                The plugin provides detailed information on the selected meaning, including synonyms, antonyms, and example usage:
                Meaning  : A representative form or pattern
                Synonyms : instance, illustration
                Antonyms : non-example
                Examples : This painting is an example of surrealism

                7. Repeat or Exit
                You can choose another meaning or leave the plugin by pressing Enter.
                """
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
                "voice":
                """
                1. Enable Sound
                Run the command:
                enable sound
                Jarvis will use a voice engine. Consent for data collection by typing "gtts".

                2. Disable Sound
                Run the command:
                disable sound
                Jarvis will stop using voice output.

                3. Use Google Text-to-Speech (GTTS)
                Run the command:
                gtts
                Jarvis will use Google’s speech engine for voice output.

                4. Disable GTTS
                Run the command:
                disable gtts
                Switch back to the built-in speech engine if GTTS is enabled.

                5. Change Speech Rate
                Run the commands:
                talk faster
                talk slower
                Adjust the speech speed of Jarvis (Linux and Windows only).

                6. Make Jarvis Speak
                Run the command:
                say <message>
                Jarvis will say the message out loud.
                """,

                "voice_control":
                """
                1. Start the Plugin
                Run the command:
                hear

                2. Enter Voice Mode
                Say "listen" to activate voice mode. The system will now listen for commands.

                3. Speak Commands
                After activation, speak any valid command to Jarvis, which will execute it.

                4. Stop Listening
                Say "stop" to end the listening mode.

                5. Handling Errors
                If speech is unclear or not recognized, you will be prompted to try again. No results will be processed from unrecognized speech.
                """
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
            "caesar_cipher":

            """
            Caesar Cipher Plugin Tutorial

            1. Start the Plugin
            Type:
            caesar cipher

            2. Choose an Option
            - 1: Convert plain text to Caesar cipher.
            - 2: Convert Caesar cipher back to plain text.
            - 3: Exit the plugin.

            3. Example Plain to Cipher
            caesar cipher
            Enter your choice: 1
            Enter string to convert: hello
            Output: khoor (displayed in yellow)

            4. Example Cipher to Plain
            caesar cipher
            Enter your choice: 2
            Enter string to convert: khoor
            Output: hello (displayed in yellow)

            5. Shift Details
            - Plain text is shifted by 3 positions to convert to cipher.
            - Cipher text is shifted by -3 positions to convert back to plain text.
            """
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
                "binary":
                """
                Binary Plugin Tutorial

                1. Start the Plugin
                Run the command:
                binary [number]

                If no number is provided, the plugin will prompt you for input.

                2. Example Usage
                binary 10
                Output:
                1010 (displayed in yellow)

                If you provide a negative number:
                binary -10
                Output:
                -1010 (displayed in yellow)

                3. Error Handling
                If the input is not a valid number:
                binary abc
                Output:
                This is no number, right? (displayed in red)
                """,

                "evaluator":
                """
                Calculate Plugin Tutorial

                1. Perform a Calculation
                Run the command:
                calc 3 + 5

                2. Solve an Equation
                Solve an expression or equation:
                solve x**2 + 5*x + 3

                3. Solve a System of Equations
                Input equations and variables:
                equations
                1. Equation: x**2 + 2y - z = 6
                2. Equation: (x-1)(y-1) = 0
                3. Equation: y**2 - x - 10 = y**2 - y

                4. Factor an Expression
                Factor an algebraic expression:
                factor x**2 - y**2

                5. Plot a Graph
                Plot a graph of a function:
                plot x**2

                6. Calculate Limits
                Calculate limits as x approaches infinity or a number:
                limit 1/x
                limit @1 1/(1-x)

                7. Sketch a Curve
                Perform curve sketching analysis:
                curvesketch y=x**2+10x-5
                """,

                "factor":
                """
                Prime Factorization Plugin Tutorial

                1. Enter a Number
                Provide a number to factorize:
                factor
                Enter a number for me to factorize: 56

                2. View Prime Factors
                The prime factors will be displayed:
                2 x 2 x 2 x 7
                """,

                "kaprekar":
                """
                Kaprekar Plugin Tutorial

                1. Check Kaprekar Number
                Run the command:
                kaprekar

                2. Enter a Number
                Input a positive integer to check if it's a Kaprekar number:
                Enter a number: 9

                3. Result Output
                The plugin will return whether the number is a Kaprekar number:
                Yes, kaprekar number
                or
                Not kaprekar number
                """,
                "matrix_add":
                """
                Matrix Addition Plugin Tutorial

                1. Start Matrix Addition
                Run the command:
                matrix add

                2. Set Matrix Dimensions
                Enter the number of rows (M) and columns (N):
                Enter M (rows): 2
                Enter N (cols): 2

                3. Input First Matrix
                Enter each row, separating numbers with spaces:
                enter row #0: 1 2
                enter row #1: 3 4

                4. Add More Matrices
                When asked "Continue with next matrix?", type:
                yes
                Then input the next matrix as before

                5. View Current Sum
                When asked "Print current sum matrix?", type:
                yes

                6. Finish Addition
                To stop adding matrices, type:
                no
                when asked "Continue with next matrix?"

                7. View Final Result
                The final sum matrix will be displayed
                """
            }
        },
        "Utilities": {
            "plugins": ["bulkresize", "create_plugin"],
            "descriptions": {
                "bulkresize": "Resize and optionally renames all images in a directory, tailored for deep learning data preparation.",
                "create_plugin": "Create a plugin for Jarvis."
            },
            "tutorials": {
                "bulkresize":
                """
                Bulk Resizer Plugin Tutorial

                1. Start the Plugin
                Type:
                bulkresizer

                2. Input Image Directory
                - Enter the path to the directory containing the images you want to resize.

                3. Rename Images
                - Choose whether to rename images to non-repeating numbers:
                    - y: Yes
                    - n: No (keep original names)

                4. Output Directory
                - Enter the path to the directory where resized images will be saved.
                - If the output directory does not exist, the plugin will ask if you want to create it.

                5. Target Size
                - Enter the desired size for the images (e.g., 32 for 32x32 pixels).

                6. Example Input
                bulkresizer
                Enter image directory: /path/to/images
                Rename images? (y/n): y
                Enter output directory: /path/to/output
                Target size: 32

                7. Completion
                - Once the resizing process is done, you'll receive confirmation:
                Output: Resizing Completed!! Thank you for using jarvis
                """,

                "create_plugin":
                """
                Create Plugin Tutorial

                1. Start the Plugin
                Type:
                create plugin [plugin name]

                2. Example One-Line Command
                - Create a plugin named "my_cool_plugin":
                create plugin my_cool_plugin

                3. Step-by-Step Usage
                - If no plugin name is provided, you'll be prompted:
                    1. Enter the desired plugin name when aske

                4. Example Step-by-Step
                create plugin
                Please insert the name of your plugin: my_cool_plugin

                5. Plugin Creation Process
                - Checks if the plugin name already exists
                - Creates a new .py file in the Jarvis/custom folder
                - Opens the newly created file in your default text editor

                6. Plugin Template
                - A basic plugin structure is automatically generated
                - Includes necessary imports and a sample function

                7. Next Steps
                - Modify the generated plugin file to add your desired functionality
                - Restart Jarvis to apply changes

                Note: Use lowercase letters, numbers, and underscores for plugin names.
                """
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
                "battery": "",
                "cat_history": "",
                "clear": "",
                "volume": "",
                "whoami": ""
            }
        },
        "File Management": {
            "plugins": ["file_organise"],
            "descriptions": {
                "file_organise": "Organize files in a directory."
            },
            "tutorials": {
                "file_organise": ""
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
                "change_mac": "",
                "curl": "",
                "dns_lookup": "",
                "get_host_info": "",
                "ip": "",
                "wifi_password_getter": ""
            }
        },
        "Tools": {
            "plugins": ["clock", "system_update"],
            "descriptions": {
                "clock": "Display the current time, run a stopwatch, and set a timer with customizable durations.",
                "system_update": "Check for and install system updates."
            },
            "tutorials": {
                "clock": "",
                "system_update": ""
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
