"""

A Jarvis plugin for listening music according
to your mood through Spotify's Web Player!
Jarvis asks for your mood and based on your choice it
opens a specific playlist of Spotify that fits
your mood.

"""
import webbrowser
from plugin import plugin
from plugin import require
from colorama import Fore


@require(network=True)
@plugin("mood music")
def open_spotify(jarvis, s):
    jarvis.say("\nHello! What's your mood for today? \n")
    # list that stores the available mood choices
    list_of_moods = ["1.Feel Good Morning",
                     "2.So excited just can't hide it!",
                     "3.Party time",
                     "4.Workout beats",
                     "5.Me, myself and I",
                     "6.Chilled out",
                     "7.Roadtrip",
                     "8.Sunset to Sunrise",
                     "9.Jazz Chills",
                     "10.Back to 90s",
                     "11.Stress Relief",
                     "12.Not my Day,my Week,my Month or even my Year",
                     ]
    # loops for printing the available moods
    for i in range(0, 3):
        jarvis.say(list_of_moods[i], Fore.LIGHTCYAN_EX)
    for i in range(3, 6):
        jarvis.say(list_of_moods[i], Fore.CYAN)
    for i in range(6, 9):
        jarvis.say(list_of_moods[i], Fore.LIGHTMAGENTA_EX)
    for i in range(9, 12):
        jarvis.say(list_of_moods[i], Fore.MAGENTA)
    print()
    stop = False
    while not stop:
        # variable for validating the input mood
        # initialize it as True
        invalid_mood = True
        # loop for validating the input mood
        # input must be integer
        # and in the range of 1-14
        while invalid_mood:
            mood = jarvis.input("Choose your mood (1-12): ")
            print()
            try:
                int_mood = int(mood)
                if int_mood < 1 or int_mood > 12:
                    print("Sorry invalid input was given! "
                          "Please enter a valid one!(1-12)")
                else:
                    invalid_mood = False
            except ValueError:
                invalid_mood = True
                print("Sorry invalid input was given! "
                      "Please enter a valid one!(1-12)")

        # variable containing the main url
        # of a Spotify's playlist
        url = "https://open.spotify.com/playlist/"
        # dictionary for storing the urls based on every mood
        # url is defined by the main url
        # plus the unique ending of each url
        url_dict = {"1": url + "3IBrsav3Sh8AImtaGoaP07",
                    "2": url + "37i9dQZF1DWSf2RDTDayIx",
                    "3": url + "4MKC0zUOwvz5gGfKX93LV1",
                    "4": url + "190wZ2oVo7MTrBvNlPiub2",
                    "5": url + "37i9dQZF1DWZLcGGC0HJbc",
                    "6": url + "37i9dQZF1DX889U0CL85jj",
                    "7": url + "0l0a4uSRYz0VWnt38VAEzR",
                    "8": url + "0Au3b2NB5uz8Iwwx5sl6K5",
                    "9": url + "37i9dQZF1DX0SM0LYsmbMT",
                    "10": url + "37i9dQZF1DXbTxeAdrVG2l",
                    "11": url + "37i9dQZF1DWXe9gFZP0gtP",
                    "12": url + "3c0Nv5CY6TIaRszlTZbUFk",
                    }
        # opens the Spotify Web Player
        webbrowser.open(url_dict[mood])
        jarvis.say("Changed your mood?")
        answer = jarvis.input("Type anything to continue or No to exit: ")
        print()
        if answer.upper() == "NO":
            stop = True
