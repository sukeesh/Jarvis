import re

from flask import Flask


class JarvisServer:
    QUALITY = 1

    def __init__(self, jarvis):
        self.jarvis = jarvis

        self.server_app = Flask(__name__)
        self.host_name = jarvis.get_data('SERVER_HOSTNAME')
        if self.host_name is None:
            self.host_name = '0.0.0.0'
        self.port = jarvis.get_data('SERVER_PORT')
        if self.port is None:
            self.port = 8080

        self.auth_string = "new String that I created just so I could access this just for myself"
        self.routes = [
            dict(route="/health", endpoint="/health", func=self._health)
        ]

        self.init_server_endpoints(jarvis_plugins=jarvis.get_plugins().values())
        self.recorded_texts = []

    def get_name():
        return 'Remote frontend'

    def say(self, text, color=''):
        self.recorded_texts.append(text)

    def prompt(self):
        pass

    def input(self, prompt="", color=""):
        # TO IMPLEMENT PROBABLY LATER
        # because 'input' might be tricky to implement
        pass

    def start(self):
        self.jarvis.say("Starting a thread for home server!")
        self.server_app.run(host=self.host_name, port=self.port, threaded=True, debug=True, use_reloader=False)

    def stop(self):
        # STOP SERVER
        pass

    def fetch_recorded_texts(self):
        tmp = self.recorded_texts
        self.recorded_texts = []
        return tmp

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
            plugin.run(self.jarvis, '')
            _text = self.fetch_recorded_texts()
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
