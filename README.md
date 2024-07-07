# Jarvis

[![Build Status](https://travis-ci.org/sukeesh/Jarvis.svg?branch=master)](https://travis-ci.org/sukeesh/Jarvis) [![Join the chat at https://gitter.im/Sukeesh_Jarvis/Lobby](https://badges.gitter.im/Sukeesh_Jarvis/Lobby.svg)](https://gitter.im/Sukeesh_Jarvis/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

A Personal Assistant for Linux, MacOS and Windows

![Jarvis](http://i.imgur.com/xZ8x9ES.jpg)

Jarvis is a simple personal assistant for Linux, MacOS and Windows which works on the command line. He can talk to you if you enable his voice. He can tell you the weather, he can find restaurants and other places near you. He can do some great stuff for you.

## 20 Different Tasks That Jarvis Can Do For You ("Plugin Name" Included)
1. Suggest a random activity for you to do if you're bored ("activity", "bored")
2. Give ideas for what to draw, watch, do, listen to (“prompt”, “top_media”, “taste dive”, “mood music”)
3. Receive up-to-date information about different sports such as team ranking, match starts times, player stats ( “basketball” , “cricket”, “soccer”, “tennis”)
4. Play games (“blackjack”, “connect_four”, “guess_number_game”, “hangman”, “rockpaperscissors”. “roulette”, “tic_tac_toe”,”word_game”, “wordle”)
5. Help you stay fit by giving food nutrition facts, recipes, workout programs, and health trackers (“bmi”, “bmr”, “calories”, “food recipe”, “fruit”, “fruit nutrition”, “workout”)
6. Teach you how to make a cocktail (“cocktail”, “drink”)
7. Generate random lists, numbers, passwords (“random list”, “random number”, “random password”)
8. Perform conversions for binary numbers, money, hexadecimal numbers, distance, mass, speed, strings, temp, time (“binary”, “currencyconv”, “hex”, “lengthconv”, “massconv”, “speedconv”, “string_convert”, “tempconv”, “timveconv”)
9. Take pictures (“open camera”, “screencapture”)
10. Tell you different specifications for your current computer system (“battery”,  “cat his”, “dns forward”, “dns reverse”, “hostinfo”, “ip”, “scan_network”, “speedtest”, “os”, “check ram”, “systeminfo”)
11. Manage files on your computer (“file manage”, “file organize”
12. Upload, edit, and convert images (“imgur”, “image to pdg”,  “image compressor”)
13. Convert webpages to PDF or PDFs to images (“htmptopdg”, “pdf to images”)
14. Tell jokes (“dadjoke”, “joke daily”, “joke chuck”, “joke”) 
15. Perform arithmetic and calculations (“calculate”, “factor”, “solve”, “equations”, “plot”, “matrix add”)
16. Generate a QR code to attach to a URL (“qr”)
17. Check the weather (“weather report”)
18. Provide language translations (“translate”)
19. Tell random facts (“fact”, “cat fact”)
20. Display stock market information (“stock”, “cryptotracker”)

## Getting Started With Installation

In order to install Jarvis, follow these steps:
1. Clone [this repository](https://github.com/sukeesh/Jarvis.git) with `git clone https://github.com/sukeesh/Jarvis.git`
2. Run the command `python installer` (or `python3 installer` if that doesn't work) from the terminal.

Run **Jarvis** from anywhere by command `jarvis`, or `./jarvis` from within the project directory to start up Jarvis!

You can start by typing `help` within the Jarvis command line to check what Jarvis can do for you.

### Frequently encountered issues
**Question**: When I run Jarvis, it shows an error relating to module not found<br>
**Platform**: Windows<br>
**Solution 1**: Uninstall and/or install the module package<br>
Example:<br>
Error: `ImportError: DLL load failed while importing win32api: The specified module could not be found.`<br>
Solution:<br>
`pip uninstall pywin32`<br>
`pip install pywin32` or `conda install pywin32`<br>
**Solution 2**: add the package to your environment variables system PATH.<br>

**Question**: After cloning the repo in terminal it gives an error when running python3 installer saying please install virtual environemnt
**Solution**: 
- Install virtual env using this command "python3 -m pip install virtualenv"
- OR: On Linux use package manager (e.g. Ubuntu sudo apt install python3-venv)
- Restart Installer


If you find other issues and/or have found solutions to them on any platform, please consider adding to this list!

## Youtube Video Showing Jarvis

[Click here](https://www.youtube.com/watch?v=PR-nxqmG3V8)

## Contributing

Check out our [CONTRIBUTING.md](CONTRIBUTING.md) to learn how you can contribute!

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
