from hashlib import new
import math, decimal, datetime, random
from multiprocessing.dummy import current_process
from operator import index
from numpy import who


from plugin import plugin

"""
The script used to calculate the moon phases is inspired by:
https://gist.github.com/miklb/ed145757971096565723

The algorithm used to calculate the moon phases belongs to:
Author: Sean B. Palmer, inamidst.com
http://en.wikipedia.org/wiki/Lunar_phase#Lunar_phase_calculation
"""

dec = decimal.Decimal

# Colors meant for the display of the lunar phases
COLORS = [
'\33[31m',
'\33[32m',
'\33[33m',
'\33[34m',
'\33[35m',
'\33[31m',
'\33[32m',
'\33[33m']

@plugin('moonphase')
def moonphase(jarvis, s):

    pos = position()
    current_phase = phase_calculator(pos)
    phasename = phase(current_phase)

    print(COLORS[current_phase])
    details_text =  True
    # Illumination request
    if s == "illumination":
        jarvis.say("Phase: "+ phasename)
        jarvis.say("Illumination: " + f"{pos: .2%}")
    # Art request
    elif s == "art" or s == "ascii":
        jarvis.say(ascii_art(current_phase))
    # Help request
    elif s == "help":
        jarvis.say(help_text())
        details_text = False
    # Fullmoon request
    elif s == "fullmoon" or s =="full":
        fullmoon_day = fullmoon_finder()
        details_text = False   
        fullmoon_text(fullmoon_day)
    # Default request
    else:
        jarvis.say("The current moon phase for today is: " + phasename)
    
    # The next prints will appear only if the user request is about the current day
    if details_text == True:
        # Links to nineplanets.org moon phase site
        jarvis.say("")
        jarvis.say("More details at:")
        jarvis.say("\033[0;40mhttps://nineplanets.org/moon/phase/today/")

def position(now=None): 
   if now is None: 
      now = datetime.datetime.now()
   diff = now - datetime.datetime(2001, 1, 1)
   days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
   lunations = dec("0.20439731") + (days * dec("0.03386319269"))
   return lunations % dec(1)

# Modified version of the position function that runs a loop until the next Fullmoon Phase appears
# Returns the days left until the next Fullmoon Phase as an integer
# Note: due to the nature of the algorithm used, the days are not always 100% accurate 
def fullmoon_finder(now=None):
    if now is None: 
      now = datetime.datetime.now()
    is_full = False
    extra_day = 0
    while is_full == False:
      new_date = now + datetime.timedelta(days=extra_day)
      diff = new_date - datetime.datetime(2001, 1, 1)
      days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
      lunations = dec("0.20439731") + (days * dec("0.03386319269"))
      position = lunations % dec(1)
      new_phase = phase_calculator(position)
      if new_phase == 4:
        is_full = True
      else:
        extra_day += 1
    return extra_day

def fullmoon_text(fullmoon_day):
    print("\33[33mNote: This tool is not always accurate and will may be off 2 days at a time")
    print(COLORS[4])
    print("")
    if fullmoon_day == 0:
      print("The next full moon will approximately appear today")
      print("")
      print("Hope you enjoy the Full Moon!")
    elif fullmoon_day == 1:
        print("The next full moon will approximately appear tomorrow")
    else:
        print("The next full moon will appear in approximately ", fullmoon_day, " days")
    
    print("")
    print("More details at:")
    print("\033[0;40mhttps://www.timeanddate.com/astronomy/moon/full-moon.html")

# Receives the user's position to calculate and return the current lunar phase in integer form (0-7)
def phase_calculator(pos):
    index = (pos * dec(8)) + dec("0.5")
    index = math.floor(index)
    return index

# Prints a help message
def help_text():
    help_text = """
    The moonphase plugin aims to inform the user about the current moon phase


    moonphase: (Default request) Displays the current moonphase

    moonphase art, moonphase ascii: Displays the current moonphase with ASCII art

    moonphase fullmoon: Displays the approximate days left until the next Full Moon

    moonphase illumination: Displays the current lunar illumination percent

    moonphase help: Prints this help prompt
    """
    return help_text

# Receives the current lunar phase in integer form 
# and returns the current lunar phase's scientific name
def phase(index):
   return {
      0: "New Moon", 
      1: "Waxing Crescent", 
      2: "First Quarter", 
      3: "Waxing Gibbous", 
      4: "Full Moon", 
      5: "Waning Gibbous", 
      6: "Last Quarter", 
      7: "Waning Crescent"
   }[int(index) & 7]

# Receives the current lunar phase in integer form and returns the current lunar phase's ASCII art
# Source: https://www.asciiart.eu/space/moons
def ascii_art(index):
    ART = [r"""       _..._     
     .:::::::.    
    :::::::::::   NEW  MOON
    ::::::::::: 
    `:::::::::'  
      `':::'' """,
      r"""       _..._     
     .::::. `.    
    :::::::.  :    WAXING CRESCENT
    ::::::::  :  
    `::::::' .'  
      `'::'-' """,
      r"""       _..._     
     .::::  `.    
    ::::::    :    FIRST QUARTER
    ::::::    :  
    `:::::   .'  
      `'::.-'""",
      r"""       _..._     
     .::'   `.    
    :::       :    WAXING GIBBOUS
    :::       :  
    `::.     .'  
      `':..-'  """,
      r"""       _..._     
     .'     `.    
    :         :    FULL MOON
    :         :  
    `.       .'  
      `-...-'  """,
      r"""       _..._     
     .'   `::.    
    :       :::    WANING GIBBOUS
    :       :::  
    `.     .::'  
      `-..:'' """,
      r"""       _..._     
     .'  ::::.    
    :    ::::::    LAST QUARTER
    :    ::::::  
    `.   :::::'  
      `-.::''   """,
      r"""       _..._     
     .' .::::.    
    :  ::::::::    WANING CRESCENT
    :  ::::::::  
    `. '::::::'  
      `-.::'' """]
    return ART[index]