from plugin import plugin
import random
import tkinter as tk
import math


def create_wheel(sectors):
    """
    Creates GUI of a spinwheel and closes the window after 5 seconds.

    """
    # Define the size of the canvas and the radius of the wheel
    canvas_width = 500
    canvas_height = 500
    wheel_radius = min(canvas_width, canvas_height) * 0.4
    rgb_range = range(0, 256)

    # Create a tkinter window and canvas
    root = tk.Tk()
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
    canvas.pack()

    # Calculate the angle for each sector
    num_sectors = len(sectors)
    num_colors = num_sectors
    sector_angle = 360 / num_sectors
    get_colors = lambda n: ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(n)]
    colors = get_colors(num_colors)

    # Draw the sectors of the wheel
    start_angle = 0
    for i in range(num_sectors):
        end_angle = start_angle + sector_angle
        center_x = canvas_width / 2 + (wheel_radius / 2) * math.cos(math.radians(start_angle + sector_angle / 2))
        center_y = canvas_height / 2 - (wheel_radius / 2) * math.sin(math.radians(start_angle + sector_angle / 2))
        canvas.create_arc((canvas_width / 2 - wheel_radius, canvas_height / 2 - wheel_radius,
                           canvas_width / 2 + wheel_radius, canvas_height / 2 + wheel_radius),
                          start=start_angle, extent=sector_angle, fill=colors[i], outline='black',
                          width=2, style='pie')
        canvas.create_text(center_x, center_y, text=sectors[i], font=('Arial', 12, 'bold'))
        start_angle = end_angle

    # Draw an arrow pointing to the center of the circle
    # Calculate the angle for the selected sector
    selected_sector = sectors.index(spinit(sectors))
    selected_angle = selected_sector * sector_angle + sector_angle / 2

    # Calculate the coordinates of the base of the arrow
    arrow_base_x = canvas_width / 2
    arrow_base_y = canvas_height / 2

    # Calculate the coordinates of the tip of the arrow
    arrow_tip_x = arrow_base_x + (wheel_radius * 0.4) * math.sin(math.radians(selected_angle))
    arrow_tip_y = arrow_base_y - (wheel_radius * 0.4) * math.cos(math.radians(selected_angle))

    # Draw the arrow
    canvas.create_line(arrow_base_x, arrow_base_y, arrow_tip_x, arrow_tip_y, fill='red', width=10, arrow='last',
                       arrowshape=(15, 20, 5))

    # Schedule the window to close after 5 seconds
    root.after(3000, root.destroy)

    # Start the tkinter event loop
    root.mainloop()

def spinit(list):
    """
    Returns a random element from the list towards which the arrow will point
    """
    return random.choice(list)


@plugin("spinwheel")
def spin(jarvis, s):
    """
    \nThis code picks one of the random inputs given by the user
    smilar to spin wheel

    """
    jarvis.say(' ')
    jarvis.say('welcome to spin the wheel\n')
    jarvis.say('enter the number of elements in the wheel')
    num = jarvis.input_number()
    jarvis.say('enter the elements one after another\n')
    wheel = []
    for i in range(0, int(num)):
        entry = jarvis.input()
        wheel.append(entry)
    reply = 'y'
    while reply == 'y':
        create_wheel(wheel)
        print('Do you want to spin again?? press:y ')
        reply = input()
    print("Thank you for trying spin wheel ")
    jarvis.say("Thank you for trying spin wheel ")
