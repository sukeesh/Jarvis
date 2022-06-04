
from plugin import plugin,require
from colorama import Fore
import requests
import os
import re


@require(network=True)
@plugin("qr")

class QRGenerator:
    """
    Provides you with a png image of a QR for a specified URL

    Enter 'qr' or 'QR' to use:
    

    Attribution:
        QR generated from https://goqr.me/api/
    """
    
    def __init__(self):
        self.url = "http://api.qrserver.com/v1/create-qr-code/"
    

    def __call__(self,jarvis,s):
        if s == 'help':
            self._print_help(jarvis)
            return

        jarvis.say("\ntype 'qr  help' for additional information")
        jarvis.say("")

        prompt_url = ("\nType the URL that you want to create a QR code \n" 
                      "or 'end' if you wish to exit: ")
        # get url from user prompt
        url = self._get_url(prompt_url,jarvis)
        if url == "end":
            return
        jarvis.say("")

        prompt_path = ("\nType the filepath where you want the QR to be stored \n"
                       "or 'end' if you wish to exit: ")
        # get path from user prompt
        self.path = self._get_path(prompt_path,jarvis)
        if self.path == "end":
            return
        jarvis.say("")

        prompt_name = ("\nEnter the name of the png file that will be created: ")
        # get filename from user prompt
        name = jarvis.input(prompt_name,Fore.CYAN)
        # replace whitespaces with underscores
        name = name.strip().replace(' ', '_')
        self.filename = re.sub(r'(?u)[^-\w.]', '', name)
        # generate query and add the needed parameters 
        query = self.url + "?data=" + url + "&size=250x250"
        # generate QR code from the query
        self._generate_qr(jarvis,query)

        return
    


    def _get_url(self, prompt, jarvis):
        """
        checks if the URL the user gave is in valid form(can be reached).
        The user can type 'end' to exit in case his URL is continuously rejected.
        The method covers the basic exceptions created by invalid URLs.
        """

        while True:
            try:
                response = jarvis.input(prompt,Fore.CYAN)
                # the user wants to exit
                if response == "end":
                    break
                # tries to get website from URL 
                website = requests.get(response)
                break
            # list of possible exceptions from URLs with invalid form
            except requests.exceptions.MissingSchema:
                jarvis.say("\nSorry, your input URL is not valid.",Fore.RED)
                jarvis.say("Try something in this form 'https://github.com/.../...'")
            # handles the exception where the user misses part of the 'http' part of the URL
            except requests.exceptions.InvalidSchema:
                jarvis.say("\nSorry, your input URL is not valid.",Fore.RED)
                jarvis.say("Try something in this form 'https://github.com/.../...'")
            except requests.exceptions.ConnectionError:
                jarvis.say("\nSorry, your input URL is not valid.",Fore.RED)
                jarvis.say("Try something in this form 'https://github.com/.../...'")
            except requests.exceptions.InvalidURL:
                jarvis.say("\nSorry, your input URL is not valid.",Fore.RED)
                jarvis.say("Try something in this form 'https://github.com/.../...'")
                
        return response
    

    def _get_path(self, prompt, jarvis):
        """
        checks if the path the user gave is valid(directory exists on the computer).
        The user can type 'end' to exit in case his path is continuously rejected.
        """

        while True:
            path = jarvis.input(prompt,Fore.CYAN)
            # the user wants to exit
            if path == "end":
                response = path
                break
            isFile = os.path.isdir(path)
            # directory exists
            if isFile:
                response = path
                break
            jarvis.say("\nSorry, the path that you specified couldn't be found",Fore.RED)
            jarvis.say("Try something in this form 'C:\..\..' if you are using Windows for example.")
            
        return response
    

    def _generate_qr(self, jarvis, query):
        try:
            # send request
            jarvis.spinner_start('Creating QR ')
            response = requests.get(query)
            # where the png file will be stored
            location = os.path.join(self.path,self.filename + '.png')
            file = open(location, "wb")
            file.write(response.content)
            jarvis.spinner_stop()
            file.close
        except BaseException:
            jarvis.spinner_stop(
            message="\nTask execution Failed!", color=Fore.RED)
            jarvis.say(
                "Please check that the URL you have entered is valid!", Fore.RED)
            jarvis.say(
                "If error occures again, then API might have crashed. Try again later.\n", Fore.RED)
        finally:
            return 

        

    # manual for plugin
    def _print_help(self, jarvis):
        jarvis.say("\nWelcome to QR Generator!", Fore.CYAN)
        jarvis.say("You can use current plugin as follows:", Fore.CYAN)
        jarvis.say("    'qr' or 'QR' ", Fore.CYAN)
        jarvis.say(    
            "Result: The user receives a png image containing a QR.", Fore.CYAN)
        jarvis.say(    
            "        The QR code leads to the URL the user specified, and it is stored on a directory of his choice!", Fore.CYAN)
        jarvis.say("\nExample: ", Fore.CYAN)
        jarvis.say(
            "         'qr' - initial call ", Fore.CYAN)
        jarvis.say(
            "         'https://github.com/sukeesh/Jarvis' - valid URL or type 'end' to exit ", Fore.CYAN)
        jarvis.say(
            "         'C:\\Users\\Public\\Downloads' -  valid file location or type 'end' to exit ", Fore.CYAN)
        jarvis.say(
            "         'jarvis_qr' - name of the png file ", Fore.CYAN)
        jarvis.say(
            "The steps above create a QR code on the specified directory that leads to Jarvi's central page on GitHub!", Fore.CYAN)

    