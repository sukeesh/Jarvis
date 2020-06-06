from __future__ import division
from plugin import plugin


@plugin('massconv')
class massconv():
    """
    massconv Documentation.
    massconv is a mass converter.
    Supports: microgram, miligram, gram, kilogram, tonne, ounce, pound,
        stone, hundredweight
    Usage: The input mass measurement units are:
        mcg: microgram,
        mg: miligram,
        g: gram,
        kg: kilogram,
        t: tonne,
        oz: ounce,
        lb: pound,
        st: stone,
        cwt: hundredweight

        First you will be asked to enter the amount you want to convert.
        Second you will be asked to enter the mass measurement unit of the amount.
        And then you will be asked to enter which mass measurement unit you want to convert to.
        A user can enter both short and full names of the units.
    """

    mass_units = [
        "mcg", "mg", "g", "kg", "t", "oz", "lb", "st", "cwt"
    ]

    units_data = {
        "mcg2mg": 0.001,
        "mg2g": 0.001,
        "g2kg": 0.001,
        "kg2t": 0.001,
        "t2oz": 35274,
        "oz2lb": 0.0625,
        "lb2st": 0.0714286,
        "st2cwt": 0.125,
    }

    units = {
        "mcg": "microgram",
        "mg": "miligram",
        "g": "gram",
        "kg": "kilogram",
        "t": "tonne",
        "oz": "ounce",
        "lb": "pound",
        "st": "stone",
        "cwt": "hundredweight"
    }

    rev_units = {full: short for short, full in units.items()}

    def __call__(self, jarvis, s):
        while True:
            amount = jarvis.input_number('Enter an amount: ')
            from_unit = self.get_units(jarvis, 'Enter from which unit: ')
            to_unit = self.get_units(jarvis, 'Enter to which unit: ')

            if (from_unit != to_unit):
                break
            else:
                jarvis.say('Please enter different units')

        convamount = self.mass_convert(jarvis, amount, from_unit, to_unit)

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

    def mass_convert(self, jarvis, amount, fr, to):
        if fr in self.rev_units:
            fr = self.rev_units[fr]
        if to in self.rev_units:
            to = self.rev_units[to]

        for i in range(len(self.mass_units)):
            if (self.mass_units[i] == fr):
                start = i

            if (self.mass_units[i] == to):
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
            kbuild = self.mass_units[i] + "2" + self.mass_units[i + 1]
            multiplier = multiplier * self.units_data.get(kbuild)

        multiplier = round(multiplier, 17)

        if reverse:
            convamount = (1 / multiplier) * amount
        else:
            convamount = multiplier * amount

        convamount = round(convamount, 12)

        return convamount

    def get_units(self, jarvis, prompt):

        while True:
            u = jarvis.input(prompt).lower()
            if u in self.mass_units:
                return u
            elif u in self.rev_units:
                return self.rev_units[u]
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
