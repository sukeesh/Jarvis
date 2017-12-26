from pyowm.caches import nullcache
from pyowm.webapi25 import observationparser, observationlistparser, \
    forecastparser, weatherhistoryparser, stationparser, stationlistparser, \
    stationhistoryparser, uvindexparser, coindexparser, weathercoderegistry,\
    cityidregistry, ozone_parser

"""
Configuration for the PyOWM library specific to OWM web API version 2.5
"""

# OWM web API URLs
ROOT_API_URL = 'http://%s.openweathermap.org/data/2.5'
ICONS_BASE_URL = 'http://openweathermap.org/img/w'
OBSERVATION_URL = '/weather'
GROUP_OBSERVATIONS_URL = '/group'
STATION_URL = '/station'
FIND_OBSERVATIONS_URL = '/find'
FIND_STATION_URL = '/station/find'
BBOX_STATION_URL = '/box/station'
THREE_HOURS_FORECAST_URL = '/forecast'
DAILY_FORECAST_URL = '/forecast/daily'
CITY_WEATHER_HISTORY_URL = '/history/city'
STATION_WEATHER_HISTORY_URL = '/history/station'

# OWM UV web API URLs
ROOT_UV_API_URL = 'http://api.openweathermap.org/v3'
UV_INDEX_URL = '/uvi'

# OWM Air Pollution API URLs
ROOT_POLLUTION_API_URL = 'http://api.openweathermap.org/pollution/v1'
CO_INDEX_URL = '/co'
OZONE_URL = '/o3'


# Parser objects injection for OWM web API responses parsing
parsers = {
  'observation': observationparser.ObservationParser(),
  'observation_list': observationlistparser.ObservationListParser(),
  'forecast': forecastparser.ForecastParser(),
  'weather_history': weatherhistoryparser.WeatherHistoryParser(),
  'station_history': stationhistoryparser.StationHistoryParser(),
  'station': stationparser.StationParser(),
  'station_list': stationlistparser.StationListParser(),
  'uvindex': uvindexparser.UVIndexParser(),
  'coindex': coindexparser.COIndexParser(),
  'ozone': ozone_parser.OzoneParser()
}

# City ID registry
city_id_registry = cityidregistry.CityIDRegistry('cityids/%03d-%03d.txt')

# Cache provider to be used
cache = nullcache.NullCache()

# Default language for OWM web API queries text results
language = 'en'

# Default API subscription type ('free' or 'pro')
API_SUBSCRIPTION_TYPE = 'free'

# OWM web API availability test timeout in seconds
API_AVAILABILITY_TIMEOUT = 2

# Weather status code registry
weather_code_registry = weathercoderegistry.WeatherCodeRegistry({
    "rain": [{
        "start": 500,
        "end": 531
    },
    {
        "start": 300,
        "end": 321
    }],
    "sun": [{
        "start": 800,
        "end": 800
    }],
    "clouds": [{
        "start": 801,
        "end": 804
    }],
    "fog": [{
        "start": 741,
        "end": 741
    }],
    "haze": [{
        "start": 721,
        "end": 721
    }],
    "mist": [{
        "start": 701,
        "end": 701
    }],
    "snow": [{
        "start": 600,
        "end": 622
    }],
    "tornado": [{
        "start": 781,
        "end": 781
    },
    {
        "start": 900,
        "end": 900
    }],
    "storm": [{
        "start": 901,
        "end": 901
    },
    {
        "start": 960,
        "end": 961
    }],
    "hurricane": [{
        "start": 902,
        "end": 902
    },
    {
        "start": 962,
        "end": 962
    }]
})
