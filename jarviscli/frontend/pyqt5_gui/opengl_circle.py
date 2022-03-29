from frontend.pyqt5_gui.utils import *


class OpenGLCircle:

    def __init__(self, center_x: float, center_y: float, radius: float, degree_of_circle: int):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.degree_of_circle = degree_of_circle
        self.circle_points = np.array([])

    def create_circle_points(self):
        self.circle_points = np.array([])
        for sep in range(self.degree_of_circle):
            first_point = polar_to_cartesian(self.center_x, self.center_y, self.radius, sep)
            second_point = polar_to_cartesian(self.center_x, self.center_y, self.radius, sep + 1)
            random_number = float(np.random.randint(0, 20))
            self.circle_points = np.append(self.circle_points,
                                           create_six_point_line(first_point, second_point, sep, random_number))
