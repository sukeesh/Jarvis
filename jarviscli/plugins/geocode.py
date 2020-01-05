import re
import requests
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin('geocode')
class Geocoder:
    """
    Geocoding tool to convert street addresses to latitude and longitude.

    Attributes
    ----------
    jarvis : CmdInterpreter.JarvisAPI
        An instance of Jarvis that will be used to interact with the user
    input_addr : str
        A street address input by the user
    cleaned_addr : str
        A street address cleaned for use in a URL
    output : dict of str: str
        Parsed results from the API request if a match was found
    response : request.Response
        Geocoding response returned by API if API could be accessed
    help_prompt : str
        A description of this tool that the user can directly access from
        within the plugin
    """
    jarvis = None
    input_addr = None
    cleaned_addr = None
    output = None
    response = None
    help_prompt = ("Geocoding converts street addresses to geographic"
                   " latitude and longitude. To use this tool, you can enter a"
                   " street address in this form: STREET NUMBER STREET NAME, CITY,"
                   " STATE, ZIP. For example: 1000 Main Street, Los Angeles, CA,"
                   " 90012. Currently, this tool only works for addresses in the"
                   " United States.")

    def __call__(self, jarvis, s):
        """Run the geocoding tool by getting an address from the user, passing
        it to the geocoding API, and displaying the result.

        Parameters
        ----------
        jarvis : CmdInterpreter.JarvisAPI
            An instance of Jarvis that will be used to interact with the user
        s : str
            The input string that was submitted when the plugin was launched.
            Likely to be empty.
        """
        self.jarvis = jarvis
        # Required disclaimer per API terms of service
        self.jarvis.say("Disclaimer: This product uses the Census Bureau Data"
                        " API but is not endorsed or certified by the Census"
                        " Bureau.", Fore.LIGHTBLACK_EX)

        self.input_addr = self.get_input_addr(s)
        self.cleaned_addr = self.clean_addr(self.input_addr)
        self.response = self.get_response()

        # Request failed
        if not self.response:
            self.jarvis.say("The geocoding service appears to be unavailable."
                            " Please try again later.", Fore.RED)

        # Request succeeded
        else:
            self.output = self.parse_response(self.response)

            if self.output:
                for result in self.output:
                    self.jarvis.say("{}: {}".format(result,
                                                    self.output[result]),
                                    Fore.CYAN)

            else:
                self.jarvis.say("No matching addresses found.", Fore.RED)

    @property
    def url(self):
        """Format a url to access the geocoding API by combining the cleaned
        input address with the API url.

        Returns:
        -------
        str
            URL for the geocoding API using the input address
        """
        return ("https://geocoding.geo.census.gov/geocoder/locations/"
                "onelineaddress?address={}&benchmark=Public_AR_Current&format="
                "json".format(self.cleaned_addr))

    def help(self):
        """Print the help prompt for the plugin"""
        self.jarvis.say(self.help_prompt, Fore.BLUE)

    def get_input_addr(self, s):
        """Get an input address from the user and handle help commands

        Parameters
        ----------
        s : str
            The input string that was submitted when the plugin was launched.
            Likely to be empty.

        Returns:
        -------
        str
            A street address (unvalidated)
        """
        while True:
            if not s:
                s = self.jarvis.input("Enter the full street address to"
                                      " geocode (or type help for options): ")

            if s.lower() == 'help':
                self.help()
                s = None
            else:
                return s.lower()

    def clean_addr(self, s):
        """Reformat a string to be URL friendly

        Parameters
        ----------
        s : str
            A street address (unvalidated)

        Returns:
        -------
        str
            The street address with all special characters removed and
            whitespace replaced with +
        """
        # Remove everything that isn't alphanumeric or whitespace
        s = re.sub(r"[^\w\s]", '', s)

        # Replace all whitespace
        s = re.sub(r"\s+", '+', s)

        return s

    def get_response(self):
        """Make a request to the geocoding API and return the Response
        if it succeeds

        Returns:
        -------
        requests.Response
            A Response object returned by the API. If any errors were
            encountered during the request, the return will be None.
        """
        try:
            response = requests.get(self.url)
            # Raise HTTPErrors if encountered
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError):
            return None

    def parse_response(self, response):
        """Parse a Response returned by the geocoding API to extract all
        relevant geocoding data

        Parameters
        ----------
        response : request.Response
            The Response object returned by the geocoding API for an address
            search

        Returns:
        -------
        dict of str: str
            A dictionary of geocoding results for the best matched address
            from the request
        """
        data = response.json()
        matches = data['result']['addressMatches']

        if matches:
            best_match = matches[0]

            output = {'Address matched': best_match['matchedAddress'],
                      'Latitude': str(best_match['coordinates']['y']),
                      'Longitude': str(best_match['coordinates']['x'])}

        else:
            output = None

        return output
