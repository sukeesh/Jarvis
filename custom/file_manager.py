from plugin import plugin
import os
import shutil

@plugin("file manage")
class file_manage:
    def __call__(self,jarvis,s):
        self.get_file_directory(jarvis)
        self.get_cmd(jarvis)
        self.delete(jarvis,self.file)

    def get_file_directory(self,jarvis):
        self.file = jarvis.input("Enter the directory of the file you would like to edit: ")

    def get_cmd(self,jarvis):
        # function to find command to be performed to file

        self.possibleCmds = ["delete","move","rename"]

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
                jarvis.say("invalid command")
            else:
                cmdValid = True

    def delete(self,jarvis,file):
        # function to delete files

        # first, check if file exists
        if os.path.exists(file):

            yes = True
            while yes:
                # confirm that file should be deleted
                confirmation = jarvis.input("Are you sure you want to delete this file? This cannot be undone. (y/n)").lower()

                if confirmation == "y":
                    # delete file
                    os.remove(file)

                    # break loop after removing file
                    yes = False

                elif confirmation == "n":

                    # break loop if no confirmation
                    yes = False
                else:
                    jarvis.say("invalid input")

        else:
            jarvis.say("file does not exist")

    def move(self,jarvis,file):
        # function to move files

        # get destination
        dest = jarvis.input("Where would you like to move this file to?")

        # move from old location
        shutil.move(file,dest)