import os
import sys

from jarvis import Jarvis
from plugin_manager import PluginManager


def assert_python_version():
    if sys.version_info[0] != 3:
        print("Sorry! Only Python 3 supported.")
        sys.exit('-1')


def build_jarvis():
    from language import snips

    language_parser = snips.LanguageParser()
    if 'ANDROID_ARGUMENT' in os.environ:
        import frontend.gui.android_plugins
        plugin_manager = frontend.gui.android_plugins.build_plugin_manager()
    else:
        plugin_manager = build_plugin_manager()
    return Jarvis(language_parser, plugin_manager)


def start(args, jarvis):
    if args.server_hostname is not None:
        jarvis.update_data('SERVER_HOSTNAME', args.server_hostname)
    if args.server_port is not None:
        jarvis.update_data('SERVER_PORT', args.server_port)

    if args.enable_cli:
        jarvis.activate_frontend('cli')
    if args.enable_server:
        jarvis.activate_frontend('server')
    voice = jarvis.get_data('voice_status')
    if args.enable_voice or voice and not args.disable_voice:
        jarvis.activate_frontend('voice')
    if args.enable_voice_control:
        jarvis.activate_frontend('voice_control')
    if args.enable_gui:
        gui_selection = select_gui_framework()
        if gui_selection == 1:
            jarvis.activate_frontend('gui')
        elif gui_selection == 2:
            start_pyqt5_gui(jarvis)

    if len(args.CMD) == 0:
        jarvis.run()
    else:
        jarvis.execute_once(' '.join(args.CMD))


def start_cli(jarvis):
    from frontend.cmd_interpreter import CmdInterpreter
    cmd_interpreter = CmdInterpreter(jarvis)

    command = " ".join(sys.argv[1:]).strip()
    cmd_interpreter.executor(command)


def start_gui(jarvis):
    from ui.gui.application import JarvisApp
    jarvis_gui = JarvisApp(jarvis)
    jarvis_gui.run()


def select_gui_framework():
    while True:
        print("\nWith which GUI framework would you like to run Jarvis?\n")
        print("1. Run Jarvis with Kivy Framework.")
        print("2. Run Jarvis with PyQt5 Framework.")
        try:
            gui_selection = int(input("Gui Selection: "))
        except ValueError as err:
            print("Please enter an invalid input as integer! (e.g: 1)")
            continue
        if gui_selection == 1 or gui_selection == 2:
            return gui_selection
        else:
            print("Please select an option in the list!")


def start_pyqt5_gui(jarvis):
    from frontend.pyqt5_gui.custom_circle_widget import OpenGLWidget
    from frontend.pyqt5_gui.utils import trace_function
    from PyQt5.QtWidgets import QApplication
    from threading import Thread
    from PyQt5.QtCore import Qt

    sys.argv = [sys.argv[0]]
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    a = QApplication(sys.argv)
    w = OpenGLWidget()

    jarvis.say = trace_function(jarvis.say, w)
    jarvis_run_thread = Thread(target=jarvis.run)
    jarvis_run_thread.start()

    w.show()
    sys.exit(a.exec_())


def build_plugin_manager():
    directories = ["jarviscli/core", "jarviscli/plugins", "custom", 'marketplace']
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
    import nltk
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
    assert_python_version()
    start_gui(build_jarvis)
