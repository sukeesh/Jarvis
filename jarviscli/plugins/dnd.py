from plugin import plugin
import random

@plugin("dnd")
def Initialize(jarvis, s):
    stillUsing = True
    jarvis.say("\nWelcome to Dungeons and Dragons! Enter \'Help\' for a list of available actions.")
    while(stillUsing):
        request = input("\nDnD - What would you like to do: ")
        match request:
            case "exit":
                stillUsing = False
                break
            case "help":
               Help(jarvis)
            case "roll":
                prepareRoll(jarvis)
            case "npcName":
                npcNames(jarvis)
            case "loot":
                loot(jarvis, loots)
            case _: 
                jarvis.say("\nSorry, I do not understand this command..\n")

def Help(jarvis):
       commands = ["\n* exit", "* help", "* roll","* loot", "* npcName\n"]
       for command in commands:      
        jarvis.say(command)

def loadLoots(filePath):
    with open(filePath) as f:
        myLoots = [line.strip() for line in f]
    return myLoots

def loot(jarvis, loots):
    numberOfItems = random.randint(1, 5)
    for _ in range(numberOfItems):
        jarvis.say(random.choice(loots))

def npcNames(jarvis):
    jarvis.say("\nPlease specify your npc. Enter help for clarification.\n")
    stillUsing = True
    while(stillUsing):
        userInput =  input("\nEnter your npc: ").split()
        if len(userInput) == 2:
            race, gender = userInput
            race = race.lower()
            gender = gender.lower()

            if race in names and gender in names[race]:
                jarvis.say("\n" + random.choice(names[race][gender]))
            else:
                jarvis.say("\nWe do not include that races or gender\n")

        elif len(userInput) == 1:
            command = userInput[0]
            match command:
                case "help":
                    jarvis.say("\nRaces: Dwarf, Elf, Halfling, Human, Dragonborn, Gnome, Half-elf, Half-orc, Tiefling\nfemale, male\n")
                case "exit":
                    stillUsing = False
                    break
                case _:
                    jarvis.say("\nI didn't recognize this command.\n")


def prepareRoll(jarvis):
    jarvis.say("\nPlease specify your roll. Enter help for clarification.\n")
    stillUsing = True
    while(stillUsing):
        theRoll = input("\nEnter your roll: ")
        match theRoll:
            case "help":
                jarvis.say("\nThe command has the following structure: number of dice + die type + advantage/disadvantage (optional)\ndie types: D4, D6, D8, D10, D12, D20, D100\nadv - advantage, dis - disadvantage\nexample: \"4d6\" rolls four 6 sided dice\n\"2d20 adv\" rolls two twenty sided dice with advantage (chooses the highest number)\n")
            case "exit":
                stillUsing = False
            case _:
                numberOfDice, dieType, adv = parseRoll(theRoll)
                
                if numberOfDice != 0 and dieType != 0:
                    if dieType != 4 and dieType != 6 and dieType != 8 and dieType != 10 and dieType != 12 and dieType != 20 and dieType != 100:
                        jarvis.say("\nThis die type does not exist, but we will roll it anyways.. :)\n")
                    rolls = Roll(numberOfDice, dieType)
                    for roll in rolls:
                        jarvis.say(str(roll))
                        
                    if numberOfDice > 1:
                        if adv == None:
                            jarvis.say("\nSum: " + str(sumRolls(rolls)))
                        elif adv != 0:
                            jarvis.say("\nRoll result: " + str(getAdvRoll(rolls, adv)))
                else:
                    jarvis.say("\nWrong roll.\n")

def getAdvRoll(rolls, adv):
    if adv == 1:
        return max(rolls)
    elif adv == -1:
        return min(rolls)
    else: 
        raise SystemError("GetAdvantage error")

def sumRolls(rolls):
    result = 0
    for roll in rolls:
        result = result + roll
    return result

def Roll(nod, dt):
    rolls = []
    while(nod != 0):
        rolls.append(random.randint(1, dt))
        nod = nod - 1
    return rolls

