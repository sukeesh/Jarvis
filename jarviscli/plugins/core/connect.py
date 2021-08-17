from plugin import alias, plugin


@alias("reconnect")
@plugin('connect')
def connect(jarvis, s):
    """Recheck internet connect"""
    if jarvis.offline_only:
        jarvis.say('Cannot connect in offline mode')
        return
    jarvis.online_status.refresh()
    if jarvis.online_status.get_online_status():
        jarvis.say('Connected.')
    else:
        jarvis.say('It seems like I\'m not connected to the Internet.')
