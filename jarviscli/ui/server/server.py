from flask import Flask
import re


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

    def start_server(self):
        print("Starting a thread for home server!")
        self.server_app.run(host=self.host_name, port=self.port, threaded=True, debug=True, use_reloader=False)

    def check_running(self) -> bool:
        pass

    def init_server_endpoints(self, jarvis, jarvis_plugins):

        self._get_all_routes(jarvis_plugins)

        for route in self.routes:
            self.server_app.add_url_rule(
                route["route"],
                route["endpoint"],
                route["func"],
                (jarvis, "")
            )

    def _get_all_routes(self, jarvis_plugins):
        for plugin in jarvis_plugins:
            route = dict()
            endpoint_string = "/" + '_'.join(re.findall(r"[\w']+", plugin.get_name()))

            # handle sub commands (recursive)
            if len(plugin.get_plugins().values()):
                self._get_all_routes(plugin.get_plugins().values())
            else:
                route["route"] = endpoint_string
                route["endpoint"] = endpoint_string
                route["func"] = plugin.run
                self.routes.append(route)

    def _health(self):
        return "Healthy"


# Let's see if adding a separate class for
class IO(JarvisServer):

    def __init__(self):
        super.__init__()

    def say(self, text, color=''):
        # TO IMPLEMENT FIRST
        pass

    def input(self, prompt="", color=""):
        # TO IMPLEMENT PROBABLY LATER
        # because 'input' might be tricky to implement
        pass

    def exit(self):
        # STOP SERVER
        pass
