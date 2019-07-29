from __future__ import division
from plugin import plugin


@plugin('lengthconv')
class lengthconv():
    """
    lengthconv Documentation.
    lengthconv is a length converter.
    Supports: kilometer, meter, decimetre centimeter, millimeter, micrometer, nanometer,
        mile, yard, foot, inch
    Usage: The input length measurement units are:
        nm : nanometer,
        mum : micrometer,
        mm : millimeter,
        cm : centimeter,
        dm : decimeter,
        m : meter,
        km : kilometer,
        mi : mile,
        yd : yard,
        ft : foot,
        in : inch

        First you will be asked to enter the amount you want to convert.
        Second you will be asked to enter the length measurement unit of the amount.
        And then you will be asked to enter to which length measurement unit you want to convert.
    """

    length_units = [
        "nm", "mum", "mm", "cm", "dm", "m", "km", "mi", "yd", "ft", "in"
    ]

    units = {
        "nm": "nanometer",
        "mum": "micrometer",
        "mm": "millimeter",
        "cm": "centimeter",
        "dm": "decimeter",
        "m": "meter",
        "km": "kilometer",
        "mi": "mile",
        "yd": "yard",
        "ft": "foot",
        "in": "inch"
    }

    units_data = {
        "nm2mum": 0.001,
        "mum2mm": 0.001,
        "mm2cm": 0.1,
        "cm2dm": 0.1,
        "dm2m": 0.1,
        "m2km": 0.001,
        "km2mi": 0.621371192,
        "mi2yd": 1760,
        "yd2ft": 3,
        "ft2in": 12
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

        convamount = self.length_convert(jarvis, amount, from_unit, to_unit)

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

    def length_convert(self, jarvis, amount, fr, to):

        for i in range(len(self.length_units)):
            if (self.length_units[i] == fr):
                start = i

            if (self.length_units[i] == to):
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
            kbuild = self.length_units[i] + "2" + self.length_units[i + 1]
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
            if u in self.length_units:
                return u
            else:
                prompt = 'Please enter a valid unit: '
                continue

    def txt_build(self, amount, convamount, from_unit, to_unit):

        if (amount == 1):
            fromdisp = self.units.get(from_unit)
        else:
            if (from_unit == "ft"):
                fromdisp = "feet"
            elif (from_unit == "in"):
                fromdisp = "inches"
            else:
                fromdisp = self.units.get(from_unit) + "s"

        if (convamount == 1):
            todisp = self.units.get(to_unit)
        else:
            if (to_unit == "ft"):
                todisp = "feet"
            elif (to_unit == "in"):
                todisp = "inches"
            else:
                todisp = self.units.get(to_unit) + "s"

        txt = str(amount) + " " + fromdisp + " is equal to " + str(convamount) + " " + todisp

        return txt
