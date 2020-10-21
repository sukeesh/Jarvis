import colorama
import kivy
from kivy.utils import platform

_JARVIS_APP = None


def app():
    return _JARVIS_APP


def main():
    from jarvisgui.application import JarvisApp, JarvisGuiAPI
    from jarviscli.Jarvis import Jarvis

    # enable color on windows
    colorama.init()
    # start Jarvis
    if platform == 'android':
        from jarvisgui.android_plugins import build_plugin_manager
    else:
        from jarviscli import build_plugin_manager

    plugin_manager = build_plugin_manager()
    jarviscli = Jarvis(plugin_manager, jarvis_api_class=JarvisGuiAPI)
    jarvisgui = JarvisApp(jarviscli)
    global _JARVIS_APP
    _JARVIS_APP = jarvisgui

    jarvisgui.run()


if __name__ == '__main__':
    main()
