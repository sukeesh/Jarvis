# -*- encoding: utf-8 -*-

"""

 * Author(s):    Ahmet Furkan YENİPINAR
 * Created:      24.08.2021
 * Title:        OpenGL Widget Class

"""

from PyQt5.QtGui import (QOpenGLBuffer, QOpenGLShaderProgram, QOpenGLShader)
from PyQt5.QtWidgets import QOpenGLWidget

from frontend.pyqt5_gui.opengl_circle import OpenGLCircle
from OpenGL import GL as gl
import numpy as np
import time


class OpenGLWidget(QOpenGLWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS GUI v0.1.0")
        self.resize(800, 600)
        self.vertPosBuffer = QOpenGLBuffer()
        self.texture_coord_buffer = QOpenGLBuffer()
        self.opengl_circle = OpenGLCircle(0.0, 0.0, 200.0, 360)
        # The circle points are created by calling 'create_circle_points()' method.
        self.opengl_circle.create_circle_points()
        self.vertPositions = np.array(self.opengl_circle.circle_points, dtype=np.float32)

        self.update_control = False

    def initializeGL(self):
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)

        vertex_shader_src = """
        attribute vec3 aPosition;
        attribute vec2 texture_coordinates;
        void main()
        {
            gl_Position = vec4(aPosition, 1.0);
        }
        """
        fragment_shader_src = """
        void main()
        {
            gl_FragColor = vec4(0.03, 0.57, 0.81, 1.0);

        }
        """
        program = QOpenGLShaderProgram()
        program.addShaderFromSourceCode(QOpenGLShader.Vertex, vertex_shader_src)
        program.addShaderFromSourceCode(QOpenGLShader.Fragment, fragment_shader_src)
        program.link()
        program.bind()

        self.vertPosBuffer.create()
        self.vertPosBuffer.bind()
        self.vertPosBuffer.allocate(self.vertPositions, len(self.vertPositions) * 4)

        program.bindAttributeLocation("aPosition", 0)
        program.setAttributeBuffer(0, gl.GL_FLOAT, 0, 3, 5 * 4)
        program.enableAttributeArray(0)

    def update_with_timer(self):
        while self.update_control:
            time.sleep(0.05)
            self.update()

    def update_buffer_values(self):
        self.opengl_circle.create_circle_points()
        self.vertPositions = np.array(self.opengl_circle.circle_points, dtype=np.float32)
        self.vertPosBuffer.allocate(self.vertPositions, len(self.vertPositions) * 4)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glPointSize(1.5)
        self.update_buffer_values()
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6 * 359)
