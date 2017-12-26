In the following sections you will find a brief explanation of PyOWM's object model, with detail about the classes and datastructures of interest. For a detailed description of the classes, please refer to the [SW API documentation](https://pyowm.readthedocs.org/).

# Abstractions

A few abstract classes are provided in order to allow code reuse for supporting new OWM web API versions and to eventually patch the currently supported ones.

### The OWM abstract class
The _OWM_ class is an abstract entry-point to the library. Clients can obtain a concrete implementation of this class through a factory method that returns the _OWM_ subclass instance corresponding to the OWM web API version that is specified (or to the latest OWM web API version available).

In order to leverage the library features, you need to import the OWM factory and then feed it with an API key, if you have one (read [here](http://openweathermap.org/appid) on how to obtain an API key). Of course you can change your API Key after object instantiation, if you need.

Each kind of weather query you can issue against the OWM web API is done through a correspondent method invocation on your _OWM_ object instance.

Each OWM web API version may have different features, and therefore the mapping _OWM_ subclass may have different methods. The _OWM_ common parent class provides methods that tells you the PyOWM library version, the supported OWM web API version and the availability of the web API service: these methods are inherited by all the _OWM_ children classes.

### The JSONParser abstract class
This abstract class states the interface for OWM web API responses' JSON parsing: every API endpoint returns a different JSON message that has to be parsed to a specific object from the PyOWM object model.
Subclasses of _JSONParser_ shall implement this contract: instances of these classes shall be used by subclasses of the _OWM_ abstract class.

### The OWMCache abstract class
This abstract class states the interface for OWM web API responses' cache. The target of subclasses is to implement the get/set methods so that the JSON payloads of OWM web API responses are cached and looked up using the correspondent HTTP full URL that originated them.

### The LinkedList abstract class
This abstract class models a generic linked list data structure.

# OWM web API 2.5 object model

### The configuration25 module
This module contains configuration data for the OWM web API 2.5 object model. Specifically:

    * OWM web API endpoint URLs
    * parser objects for API JSON payloads parsing
    * registry object for City ID lookup
    * cache providers
    * misc data

As regards cache providers:
* by default, the library doesn't use any cache (it uses a null-object cache instance)
* the library provides a basic LRU cache implementation (class ``LRUCache`` in module ``caches.lrucache.py``)
* you can leverage 3rd-party caching systems (eg: Memcached, MongoDB, Redis, file-system caches, etc..): all you have to do is write/obtain a wrapper module for those systems which conforms to the interface stated into the ``abstractions.owmcache`` abstract class.

You can write down your own configuration module and inject it into the PyOWM when you create the OWM global object, provided that you strictly follow the format of the `config25` module - which can be seen from the source code - and you put your own module in a location visible by the PYTHONPATH.

### The OWM25 class
The _OWM25_ class extends the _OWM_ abstract base class and provides a method for each of the OWM web API 2.5 endpoint:

    # CURRENT WEATHER QUERYING
    * find current weather at a specific location ---> eg: owm.weather_at_place('London,UK')
    * find current weather at a specific city ID  ---> eg: owm.weather_at_id(1812597)
    * find current weather at specific lat/lon ------> eg: owm.weather_at_coords(-0.107331,51.503614)
    * find weather currently measured by station ----> eg: owm.weather_at_station(1000)
    * find current weathers in all locations
      with name is equal/similar to a specific name -> eg: owm.weather_at_places('Springfield',search='accurate')
    * find current weathers in all locations
      in the surroundings of specific lon/lat -------> eg: owm.weather_around_coords(-2.15, 57.0)

    # METEOSTATIONS QUERYING
    * find stations close to specific lat/lon -------> eg: owm.stations_at_coords(-0.107331,51.503614)

    # WEATHER FORECAST QUERYING
    * find 3 hours weather forecast at a specific
      location --------------------------------------> eg: owm.three_hours_forecast('Venice,IT')
    * find daily weather forecast at a specific
      location --------------------------------------> eg: owm.daily_forecast('San Francisco,US')

    # WEATHER HISTORY QUERYING
    * find weather history for a specific location --> eg: owm.weather_history_at_place('Kiev,UA')
    * find weather history for a specific city id  --> eg: owm.weather_history_at_id(12345)
    * find historic minutely data measurements for a
      specific meteostation -------------------------> eg: owm.station_tick_history(39276)
    * find historic hourly data measurements for a
      specific meteostation -------------------------> eg: owm.station_hour_history(39276)
    * find historic daily data measurements for a
      specific meteostation -------------------------> eg: owm.station_day_history(39276)

The methods illustrated above return a single object instance (_Observation_ or _Forecast_ types) a list of instances. In all cases, it is up to the clients to handle the returned entities.

The _OWM25_ class is injected with _jsonparser_ subclasses instances: each one parses a JSON response coming from a specific API endpoint and creates the objects returned to the clients. These dependencies are configured into the _configuration25_ module and injected into this class.

In order to interact with the web API, this class leverages an _OWMHTTPClient_ instance.

### The Location class
The _Location_ class represents a location in the world. Each instance stores the geographic name of the location, the longitude/latitude couple and the country name. These data are retrieved from the OWM web API 2.5 responses' payloads.

_Location_ instances can also be retrieved from City IDs using the _CityIDRegistry_ module.

### The Weather class
This class is a databox containing information about weather conditions in a place. Stored data include text information such as weather status (sunny/rainy/snowy/...) and numeric information such as the values of measured phyisical entities (mx/min/current temperatures, wind speed/orientation, humidity, pressure, cloud coverage, ...).

Some types of data are grouped and stored into Python dictionaries, such as weather and temperature info.

This class also stores the reference timestamp for the weather data, that is to say the time when the data was measured.

When using _OWM25_ class for the retrieval of weather history on a location, eg:

    owm.weather_history_at_place('Kiev,UA')

a list of _Weather_ objects is returned.

### The Observation class
An instance of this class is returned whenever a query about currently observed weather in a location is issued (hence, its name).

The _Observation_ class binds information about weather features that are currently being observed in a specific location in the world and that are stored as a _Weather_ object instance and the details about the location, which is stored into the class as a _Location_ object instance. Both current weather and location info are obtained via OWM web API responses parsing, which done by other classes in the PyOWM library: usually this data parsing stage ends with their storage into a newly created _Observation_ instance.

When created, every _Observation_ instance is fed with a timestamp that tells when the weather observation data have been received.

When using _OWM25_ class for the retrieval of currently observed weather in multiple locations, eg:

    owm.weather_at_places('Springfield',search='accurate')
    owm.weather_around_coords(-2.15, 57.0)

a list of _Observation_ instances is returned to the clients.

### The Forecast class
This class represents a weather forecast for a specific location in the world. A weather forecast is made out by location data - encapsulated by a _Location_ object - and a collection of weather conditions - a list of _Weather_ objects.

The OWM web API 2.5 provides two types of forecast intervals: three hours and daily; each _Forecast_ instance has a specific fields that tells the interval of the forecast.

_Forecast_ instances can also tell the reception timestamp for the weather forecast, that is to say the time when the forecast has been recevied from the OWM web API.

This class also provides an iterator for easily iterating over the encapsulated _Weather_ list:

	>>> fcst = owm.daily_forecast('Tokyo')
	>>> for weather in fcst:
	...   print (weather.get_reference_time(format='iso'), weather.get_status())
	('2013-09-14 14:00:00+0','Clear')
	('2013-09-14 17:00:00+0','Clear')
	('2013-09-14 20:00:00+0','Clouds')

### The Forecaster class
Instances of this class are returned by weather forecast queries such as:

    f = owm.three_hours_forecast('London')
    f = owm.daily_forecast('Buenos Aires',limit=6)

A _Forecaster_ object wraps a _Forecast_ object and provides convenience methods that makes it possible to perform complex weather forecast data queries, which could not otherwise be possible using only the _Forecast_ class interface. A central concept with this regard is the "time coverage" of the forecast, that is to say the temporal length of the forecast.

It is then possible to know when a weather forecast starts/ends, know which _Weather_ items in the forecast carry sunny/cloudy/... weather conditions, determine wether the forecast contains sunny/cloudy/... _Weather_ items or not and to obtain the closest _Weather_ item of the forecast to the time provided by the
clients.

### The StationHistory class
Instances of this class are returned by historic weather data query for meteostations, such as:

    sh = owm.station_tick_history(39276)
    sh = owm.station_hour_history(2865, limit=3)
    sh = owm.station_day_history(2865)

A _StationHistory_ object contains information about the ID of the meteostation, the time granularity of the retrieved data ('tick','hour' or 'day' - where 'tick' represents data sampled every minute) and of course the raw data: temperature, humidity, pressure, rain and wind speed.

### The Historian class
This convenience class is dual to Forecaster.
Instances of this class are returned by meteostation weather history queries such as:

    h = owm.station_hour_history(39276)
    h = owm.station_tick_history(39276)

A _Historian _ object wraps a _StationHistory_ object and provides convenience methods that make it possible, in example, to obtain the time series of each of the measured physical entities: this is particularly useful for example when creating cartesian charts.

### The weatherutils module
This utility module provides functions for searching and filtering collections of _Weather_ objects.

# Caches
Collection of caches

### The NullCache class
This is a null-object that does nothing and is used by default as the PyOWM library caching mechanism

### The LRUCache class
This is a Least-Recently Used simple cache with configurable size and elements expiration time.

# Commons
A few common classes are provided to be used by all codes supporting different OWM web API versions.

### The OWMHTTPClient class

This class is used to issue HTTP requests to the OWM web API endpoints.

### The FrontLinkedList class

This class realizes a linked list that performs insertions only at the front of the list (time: O(1)) and deletions at any of its places (time: O(n))

# Utilities
A few packages are provided, containing utility functions that support the base PyOWM entity classes and the user:

+ **conversion utils**: conversions between temperature units and timeformats
+ **time utils**: convenience time functions for library users
+ **XML utls**: dump data to XML

# Exceptions
+ **APICallError** class: raises when failures in OWM web API invocation occur
+ **APIResponseError** class: raised when HTTP error status codes occur in OWM web API responses
+ **NotFoundError** class: raised when a search for an item in a collection has no result
+ **ParseResponseError** class: raised when failures occur in parsing payload data coming from OWM web API responses