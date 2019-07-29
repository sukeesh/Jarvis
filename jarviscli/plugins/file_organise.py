from __future__ import print_function
from colorama import Fore
import os
import sys
from plugin import plugin, require, UNIX


@require(platform=UNIX)
@plugin('file organise')
class File_Organise():
    """
    Type file_organise and follow instructions
    It organises selected folder based on extension
    """

    def __call__(self, jarvis, s):
        self.file_manage(jarvis)

    def source_path(self, jarvis, dir_name):
        all_paths = []
        # Changing static path to get the home path from PATH variables.
        # The '/home' was causing script to exit with "file not found" error
        # on Darwin.
        home_dir = os.environ.get("HOME")
        user_name = os.environ.get("USER")
        home_path = home_dir.split(user_name)[0].rstrip('/')
        for root in os.walk(home_path):
            print(
                Fore.LIGHTBLUE_EX
                + "Searching in {}...".format(
                    (root[0])[
                        :70]),
                end="\r")
            sys.stdout.flush()
            if dir_name == root[0].split('/')[-1]:
                all_paths.append(root[0])

        for i, path_info in enumerate(all_paths):
            print()
            print("{}. {}".format(i + 1, path_info))

        if len(all_paths) == 0:
            print(Fore.LIGHTRED_EX + 'No directory found')
            exit()

        choice = int(jarvis.input('\nEnter the option number: '))

        if choice < 1 or choice > len(all_paths):
            path = ''
            print(Fore.LIGHTRED_EX + 'Wrong choice entered')
            exit()

        else:
            path = all_paths[choice - 1]

        return path

    def print_before(self, path):
        print("Cleaning {} located at {}\n".format(path.split('/')[-1], path))

        print(Fore.LIGHTBLUE_EX + "Folders before cleaning\n" + Fore.RESET)

        for files in os.listdir(path):
            print(files, end='\t')
        print()

    def destination_path(self, path):
        os.chdir(path)
        extension = set()
        for f in os.listdir(path):
            ext = (os.path.splitext(f))[1]

            extension.add(ext[1:])

        new_dir = "New" + path.split('/')[-1]
        new_dir_path = os.path.join(path, new_dir)

        if not os.path.exists(new_dir_path):
            os.mkdir(new_dir_path)

        return new_dir_path, new_dir, extension

    def organise(self, new_dir_path, new_dir, path, extension):
        for ext in extension:
            folder = os.path.join(new_dir_path, ext)

            if not os.path.exists(folder):
                os.mkdir(folder)

            if ext != '':
                for f in os.listdir(path):
                    if os.path.splitext(f)[1].strip('.') == ext:
                        os.rename(f, os.path.join(folder, f))

            else:
                for f in os.listdir(path):
                    if f != new_dir and os.path.splitext(
                            f)[1].strip('.') == ext:
                        inner_folder = os.path.join(new_dir_path, f)

                        if os.path.exists(inner_folder):
                            os.chdir(os.path.join(path, f))
                            for file in os.listdir():
                                new_path = os.path.join(inner_folder, file)
                                os.rename(file, new_path)
                            os.rmdir(os.path.join(path, f))

                        else:
                            os.rename(f, inner_folder)

    def print_after(self, path):
        print(Fore.LIGHTBLUE_EX + "\nFolders after cleaning\n" + Fore.RESET)

        for files in os.listdir(path):
            print(files, sep=',\t')

        print(Fore.LIGHTMAGENTA_EX + "\nCLEANED\n" + Fore.RESET)

    def file_manage(self, jarvis):
        dir_name = jarvis.input('Enter the name of directory you want to clear: ')
        dir_path = self.source_path(jarvis, dir_name)
        self.print_before(dir_path)
        new_dir_path, new_dir, extension = self.destination_path(dir_path)
        self.organise(new_dir_path, new_dir, dir_path, extension)
        self.print_after(dir_path)
