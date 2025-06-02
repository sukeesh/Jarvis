import re
from plugin import plugin
from colorsys import rgb_to_hls, hls_to_rgb

# HEX to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# RGB to HEX
def rgb_to_hex(rgb_color):
    return '#%02x%02x%02x' % rgb_color

# RGB to HSL
def rgb_to_hsl(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, l, s = rgb_to_hls(r, g, b)
    return int(h * 360), int(s * 100), int(l * 100)

# HSL to RGB
def hsl_to_rgb(h, s, l):
    h, s, l = h / 360.0, s / 100.0, l / 100.0
    r, g, b = hls_to_rgb(h, l, s)
    return int(r * 255), int(g * 255), int(b * 255)

# Convert RGB to ANSI escape code
def rgb_to_ansi(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

# Reset ANSI color
RESET_COLOR = '\033[0m'

@plugin('colorconverter')
def color_converter(jarvis, s):
    """
    Convert colors between HEX, RGB, and HSL formats.

    This plugin interacts with the user to choose the input color format 
    and the desired output format.
    """
    # Ask origin format
    jarvis.say("Please choose the original format (rgb, hsl, hex): ")
    original_format = input().strip().lower()

    if original_format not in ['rgb', 'hsl', 'hex']:
        jarvis.say("Invalid format. Please choose between 'rgb', 'hsl', or 'hex'.")
        return

    # Ask convert format
    jarvis.say("Please choose the target format (rgb, hsl, hex): ")
    target_format = input().strip().lower()

    if target_format not in ['rgb', 'hsl', 'hex']:
        jarvis.say("Invalid format. Please choose between 'rgb', 'hsl', or 'hex'.")
        return

    if original_format == target_format:
        jarvis.say("The original and target formats are the same. Nothing to convert.")
        return

    # Enter the color value
    jarvis.say(f"Please enter the color value in {original_format.upper()}: ")
    color_value = input().strip()

    # HEX conversion
    if original_format == 'hex':
        if not re.match(r'^#?[0-9a-fA-F]{6}$', color_value):
            jarvis.say("Invalid HEX color format.")
            return
        rgb = hex_to_rgb(color_value)
        ansi_color = rgb_to_ansi(*rgb)
        if target_format == 'rgb':
            jarvis.say(f"{ansi_color}RGB: {rgb}{RESET_COLOR}")
        elif target_format == 'hsl':
            hsl = rgb_to_hsl(*rgb)
            jarvis.say(f"{ansi_color}HSL: {hsl}{RESET_COLOR}")

    # RGB conversion
    elif original_format == 'rgb':
        try:Ò
            rgb = tuple(map(int, color_value.split(',')))
            if any(not (0 <= x <= 255) for x in rgb):
                raise ValueError
        except ValueError:
            jarvis.say("Invalid RGB format. Please provide as R,G,B (0-255).")
            return
        ansi_color = rgb_to_ansi(*rgb)
        if target_format == 'hex':
            hex_color = rgb_to_hex(rgb)
            jarvis.say(f"{ansi_color}HEX: {hex_color}{RESET_COLOR}")
        elif target_format == 'hsl':
            hsl = rgb_to_hsl(*rgb)
            jarvis.say(f"{ansi_color}HSL: {hsl}{RESET_COLOR}")

    # HSL conversion
    elif original_format == 'hsl':
        try:
            hsl = tuple(map(int, color_value.split(',')))
            if not (0 <= hsl[0] <= 360) or not (0 <= hsl[1] <= 100) or not (0 <= hsl[2] <= 100):
                raise ValueError
        except ValueError:
            jarvis.say(
                "Invalid HSL format. Please provide as H,S,L (0-360, 0-100, 0-100)."
            )
            return
        rgb = hsl_to_rgb(*hsl)
        ansi_color = rgb_to_ansi(*rgb)
        if target_format == 'rgb':
            jarvis.say(f"{ansi_color}RGB: {rgb}{RESET_COLOR}")
        elif target_format == 'hex':
            hex_color = rgb_to_hex(rgb)
            jarvis.say(f"{ansi_color}HEX: {hex_color}{RESET_COLOR}")
