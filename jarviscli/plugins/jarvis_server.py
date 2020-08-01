from multiprocessing import Process
from plugin import Platform, require, plugin


@require(network=True, platform=Platform.MACOS)
@plugin("server start")
def server_start(jarvis, s):
    jarvis_server = jarvis.get_server()

    if s != "":
        if ":" in s:
            jarvis_server.server_host, jarvis_server.port = s.split(":")[0], int(s.split(":")[1])
        else:
            jarvis_server.server_host, jarvis_server.port = s.split(" ")[0], int(s.split(" ")[1])

    jarvis.server_thread = Process(target=jarvis_server.start_server, args=(jarvis, ))
    jarvis.server_thread.start()


@require(network=True, platform=Platform.MACOS)
@plugin("server stop")
def server_stop(jarvis, s):
    if not hasattr(jarvis, "server_thread") or jarvis.server_thread is not None:
        jarvis.say("No server is running.")
        return
    # server.stop_server(jarvis)
    # print(jarvis.server_thread.isAlive())
    jarvis.server_thread.terminate()
    jarvis.server_thread.join()
    jarvis.server_thread = None


@require(network=True, platform=Platform.MACOS)
@plugin("server restart")
def server_restart(jarvis, s):
    server_stop(jarvis, s)
    server_start(jarvis, s)

#
#
# @require(network=True)
# @plugin("home server")
# class HomeServer(BaseHTTPRequestHandler):
#
#     def __init__(self, request, client_address, server):
#         super().__init__(request, client_address, server)
#         self.devices = dict()
#         self.app_logins = dict()
#
#     def do_POST(self):
#         if self.request_handler.headers["Auth"] != auth:
#             self._return_unauthorized()
#         else:
#             content_len = int(self.headers.get('Content-Length'))
#             device_type = self.headers.get('User-Agent')
#             post_body = self.rfile.read(content_len)
#             print(self.headers.get('Device-Agent') + " found!")
#             if device_type.contains("ESP8266"):
#                 self._register_device(self.headers, post_body)
#                 self._respond(200, '')
#             else:
#                 response_type = self._respond_to_agent(self.headers, post_body)
#                 if response_type == "Success":
#                     self._respond(200, response_type)
#                 elif response_type is not None:
#                     self._respond(404, response_type)
#
#     def _respond(self, code: int, message: str):
#         self.send_response(code)
#         self.send_header("Auth", auth)
#         self.end_headers()
#         self.wfile.write(message.encode('utf-8'))
#
#     def _register_device(self, headers, body):
#         agent = headers["Device-Agent"]
#         self.devices[agent] = dict(json.loads(body.decode('utf-8')))
#         self.devices[agent]["counter"] = 0
#         self.devices[agent]["connected"] = True
#         self.devices[agent]["thread"] = Thread(target=self._handle_heartbeat,
#                                                args=(agent,))
#         self.devices[agent]["thread"].start()
#
#     def _respond_to_agent(self, headers, body):
#         agent = headers["Device-Agent"]
#         self.app_logins[agent] = dict(json.loads(body.decode('utf-8')))
#         self.app_logins[agent]["connected"] = True
#         return self._handle_app_request(agent)
#
#     def _handle_app_request(self, agent: str):
#         app_request_type = self.app_logins[agent]["request_type"]
#
#         if app_request_type == 'intro':
#             return self._send_intro_to_app()
#
#         return self._respond_to_app_request(agent)
#
#     def _send_intro_to_app(self):
#         app_intro = dict()
#         app_intro["devices"] = self.get_connected_devices()
#         app_intro["users"] = self.get_connected_users()
#         return json.dumps(app_intro)
#
#     def _respond_to_app_request(self, agent: str):
#         app_request = self.app_logins[agent]["request"]
#         device = app_request["device"]
#         device_switch = app_request["switch"]
#         device_switch_request = device_switch["request"]
#         device_switch_value = device_switch["value"]
#         if not self.devices[device]["connected"]:
#             return "Device disconnected"
#         device_url = self.devices[device]["localIP"]
#         device_headers = dict({"Auth": auth})
#
#         try:
#             request = requests.get(device_url + "/" + device_switch_request +
#                                    "/" + device_switch_value, headers=device_headers)
#         except requests.exceptions.ConnectionError as ce:
#             print("Device Connection Error: " + agent)
#             self.devices[agent]["connected"] = False
#             return "Device disconnected"
#         return "Success"
#
#     def _handle_heartbeat(self, agent: str):
#         device_url = self.devices[agent]["localIP"]
#         while self.devices[agent]["connected"]:
#             device_headers = dict({"Auth": auth})
#             try:
#                 request = requests.get(device_url + "/heartbeat",
#                                        headers=device_headers)
#                 self.devices[agent]["counter"] = 0
#             except requests.exceptions.ConnectionError as ce:
#                 print(ce)
#                 print("Device Connection Error: " + agent)
#                 self.devices[agent]["counter"] += 1
#                 if self.devices[agent]["counter"] >= 3:
#                     self.devices[agent]["connected"] = False
#             time.sleep(5)
#
#     def get_connected_devices(self):
#         connected_devices = [device for device in self.devices.keys()
#                              if self.devices[device]["connected"]]
#         print(connected_devices)
#         return connected_devices
#
#     def get_connected_users(self):
#         connected_users = [user for user in self.app_logins.keys()
#                            if self.app_logins[user]["connected"]]
#         return connected_users
#
#     def _return_unauthorized(self):
#         self.send_response(403)
#         self.send_header("Status Code", 403)
#         self.end_headers()
#         self.wfile.write(b'Unauthorized')
#
#
# @require(network=True, platform=MACOS)
# @plugin('home server start')
# def home_server(jarvis, s):
#     web_server = HTTPServer((hostName, serverPort), HomeServer)
#     web_server.serve_forever()
#     jarvis.say("Server started http://%s:%s" % (hostName, serverPort))
#
#
# @require(network=True, platform=MACOS)
# @plugin('home server connections')
# def home_server_get_connections(jarvis, s):
#     if web_server is None:
#         jarvis.say("Unable to find a running server. Did you start a Server ?")
#         return
#     connections = dict()
#     connections["devices"] = web_server.get_connected_devices()
#     connections["users"] = web_server.get_connected_users()
#     return json.dumps(connections)
#
#
# @require(network=True, platform=MACOS)
# @plugin('home server stop')
# def home_server_stop(jarvis, s):
#     if web_server is None:
#         jarvis.say("Unable to stop server. Did you start a Server ?")
#         return
#     web_server.server_close()
#     jarvis.say("Server killed!")
