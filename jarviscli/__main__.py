# -*- coding: utf-8 -*-
import os
import subprocess
import sys

import colorama

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PLUGIN_DIR = os.path.join(BASE_DIR, 'jarviscli', 'plugins')
PLUGIN_FILE = os.path.join(BASE_DIR, 'plugins.txt')


def check_python_version():
    return sys.version_info[0] == 3


def load_plugins():
    import jarviscli
    from core.manifest import ManifestFile

    plugins = {}
    assert os.path.exists(
        PLUGIN_FILE), 'plugins.txt does not exist, run select plugins first'
    with open(PLUGIN_FILE) as reader:
        for file in reader.read().splitlines():
            file_path = os.path.join(PLUGIN_DIR, file)
            manifest = ManifestFile(file_path).verify()
            # import py file
            __import__('plugins.' + file.split('.')[0])
            plugins[manifest['name']] = jarviscli.loaded_entrypoint
    return plugins


def main():
    from core.jarvis import Jarvis

    # enable color on windows
    colorama.init()
    # start Jarvis
    jarvis = Jarvis(load_plugins(), ['cli'], 'default')

    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:]).strip()
        jarvis.executor_once(command)
    else:
        jarvis.run()


if __name__ == '__main__':
    if not os.path.exists(PLUGIN_FILE):
        subprocess.check_call(
            [sys.executable, os.path.join(BASE_DIR, 'jarviscli', 'core', 'plugin_selection.py')])
    if check_python_version():
        main()
    else:
        print("Sorry! Only Python 3 supported.")
