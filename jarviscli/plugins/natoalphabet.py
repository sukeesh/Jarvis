from plugin import plugin


@plugin('natoalphabet')
def natoalphabet(jarvis, s):
    if len(s) == 0:
        jarvis.say('\nEnter word')
        word = jarvis.input()
    else:
        word = s

    if len(word) == 0:
        jarvis.say("Don't recognise that word")
        return

    nato_alphabet = {
        'a': 'alpha',
        'b': 'bravo',
        'c': 'charlie',
        'd': 'delta',
        'e': 'echo',
        'f': 'foxtrot',
        'g': 'golf',
        'h': 'hotel',
        'i': 'india',
        'j': 'juliet',
        'k': 'kilo',
        'l': 'lima',
        'm': 'mike',
        'n': 'november',
        'o': 'oscar',
        'p': 'papa',
        'q': 'quebec',
        'r': 'romeo',
        's': 'sierra',
        't': 'tango',
        'u': 'uniform',
        'v': 'victor',
        'w': 'whiskey',
        'x': 'x-ray',
        'y': 'yankee',
        'z': 'zulu'
    }

    for letter in word:
        if letter.lower() not in nato_alphabet:
            print(letter)
        else:
            print(letter, ' - ', nato_alphabet[letter])
