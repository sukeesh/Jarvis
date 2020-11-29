from multiprocessing import Process

from plugin import Platform, plugin, require


@require(network=True, platform=Platform.MACOS)
@plugin("server start")
def server_start(jarvis, s):
    if s != "":
        if ":" in s:
            server_host, port = s.split(":")[0], int(s.split(":")[1])
        else:
            server_host, port = s.split(" ")[0], int(s.split(" ")[1])
        jarvis.update_data('SERVER_HOSTNAME', server_host)
        jarvis.update_data('SERVER_PORT', port)

    jarvis.activate_frontend('server')


@require(network=True, platform=Platform.MACOS)
@plugin("server stop")
def server_stop(jarvis, s):
    jarvis.deactivate_frontend('server')


@require(network=True, platform=Platform.MACOS)
@plugin("server restart")
def server_restart(jarvis, s):
    jarvis.deactivate_frontend('server')
    jarvis.activate_frontend('server')
