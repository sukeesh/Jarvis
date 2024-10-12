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
            "plugins": ["workout", "bmi"],
            "descriptions": {
                "workout": "Customized push-up and pull-up workout plans based on user's fitness level.",
                "bmi": "Calculate your Body Mass Index (BMI)."
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
                """,

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
                """
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
                "hash": """
Hash Plugin Tutorial
 
1. Start the Hash Process
Run the command:
hash

2. Choose Input Type
Decide whether to hash a string or a file:
Do you want to hash a string or a file? (Enter 'string' or 'file'): string

3. Choose Hash Function
Enter the desired hash function (e.g., md5, sha1, sha256):
Enter the hash function (md5, sha1, sha256, etc.): sha256

4. Hash a String (if chosen)
Provide the string you want to hash:
Enter the string to hash: example_string

5. Hash a File (if chosen)
Provide the file path for the file to be hashed:
Enter the path to the file: /path/to/file.txt

6. View the Hashed Result
The hashed result will be displayed after processing.
 """,
                "hex": """
Hex Plugin Tutorial

1. Invoke the Plugin
Run the command:
hex

2. Input a Number
If no number is provided, you will be prompted:
What's your number?

3. Enter an Integer
Provide a valid integer. Example input:
255

4. View Result
The output will display the hexadecimal representation:
FF
(If the number is negative, it will show as -FF)

5. Error Handling
If the input is not a valid number, you will see:
That's not a number!
""",
                "length_conv": """
Length Converter Plugin Tutorial

1. Start the Length Converter
   Command: lengthconv

2. Supported Units
   The following length units are supported for conversion:
   nm   : nanometer
   mum  : micrometer
   mm   : millimeter
   cm   : centimeter
   dm   : decimeter
   m    : meter
   km   : kilometer
   mi   : mile
   yd   : yard
   ft   : foot
   in   : inch

3. Enter Conversion Details
   - Enter the amount to convert.
   - Enter the unit of the value to convert from.
   - Enter the unit to convert to.

4. Precision
   If the result is not an integer, specify the precision (max 12).

5. Example Usage
   - Enter an amount: 1000
   - Enter from which unit: mm
   - Enter to which unit: cm
   - Output: 1000 millimeters is equal to 100 centimeters

6. Invalid Input
   If an invalid unit or the same units are entered for conversion, the plugin will prompt to enter valid or different units.
                """,
                "massconv": """
Mass Converter Plugin Tutorial

1. Start the Mass Converter
   Run the command:
   massconv

2. Enter Amount
   When prompted, input the amount you want to convert:
   Enter an amount: 100

3. Specify Source Unit
   Enter the unit you're converting from (short or full name):
   Enter from which unit: kg (or use 'kilogram')

4. Specify Target Unit
   Enter the unit you're converting to (short or full name):
   Enter to which unit: lb (or use 'pound')

5. Set Precision (Optional)
   If result isn't a whole number, you'll be asked for precision:
   Please enter precision (max:12): 2

6. View Result
   The converted amount will be displayed:
   100 kilograms is equal to 220.46 pounds

Supported Units:
mcg (microgram), mg (milligram), g (gram), kg (kilogram),
t (tonne), oz (ounce), lb (pound), st (stone), cwt (hundredweight)
                """,
                "mips": """
MIPS Plugin Tutorial

1. Convert Assembly to Machine Code:
   mips <assembly instruction>

   Example:
   mips Addi $t2, $t1, 0x12

2. Convert Machine Code to Assembly:
   mips <8-digit hex code>

   Example:
   21490012

3. Formatting Tips:
   - Use spaces between instruction parts
   - Separate registers with commas
   - Use $ before register names
   - Use 0x prefix for hex values

4. Supported Instructions:
   - R-type: ADD, ADDU, AND, JR, NOR, OR, SLT, SLTU, SLL, SRL, SUB, SUBU
   - I-type: ADDI, ADDIU, ANDI, BEQ, BNE, LW, ORI, SLTI, SLTIU, SW
   - J-type: J, JAL

5. Register Names:
   $zero, $at, $v0-$v1, $a0-$a3, $t0-$t7, $s0-$s7, $t8-$t9, $k0-$k1, $gp, $sp, $fp, $ra

6. Examples:
   Assembly to Machine Code:
   mips ADD $t0, $s1, $s2

   Machine Code to Assembly:
   mips 02324020
                """,
                "morse_code": """
Morse Code Translator Plugin Tutorial

1. Start Morse Code Translator
   Run the command:
   morsecode

2. Choose Operation
   Enter 1 for encoding or 2 for decoding

3. Enter Text
   For encoding: Enter text using A-Z, 0-9, and some punctuation
   For decoding: Use '.' for dot, '-' for dash, space between letters, '|' between words

4. View Result
   The plugin will display the translated text

Example:
Encoding: HELLO WORLD
Decoding: .... . .-.. .-.. --- | .-- --- .-. .-.. -..
                """,
                "natoalphabet": """
NATO Alphabet Plugin Tutorial

1. Start the Plugin
   Run the command:
   natoalphabet

2. Enter a Word
   You can either provide a word immediately after the command or input it when prompted.
   Example: natoalphabet hello

3. View Results
   The plugin will return the NATO phonetic alphabet equivalent for each letter in the word.
   Example Output:
   h - hotel
   e - echo
   l - lima
   l - lima
   o - oscar

                """,
                "qr_generator": """
QR Code Generator Plugin

1. Start QR Generation
   Run the command:
   qr

2. Enter URL
   Input the URL you want to generate a QR code for:
   Example: https://github.com/sukeesh/Jarvis

3. Specify Filepath
   Enter the path where the QR code image will be saved:
   Example: C:/Users/Public/Downloads

4. Name the File
   Provide a name for the QR image file:
   Example: jarvis_qr

5. Result
   Your QR code will be saved as a PNG file in the specified directory. 

                """,
                "speed_conv": """
Speed Converter Plugin Tutorial

1. Start the Speed Converter
   Command: speedconv

2. Supported Units
   The following speed units are supported:
   m/s  : meter per second
   km/h : kilometer per hour
   ft/s : foot per second
   mi/h : miles per hour
   kn   : knot
   Use the abbreviated forms for input.

3. Enter Value to Convert
   Input the speed value to convert:
   value to convert: 50

4. Enter Original Unit
   Enter the speed unit of the value:
   from which unit: km/h

5. Enter Target Unit
   Enter the speed unit to convert to:
   to which unit: m/s

6. Conversion Result
   The converted value will be displayed:
   Example output:
   13.888889
                """,
                "temp_conv": """
Temperature Converter Plugin Tutorial

1. Start the Temperature Converter
   Command: tempconv

2. Supported Conversion
   Convert between Fahrenheit and Celsius:
   - To convert Fahrenheit to Celsius, append 'F' or 'f' to the value (e.g., 32f, -20F).
   - To convert Celsius to Fahrenheit, append 'C' or 'c' to the value (e.g., 18C, -8c).

3. Example Usage
   - Enter a temperature: 32f
   - Output: 32.0° F is 0.0° C

   - Enter a temperature: 18C
   - Output: 18.0° C is 64.4° F

4. Invalid Input
   If an invalid input is provided, the plugin will prompt:
   "I'm sorry, invalid input. Please see 'help tempconv' for syntax."
"""
            }
        },
        "File Operations": {
            "plugins": ["imgcompressor", "imgtopdf"],
            "descriptions": {
                "imgcompressor": "Compress image files.",
                "imgtopdf": "Converts single or multiple images into a PDF file."
            },
            "tutorials": {
                "imgcompressor": """
Image Compressor Plugin Tutorial

1. Start the Image Compressor
   Run the command:
   image compressor

2. Choose Compression Option
   You will be prompted to choose:
   1: Compress a single image
   2: Compress all images in a folder
   3: Quit

3. Compress a Single Image
   If you choose option 1, you will be asked to enter the full path of the image:
   Enter the full path of the image: /path/to/your/image.jpg

4. Compress Multiple Images in a Folder
   If you choose option 2, you will be asked to enter the full path of a folder:
   Enter the full path of a folder: /path/to/your/folder

5. Set Compression Quality
   For both single and multiple images, you will be prompted to enter a quality value:
   Enter desired quality of compression (0-100 where 100 is maximum compression): 85

6. Compressed Image Output
   The compressed images will be saved in the same directory with a prefix "compressed_".

7. Quit the Plugin
   To quit the plugin, choose option 3 or type 'q' or 'quit'.

                """,
                "imgtopdf": """
Image to PDF Plugin Tutorial

1. Start Image to PDF Conversion
   Run the command:
   image to pdf

2. Select Conversion Option
   Choose one of the following options:
   1: Convert a single image
   2: Convert all images in a folder
   3: Quit

3. Convert a Single Image
   Enter the full path of the image you want to convert:
   Enter the full path of the image: /path/to/image.jpg

4. Convert Multiple Images in a Folder
   Enter the full path of the folder containing images:
   Enter the full path of the folder: /path/to/folder

5. Save PDF
   After conversion, choose where to save the PDF file:
   What would you like to name your pdf? myfile
   Final Destination: /path/to/save/myfile.pdf

6. Completion Message
   Once the PDF is created successfully, you will see:
   Your pdf is created successfully

"""
            }
        },
        "Random Generator": {
            "plugins": ["random_password"],
            "descriptions": {
                "random_password": "Generate secure random passwords."
            },
            "tutorials": {
                "random_password": """
1. Generate Random Password
   Run the command:
   random password
   Generate a secure random password with customizable length and characters.

2. Enter Password Length
   Input the desired length of the password:
   Enter password length: 12

3. Special Characters Option
   Choose whether to include special characters:
   Do you want special characters?(y/n): y

4. Result
   Get your randomly generated password:
   Example output:
   Your random password is: aB3!kT9#L1x

"""
            }
        },
        "Reminder": {
            "plugins": ["reminder"],
            "descriptions": {
                "reminder": "Set reminders for important tasks or events."
            },
            "tutorials": {
                "reminder": """
Todo and Remind Plugin Tutorial

1. List Todos
   Run the command:
   todo

2. Add a Todo
   Run the command:
   todo add buy groceries

3. Set Progress on a Todo
   Run the command:
   todo progress
   Select a todo from the list
   Enter progress (0-100): 50

4. Add a Tag to a Todo
   Run the command:
   todo tag
   Select a todo from the list
   Select a tag to add

5. Filter Todos by Tag
   Run the command:
   todo filter
   Select a tag to filter by

6. Create a Reminder
   For a specific time:
   remind at 18:00 to cook dinner

   For a duration:
   remind in 1 hour to take a break

7. List Reminders
   Run the command:
   remind

8. Remove a Todo or Reminder
   For todos:
   todo remove

   For reminders:
   remind remove

9. Manage Tags
   List tags:
   tags

   Create a new tag:
   tags new work

   Remove a tag:
   tags remove
"""
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
                "tasks": """
Task Manager Plugin Tutorial

1. Start the Task Manager
   Command: tasks

2. Available Options
   After starting the plugin, choose one of the following options:
   1. List All My Tasks
      - View all tasks currently in the task list.
   2. Add New Task
      - Add a new task to your list.
   3. Edit Existing Task
      - Update the name of an existing task.
   4. Delete Task
      - Remove a task from your list.
   5. Add Priority to Task
      - Set priority for a task (High, Medium, Low).
   6. Sort
      - Sort tasks by name or by priority.
   7. Exit
      - Exit the Task Manager.

3. Task Priority
   - You can add priority to a task: High, Medium, or Low.
   - Tasks are displayed in different colors based on priority (Red for High, Yellow for Medium, Green for Low).

4. Example Usage
   1. To add a new task, select option 2.
   2. Enter the name of the new task.
   3. To add priority, select option 5 and choose the task.
   4. To list all tasks, select option 1.
                """,
                "timeconv": """
1. Convert Time Units
   Run the command:
   timeconv
   Convert between different time units such as seconds, minutes, hours, and more.

2. Enter Amount
   Input the amount of time to convert:
   Enter an amount: 1000

3. Choose Source Unit
   Input the time unit of the amount:
   Enter from which unit: s

4. Choose Target Unit
   Input the time unit to convert to:
   Enter to which unit: min

5. Result
   Get the converted result with precision options.
   Example output:
   1000 seconds is equal to 16.6667 minutes
                
                """,
                "website_status": """
1. Start the Plugin
   Run the command:
   website status

2. Enter Website URL
   Input the website URL to check its status:
   Example: www.example.com

3. View Status Code
   The plugin will display the HTTP status code for the entered URL.

4. Error Handling
   If an error occurs, you can choose to try again or exit by typing 'y' or 'n'.

5. Exit
   After checking the website status or exiting, the plugin will terminate automatically.

                """,
                "write_agenda": """
1. Write an Event to the Agenda
   Run the command:
   write agenda

2. Input Event Details
   Enter the required details as prompted:
   - Event Date (e.g., 2021-09-21)
   - Event Time (e.g., 13:00)
   - Event Place
   - Event Title
   - Event Description

3. Add More Events
   You will be asked if you'd like to add another event:
   Would you like to add anything more? (y/n)

4. Save the Event
   After you finish adding events, they will be saved to `agenda.csv`.

5. Read the Agenda
   Run the command:
   read agenda
   The list of all saved events will be displayed.

"""
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
