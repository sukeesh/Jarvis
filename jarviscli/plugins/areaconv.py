from plugin import plugin
from utilities.GeneralUtilities import get_float

@plugin('areaconv')
class areaconv():
    """
    areaconv Documentation.
    areaconv is a area converter.
    Supports: square kilometers/meters/centimeters/millimeter/micrometer,
        square mile/yard/foot/inch, acre, hectare
    Usage: The input area measurement units are:
        μm2 : square micrometer,
        mm2 : square millimeter,
        cm2 : square centimeter,
        m2 : square meter,
        km2 : square kilometer,
        ha : hectare,
        ac : acre,
        mi2 : square mile,
        yd2 : square yard,
        ft2 : square foot,
        in2 : square inch

        First you will be asked to enter the amount you want to convert.
        Second you will be asked to enter the area measurement unit of the amount.
        And then you will be asked to enter to which area measurement unit you want to convert.
    """

    area_units = [
        "μm2", "mm2", "cm2", "m2", "km2", "ha", "ac", "mi2", "yd2", "ft2", "in2"
    ]

    units = {
        "μm2": "square micrometer",
        "mm2": "square millimeter",
        "cm2": "square centimeter",
        "m2": "square meter",
        "km2": "square kilometer",
        "ha": "hectare",
        "ac": "acre",
        "mi2": "square mile",
        "yd2": "square yard",
        "ft2": "square foot",
        "in2": "square inch"
    }

    units_data = {
        "μm2tomm2": 0.000001,
        "mm2tocm2": 0.01,
        "cm2tom2": 0.00001,
        "m2tokm2": 0.000001,
        "km2toha": 100,
        "hatoac": 2.4710538147,
        "actomi2": 0.0015624989,
        "mi2toyd2": 3097602.26,
        "yd2toft2": 9,
        "ft2toin2": 144
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

        self.area_convert(jarvis, amount, from_unit, to_unit)

    def area_convert(self, jarvis, amount, fr, to):

        for i in range(len(self.area_units)):
            if (self.area_units[i] == fr):
                start = i

            if (self.area_units[i] == to):
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
            kbuild = self.area_units[i] + "to" + self.area_units[i + 1]
            jarvis.say(kbuild)
            multiplier = multiplier * self.units_data.get(kbuild)

        if reverse:
            convamount = (1/multiplier) * amount
        else:
            convamount = multiplier * amount


        outputText = self.txt_build(amount, convamount, fr, to)

        jarvis.say(outputText)

    def get_units(self, prompt):

        while True:
            u = input(prompt).lower()
            if u in self.area_units:
                return u
            else:
                prompt = 'Please enter a valid unit: '
                continue

    def txt_build(self, amount, convamount, from_unit, to_unit):

        if (amount == 1):
            fromdisp = self.units.get(from_unit)
        else:
            if (from_unit == "ft2"):
                fromdisp = "square feet"
            elif (from_unit == "in2"):
                fromdisp = "square inches"
            else:
                fromdisp = self.units.get(from_unit) + "s"

        if (convamount == 1):
            todisp = self.units.get(to_unit)
        else:
            if (to_unit == "ft2"):
                todisp = "square feet"
            elif (to_unit == "in"):
                todisp = "square inches"
            else:
                todisp = self.units.get(to_unit) + "s"

        txt = str(amount) + " " + fromdisp + " is equal to " + str(convamount) + " " + todisp

        return txt