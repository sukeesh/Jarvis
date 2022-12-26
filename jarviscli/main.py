import os
import sys

from jarvis import Jarvis
from plugin_manager import PluginManager


def assert_python_version():
    if sys.version_info[0] != 3:
        print("Sorry! Only Python 3 supported.")
        sys.exit('-1')


def build_jarvis(args):
    from language import snips

    language_parser = snips.LanguageParser
    if 'ANDROID_ARGUMENT' in os.environ:
        import frontend.gui.android_plugins
        plugin_manager = frontend.gui.android_plugins.build_plugin_manager()
    else:
        plugin_manager = build_plugin_manager()
    return Jarvis(language_parser, plugin_manager, args.quality)


def start(args, jarvis):
    if args.server_hostname is not None:
        jarvis.update_data('SERVER_HOSTNAME', args.server_hostname)
    if args.server_port is not None:
        jarvis.update_data('SERVER_PORT', args.server_port)
    if args.offline:
        jarvis.set_offline_mode()

    if args.enable_gui != '':
        jarvis.activate_frontend('gui_' + args.enable_gui)

    def startup(args_enable, args_disable, frontend_id):
        if args_disable:
            pass
        elif args_enable or jarvis.get_data('status_' + frontend_id) is True:
            jarvis.activate_frontend(frontend_id)

    startup(args.enable_server, args.disable_server, 'server')
    startup(args.enable_tts, args.disable_tts, 'tts')
    startup(args.enable_voice_control, args.disable_voice_control, 'voice_control')
    startup(True, args.disable_cli, 'cli')

    if len(args.CMD) == 0:
        jarvis.run()
    else:
        jarvis.eval(' '.join(args.CMD))


def start_cli(jarvis):
    from frontend.cmd_interpreter import CmdInterpreter
    cmd_interpreter = CmdInterpreter(jarvis)

    command = " ".join(sys.argv[1:]).strip()
    cmd_interpreter.executor(command)


def start_gui(jarvis):
    from ui.gui.application import JarvisApp
    jarvis_gui = JarvisApp(jarvis)
    jarvis_gui.run()


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
