# -*- coding: utf-8 -*-
import Jarvis

global isSpeech
isSpeech = 0

def main():
    if isSpeech:
        """
        Code for audio handler
         """
    else:
        jarvis = Jarvis.Jarvis()
        jarvis.executor()

if __name__ == '__main__':
    main()