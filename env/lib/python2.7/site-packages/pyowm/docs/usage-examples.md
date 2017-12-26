# Import the PyOWM library
As simple as:

    >>> from pyowm import OWM

# Create global OWM object
Use your OWM API key if you have one (read [here](http://openweathermap.org/appid)
on how to obtain an API key). By default, if you don't specify which API subscription type you want to use, a free-subscription OWM global object is instantiated:

    >>> API_key = 'G097IueS-9xN712E'
    >>> owm = OWM(API_key)

Of course you can change your API key at a later time if you need:

    >>> owm.get_API_key()
    'G09_7IueS-9xN712E'
    >>> owm.set_API_key('6Lp$0UY220_HaSB45')

The same happens with the language: you can speficy in which language the OWM web API will return textual data of weather queries. Language is specified by passing its corresponding two-characters string, eg: ``es``, ``sk``, etc. The default language is English (``en``):

    >>> owm_en = OWM()              # default language is English
    >>> owm_ru = OWM(language='ru') # Russian

You can obtain the OWM global object related to a specific OWM web API version,
just specify it after the API key parameter(check before that the version is supported!):

    >>> owm = OWM(API_key='abcdef', version='2.5')

If you don't specify an API version number, you'll be provided with the OWM
object that represents the latest available OWM web API version.

Advanced users might want to inject into the library a specific configuration: this can be done by injecting the Python path of your personal configuration module as a string into the library instantiation call like this:

    >>> owm = OWM(API_key='abcdef', version='2.5', config_module='mypackage.mysubpackage.myconfigmodule')

Be careful! You must provide a well-formatted configuration module for the library to work properly and your module must be in your PYTHONPATH. More on configuration modules formatting can be found [here](https://github.com/csparpa/pyowm/blob/master/pyowm/docs/usage-examples.md#wiki-the-configuration25-module).

# Using a paid (pro) API key subscription
If you purchased a pro subscription on the OWM web API, you can instantiate the global OWM like this:

    >>> owm = pyowm.OWM('abcdef', subscription_type='pro')

When instantiating paid subscription OWM objects, you must provide an API key.

# OWM web API version 2.5 usage examples

### Setting a local cache provider
The PyOWM library comes with a built-in support for local caches: OWM web API reponses can be cached in order to save time and bandwidth. The default configuration uses no cache, however the library contains a built-in simple LRU cache implementation that can be plugged in by changing the ``configuration25.py`` module and specifying a ``LRUCache`` class instance:

    ...
    # Cache provider to be used
    from pyowm.caches.lrucache import LRUCache
    cache = LRUCache()
    ...

By using the ``configuration25.py`` module, it is also possible to leverage external cache providers  module, provided that they implement the interface that is expected by the library code.

### Getting currently observed weather for a specific location.
Querying for current weather is simple: provide an ``OWM`` object with the location you want the current weather be looked up for and the job is done. You can specify the location either by passing its toponym (eg: "London"), the city ID (eg: 2643741) or its geographic coordinates (lon/lat):

    obs = owm.weather_at_place('London,uk')                          # Toponym
    obs = owm.weather_at_id(2643741)                           # City ID
    obs = owm.weather_at_coords(-0.107331,51.503614)           # lat/lon

An ``Observation`` object will be returned, containing weather info about the location matching the toponym/ID/coordinates you provided. Be precise when specifying locations!

### Retrieving city ID for a location
City IDs can be retrieved using a registry:

    reg = owm.city_id_registry()
    reg.ids_for('London')       # [ (123, 'London', 'UK'), (456, 'London', 'MA'), (789, 'London', 'WY')]
    reg.locations_for("London")  # gives a list of Location instances

You can pass the retrieved IDs with ``owm.weather_at_id`` method.

As multiple locations with the same name exist in different states, the registry
comes with support for narrowing down queries on specific countries...

    london = reg.ids_for('London', country='UK')            # [ (123, 'London, UK') ]
    london_loc = reg.locations_for('London', country='UK')  # [ <Location obj> ]

... as well as for changing the type of matches between the provided string and
the locations' toponyms:

    reg.ids_for("london", matching='exact')  # literal matching
    reg.ids_for("london", matching='nocase') # case-insensitive
    reg.ids_for("london", matching='like')   # substring search

Please refer to the SW API docs for details.


### Currently observed weather extended search
You can query for currently observed weather:

+ for all the places whose name equals the toponym you provide (use ``search='accurate'``)
+ for all the places whose name contains the toponym you provide (use ``search='like'``)
+ for all the places whose lon/lat coordinates are in the surroundings of the lon/lat couple you provide

In all cases, a list of ``Observation`` objects is returned, each one describing the weather currently observed in one of the places matching the search. You can control how many items the returned list will contain by using the ``limit`` parameter.

Examples:

    # Find observed weather in all the "London"s in the world
    obs_list = owm.weather_at_places('London', 'accurate')
    # As above but limit result items to 3
    obs_list = owm.weather_at_places('London',searchtype='accurate',limit=3)

    # Find observed weather for all the places whose name contains the word "London"
    obs_list = owm.weather_at_places('London', 'like')
    # As above but limit result items to 5
    obs_list = owm.weather_at_places('London',searchtype='like', 5)

    # Find observed weather for all the places in the surroundings of lon=-2.15,lat=57
    obs_list = owm.weather_around_coords(-2.15, 57)
    # As above but limit result items to 8
    obs_list = owm.weather_around_coords(-2.15, 57, limit=8)

### Getting data from Observation objects
``Observation`` objects store two useful objects: a ``Weather`` object that contains the weather-related data and a ``Location`` object that describes the location the weather data is provided for.

If you want to know when the weather observation data have been received, just call:

    >>> obs.get_reception_time()                           # UNIX GMT time
    1379091600L
    >>> obs.get_reception_time(timeformat='iso')           # ISO8601
    '2013-09-13 17:00:00+00'
    >>> obs.get_reception_time(timeformat='date')          # datetime.datetime instance
    datetime.datetime(2013, 09, 13, 17, 0, 0, 0)

You can retrieve the ``Weather`` object like this:

    >>> w = obs.get_weather()

and then access weather data using the following methods:

    >>> w.get_reference_time()                             # get time of observation in GMT UNIXtime
    1377872206L
    >>> w.get_reference_time(timeformat='iso')             # ...or in ISO8601
    '2013-08-30 14:16:46+00'
    >>> w.get_reference_time(timeformat='date')            # ...or as a datetime.datetime object
    datetime.datetime(2013, 08, 30, 14, 16, 46, 0)

    >>> w.get_clouds()                                     # Get cloud coverage
    65

    >>> w.get_rain()                                       # Get rain volume
    {'3h': 0}

    >>> w.get_snow()                                       # Get snow volume
    {}

    >>> w.get_wind()                                       # Get wind degree and speed
    {'deg': 59, 'speed': 2.660}

    >>> w.get_humidity()                                   # Get humidity percentage
    67

    >>> w.get_pressure()                                   # Get atmospheric pressure
    {'press': 1009, 'sea_level': 1038.381}

    >>> w.get_temperature()                                # Get temperature in Kelvin
    {'temp': 293.4, 'temp_kf': None, 'temp_max': 297.5, 'temp_min': 290.9}
    >>> w.get_temperature(unit='celsius')                  # ... or in Celsius degs
    >>> w.get_temperature('fahrenheit')                    # ... or in Fahrenheit degs

    >>> w.get_status()                                     # Get weather short status
    'clouds'
    >>> w.get_detailed_status()                           # Get detailed weather status
    'Broken clouds'

    >>> w.get_weather_code()                               # Get OWM weather condition code
    803

    >>> w.get_weather_icon_name()                          # Get weather-related icon name
    '02d'

    >>> w.get_sunrise_time()                               # Sunrise time (GMT UNIXtime or ISO 8601)
    1377862896L
    >>> w.get_sunset_time('iso')                           # Sunset time (GMT UNIXtime or ISO 8601)
    '2013-08-30 20:07:57+00'

Support to weather data interpreting can be found [here](http://bugs.openweathermap.org/projects/api/wiki/Weather_Data#Description-parameters)
and [here](http://bugs.openweathermap.org/projects/api/wiki/Weather_Condition_Codes) you can read about OWM weather condition codes and icons.

As said, ``Observation`` objects also contain a ``Location`` object with info about the weather location:

    >>> l = obs.get_location()
    >>> l.get_name()
    'London'
    >>> l.get_lon()
    -0.12574
    >>> l.get_lat()
    51.50863
    >>> l.get_ID()
    2643743

The last call returns the OWM city ID of the location - refer to the
[OWM API documentation](http://bugs.openweathermap.org/projects/api/wiki/Api_2_5_weather#3-By-city-ID)
for details.

### Getting weather forecasts
The OWM web API currently provides weather forecasts that are sampled :

+ every 3 hours
+ every day (24 hours)

The 3h forecasts are provided for a streak of 5 days since the request time and daily forecasts are provided for a maximum streak of 14 days since the request time (but also shorter streaks can be obtained).

You can query for 3h forecasts for a location using:

    # Query for 3 hours weather forecast for the next 5 days over London
    >>> fc = owm.three_hours_forecast('London,uk')

You can query for daily forecasts using:

    # Query for daily weather forecast for the next 14 days over London
    >>> fc = owm.daily_forecast('London,uk')

and in this case you can limit the amount of days the weather forecast streak will contain by using the ``limit`` parameter:

    # Daily weather forecast just for the next 6 days over London
    >>> fc = owm.daily_forecast('London,uk', limit=6)

Both of the above calls return a ``Forecaster`` object. ``Forecaster`` objects contain a ``Forecast`` object, which has all the information about your weather forecast. If you need to manipulate the latter, just go with:

    >>> f = fc.get_forecast()

A ``Forecast`` object encapsulates the ``Location`` object relative to the forecast and a list of ``Weather`` objects:

    # When has the forecast been received?
    >>> f.get_reception_time()                           # UNIX GMT time
    1379091600L
    >>> f.get_reception_time('iso')                      # ISO8601
    '2013-09-13 17:00:00+00'
    >>> f.get_reception_time('date')                     # datetime.datetime instance
    datetime.datetime(2013, 09, 13, 17, 0, 0, 0)

    # Which time interval for the forecast?
    >>> f.get_interval()
    'daily'

    # How many weather items are in the forecast?
    >>> len(f)
    20

    # Get Location
    >>> f.get_location()
    <pyowm.location.Location object at 0x01921DF0>

Once you obtain a ``Forecast`` object, reading the forecast data is easy - you can get the whole list of ``Weather`` objects or you can use the built-in iterator:

    # Get the list of Weather objects...
    >>> lst = f.get_weathers()

    # ...or iterate directly over the Forecast object
    >>> for weather in f:
          print (weather.get_reference_time('iso'),weather.get_status())
    ('2013-09-14 14:00:00+0','Clear')
    ('2013-09-14 17:00:00+0','Clear')
    ('2013-09-14 20:00:00+0','Clouds')

The ``Forecaster`` class provides a few convenience methods to inspect the weather forecasts in a human-friendly fashion. You can - for example - ask for the GMT time boundaries of the weather forecast data:

    # When in time does the forecast begin?
    >>> fc.when_starts()                                  # UNIX GMT time
    1379090800L
    >>> fc.when_starts('iso')                             # ISO8601
    '2013-09-13 16:46:40+00'
    >>> fc.when_starts('date')
    datetime.datetime(2013, 09, 13, 16, 46, 40, 0)        # datetime.datetime instance

    # ...and when will it end?
    >>> fc.when_ends()                                    # UNIX GMT time
    1379902600L
    >>> fc.when_ends('iso')                               # ISO8601
    '2013-09-23 02:16:40+00'
    >>> fc.when_ends('date')                              # datetime.datetime instance
    datetime.datetime(2013, 09, 13, 16, 46, 40, 0)

In example, you can ask the ``Forecaster`` instance to tell which is the weather forecast for a specific point in time. You can specify this time using a UNIX timestamp, an ISO8601-formatted string or a Python ``datetime.datetime`` object (all times must will be handled as GMT):

    # Tell me the weather for tomorrow at this hour
    >>> from datetime import datetime
    >>> date_tomorrow = datetime(2013, 9, 19, 12, 0)
    >>> str_tomorrow = "2013-09-19 12:00+00"
    >>> unix_tomorrow = 1379592000L
    >>> fc.get_weather_at(date_tomorrow)
    <weather.Weather at 0x00DF75F7>
    >>> fc.get_weather_at(str_tomorrow)
    <weather.Weather at 0x00DF75F7>
    >>> fc.get_weather_at(unix_tomorrow)
    <weather.Weather at 0x00DF75F7>

You will be provided with the ``Weather`` sample that lies closest to the time that you specified. Of course this will work only if the specified time is covered by the forecast! Otherwise, you will be prompted with an error:

    >>> fc.get_weather_at("1492-10-12 12:00:00+00")
    pyowm.exceptions.not_found_error.NotFoundError: The searched item was not found.
    Reason: Error: the specified time is not included in the weather coverage range

Keep in mind that you can leverage the convenience ``timeutils`` module's functions to quickly build datetime objects:

    >>> from pyowm import timeutils
    >>> timeutils.tomorrow()                              # Tomorrow at this hour
    datetime.datetime(2013, 9, 19, 12, 0)
    >>> timeutils.yesterday(23, 27)                       # Yesterday at 23:27
    datetime.datetime(2013, 9, 19, 12, 0)
    >>> timeutils.next_three_hours()
    datetime.datetime(2013, 9, 18, 15, 0)                 # 3 hours from now
    >>> t = datetime.datetime(2013, 19, 27, 8, 47, 0)
    >>> timeutils.next_three_hours(t)
    datetime.datetime(2013, 19, 27, 11, 47, 0)            # 3 hours from a specific datetime

Other useful convenicence methods in class ``Forecaster`` are:

    # Will it rain, be sunny, foggy or snow during the covered period?
    >>> fc.will_have_rain()
    True
    >>> fc.will_have_sun()
    True
    >>> fc.will_have_fog()
    False
    >>> fc.will_have_clouds()
    False
    >>> fc.will_have_snow()
    False

    # Will it be rainy, sunny, foggy or snowy at the specified GMT time?
    time = "2013-09-19 12:00+00"
    >>> fc.will_be_rainy_at(time)
    False
    >>> fc.will_be_sunny_at(time)
    True
    >>> fc.will_be_foggy_at(time)
    False
    >>> fc.will_be_cloudy_at(time)
    False
    >>> fc.will_be_snowy_at(time)
    False
    >>> fc.will_be_sunny_at(0L)           # Out of weather forecast coverage
    pyowm.exceptions.not_found_error.NotFoundError: The searched item was not found.
    Reason: Error: the specified time is not included in the weather coverage range

    # List the weather elements for which the condition will be:
    # rain, sun, fog and snow
    >>> fc.when_rain()
    [<weather.Weather at 0x00DB22F7>,<weather.Weather at 0x00DB2317>]
    >>> fc.when_sun()
    [<weather.Weather at 0x00DB62F7>]
    >> fc.when_clouds()
    [<weather.Weather at 0x00DE22F7>]
    >>> fc.when_fog()
    [<weather.Weather at 0x00DC22F7>.]
    >>> fc.when_snow()
    []                                   # It won't snow: empty list

    # Get weather for the hottest, coldest, most humid, most rainy, most snowy
    # and most windy days in the forecast
    >>> fc.most_hot()
    <weather.Weather at 0x00DB67D9>
    >>> fc.most_cold()
    <weather.Weather at 0x00DB62F7>
    >>> fc.most_humid()
    <weather.Weather at 0x00DB62F7>
    >>> fc.most_rainy()
    <weather.Weather at 0x00DB62F7>
    >>> fc.most_snowy()
    None                                 # No snow in the forecast
    >>> fc.most_windy()
    <weather.Weather at 0x00DB62F7>

When calling the ``will_be_*_at()`` methods you can specify either a UNIX timestamp, a ``datetime.datetime`` object or an ISO8601-formatted string (format: "YYYY-MM-DD HH:MM:SS+00"). A boolean
value will be returned, telling if the queried weather condition will apply to the time you specify (the check will be performed on the _Weather_ object of the forecast which is closest in time to the time value that you provided).

When calling the ``when_*()``  methods you will be provided with a sublist of the ``Weather`` objects list in into the ``Forecaster`` instance, with items having as weather condition the one the method queries for.

### Note on weather history
Weather history retrieval is a *[paid OWM API feature](https://openweathermap.org/price)*.

### Getting weather history on a location
Weather history on a specific toponym can be retrieved using:

    >>> owm.weather_history_at_place('London,uk')
    [ <weather.Weather at 0x00BF81A2>, <weather.Weather at 0x00BF81C8>, ... ]

A list of ``Weather`` objects is returned. You can can specify a time window in which you want the results to be filtered:

    >>> owm.weather_history_at_place('London,uk', start=1379090800L, end=1379099800L)
    >>> owm.weather_history_at_place('London,uk', '2013-09-13 16:46:40+00', '2013-09-13 19:16:40+00')
    >>> from datetime import datetime
    >>> owm.weather_history_at_place('London,uk', datetime(2013, 9, 13, 16, 46, 40), datetime(2013, 9, 13, 19, 16, 40))

The time boundaries can be expressed either as a UNIX timestamp, a _datetime.datetime_ object or an ISO8601-formatted string (format: "YYYY-MM-DD HH:MM:SS+00").

What said before also applies for city ID-based queries:

    >>> owm.weather_history_at_id(12345, start=1379090800L, end=1379099800L)

### Getting meteostation measurements history
Weather data measurements history for a specific meteostation is available in three sampling intervals: ``'tick'`` (which stands for minutely), ``'hour'`` and ``'day'``. The calls to be made are:

    # Get tick historic data for station 39276, only 4 data items
    >>> hist = owm.station_tick_history(39276, limit=4)
    # Get hourly historic data for station 39276
    >>> hist = owm.station_hour_history(39276)
    # Get daily historic data for station 39276, only 10 data items
    >>> hist = owm.station_day_history(39276, 10)

and all of them return a ``Historian`` object. As you can notice, the amount of data measurements returned can be limited usign the proper parameter: by default, all available data items are retrieved. Each data item is composed by a temperature sample, a humidity sample, a pressure sample, a rain volume sample and a wind speed sample.

Once you have a ``Historian`` instance, you can obtain its encapsulated ``StationHistory`` object, which is a databox containing the data:

    >>> sh = his.get_station_history()

and query data directly on it:

    >>> sh.get_station_ID()                   # Meteostation ID
    39276
    >>> sh.get_interval()                     # Data sampling interval
    'tick'
    >>> sh.get_reception_time()               # Timestamp when data was received (GMT UNIXtime, ISO8601
                                              # or datetime.datetime)
    1377862896L
    >>> sh.get_reception_time("iso")
    '2013-08-30 20:07:57+00'
    >>> sh.get_measurements()                 # Get historic data as a dict
    {
        1362933983: {
             "temperature": 266.25,
             "humidity": 27.3,
             "pressure": 1010.02,
             "rain": None,
             "wind": 4.7
         },
        [...]
    }

The last call gives you back a dictionary containing the historic weather data: the keys of the dictionary are the UNIX timestamps of data sampling and the values are dictionaries having a fixed set of keys (_temperature_, _humidity_, _pressure_, _rain_, _wind_) along with their corresponding numeric values.

If you have no specific need to handle the raw data by yourself, you can leverage the convenience methods provided by the ``Historian`` class:

    # Get the temperature time series (in different units of measure)
    >>> his.temperature_series()
    [(1381327200, 293.4), (1381327260, 293.6), (1381327320, 294.4), ...]
    >>> his.temperature_series(unit="celsius")
    [(1381327200, 20.25), (1381327260, 20.45), (1381327320, 21.25), ...]
    >>> his.temperature_series("fahrenheit")
    [(1381327200, 68.45), (1381327260, 68.81), (1381327320, 70.25), ...]

    # Get the humidity time series
    >>> his.humidity_series()
    [(1381327200, 27.3), (1381327260, 27.2), (1381327320, 27.2), ...]

    # Get the atmospheric pressure time series
    >>> his.pressure_series()
    [(1381327200, 1010.02), (1381327260, 1010.23), (1381327320, 1010.79), ...]

    # Get the rain volume time series
    >>> his.rain_series()
    [(1381327200, None), (1381327260, None), (1381327320, None), ...]

    # Get the wind speed time series
    >>> his.wind_series()
    [(1381327200, 4.7), (1381327260, 4.7), (1381327320, 4.9), ...]

Each of the ``*_series()`` methods returns a list of tuples, each tuple being a couple in the form: (timestamp, measured value). When in the series values are not provided by the OWM web API, the numeric value is ``None``. These convenience methods are especially useful if you need to chart the historic time series of the measured physical entities.

You can also get minimum, maximum and average values of each series:

    # Get the minimum temperature value in the series
    >>> his.min_temperature(unit="celsius")
    (1381327200, 20.25)

    # Get the maximum rain value in the series
    >>> his.max_rain()
    ()

    # Get the average wind value in the series
    >>> his.average_wind()
    4.816


### Dumping objects' content to JSON and XML
The PyOWM object instances can be dumped to JSON or XML strings:

    # Dump a Weather object to JSON...
    >>> w.to_JSON()
    {'referenceTime':1377851530,'Location':{'name':'Palermo',
    'coordinates':{'lon':13.35976,'lat':38.115822}'ID':2523920},...}

    #... and to XML
    >>> w.to_XML()
    <?xml version='1.0' encoding='utf8'?>
    <weather xmlns:w="http://github.com/csparpa/pyowm/tree/master/pyowm/webapi25/xsd/weather.xsd">
    <w:status>Clouds</w:status>[...]</weather>

When you dump to XML you can decide wether or not to print the standard XML encoding declaration line and XML Name Schema prefixes using the relative switches:

    >>> w.to_XML(xml_declaration=True, xmlns=False)

### Checking if OWM web API is online
You can check out the OWM web API service availability:

    >>> owm.is_API_online()
    True

### Printing objects
Most of PyOWM objects can be pretty-printed for a quick introspection:

    >>> print w
    <pyowm.webapi25.weather.Weather - reference time=2013-12-18 16:41:00, status=Drizzle>
    >>> print w.get_location()
    <pyowm.webapi25.location.Location - ID=1234, name=Barcelona, lon=2.9, lat=41.23>d