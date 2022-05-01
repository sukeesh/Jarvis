from tests import PluginTest
from plugins.name_day import NameDay
import requests


class TestNameDay(PluginTest):
    def setUp(self):
        self.plugin = self.load_plugin(NameDay)
        self.plugin.location = "Greece"
        self.plugin.jarvis = self.jarvis_api

    def test_request_response(self):
        response = requests.get("https://nameday.abalin.net/api/V1/today")
        self.assertTrue(response.ok)

    def test_a_specific_date_from_the_api(self):
        # 17th of March in Greece
        response = requests.get("https://nameday.abalin.net/api/V1/getdate?country=gr&day=17&month=3")
        response_body = response.json()
        self.assertTrue("Alexios" in response_body["nameday"]["gr"])

    def test_request_status(self):
        request = requests.get("https://nameday.abalin.net/api/V1/today")
        self.assertEqual(request.status_code, 200)

    def test_request_response_body(self):
        response = requests.get("https://nameday.abalin.net/api/V1/getdate?day=18&month=11")
        response_body = response.json()
        expected = {
            "day": 18,
            "month": 11,
            "nameday": {
                "fi": "Tenho",
                "bg": "n/a",
                "us": "Odelia, Odell, Odo, Sutherland, Sutton",
                "hr": "Posveta Bazilike sv. Petra i Pavla",
                "es": "Aurelio",
                "dk": "Hesychius",
                "it": "Dedicazione Delle Basiliche Dei Santi Pietro E Paolo",
                "lt": "Ginvydas, Ginvyde, Otonas, Romanas, Salomeja",
                "gr": "Platonas",
                "fr": "Aude",
                "hu": "Jenő",
                "at": "Odo, Philippine",
                "lv": "Aleksandrs, Doloresa",
                "de": "Alda, Bettina, Odo, Roman",
                "ru": "n/a",
                "pl": "Aniela, Cieszymysł, Klaudyna, Roman, Tomasz",
                "sk": "Eugen",
                "se": "Magnhild",
                "cz": "Romana",
                "ee": "Ilo, Ilu"
            }
        }
        self.assertEqual(response_body, expected)

    def test_today(self):
        self.plugin.today()
        request = requests.get("https://nameday.abalin.net/api/V1/today", params={"country": "gr"})
        request_body = request.json()["nameday"]["gr"]
        if request_body != "n/a":
            self.assertEqual(self.history_say().last_text(), "Say some kind words to " + request_body)
        else:
            self.assertEqual(self.history_say().last_text(),
                             "No name days today in " + str(self.plugin.location))

    def test_tomorrow(self):
        self.plugin.tomorrow()
        request = requests.get("https://nameday.abalin.net/api/V1/tomorrow", params={"country": "gr"})
        request_body = request.json()["nameday"]["gr"]
        if request_body != "n/a":
            self.assertEqual(self.history_say().last_text(), "Say some kind words to " + request_body)
        else:
            self.assertEqual(self.history_say().last_text(),
                             "No name days for tomorrow in " + str(self.plugin.location))

    def test_specific_date(self):
        day = 15
        month = 11
        self.queue_input(str(day) + "/" + str(month))
        self.plugin.specific_date()
        request = requests.get("https://nameday.abalin.net/api/V1/getdate", params={"day": day, "month": month})
        request_body = request.json()["nameday"]["gr"]
        if request_body != "n/a":
            self.assertEqual(self.history_say().last_text(), "Say some kind words to "
                             + request_body + " on " + str(day) + "/" + str(month))
        else:
            self.assertEqual(self.history_say().last_text(),
                             "No name days at " + str(day) + "/" + str(month) + " in " + self.plugin.location)

    def test_specific_name(self):
        name = "Alexios"
        name_day_of_name = "17/3"
        self.queue_input(name)
        self.plugin.specific_name()
        self.assertIn(self.history_say().last_text(),
                      ("Say some kind words to " + name + " at " + name_day_of_name, "No name days found for " + name))
