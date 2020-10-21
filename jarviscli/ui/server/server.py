import re

from flask import Flask

from jarvis import Jarvis
from language import snips


class ServerIO:
    def __init__(self):
        self.recorded_texts = []

    def say(self, text, color=''):
        self.recorded_texts.append(text)

    def input(self, prompt="", color=""):
        # TO IMPLEMENT PROBABLY LATER
        # because 'input' might be tricky to implement
        pass

    def exit(self):
        # STOP SERVER
        pass

    def fetch_recorded_texts(self):
        tmp = self.recorded_texts
        self.recorded_texts = []
        return tmp


class JarvisServer:

    def __init__(self):

        self.server_app = Flask(__name__)
        self.host_name = "0.0.0.0"
        self.port = 8008
        self.auth_string = "new String that I created just so I could access this just for myself"
        self.routes = [
            dict(route="/health", endpoint="/health", func=self._health)
        ]

    def start_server(self):
        print("Starting a thread for home server!")

        from main import build_plugin_manager
        plugin_manager = build_plugin_manager()
        language_parser = snips.LanguageParser()
        jarvis_server = JarvisServer()
        self.io = ServerIO()

        self.jarvis = Jarvis(language_parser, plugin_manager, jarvis_server)
        self.jarvis.register_io(self.io)

        self.server_app.run(host=self.host_name, port=self.port, threaded=True, debug=True, use_reloader=False)

    def check_running(self) -> bool:
        pass

    def init_server_endpoints(self, jarvis_plugins):

        self._get_all_routes(jarvis_plugins)

        for route in self.routes:
            try:
                self.server_app.add_url_rule(
                    route["route"],
                    route["endpoint"],
                    route["func"]
                )
            except Exception as e:
                print(e)

    def _wrap_plugin(self, plugin):
        def _run():
            plugin.run(self.jarvis.jarvis_api, '')
            _text = self.io.fetch_recorded_texts()
            print(_text)
            return '\n'.join(_text)
        return _run

    def _get_all_routes(self, jarvis_plugins):
        for plugin in jarvis_plugins:
            route = dict()
            endpoint_string = "/" + '_'.join(re.findall(r"[\w']+", plugin.get_name()))

            if len(plugin.get_plugins().values()) != 0:
                self._get_all_routes(plugin.get_plugins().values())
            else:
                route["route"] = endpoint_string
                route["endpoint"] = endpoint_string
                _plug = plugin
                route["func"] = self._wrap_plugin(plugin)
                self.routes.append(route)

    def _health(self):
        return "Healthy"
