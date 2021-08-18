"""Plugin that creates templated workspace folders for various languages."""
import os
import pathlib
from distutils.dir_util import copy_tree

from colorama import Fore

import git
# All plugins should inherite from this library
from plugin import plugin


@plugin("workspace")
def generate_workspace(jarvis, s):
    DATA_PATH = jarvis.data_file('workspaces')

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
