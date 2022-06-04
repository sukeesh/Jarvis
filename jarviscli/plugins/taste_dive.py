
from plugin import plugin,require
from colorama import Fore
import requests
import textwrap
 

@require(network=True)
@plugin("taste dive")
class TasteDive:
    """
    Provides you with a list of suggestions depending on your taste

    Enter 'taste dive' to use:
    * taste dive <argument>

    Attribution:
        Data provided from https://tastedive.com
    """
    
    def __init__(self):
        self.url = "https://tastedive.com/api/similar"
    
    
    def __call__(self,jarvis, s):
        if s == 'help':
            self._print_help(jarvis)
            return
        
        jarvis.say("\ntype 'taste dive  help' for additional information")
        
        # add the parameter for the query using the user's prompt
        query = self.url + "?q=" + s
        # add the parameter for additional info
        query = query + "&info=1"
        # the list with the suggestions is returned
        # including the whole json file for any additional information the user needs
        result,json_file = self._get_data(jarvis, query)
        
        # no suggestions found for the user's argument
        if  not result:
            jarvis.say("")
            jarvis.say("I couldn't find any suggestions for your input.Try something else!",Fore.CYAN)
            return
        
        # output data
        jarvis.say("")
        jarvis.say("You should definetely try:")
        for suggestion in result:
            jarvis.say(suggestion, Fore.CYAN)
        
        jarvis.say("")
        # dialog option for additional ifnormation about a specific suggestion
        prompt_info = 'Press 1 to get info about a specific suggestion \n or 0 to exit : '
        # makes sure that the user prompt is either 0 or 1
        user_input = self._get_input(prompt_info,jarvis)
        
        # no additional information
        if user_input == 0:
            return
        else:
            prompt_suggestion = 'Type the name of the suggestion that you would like to get information:'
            # makes sure that the user prompt is included in the returned list 
            # and displays the additional information
            self._get_info(jarvis,prompt_suggestion,json_file)
            



    def _get_input(self, prompt, jarvis):
        """
        checks if the input the user gave is valid(either 0 or 1)
        """

        while True:
            try:
                response = int(jarvis.input(prompt))
                jarvis.say('')
            except ValueError:
                jarvis.say("\nSorry, I didn't understand that.")
                continue

            if (response != 0) and (response != 1):
                jarvis.say("\nSorry, your response is not valid.")
                continue
            else:
                break
        return response
    
    
    
    def _get_suggestion(self, prompt,result, jarvis):
        """
        checks if the input the user gave is valid(it is included in the list with the suggestions)
        else, the user can type end to exit the process of additional information 
        """
        
        found = None
        while True:
            try:
                
                response = jarvis.input(prompt)
                jarvis.say('')
            except ValueError:
                jarvis.say("\nSorry, I didn't understand that.")
                continue
            
            if response == "end":
                return found
            for s in result:
                if s["Name"]==response:
                    found = s
                    return found
            if found is None and response!=exit:
                jarvis.say("\nSorry, your response is not valid. Try typing the name of the suggestion as it is displayed above!" 
                           "\n or type end to exit ",Fore.RED)
                continue
         

    
    # send request and retrieves data from API
    def _get_data(self, jarvis, query):
        data = []
        try:
            # send request
            jarvis.spinner_start('Searching suggestions ')
            response = requests.get(query)
            # parse into json
            result = response.json()
            # gets the value of "Similar"
            general = result["Similar"]
            # uses the value of "Similar" to get the value of "Results"
            re = general["Results"]
            # generate data from result by only taking the name from each suggestion
            for suggestion in re:
                data.append( suggestion["Name"])
            jarvis.spinner_stop()
        except BaseException:
            jarvis.spinner_stop(
            message="\nTask execution Failed!", color=Fore.RED)
            jarvis.say(
                "Please check that the argument you have entered is valid!", Fore.RED)
            jarvis.say(
                "If error occures again, then API might have crashed. Try again later.\n", Fore.RED)
        finally:
            # return a list with suggestions and the json file with the additional information
            return data,result



    # gets additional information for a specific suggestion
    def _get_info(self,jarvis,suggestion,file):
        # gets the value of "Similar" from the json file
        general = file["Similar"]
        # uses the value of "Similar" to get the value of "Results"
        re = general["Results"]
        # makes sure that the user types the correct name for a specific suggestion so the additional information can be found
        found = self._get_suggestion(suggestion,re,jarvis)
        
        # the users input was found in the suggestion list 
        if found:
            jarvis.say("")
            jarvis.say(found["Name"],Fore.CYAN)
            jarvis.say("")
            # description exists
            if found["wTeaser"]:
                # use of textwrap for easier viewing
                about = textwrap.wrap(found["wTeaser"],width=70)
                jarvis.say("About: " )
                for el in about:
                    jarvis.say(el)
                jarvis.say("")
            # wikipedia link exists
            if found["wUrl"]:
                jarvis.say("Wikipedia: " + found["wUrl"])
                jarvis.say("")
            # youtube link exists
            if found["yUrl"]:
                jarvis.say("YouTube: " + found["yUrl"])
                jarvis.say("")
        # user decided to end the additional information process
        else :
            return

            

    # manual for plugin
    def _print_help(self, jarvis):
        jarvis.say("\nWelcome to Taste Dive!", Fore.CYAN)
        jarvis.say("You can use current plugin as follows:", Fore.CYAN)
        jarvis.say("    taste dive <argument>", Fore.CYAN)
        jarvis.say(
            "    <argument> cl- Can be the name of your favorite band,TV Show, movie, game and also book ", Fore.CYAN)
        jarvis.say(    
            "Result: The user receives a list with suggestions for the given argument, based on his taste!", Fore.CYAN)
        jarvis.say("Example: ", Fore.CYAN)
        jarvis.say(
            "         'taste dive Rolling Stones' - list of bands similar to Rolling Stones", Fore.CYAN)
        jarvis.say(
            "         'taste dive Breaking Bad'   - list of TV shows similar to Breaking Bad", Fore.CYAN)
        jarvis.say(
            "The user can also get more information like description, wikipedia and youtube links for a specific suggestion", Fore.CYAN)
        jarvis.say(
            "by entering 1 as dialog option and typing the name of the suggestion as it is displayed on the returned list", Fore.CYAN)
        

        



        
    