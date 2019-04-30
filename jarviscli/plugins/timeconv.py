from plugin import plugin
from utilities.GeneralUtilities import get_float

@plugin('timeconv')
class timeconv():
    """
    timeconv Documentation.
    timeconv is a time converter.
    Supports: picosecond, nanosecond, microsecond, millisecond, second, minute, hour, day, week, month, year
    Usage: The input time measurement units are:
        ps : picosecond,
        ns : nanosecond,
        μm : microsecond,
        mm : millisecond,
        s : second,
        min : minute,
        h : hour,
        d : day,
        wk : week,
        mon : month,
        yr : year

        First you will be asked to enter the amount you want to convert.
        Second you will be asked to enter the time measurement unit of the amount.
        And then you will be asked to enter to which time measurement unit you want to convert.
    """

    time_units = [
        "ps", "ns", "μs", "ms", "s", "min", "h", "d", "wk", "mon", "yr"
    ]

    units = {
        "ps": "picosecond",
        "ns": "nanosecond",
        "μm": "microsecond",
        "mm": "millisecond",
        "s": "second",
        "min": "minute",
        "h": "hour",
        "d": "day",
        "wk": "week",
        "mon": "month",
        "yr": "year"
    }

    units_data = {
        "ps2ns": 0.001,
        "ns2μs": 0.001,
        "μs2ms": 0.001,
        "ms2s": 0.001,
        "s2min": 0.0166666667,
        "min2h": 0.0166666667,
        "h2d": 0.0416666667,
        "d2wk": 0.1428571429,
        "wk2mon": 0.2299794661,
        "mon2yr": 0.0833333333
    }

    def __call__(self, jarvis, s):
        while True:
            amount = get_float('Enter an amount: ')
            from_unit = self.get_units('Enter from which unit: ')
            to_unit = self.get_units('Enter to which unit: ')

            if (from_unit != to_unit):
                break
            else:
                jarvis.say('Please enter different units')

        self.time_convert(jarvis, amount, from_unit, to_unit)

    def time_convert(self, jarvis, amount, fr, to):

        for i in range(len(self.time_units)):
            if (self.time_units[i] == fr):
                start = i

            if (self.time_units[i] == to):
                end = i

        if ((end - start) > 0):
            reverse = False

        if ((end - start) < 0):
            reverse = True
            tmp = start
            start = end
            end = tmp

        multiplier = 1

        convamount = multiplier

        for i in range(start, end, 1):
            kbuild = self.time_units[i] + "2" + self.time_units[i + 1]
            multiplier = multiplier * self.units_data.get(kbuild)

        if reverse:
            convamount = (1 / multiplier) * amount
        else:
            convamount = multiplier * amount


        outputText = self.txt_build(amount, convamount, fr, to)

        jarvis.say(outputText)

    def get_units(self, prompt):

        while True:
            u = input(prompt).lower()
            if u in self.time_units:
                return u
            else:
                prompt = 'Please enter a valid unit: '
                continue

    def txt_build(self, amount, convamount, from_unit, to_unit):

        if (amount == 1):
            fromdisp = self.units.get(from_unit)
        else:
            fromdisp = self.units.get(from_unit) + "s"

        if (convamount == 1):
            todisp = self.units.get(to_unit)
        else:
            todisp = self.units.get(to_unit) + "s"

        txt = str(amount) + " " + fromdisp + " is equal to " + str(convamount) + " " + todisp

        return txt