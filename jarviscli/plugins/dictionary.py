from plugin import plugin
import requests

@plugin('dictionary')
def dictionary(jarvis, s):
    """
    Get meaning, synonym and antonym of any word
    """
    if len(s) == 0:
        jarvis.say('\nEnter word')
        word = jarvis.input()
    else:
        word = s

    api_url = 'https://api.api-ninjas.com/v1/dictionary?word={}'.format(word)
    response = requests.get(api_url, headers={'X-Api-Key': 'dDcouxccX+Ne1OKZj+rRrw==CW8Mg7Tvlk3u8omW'})
    if response.status_code == requests.codes.ok:
        print(response.text)
    else:
        print("Error:", response.status_code, response.text)