def parseRoll(userInput):
    numberOfDice = 0
    dieType = 0
    parsingSecondHalf = False
    parsingThirdHalf = False
    advantage = ""
    adv = 0 # 1 -> advantage, -1 -> disadvantage, None -> nothing, 0 -> error

    for letter in userInput:
        if parsingSecondHalf == False:
            if letter.isdigit():
                numberOfDice = numberOfDice * 10 + int(letter) 
            elif letter == 'd' or letter == 'D':
                parsingSecondHalf = True
        else:
            if parsingThirdHalf == False and letter.isdigit():
                dieType = dieType * 10 + int(letter) 
            elif letter.isalpha():
                advantage += letter
                parsingThirdHalf = True

    if advantage == "adv" or advantage == "Adv" or advantage == "ADV":
        adv = 1
    elif advantage == "dis" or advantage == "Dis" or advantage == "DIS":
        adv = -1
    elif advantage == "": 
        adv = None
    else:
        adv = 0
    return numberOfDice, dieType, adv

loots_dictionary = 'jarviscli/data/dnd_files/loots.txt'
loots = loadLoots(loots_dictionary)
names = {
        "dwarf": {
            "male": ["Adrik", "Baern", "Barendd", "Brottor", "Eberk", "Flint", "Harbek", "Rurik", "Vondal"],
            "female": ["Amber", "Artin", "Audhild", "Bardryn", "Dagnal", "Eldeth", "Falkrunn", "Gunnloda", "Vistra"]
        },
        "elf": {
            "male": ["Adran", "Aelar", "Aramil", "Arannis", "Aust", "Enialis", "Heian", "Lucan", "Peren", "Thamior"],
            "female": ["Adrie", "Althaea", "Anastrianna", "Caelynn", "Drusilia", "Enna", "Ielenia", "Lia", "Mialee", "Shanairra"]
        },
        "halfling": {
            "male": ["Alton", "Ander", "Cade", "Corrin", "Eldon", "Errich", "Finnan", "Garret", "Lyle", "Merric", "Roscoe", "Wellby"],
            "female": ["Andry", "Bree", "Callie", "Cora", "Euphemia", "Jillian", "Kithri", "Lavinia", "Lidda", "Merla", "Nedda", "Seraphina"]
        },
        "human": {
            "male": ["Ander", "Bram", "Darek", "Joris", "Krynt", "Morn", "Randal", "Stedd", "Taman", "Urth"],
            "female": ["Arveene", "Esvele", "Jhessail", "Kara", "Lureene", "Miri", "Rowan", "Shandri", "Tessele"]
        },
        "dragonborn": {
            "male": ["Arjhan", "Balasar", "Donaar", "Ghesh", "Kriv", "Medrash", "Pandjed", "Patrin", "Rhogar", "Tarhun"],
            "female": ["Akra", "Biri", "Daar", "Farideh", "Harann", "Jheri", "Kava", "Korinn", "Mishann", "Nala"]
        },
        "gnome": {
            "male": ["Alston", "Alvyn", "Boddynock", "Brocc", "Eldon", "Erky", "Fonkin", "Frug", "Gerbo", "Jebeddo"],
            "female": ["Bimpnottin", "Breena", "Caramip", "Carlin", "Donella", "Duvamil", "Ella", "Ellyjobell", "Loopmottin", "Roywyn"]
        },
        "half-elf": {
            "male": ["Arlen", "Berrian", "Carric", "Enialis", "Erevan", "Galinndan", "Hadarai", "Kharis", "Laucian", "Mindartis"],
            "female": ["Dara", "Elia", "Jelenneth", "Keyleth", "Leshanna", "Mara", "Sariel", "Shanairra", "Thia", "Valanthe"]
        },
        "half-orc": {
            "male": ["Dench", "Feng", "Gell", "Henk", "Holg", "Imsh", "Keth", "Krusk", "Ront", "Shump"],
            "female": ["Baggi", "Emen", "Engong", "Kansif", "Myev", "Neega", "Ovak", "Ownka", "Shautha", "Sutha"]
        },
        "tiefling": {
            "male": ["Akmenos", "Amnon", "Barakas", "Damakos", "Ekemon", "Iados", "Kairon", "Leucis", "Mordai", "Morthos"],
            "female": ["Akta", "Anakis", "Bryseis", "Criella", "Damaia", "Ea", "Kallista", "Lerissa", "Makaria", "Nemeia"]
        }
        
    }
