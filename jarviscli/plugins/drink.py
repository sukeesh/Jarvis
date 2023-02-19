from plugin import plugin
import requests
import json

# simple plugin that gives preparation info about given cocktail
# uses the API https://www.thecocktaildb.com with a total of 635 cocktails/drinks


@plugin("drink")
def cocktail(jarvis, s):
    cocktail = input("Enter a drink: ").strip()
    url = 'https://www.thecocktaildb.com/api/json/v1/1/search.php?s=' + cocktail
    r = requests.get(url)
    json_data = json.loads(r.content)
    try:
        # collects the neccasary data from the JSON and saves in 
        cocktail_name = json_data['drinks'][0]['strDrink']
        ingredients_str = 'Ingredients: \n'
        i=1
        temp = json_data['drinks'][0]['strIngredient' + str(i)]
        while True:
            temp = json_data['drinks'][0]['strIngredient' + str(i)]
            if not temp:
                break
            ingredients_str += temp + '\n'
            i+=1
        # prints all the info in the command prompt in a pretty format
        seperator = '-----'
        jarvis.say(seperator)
        jarvis.say(cocktail_name)
        jarvis.say(seperator)
        jarvis.say(ingredients_str + seperator)
        jarvis.say(json_data['drinks'][0]['strInstructions'])
        jarvis.say(seperator)
    except:
        # wrong user input
        jarvis.say("Drink not found. Please try again.")
    

