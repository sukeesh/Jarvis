import datetime
from plugin import plugin

@plugin('rosary')
def rosary(jarvis, s):
    ##Provides names of the days of the week
    weekdayList = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
        'Saturday', 'Sunday']
    ##Function to convert the index of the weekday into the date
    ##(eg Monday, Tuesday)
    def convertDayIndexToWord():
        return weekdayList[y]
    ##Fetches the day of the week
    y = datetime.datetime.today().weekday()
    ##Calls the function
    convertDayIndexToWord()
    ##Displays the day of the week in user-readable format
    print('Today is', weekdayList[y])
    ##Uses the weekday to display the appropriate mysteries of the Rosary
    ##TODO would probably have been better to write these as lists or something
    ##instead of printing them straight out
    ##TODO add a 'trad mode' to change Thursday's mysteries to whatever it was before
    ##JPII introduced the Luminous Mysteries
    ##TODO Maybe add clickable beads?
    if y == 1 or y == 4:
        print("Today's mysteries of the Rosary are the Sorrowful Mysteries.")
        print("The Sorrowful Mysteries are:")
        print("1. The Agony in the Garden")
        print("2. The Scourging at the Pillar")
        print("3. The Crowning of Thorns")
        print("4. The Carrying of the Cross")
        print("5. The Crucifixion and Death of Our Lord")
    elif y == 0 or y == 5:
        print("Today's mysteries of the Rosary are the Joyful Mysteries.")
        print("The Joyful Mysteries are:")
        print("1. The Annunciation")
        print("2. The Visitation")
        print("3. The Nativity")
        print("4. The Presentation in the Temple")
        print("5. The Finding of Our Lord in the Temple")
    elif y == 3 or y == 6:
        print("Today's mysteries of the Rosary are the Glorious Mysteries.")
        print("The Glorious Mysteries are:")
        print("1. The Resurrection")
        print("2. The Ascension")
        print("3. The Descent of the Holy Spirit at Pentecost")
        print("4. The Dormition of the Theotokos")
        print("5. The Crowing of the Theotokos as Queen of Heaven")
    elif y == 3:
        print("Today's mysteries of the Rosary are the Luminous Mysteries.")
        print("The Luminous Mysteries are:")
        print("1. The Baptism of Our Lord")
        print("2. The Wedding at Cana")
        print("3. The Preaching of the Gospel")
        print("4. The Transfiguration of Our Lord")
        print("5. The Institution of the Holy Eucharist")
    else: ##Input Validation
        print('Oops! Something went wrong with fetching the date.')
