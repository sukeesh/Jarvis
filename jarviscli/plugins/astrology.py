import requests
from plugin import plugin

BASE_URL = "https://sameer-kumar-aztro-v1.p.rapidapi.com/"

@plugin("astrology")
def astrology(jarvis, s):

    # Getting user input on their zodiac sign
    while True:
        jarvis.say('\nEnter your zodiac sign.')
        zodiacSign = jarvis.input().strip().lower()

        validSigns = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']

        # Checking if zodiac sign input is valid
        if zodiacSign in validSigns:
            break
        else:
            jarvis.say('Invalid zodiac sign entered. Please enter a valid sign.')

    # Getting user input on which day they want horoscope information on
    while True:
        jarvis.say('\nEnter whether you want your horoscope for yesterday, today, or tomorrow.')
        day = jarvis.input().strip().lower()

        validDays = ['yesterday', 'today', 'tomorrow']

        # Checking if day input is valid
        if day in validDays:
            break
        else:
            jarvis.say('Invalid day entered. Please enter yesterday, today, or tomorrow.')

    # Headers for HTTP request
    headers = {
        'X-RapidAPI-Host': 'sameer-kumar-aztro-v1.p.rapidapi.com',
        'X-RapidAPI-Key': 'a98e762323msh4beea42cfb4520ep16c3abjsnb3918dcc145a',
    }

    # Query parameters in the HTTP request 
    params = {
        'sign': zodiacSign,
        'day': day,
    }

    # Making a POST request to the API
    try:
        response = requests.post(BASE_URL, headers=headers, params=params)
        data = response.json()

        # HTTP request was successful, displaying the horoscope information
        if response.status_code == 200:
            jarvis.say(f"\n{zodiacSign.capitalize()} Horoscope for {day.capitalize()}:")
            jarvis.say(f"Date Range: {data['date_range']}")
            jarvis.say(f"Current Date: {data['current_date']}")
            jarvis.say(f"Compatibility: {data['compatibility']}")
            jarvis.say(f"Lucky Number: {data['lucky_number']}")
            jarvis.say(f"Lucky Color: {data['color']}")
            jarvis.say(f"Mood: {data['mood']}")
            jarvis.say(f"Description: {data['description']}")
        # HTTP request was not successful, displaying the appropriate error message 
        else:
            jarvis.say(f"Error: {data['message']}")
            jarvis.say(f"Response Status Code: {response.status_code}")
            jarvis.say(f"Response Text: {response.text}")

    # Exception Catching
    except Exception as e:
        jarvis.say(f"Error: {str(e)}")