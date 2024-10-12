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
                "blackjack":
                    """
                    Blackjack Plugin Tutorial
                    
                    1. Start the Game
                       Type:
                       blackjack
                    
                    2. Game Setup
                       - The game will ask for your bet.
                       - Two cards will be dealt to you and the dealer.
                    
                    3. Player Actions
                       - You will see your hand and its sum. You can choose to:
                         - Hit (H): Get another card.
                         - Stand (S): Keep your hand.
                         - Double Down (D): Double your bet and get one final card.
                         - Split (P): Split your hand into two if you have identical cards.
                    
                    4. Dealer’s Turn
                       - The dealer will play after your turn, drawing cards until they reach 17 or more.
                    
                    5. Results & Profit
                       - Compare hands with the dealer. Profit or loss will be calculated based on your bets.
                    
                    6. Example Gameplay
                       blackjack
                       How much are you betting? 50
                       Your cards: ['5 of hearts', '6 of spades']
                       Dealer hand: ['9 of diamonds', 'hidden']
                       Press H to Hit, S to Stand, D to Double-Down, P to Split: H
                       Newcard is 10 of hearts
                       Updated hand: ['5 of hearts', '6 of spades', '10 of hearts']
                    """
                ,
                "coin_flip":
                    """
                    Coin Flip Plugin Tutorial
                    
                    1. Usage
                       Type:
                       coin flip
                    
                    2. Function
                       Randomly outputs either "Heads" or "Tails"
                    
                    3. Example
                       Input: coin flip
                       Output: Heads
                    
                       Input: coin flip
                       Output: Tails
                    
                    4. Notes
                       - No additional arguments needed
                       - Each execution gives a 50/50 chance of Heads or Tails
                    """,
                "connect_four":
                    """
                    Connect Four Plugin Tutorial
                    
                    1. Start the Game
                       Type:
                       connect_four
                    
                    2. Gameplay
                       - Two players take turns
                       - Choose a column (1-7) to drop your token
                       - First to connect four tokens horizontally, vertically, or diagonally wins
                    
                    3. Commands
                       - Enter a number (1-7) to place your token
                       - 'Y' to play again after a game ends
                       - 'N' to quit after a game ends
                    
                    4. Tips
                       - Plan ahead to block your opponent
                       - Try to create multiple winning opportunities
                       - Watch for diagonal connections
                    
                    5. Example Game Flow
                       connect_four
                       Pick a column (1-7):
                       3
                       [Game board displays]
                       Pick a column (1-7):
                       4
                       [Game continues until win or tie]
                       Would you like to play again? (Y/N)
                       Y
                       [New game starts]
                    
                    6. Error Handling
                       - Invalid column: "Out of bounds. Pick another column."
                       - Full column: "Column is full. Pick another."
                       - Non-numeric input: "Enter a valid numeric input."
                                """
                ,
                "guess_number_game":
                    """
                    Guess Number Game Plugin Tutorial
                    
                    1. Start the Game
                       Run the command:
                       guess_number_game
                    
                    2. Game Introduction
                       Jarvis will introduce the rules and start the game.
                    
                    3. Choose Difficulty Mode
                       Select between Hard (6 lives) or Normal (8 lives):
                       Choose mode: Hard(6 lives) or Normal(8 lives)
                    
                    4. Guess the Number
                       Input a number between 1 and 100:
                       give me a number between(1-100): 50
                    
                    5. Feedback
                       Jarvis will inform you if the number is bigger or smaller:
                       The number that I am thinking is smaller than the one you guessed
                    
                    6. Continue Guessing
                       Keep guessing until you find the correct number or run out of lives:
                       make the next guess (lives: 5)
                    
                    7. Game Over
                       If you guess the correct number, Jarvis will congratulate you. If you run out of lives, the game will end.
                    """
                ,
                "hangman":
                    """
                    Hangman Plugin Tutorial
                    
                    1. Start the Game
                       Run the command:
                       hangman
                    
                    2. Game Objective
                       The goal is to guess the word by inputting one letter at a time.
                    
                    3. Input Guess
                       Enter a letter:
                       Enter Your Guess: a
                    
                    4. Stop the Game
                       Type 'stop' to end the game:
                       Enter Your Guess: stop
                    
                    5. Lose a Life
                       Enter an incorrect guess or repeat a letter:
                       Woops! You Have Entered Wrong Guess
                       Lives Decrease By 1, Remaining Lives: 7
                    
                    6. Winning the Game
                       Successfully guess all letters of the word:
                       You Won!
                    
                    7. Losing the Game
                       If you run out of lives, the game ends:
                       You Lost!
                    
                    8. Play Again
                       After finishing, you can choose to play again or quit:
                       Do You Want To Play Again? (Y/N)            
                    """
                ,
                "magic_8_ball":
                    """
                    Magic 8 Ball Plugin Tutorial
                    
                    1. Start the Magic 8 Ball
                       Run the command:
                       magic8ball
                    
                    2. Ask a Question
                       When prompted, type your question:
                       => Will I have a good day today?
                    
                    3. Receive an Answer
                       The Magic 8 Ball will display an ASCII art and provide a random answer:
                       [ASCII Art of Magic 8 Ball]
                       It is certain.
                    
                    4. Continue or Quit
                       You'll be asked if you have more questions:
                       => Do you have any further inquiries you wish to input?
                    
                       To ask another question, type:
                       yes
                    
                       To exit, type anything else or 'quit'
                    
                    5. Exit Message
                       When you're done, you'll see a random exit message:
                       May the gods shine upon you.
                    """
                ,
                "memory":
                    """
                    Memory Trainer Plugin Tutorial
                    
                    1. Start Memory Trainer
                       Run the command:
                       memory
                    
                    2. Start the Game
                       When asked "Are you ready to play?", type:
                       1
                    
                    3. Remember the Number
                       A number will be displayed briefly
                    
                    4. Guess the Number
                       Type your guess when prompted:
                       Type your guess: 123
                    
                    5. Continue Playing
                       If correct, a new number with one more digit will be shown
                       If incorrect, the game ends
                    
                    6. View Score
                       Your score (number of digits remembered) is shown when you make a mistake
                    """
                ,
                "rockpaperscissors":
                    """
                    Rock Paper Scissors Plugin Tutorial
                    
                    1. Start the Game
                       Run the command:
                       rockpaperscissors
                    
                    2. Enter Number of Rounds
                       Specify how many rounds you want to play (max. 100):
                       Enter how many rounds you will play (max. 100): 5
                    
                    3. Make Your Move
                       Input your move for each round:
                       'r' for rock
                       'p' for paper
                       's' for scissors
                       To end the game early, type 'exit'.
                       To view the current score, type 'score'.
                       To see the current round, type 'rounds'.
                       Example input:
                       Enter your move: r
                    
                    4. Jarvis Makes a Move
                       Jarvis will also make a move, and the winner of the round will be announced.
                    
                    5. Game End
                       After all rounds are played or you choose to exit, the game ends, displaying the final score.
                       Example output:
                       YOU: 3  JARVIS: 2
                       YOU WIN!!
                    """
                ,
                "roulette":
                    """
                    Roulette Plugin Tutorial
                    
                    1. Start the Game
                       Launch the roulette game:
                       roulette
                    
                    2. Welcome and Starting Cash
                       You begin with a cash balance of $100.
                    
                    3. Choose a Bet Type
                       Choose from the following betting options:
                       1. Bet on a specific number (win: 36x)
                       2. Bet on RED/BLACK (win: 2x)
                       3. Bet on ODD/EVEN (win: 2x)
                       4. Bet on ranges (1-12, 13-24, 25-36) (win: 3x)
                       5. Bet on ranges (1-18, 19-36) (win: 2x)
                       6. Exit the game
                       Enter your choice: 1-6
                    
                    4. Enter Bet Details
                       Depending on your chosen bet:
                       - If you select a specific number, enter a number between 0 and 36.
                       - If you select RED/BLACK, ODD/EVEN, or a range, make your choice accordingly.
                       - Enter the amount you want to bet (must be within your available cash balance).
                    
                    5. Spin the Roulette
                       Press Enter to spin the roulette wheel. The result will be displayed, showing whether you won or lost the bet.
                    
                    6. Game Progress
                       Your current cash balance will be updated after each round.
                       Continue playing by selecting new bets until you decide to exit or run out of cash.
                    
                    7. End Game
                       Choose option 6 to exit the game, and your final cash balance will be displayed.
                    
                    Example gameplay:
                    1. Enter bet type: 2 (RED/BLACK)
                    2. Enter your choice: 1 (RED)
                    3. Enter bet amount: 20
                    4. Press Enter to spin the roulette
                    5. Result: 18 (RED) - WIN
                    """
                ,
                "spinthewheel":
                    """
                    Spin Wheel Plugin Tutorial
                    
                    1. Start the Spin Wheel
                       Command: spinwheel
                    
                    2. Enter Number of Elements
                       Specify how many elements will be on the wheel:
                       enter the number of elements in the wheel: 4
                    
                    3. Enter Elements
                       Enter each element one by one:
                       Example:
                       - pizza
                       - burger
                       - pasta
                       - salad
                    
                    4. Spin the Wheel
                       The wheel will spin, and a graphical wheel will appear showing the selected element.
                    
                    5. Spin Again (Optional)
                       You can spin the wheel again by pressing 'y', or end the session by pressing any other key.
                    
                    6. End Game
                       Thank you message will be displayed when the game is complete.
                    
                    Example:
                    Do you want to spin again?? press: y
                    """
                ,
                "tic_tac_toe":
                    """
                    Tic Tac Toe Plugin Tutorial
                    
                    1. Start the Game
                       Command: tic_tac_toe
                    
                    2. Game Modes
                       After starting the game, choose one of the following modes:
                       1. Play against Jarvis.
                       2. Play against a friend (two players).
                    
                    3. Board Layout
                       The board layout is as follows:
                       7 | 8 | 9
                       -----------
                       4 | 5 | 6
                       -----------
                       1 | 2 | 3
                    
                    4. How to Play
                       - Player X goes first, followed by Player O.
                       - Input a number (1-9) corresponding to the board position to place your piece.
                       - For single-player mode, Jarvis will make its move after the user.
                    
                    5. Winning the Game
                       - The game ends when a player gets three pieces in a row (horizontally, vertically, or diagonally).
                       - If all nine positions are filled without a winner, the game is declared a draw.
                    
                    6. Example Gameplay
                       - X turn. Choose a position: 5
                       - O turn. Choose a position: 1
                       - Jarvis will make its move automatically in single-player mode.
                    """
                ,
                "wordgame":
                    """
                    1. Start the Game
                       Run the command:
                       word_game
                    
                    2. Set Game Options
                       Enter the number of seconds to answer:
                       Give how many seconds: (e.g., 10)
                       Enter the number of rounds:
                       Number of rounds: (e.g., 5)
                    
                    3. Begin the Game
                       Enter your first word:
                       Give a word: (e.g., apple)
                    
                    4. Continue Playing
                       Jarvis will give a word starting with the last letter of your word:
                       Jarvis' answer is: eagle
                       You must then provide a word starting with the last letter of Jarvis' word.
                    
                    5. Win or Lose
                       If you win all rounds or lose by mistake or timeout, the game ends.
                    
                    6. Play Again
                       If you wish to play again, type 'Y'. To exit, type 'N'.
                    """
                ,
                "wordle":
                    """
                    1. Start the Game
                       Run the command:
                       wordle
                    
                    2. Guess the Word
                       You have 6 attempts to guess a 5-letter word:
                       Enter Guess #1: (e.g., apple)
                    
                    3. Get Feedback
                       Letters will be colored:
                       Green: Correct letter and position
                       Yellow: Correct letter but wrong position
                       White: Incorrect letter
                    
                    4. Continue Guessing
                       Repeat until you guess the word or run out of attempts.
                    
                    5. Quit Anytime
                       Type 'q' to quit the game.
                    """
            }
        },
        "Media": {
            "plugins": ["mood_music"],
            "descriptions": {
                "mood_music": "Get music recommendations based on your mood."
            },
            "tutorials": {
                "mood_music":
                    """
                    Mood Music Plugin Tutorial
                    
                    1. Start Mood Music
                       Run the command:
                       mood music
                    
                    2. View Mood Options
                       The plugin will display 12 mood options
                    
                    3. Select Mood
                       Enter a number between 1-12 corresponding to your mood
                    
                    4. Open Spotify Playlist
                       A Spotify playlist matching your mood will open in your web browser
                    
                    5. Continue or Exit
                       Type 'NO' to exit, or anything else to choose another mood
                    """
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
