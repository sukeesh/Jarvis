# There needs to be a binary named 'stockfish' in the PATH for this to work.

import os
from plugin import plugin
from stockfish import Stockfish


@plugin('chess')
class Chess():
    def __call__(self, jarvis, s):
        fish = Stockfish()
        while (True):
            jarvis.say("Choose your option:")
            jarvis.say("1. Moves")
            jarvis.say("2. FEN")
            option = jarvis.input("Choice: ")
            if (option == '1'):
                moves = jarvis.input("Moves: ")
                print(moves.split())
                fish.set_position(moves.split())
                jarvis.say(fish.get_best_move())
            elif (option == '2'):
                fen = jarvis.input("FEN: ")
                if (fish.is_fen_valid(fen)):
                    fish.set_fen_position(fen)
                    jarvis.say(fish.get_best_move())
            else:
                jarvis.say("Invalid option\n")
