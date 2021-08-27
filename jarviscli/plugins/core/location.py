from plugin import plugin


@plugin("update providers")
def update_providers(jarvis, s):
    jarvis.location.update_providers(jarvis)


@plugin("update location")
def update_location(jarvis, s):
    jarvis.location.update(jarvis, force=True)


@plugin("update ip")
def update_ip(jarvis, s):
    jarvis.location.ask_choose_value(jarvis, jarvis.LocationFields.IP)


@plugin("update country")
def update_country(jarvis, s):
    jarvis.location.ask_choose_value(jarvis, jarvis.LocationFields.COUNTRY)


@plugin("update region")
def update_region(jarvis, s):
    jarvis.location.ask_choose_value(jarvis, jarvis.LocationFields.REGION)


@plugin("update city")
def update_city(jarvis, s):
    jarvis.location.ask_choose_value(jarvis, jarvis.LocationFields.CITY)


@plugin("update latitude")
def update_latitude(jarvis, s):
    jarvis.location.ask_choose_value(jarvis, jarvis.LocationFields.LATITUDE)


@plugin("update longitude")
def update_longitude(jarvis, s):
    jarvis.location.ask_choose_value(jarvis, jarvis.LocationFields.LONGITUDE)


@plugin("update timezone")
def update_timezone(jarvis, s):
    jarvis.location.ask_choose_value(jarvis, jarvis.LocationFields.TIMEZONE)


@plugin("update currency")
def update_currency(jarvis, s):
    jarvis.location.ask_choose_value(jarvis, jarvis.LocationFields.CURRENCY)
