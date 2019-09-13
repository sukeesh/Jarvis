from helper import *


section("Install requirements")

shell("pip install -U -r installer/requirements.txt", True).should_not_fail()
