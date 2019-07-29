from __future__ import division
from plugin import plugin


@plugin('timeconv')
class timeconv():
    """
    timeconv Documentation.
    timeconv is a time converter.
    Supports: picosecond, nanosecond, microsecond, millisecond, second, minute, hour, day, week, month, year
    Usage: The input time measurement units are:
        ps : picosecond,
        ns : nanosecond,
        mum : microsecond,
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
        "yr", "mon", "wk", "d", "h", "min", "s", "ms", "mus", "ns", "ps"
    ]

    units = {
        "ps": "picosecond",
        "ns": "nanosecond",
        "mus": "microsecond",
        "ms": "millisecond",
        "s": "second",
        "min": "minute",
        "h": "hour",
        "d": "day",
        "wk": "week",
        "mon": "month",
        "yr": "year"
    }

    units_data = {
        "yr2mon": 12,
        "mon2wk": 4.34812141,
        "wk2d": 7,
        "d2h": 24,
        "h2min": 60,
        "min2s": 60,
        "s2ms": 1000,
        "ms2mus": 1000,
        "mus2ns": 1000,
        "ns2ps": 1000
    }

    def __call__(self, jarvis, s):
        while True:
            amount = jarvis.input_number('Enter an amount: ')
            from_unit = self.get_units(jarvis, 'Enter from which unit: ')
            to_unit = self.get_units(jarvis, 'Enter to which unit: ')

            if (from_unit != to_unit):
                break
            else:
                jarvis.say('Please enter different units')

        convamount = self.time_convert(jarvis, amount, from_unit, to_unit)

        precision = 0
        if (convamount.is_integer() is False):
            precision = jarvis.input_number("Please enter precision (max:12): ")
            while True:
                if (precision.is_integer() and precision <= 12):
                    break
                else:
                    precision = jarvis.input_number("Please enter an integer (max:12): ")

        convamount = round(convamount, int(precision))

        outputText = self.txt_build(amount, convamount, from_unit, to_unit)

        jarvis.say(outputText)

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

        mulitplier = round(multiplier, 17)

        if reverse:
            convamount = (1 / multiplier) * amount
        else:
            convamount = multiplier * amount

        convamount = round(convamount, 12)

        return convamount

    def get_units(self, jarvis, prompt):

        while True:
            u = jarvis.input(prompt).lower()
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
