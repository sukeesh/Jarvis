from plugin import Platform, feature, plugin, require


@require(platform=Platform.SERVER)
@plugin("wifi device introduce")
def wifi_device_introduce(jarvis, s, body):
    print(s)
    print(body)
