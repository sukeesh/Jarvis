import json
import requests
from plugin import plugin, alias
from colorama import Fore

USER_THEME_FILEPATH = "jarviscli/data/user_theme.json"
NUM_OPTIONS = 6  # Specifies the number of different color options


@alias("switch themes")
@alias("change themes")
@alias("switch theme")
@alias("change theme")
@alias("switch colours")
@alias("change colours")
@alias("switch colour")
@alias("change colour")
@alias("switch colors")
@alias("change colors")
@alias("switch color")
@plugin("change color")

def change_color(jarvis, s):
    """The user will first input whether or not they want to use a preset theme,
    and the plugin will provide a selection of themes. If not, the user is then
    prompted to create their own custom theme, which persists."""

    f = open(USER_THEME_FILEPATH)
    data = json.load(f)
    theme = data['current']
    options = list(theme.keys())

    color_dict = {
        "black": Fore.BLACK,
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "reset": Fore.RESET,
    }

    use_preset = jarvis.input(
        "Use a preset theme? (y/n): ",
        color=theme['greeting']
    )

    # @TODO YES to preset theme
    if (use_preset.lower() == 'y'):
        presets = list(data.keys())
        jarvis.say(
            theme['default_text']
            + "\nSupported themes are:\n"
            + theme['info']
            + ', '.join(presets[1:])
        )
        choice = jarvis.input(
            "So...what'll it be?\n",
            color=theme['default_text']
        )

        if (choice in presets):
            data['current'] = data[choice]
            with open("custom/user_theme.json", 'w') as new_json:
                json.dump(data, new_json)

            jarvis.say("Preset selected!\n",
                    color=theme['positive_text'])
        else:
            jarvis.say("Invalid option. Please try again",
                        color=theme['negative_text'])


    # NO to preset theme
    elif (use_preset.lower() == 'n'):
        use_custom = jarvis.input(
            "Customize the current theme? (y/n): ",
            color=theme['greeting']
        )

        # YES to customizing theme
        if (use_custom.lower() == 'y'):
            supported_colors = ""
            for key in color_dict.keys():
                supported_colors += color_dict[key] + key.upper() + ", "

            jarvis.say(
                theme['default_text']
                + "\nSupported colors are:\n"
                + supported_colors[:-2]
            )
            jarvis.say(
                theme['default_text']
                + "If you wish to skip an option, type "
                + theme['info'] + "'skip'.\n"
            )

            it = 0
            while (it < NUM_OPTIONS):
                cur_option = options[it]
                new_color = jarvis.input(
                    "New color for "
                    + cur_option
                    + ": ",
                    color=theme[cur_option])

                if (new_color.lower() in color_dict):
                    theme[cur_option] = color_dict[new_color.lower()]
                    it = it + 1

                elif (new_color.lower() == "skip"):
                    it = it + 1

                else:
                    jarvis.say("Invalid option. Please try again",
                               color=theme['negative_text'])

            data['current'] = theme

            with open("custom/user_theme.json", 'w') as new_json:
                json.dump(data, new_json)

            jarvis.say("All done! Enjoy your new theme!\n",
                       color=theme['positive_text'])

        # NO to customizing theme (END)
        elif (use_custom.lower() == 'n'):
            jarvis.say("\n...I guess there's no pleasing you\n",
                       color=theme['negative_text'])

        # INVALID command (END)
        else:
            jarvis.say("Invalid input. Please try again.\n",
                       color=theme['negative_text'])

    # INVALID command (END)
    else:
        jarvis.say("Invalid input. Please try again.\n",
                   color=theme['negative_text'])
