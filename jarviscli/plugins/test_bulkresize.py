from unittest import mock
import unittest
import os
from Jarvis import Jarvis
from plugins.bulkresize import spin
from plugins import bulkresize

from tests import PluginTest


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(CURRENT_PATH, '..', 'data/')


class Bulkresize(PluginTest):
    pass


if __name__ == '__main__':
    unittest.main()