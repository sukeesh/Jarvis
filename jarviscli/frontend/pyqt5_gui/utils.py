# -*- encoding: utf-8 -*-

"""

 * Author(s):    Ahmet Furkan YENİPINAR
 * Created:      24.08.2021
 * Title:        OpenGL Widget Class

"""

from dataclasses import dataclass
from threading import Thread
from math import sin, cos
import numpy as np
import functools


HORIZONTAL_DISPLAY: float = 1366.0
VERTICAL_DISPLAY: float = 768.0
M_PI = 3.14159265


@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


def normalize_value(value: float, r_min: float, r_max: float, t_min: float, t_max: float) -> float:
    normalized_value: float = (value - r_min) / (r_max - r_min) * (t_max - t_min) + t_min
    return normalized_value


def degree_to_radian(angle: float) -> float:
    return angle * M_PI / 180


def polar_to_cartesian(center_x: float, center_y: float, radius: float, angle: float) -> Point:
    radian: float = degree_to_radian(angle)
    x_radius_offset: float = HORIZONTAL_DISPLAY * 0.5 + radius
    x_radius: float = abs(normalize_value(x_radius_offset, 0, HORIZONTAL_DISPLAY, -1, 1))

    y_radius_offset: float = VERTICAL_DISPLAY * 0.5 + radius
    y_radius: float = abs(normalize_value(y_radius_offset, 0, VERTICAL_DISPLAY, -1, 1))

    point = Point()

    point.x = center_x + (x_radius * cos(radian))
    point.y = center_y + (y_radius * sin(radian))

    return point


def create_six_point_line(first_point: Point, second_point: Point, degree: float, thickness: float) -> np.array:
    """
        The 'create_six_point_line' function create a OpenGL line by taking two base points which one of them
        is one degree greater than another one.

        Parameters
        ----------
        first_point : Point
            The first base point.
        second_point: Point
            The second base point.
        degree: float
            The degree at which base points are created.
        thickness:  float
            The thickness determines how thick the line will be created.

    """
    line_points_container = np.array([])
    first_point_up = polar_to_cartesian(first_point.x, first_point.y, thickness, degree)
    first_point_down = polar_to_cartesian(first_point.x, first_point.y, thickness, 180 + degree)

    second_point_up = polar_to_cartesian(second_point.x, second_point.y, thickness, degree + 1)
    second_point_down = polar_to_cartesian(second_point.x, second_point.y, thickness, 180 + degree + 1)

    # Point 1
    line_points_container = np.append(line_points_container, first_point_down.x)
    line_points_container = np.append(line_points_container, first_point_down.y)
    line_points_container = np.append(line_points_container, first_point_down.z)
    # These 2 coordinates for texture coordinates.
    line_points_container = np.append(line_points_container, 0.0)
    line_points_container = np.append(line_points_container, 0.0)

    # Point 2
    line_points_container = np.append(line_points_container, first_point_up.x)
    line_points_container = np.append(line_points_container, first_point_up.y)
    line_points_container = np.append(line_points_container, first_point_up.z)

    line_points_container = np.append(line_points_container, 1.0)
    line_points_container = np.append(line_points_container, 0.0)

    # Point 3
    line_points_container = np.append(line_points_container, second_point_down.x)
    line_points_container = np.append(line_points_container, second_point_down.y)
    line_points_container = np.append(line_points_container, second_point_down.z)

    line_points_container = np.append(line_points_container, 0.0)
    line_points_container = np.append(line_points_container, 1.0)

    # Point 4
    line_points_container = np.append(line_points_container, first_point_up.x)
    line_points_container = np.append(line_points_container, first_point_up.y)
    line_points_container = np.append(line_points_container, first_point_up.z)

    line_points_container = np.append(line_points_container, 1.0)
    line_points_container = np.append(line_points_container, 0.0)

    # Point 5
    line_points_container = np.append(line_points_container, second_point_down.x)
    line_points_container = np.append(line_points_container, second_point_down.y)
    line_points_container = np.append(line_points_container, second_point_down.z)

    line_points_container = np.append(line_points_container, 0.0)
    line_points_container = np.append(line_points_container, 1.0)

    # Point 6
    line_points_container = np.append(line_points_container, second_point_up.x)
    line_points_container = np.append(line_points_container, second_point_up.y)
    line_points_container = np.append(line_points_container, second_point_up.z)

    line_points_container = np.append(line_points_container, 1.0)
    line_points_container = np.append(line_points_container, 1.0)

    return line_points_container


def trace_function(trace_target, action):

    @functools.wraps(trace_target)
    def trace_function_closure(*args, **kwargs):

        """ 
        The 'target_function_thread' indicates the target function to be traced.
        In this case the the target is the Jarvis.say method.
        """
        target_function_thread = Thread(target=trace_target, args=(*args,))

        """ 
        The 'action_thread' runs when the target_function_thread is called and last until the call is finished.
        In this case the the target is the Jarvis.say method.
        """
        action_thread = Thread(target=action.update_with_timer)
        action.update_control = True

        target_function_thread.start()
        action_thread.start()

        target_function_thread.join()
        if target_function_thread.is_alive() is False:
            action.update_control = False
            action_thread.join()

        # The tracing target information can be used by uncommenting the below code for debug purposes.
        # print(f"{trace_target.__name__}(args={args}, kwargs={kwargs})")

    return trace_function_closure
