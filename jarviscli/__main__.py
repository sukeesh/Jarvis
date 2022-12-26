import argparse
import sys

import main

if __name__ == '__main__':
    main.assert_python_version()

    parser = argparse.ArgumentParser('Generate metadata json file')
    parser.add_argument('--offline', dest='offline', action='store_true')
    parser.add_argument('--enable-server', dest='enable_server', action='store_true')
    parser.add_argument('--disable-server', dest='disable_server', action='store_true')
    parser.add_argument('--enable-gui', dest='enable_gui', nargs=1, type=str, default='')
    parser.add_argument('--enable-tts', dest='enable_tts', action='store_true')
    parser.add_argument('--disable-tts', dest='disable_tts', action='store_true')
    parser.add_argument('--enable-voice-control', dest='enable_voice_control', action='store_true')
    parser.add_argument('--disable-voice-control', dest='disable_voice_control', action='store_true')
    parser.add_argument('--disable-cli', dest='disable_cli', action='store_true')
    parser.add_argument('--server-hostname', dest='server_hostname', nargs=1, default=None)
    parser.add_argument('--server-port', dest='server_port', nargs=1, default=None)
    parser.add_argument('--quality-level', dest='quality', type=int,  default=1)
    parser.add_argument('CMD', type=str, nargs='*')
    args = parser.parse_args()
    sys.argv = sys.argv[0]

    if isinstance(args.enable_gui, list):
        if len(args.enable_gui) > 0:
            args.enable_gui = args.enable_gui[0]
        else:
            args.enable_gui = ''

    possible_gui_arguments = ['pygame', 'kiyv', '']
    assert args.enable_gui in possible_gui_arguments

    jarvis = main.build_jarvis(args)

    main.start(args, jarvis)
