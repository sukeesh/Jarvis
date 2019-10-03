# Jarvis

[![Build Status](https://travis-ci.org/sukeesh/Jarvis.svg?branch=master)](https://travis-ci.org/sukeesh/Jarvis) [![Join the chat at https://gitter.im/Sukeesh_Jarvis/Lobby](https://badges.gitter.im/Sukeesh_Jarvis/Lobby.svg)](https://gitter.im/Sukeesh_Jarvis/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

A Personal Assistant for Linux, MacOS and Windows

![Jarvis](http://i.imgur.com/xZ8x9ES.jpg)

Jarvis is a simple personal assistant for Linux, MacOS and Windows which works on the command line. He can talk to you if you enable his voice. He can tell you the weather, he can find restaurants and other places near you. He can do some great stuff for you.

## Getting Started

In order to start Jarvis just clone [this repository](https://github.com/sukeesh/Jarvis.git) and run `./setup.sh`

Run **Jarvis** from anywhere by command `jarvis`

On Mac OS X run `source setup.sh`

On Windows run `setup.bat`

You can start by typing `help` within the Jarvis command line to check what Jarvis can do for you.


## Youtube Video Showing Jarvis

[Click here](https://www.youtube.com/watch?v=PR-nxqmG3V8)

## Contributing

- PRs are accepted!!
- We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines. Before making a PR, make sure that your code is according to PEP 8 standards.
- If you have some ideas for new features and you don't have time to implement them please open an issue with the tag new_feature
- Please don't forget to comment (document) your code



### QuickStart: Create a new feature (plugin)

Create new file custom/hello_world.py

```
from plugin import plugin


@plugin("helloworld")
def helloworld(jarvis, s):
    """Repeats what you type"""
    jarvis.say(s)
```

Check it out!
```
./jarvis
Jarvis' sound is by default disabled.
In order to let Jarvis talk out loud type: enable sound
Type 'help' for a list of available actions.

~> Hi, what can I do for you?
helloworld Jarvis is cool!
jarvis is cool
```

### Plugins

[Click here](doc/PLUGINS.md) to learn more about plugins.

### Creating a test

Creating a test is optional but never a bad idea ;).

[Click here](doc/TESTING.md) to learn more about testing.

### How to run tests:

 Run `test.sh`
 ```bash
 ./test.sh
 ```
## Optional Dependencies

- Any pyttsx3 text-to-speech engine (``sapi5, nsss or espeak``) for Jarvis to talk out loud (e.g. Ubuntu do ``sudo apt install espeak``)
- Portaudio + python-devel packages for voice control
- ``notify-send`` on Linux if you want to receive *nice* and desktop-notification instead of *ugly* pop up windows (e.g. Ubuntu do ``sudo apt install libnotify-bin``)
- ``ffmpeg`` if you want ``music`` to download songs as .mp3 instead of .webm

## Docker

Run with docker (docker needs to be installed and running):

```
[sudo] make build_docker
[sudo] make run_docker
```

## Authors

 **sukeesh**

See also the list of [contributors](https://github.com/sukeesh/Jarvis/graphs/contributors) who have participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
