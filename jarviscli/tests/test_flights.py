"""import unittest
#from jarviscli.CmdInterpreter import JarvisAPI
from tests import PluginTest  
from plugins.flights import Flights


class FlightsTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(Flights)

    def test_FlightRadar_1(self):
        d= self.test.check_value(None)
        self.assertEqual(d, 'None')

    def test_FlightRadar_2(self):
        d= self.test.check_value('Hello world')
        self.assertEqual(d, 'Hello world')
        
    def test_FligthRadar_getParams(self):
        self.queue_input("2")
        self.queue_input("KSC")
        d = self.test.getParams(self.jarvis_api)
        self.assertEqual(d,'&dep_iata=KSC')
        
    def test_FlightRadar_print(self):
        flights=[{'flight_date': '2022-11-08', 'flight_status': 'active', 'departure': {'airport': 'Tullamarine', 'timezone': 'Australia/Melbourne', 'iata': 'MEL', 'icao': 'YMML', 'terminal': '2', 'gate': '8', 'delay': 28, 'scheduled': '2022-11-08T00:40:00+00:00', 'estimated': '2022-11-08T00:40:00+00:00', 'actual': '2022-11-08T01:07:00+00:00', 'estimated_runway': '2022-11-08T01:07:00+00:00', 'actual_runway': '2022-11-08T01:07:00+00:00'}, 'arrival': {'airport': 'Kuala Lumpur International Airport (klia)', 'timezone': 'Asia/Kuala_Lumpur', 'iata': 'KUL', 'icao': 'WMKK', 'terminal': '1', 'gate': None, 'baggage': None, 'delay': 9, 'scheduled': '2022-11-08T06:00:00+00:00', 'estimated': '2022-11-08T06:00:00+00:00', 'actual': None, 'estimated_runway': None, 'actual_runway': None}, 'airline': {'name': 'LATAM Airlines', 'iata': 'LA', 'icao': 'LAN'}, 'flight': {'number': '8927', 'iata': 'LA8927', 'icao': 'LAN8927', 'codeshared': {'airline_name': 'malaysia airlines', 'airline_iata': 'mh', 'airline_icao': 'mas', 'flight_number': '128', 'flight_iata': 'mh128', 'flight_icao': 'mas128'}}, 'aircraft': None, 'live': None},
 {'flight_date': '2022-11-08', 'flight_status': 'active', 'departure': {'airport': 'Tullamarine', 'timezone': 'Australia/Melbourne', 'iata': 'MEL', 'icao': 'YMML', 'terminal': '2', 'gate': '8', 'delay': 28, 'scheduled': '2022-11-08T00:40:00+00:00', 'estimated': '2022-11-08T00:40:00+00:00', 'actual': '2022-11-08T01:07:00+00:00', 'estimated_runway': '2022-11-08T01:07:00+00:00', 'actual_runway': '2022-11-08T01:07:00+00:00'}, 'arrival': {'airport': 'Kuala Lumpur International Airport (klia)', 'timezone': 'Asia/Kuala_Lumpur', 'iata': 'KUL', 'icao': 'WMKK', 'terminal': '1', 'gate': None, 'baggage': None, 'delay': 9, 'scheduled': '2022-11-08T06:00:00+00:00', 'estimated': '2022-11-08T06:00:00+00:00', 'actual': None, 'estimated_runway': None, 'actual_runway': None}, 'airline': {'name': 'Malaysia Airlines', 'iata': 'MH', 'icao': 'MAS'}, 'flight': {'number': '128', 'iata': 'MH128', 'icao': 'MAS128', 'codeshared': None}, 'aircraft': {'registration': '9M-MTF', 'iata': 'A333', 'icao': 'A333', 'icao24': '750259'}, 'live': {'updated': '2022-11-07T14:21:44+00:00', 'latitude': -36.81, 'longitude': 143.71, 'altitude': 6751.32, 'direction': 324, 'speed_horizontal': 803.768, 'speed_vertical': 0, 'is_ground': False}}]
        self.test.print_results(self.jarvis_api,flights,2)
        self.assertEqual(
            self.history_say().view_text(1),
            {"Flight status: active"}
        )
if __name__ == '__main__':
    unittest.main()

import unittest
from tests import PluginTest  
from plugins.flights import Flights


class FlightTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(Flights)

    def test_TESTCASE_1(self):
        # run code
        self.test.run('flights')
         
        # verify that code works
        self.assertEqual(self.history_say().last_text(), 'a')


if __name__ == '__main__':
    unittest.main()
"""