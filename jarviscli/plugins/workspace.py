import git
import pathlib
from colorama import Fore
# All plugins should inherite from this library
from plugin import plugin


@plugin("workspace")
def generate_workspace(jarvis, s):
    path = pathlib.Path(jarvis.input(
        "Please input the path of your new workspace directory.\n"))
    path.mkdir(parents=True, exist_ok=True)
    to_clone = jarvis.input(
        "Would you like to clone into an existing Git repo? (yes/no)\n")
    if to_clone == "yes":
        to_clone = jarvis.input(
            "Please input the link to the directory you want to clone.\n")
        git.Git(str(path)).clone(to_clone)
        return
    to_create = jarvis.input(
        "Would you like to create a Git repo in this workspace? (yes/no)\n")
    if to_create == "yes":
        git.Repo.init(str(path))
