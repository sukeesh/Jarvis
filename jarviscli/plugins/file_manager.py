import os
import shutil

from plugin import plugin


@plugin("file manage")
class file_manage:
    """"
    Can manipulate files and folders by deleting, moving, or renaming.
    """

    def __call__(self, jarvis, s):
        self.get_file_directory(jarvis)
        self.get_cmd(jarvis)

        if self.cmd == "delete":
            self.delete(jarvis, self.file)
        elif self.cmd == "move":
            self.move(jarvis, self.file)
        elif self.cmd == "rename":
            self.rename(jarvis, self.file)

        # determine if directory entered is a file or folder
        if os.path.isfile(self.file):
            self.folder = False
        else:
            self.folder = True

    def get_file_directory(self, jarvis):
        self.file = jarvis.input("Enter the directory of the file you would like to edit: ")

    def get_cmd(self, jarvis):
        # function to find command to be performed to file

        self.possibleCmds = ["delete", "move", "rename"]

        cmdValid = False
        while not cmdValid:
            # iterate through possible commands and say each
            jarvis.say("Commands Avaliable")

            i = 1
            for cmd in self.possibleCmds:
                jarvis.say(str(i) + ". " + cmd)
                i = i + 1

            self.cmd = jarvis.input("Enter command to be performed: ")

            # check if command is valid. If not, end cycle
            if self.cmd not in self.possibleCmds:
                jarvis.say("Invalid command")
            else:
                cmdValid = True

    def delete(self, jarvis, file):
        # function to delete files

        if self.folder is False:
            # first, check if file exists
            if os.path.exists(file):

                yes = True
                while yes:
                    # confirm that file should be deleted
                    confirmation = jarvis.input("Are you sure you want to delete this file? This cannot be undone. (y/n)").lower()

                    if confirmation == "y":
                        try:
                            # delete file
                            if not self.folder:
                                os.remove(file)
                            else:
                                os.rmdir(file)
                        except:
                            jarvis.say("Invalid file path")

                        # break loop after removing file
                        yes = False

                    elif confirmation == "n":

                        # break loop if no confirmation
                        yes = False
                    else:
                        jarvis.say("Invalid input")

            else:
                jarvis.say("file does not exist")

    def move(self, jarvis, file):
        # function to move files

        path_invalid = True
        while path_invalid:
            # get destination
            dest = jarvis.input("Where would you like to move this file to? :")

            try:
                # move from old location
                shutil.move(file, dest)
                path_invalid = False
            except:
                jarvis.say("Invalid path")

    def rename(self, jarvis, file):
        # function to rename files

        path_invalid = True
        while path_invalid:
            # get new name
            new_name = jarvis.input("What would you like to rename this file to? :")

            # get root directory
            root = os.path.split(file)[0]

            new_dir = os.path.join(root, new_name)

            try:
                os.rename(file, new_dir)
                path_invalid = False
            except:
                jarvis.say("Invalid Path")
