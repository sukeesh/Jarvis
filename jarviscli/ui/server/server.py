from flask import Flask
import re


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

    class Route:

        def __init__(self, route, endpoint, function, plugin):
            self.route = route
            self.endpoint = endpoint
            self.function = function
            self.plugin = plugin

    def __init__(self):
        self.server_app = Flask(__name__)
        self.host_name = "192.168.1.234"
        self.port = 8008
        self.auth_string = "new String that I created just so I could access this just for myself"
        self.routes = [dict(route="/health", endpoint="/health", func=self._health)]

    def start_server(self, jarvis):
        print("Starting a thread for home server!")
        self.io = ServerIO()
        jarvis.server = self
        self.init_server_endpoints(jarvis, jarvis.plugin_manager.get_plugins().values())
        self.enable_server_plugins(jarvis)
        self.server_app.run(host=self.host_name, port=self.port, threaded=True, debug=True, use_reloader=False)

    def check_running(self) -> bool:
        pass

    def enable_server_plugins(self, jarvis):
        # TODO
        pass

    def init_server_endpoints(self, jarvis, jarvis_plugins):

        self._get_all_routes(jarvis, jarvis_plugins)
        print(self.routes)

        for route in self.routes:
            self.server_app.add_url_rule(
                route["route"],
                route["endpoint"],
                route["func"]
            )

    def _wrap_plugin(self, plugin, jarvis):
        def _run(s=''):
            plugin.run(jarvis, s)
            _text = self.io.fetch_recorded_texts()
            print(_text)
            return '\n'.join(_text)

        return _run

    def _get_all_routes(self, jarvis, jarvis_plugins):
        for plugin in jarvis_plugins:
            route = dict()
            endpoint_string = "/" + '_'.join(re.findall(r"[\w']+", plugin.get_name()))

            # handle sub commands (recursive)
            if len(plugin.get_plugins().values()):
                self._get_all_routes(jarvis, plugin.get_plugins().values())
            else:
                route["route"] = endpoint_string
                route["endpoint"] = endpoint_string
                route["func"] = self._wrap_plugin(plugin, jarvis)
                self.routes.append(route)

    def _health(self):
        return "Healthy"
