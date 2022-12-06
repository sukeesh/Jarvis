from plugin import plugin, require, alias
import pyaztro

@require(network=True)
@alias("astro")
@plugin("horoscope")
class Horoscope :

    def __call__(self, jarvis: "JarvisAPI", s: str) -> None:
        self.print_horoscope(jarvis)

    def print_horoscope(self, jarvis: "JarvisAPI") :
        jarvis.say("Which astrological sign are you?")
        jarvis.say("1: Aries")
        jarvis.say("2: Taurus")
        jarvis.say("3: Gemini")
        jarvis.say("4: Cancer")
        jarvis.say("5: Leo")
        jarvis.say("6: Virgo")
        jarvis.say("7: Libra")
        jarvis.say("8: Scorpio")
        jarvis.say("9: Sagittarius")
        jarvis.say("10: Capricorn")
        jarvis.say("11: Aquarius")
        jarvis.say("12: Pisces")
        sign = int(jarvis.input("Enter your number: "))
        if(sign<1 or sign>12) :
            jarvis.say("Wrong number input (Should be between 1 and 12). ")
        else :
            self.info_sign(jarvis, sign)

    def info_sign(self, jarvis: "JarvisAPI",n : int) :
        match n :
            case 1 :
                info = pyaztro.Aztro(sign = 'aries')
                element = "fire"
            case 2 :
                info = pyaztro.Aztro(sign = 'taurus')
                element = "earth"
            case 3 :
                info = pyaztro.Aztro(sign = 'gemini')
                element = "air"
            case 4 :
                info = pyaztro.Aztro(sign = 'cancer')
                element = "water"
            case 5 :
                info = pyaztro.Aztro(sign = 'leo')
                element = "fire"
            case 6 :
                info = pyaztro.Aztro(sign = 'virgo')
                element = "earth"
            case 7 :
                info = pyaztro.Aztro(sign = 'libra')
                element = "air"
            case 8 :
                info = pyaztro.Aztro(sign = 'scorpio')
                element = "water"
            case 9 :
                info = pyaztro.Aztro(sign = 'sagittarius')
                element = "fire"
            case 10 :
                info = pyaztro.Aztro(sign = 'capricorn')
                element = "earth"
            case 11 :
                info = pyaztro.Aztro(sign = 'aquarius')
                element = "air"
            case 12 :
                info = pyaztro.Aztro(sign = 'pisces')
                element = "water"
        jarvis.say("\nToday's description: \n" + info.description)
        jarvis.say("\nYour element: " + element)
        jarvis.say("\nYour current mood: " + info.mood)
        jarvis.say("\nYour lucky time: "+ info.lucky_time)
        jarvis.say("\nYour lucky number: " + str(info.lucky_number))
        jarvis.say("\nYour lucky color: " + info.color)
        jarvis.say("\nYour love compatibility: " + info.compatibility)


