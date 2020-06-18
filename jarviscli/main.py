import os
import sys

import colorama

import nltk
from jarvis import Jarvis
from language import default
from plugin_manager import PluginManager


def check_python_version():
    return sys.version_info[0] == 3


def main_cli():
    from ui.cmd_interpreter import CmdInterpreter

    language_parser = default.DefaultLanguageParser()
    plugin_manager = build_plugin_manager()
    jarvis = Jarvis(language_parser, plugin_manager)
    cmd_interpreter = CmdInterpreter(jarvis)

    command = " ".join(sys.argv[1:]).strip()
    cmd_interpreter.executor(command)


def main_gui():
    from ui.gui.application import JarvisApp
    from kivy.utils import platform

    if platform == 'android':
        import uti.ui.android_plugins
        plugin_manager = util.ui.android_plugins.build_plugin_manager()
    else:
        plugin_manager = build_plugin_manager()

    language_parser = default.DefaultLanguageParser()
    jarvis = Jarvis(language_parser, plugin_manager)
    jarvis_gui = JarvisApp(jarvis)

    jarvis_gui.run()


def build_plugin_manager():
    directories = ["jarviscli/plugins", "custom"]
    directories = _rel_path_fix(directories)

    plugin_manager = PluginManager()

    for directory in directories:
        plugin_manager.add_directory(directory)
    return plugin_manager


def _rel_path_fix(dirs):
    dirs_abs = []
    work_dir = os.path.dirname(__file__)
    # remove 'jarviscli/' from path
    work_dir = os.path.dirname(work_dir)

    # fix nltk path
    nltk.data.path.append(os.path.join(work_dir, "jarviscli/data/nltk"))

    # relative -> absolute paths
    for directory in dirs:
        if not directory.startswith(work_dir):
            directory = os.path.join(work_dir, directory)
        dirs_abs.append(directory)
    return dirs_abs


def dump_android_plugins():
    with open('ui/gui/android_plugins.py', 'w') as writer:
        writer.write(build_plugin_manager().dump_android())


if __name__ == '__main__':
    if check_python_version():
        main_gui()
    else:
        print("Sorry! Only Python 3 supported.")
