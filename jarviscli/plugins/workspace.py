"""Plugin that creates templated workspace folders for various languages."""
import git
from distutils.dir_util import copy_tree
import os
import pathlib
from colorama import Fore
# All plugins should inherite from this library
from plugin import plugin

DATA_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = DATA_PATH[:-8] + '/data/workspaces'


@plugin("workspace")
def generate_workspace(jarvis, s):
    """Generate a template workspace in the directory specified by the user."""
    path = pathlib.Path(jarvis.input(
        "Please input the path of your new workspace directory.\n", Fore.BLUE))
    path.mkdir(parents=True, exist_ok=True)
    to_clone = jarvis.input(
        "Would you like to clone into an existing Git repo? (yes/no)\n", Fore.BLUE)
    if to_clone == "yes":
        to_clone = jarvis.input(
            "Please input the link to the directory you want to clone.\n", Fore.BLUE)
        git.Git(str(path)).clone(to_clone)
        return
    to_create = jarvis.input(
        "Would you like to create a Git repo in this workspace? (yes/no)\n", Fore.BLUE)
    if to_create == "yes":
        git.Repo.init(str(path))
    to_template = jarvis.input(
        "Would you like to include a starter file and build script for" +
        "your desired language? (c++/java/none)\n", Fore.BLUE)
    if to_template == "c++":
        copy_tree(DATA_PATH + "/cpp_template", str(path))
    elif to_template == "java":
        copy_tree(DATA_PATH + "/java_template", str(path))
