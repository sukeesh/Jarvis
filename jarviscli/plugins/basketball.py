import requests
from plugin import plugin, require

API_KEY = "b13ad5f4c1msh55b5d06158c224cp14d63djsnac01e7128355"
URL = "https://api-basketball.p.rapidapi.com/"
headers = {	
    "x-rapidapi-host": "api-basketball.p.rapidapi.com",
	"x-rapidapi-key":API_KEY
}

def fetch_data(route):
    r = requests.get(URL + route, headers=headers)
    r = r.json()
    if "errorCode" in r.keys():
        return None
    return r



@require(network=True)
@plugin("basketball")
class Basketball():
    def __call__(self, jarvis, s):
        print("plugin is called")