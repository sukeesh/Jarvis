"""
This plugin generates curl request for the user. The user needs to specify the parameters
HTTP Method, Content Type, Data, Endpoint. The output is the curl request.
The plugin also validates the user input before generating the curl output.
"""


from plugin import plugin
import json
from colorama import Fore


@plugin("generate curl")
class GenerateCurl(object):

    def __call__(self, jarvis, s):
        self._input_params = {}
        self._collect_parameters(jarvis)
        self._validate_parameters(jarvis)
        self._generate_curl_request(jarvis)

    def _collect_parameters(self, jarvis):
        http_method = jarvis.input(prompt="HTTP Method: ", color=Fore.BLUE)
        jarvis.say(text="Select Content Type\n\n1. JSON\n2. No Data\n")
        content_type = jarvis.input_number(prompt="Enter you choice: ", color=Fore.BLUE, rtype=int, rmin=1, rmax=2)
        data = jarvis.input(prompt="Enter / copy the data: ", color=Fore.BLUE)
        endpoint = jarvis.input(prompt="Specify the HTTP endpoint: ", color=Fore.BLUE)

        self._input_params = {
            "method": http_method.upper(),
            "content_type": content_type,
            "data": data,
            "endpoint": endpoint
        }

    def _validate_parameters(self, jarvis):

        if "method" not in self._input_params:
            jarvis.say(text="HTTP Method missing.", color=Fore.RED)
            jarvis.exit()

        if "content_type" not in self._input_params:
            jarvis.say(text="Content Type missing.", color=Fore.RED)
            jarvis.exit()

        if "data" not in self._input_params:
            jarvis.say(text="Data missing. Could be empty but should be present.", color=Fore.RED)
            jarvis.exit()

        if "endpoint" not in self._input_params:
            jarvis.say(text="Endpoint missing.", color=Fore.RED)
            jarvis.exit()

        if self._valid_method(jarvis) and self._valid_content_type(jarvis) and \
           self._valid_data(jarvis) and self._valid_endpoint(jarvis):
            pass
        else:
            jarvis.exit()

    def _valid_method(self, jarvis):

        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        if self._input_params["method"] not in valid_methods:
            jarvis.say(text="Invalid HTTP method provided.", color=Fore.RED)
            return False
        return True

    def _valid_content_type(self, jarvis):
        return True

    def _valid_data(self, jarvis):

        data = self._input_params["data"]
        content_type = self._input_params["content_type"]

        if content_type == 2:
            return True

        if content_type == 1:
            try:
                json.loads(data)
                return True
            except ValueError as e:
                jarvis.say(text="Invalid data format based on content type.", color=Fore.RED)
                return False

    def _valid_endpoint(self, jarvis):
        return True

    def _generate_curl_request(self, jarvis):

        curl_string = "curl "

        curl_string += "-X{} ".format(self._input_params["method"])

        if self._input_params["content_type"] == 1:
            curl_string += '-H "Content-type: application/json" '

        if self._input_params["content_type"] != 2:
            curl_string += " -d '{}'".format(self._input_params["data"])

        curl_string += " '{}'".format(self._input_params["endpoint"])
        jarvis.say(text=curl_string, color=Fore.GREEN)
