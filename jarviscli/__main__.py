import argparse
import sys

import main

if __name__ == '__main__':
    main.assert_python_version()

    parser = argparse.ArgumentParser('Generate metadata json file')
    parser.add_argument('--offline', dest='offline', action='store_true')
    parser.add_argument('--enable-server', dest='enable_server', action='store_true')
    parser.add_argument('--disable-server', dest='disable_server', action='store_true')
    parser.add_argument('--enable-gui', dest='enable_gui', action='store_true')
    parser.add_argument('--disable-gui', dest='disable_gui', action='store_true')
    parser.add_argument('--enable-tts', dest='enable_tts', action='store_true')
    parser.add_argument('--disable-tts', dest='disable_tts', action='store_true')
    parser.add_argument('--enable-voice-control', dest='enable_voice_control', action='store_true')
    parser.add_argument('--disable-voice-control', dest='disable_voice_control', action='store_true')
    parser.add_argument('--disable-cli', dest='disable_cli', action='store_true')
    parser.add_argument('--server-hostname', dest='server_hostname', nargs=1, default=None)
    parser.add_argument('--server-port', dest='server_port', nargs=1, default=None)
    parser.add_argument('CMD', type=str, nargs='*')
    args = parser.parse_args()
    sys.argv = sys.argv[0]

    jarvis = main.build_jarvis()

    main.start(args, jarvis)
