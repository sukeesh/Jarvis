from plugin import plugin


@plugin("speedconv")
class speedconv:
    """
    speedconv is a speed converter.
    The supported input speed measurement units are:
        m/s  : meter per second
        km/h : kilometer per hour
        ft/s : foot per second
        mi/h : miles per hour
        kn   : knot
        use the abreviated forms for input
        for instance m/s for meter per second
    First you enter the value you want to convert.
    Second you enter the speed unit of the current value.
    And then you enter to which speed unit you want to convert to.
    The program shows the conversion
    """
    units = [
        "m/s", "km/h", "ft/s", "mi/h", "kn"
    ]
    # these are the conversions from all units to m/s
    conv_to_mpers = {
        "m/s": 1.0,
        "km/h": 0.277778,
        "ft/s": 0.3048,
        "mi/h": 0.44704,
        "kn": 0.514444
    }

    def __call__(self, jarvis, s):

        jarvis.say("The supported units are:")
        jarvis.say("m/s  : meter per second ")
        jarvis.say("km/h : kilometer per hour")
        jarvis.say("ft/s : foot per second")
        jarvis.say("mi/h : miles per hour")
        jarvis.say("kn   : knot")
        jarvis.say("use the abreviated forms for input")
        jarvis.say("for instance m/s for meter per second")
        flag = True
        while flag:
            val = jarvis.input_number("value to convert : ")
            unit_in = self.units_input(jarvis, "from which unit : ")
            unit_out = self.units_input(jarvis, "to which unit : ")

            if (unit_in != unit_out):
                flag = False
            else:
                jarvis.say("Please enter different units")

        convertedval = self.convert_speed(val, unit_in, unit_out)
        convertedval = round(convertedval, 6)

        jarvis.say(str(convertedval))

        # we can use conv_to_mpers to create every possible conversion with
        #  this formula
    def convert_speed(self, value, inside, out):
        return value * self.conv_to_mpers[inside] / self.conv_to_mpers[out]

    def units_input(self, jarvis, text):

        while True:
            unit = jarvis.input(text).lower()
            if unit in self.units:
                return unit
            else:
                text = "Not a valid unit. Try again: "
