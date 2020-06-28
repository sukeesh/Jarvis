import os
from plugin import plugin
from colorama import Fore
from pdf2image import convert_from_path

@plugin('pdf to images')

class PdfToImage:
    """
    A tool for converting and storing all the
    pages of a pdf in form of a images in a folder
    """

    def __init__(self):
        self.path = None

    def __call__(self, jarvis, s):
        self.pdf_to_img(jarvis)

    def pdf_to_img(self, jarvis):
        jarvis.say('')
        jarvis.say('This tool will help you convert pdf to images')
        while True:
            self.available_options(jarvis)
            user_input = jarvis.input('Your choice: ')
            user_input = user_input.lower()

            # For quiting the program
            if user_input == 'q' or user_input == 'quit' or user_input == '2':
                jarvis.say("See you next time :D", Fore.CYAN)
                break

            # Converting a pdf with a given path to image
            elif user_input == '1':
                pdf_path = jarvis.input('Enter the full path of the pdf: ')
                pages = self.convert_to_images(pdf_path, jarvis)

            # For an incorrectly entered option
            else:
                self.incorrect_option(jarvis)
                continue

            destination = self.get_saving_directory(jarvis)
            self.save_images(pages, destination, jarvis)
          
    def convert_to_images(self, pdf_path, jarvis):
        """
        Convert all the pages in the pdf to individual
        pages option and return it
        """
        self.path = pdf_path
        pages = convert_from_path(pdf_path)
        return pages

    def available_options(self, jarvis):
        """
        Message displayed to prompt the user about converting
        pdf to image
        """
        jarvis.say('Select one of the following options:')
        jarvis.say('1: Convert pdf to images')
        jarvis.say('2: Quit')

    def incorrect_option(self, jarvis):
        """
        A function to notify the user that an incorrect option
        has been entered and prompting him to enter a correct one
        """
        jarvis.say("Oops! Looks like you entered an incorrect option", Fore.RED)
        jarvis.say("Look at the options once again:", Fore.GREEN)

    def get_saving_directory(self, jarvis):
        """
        Returns the final directory where the files must be saved
        """
        user_choice = jarvis.input('Would you like to save the file in the same folder?[y/n] ')
        user_choice = user_choice.lower()
        if user_choice == 'yes' or user_choice == 'y':
            destination = self.get_parent_directory(self.path)
        elif user_choice == 'no' or user_choice == 'n':
            destination = jarvis.input('Enter the folder destination: ')
            if not os.path.exists(destination):
                os.makedirs(destination)

        os.chdir(destination)

        return destination

    def save_images(self, pages, destination, jarvis):
        """
        Save the thus generated images to the destination 
        specified
        """
        page_count = 1
        for page in pages:
            page.save('page_' + str(page_count) + '.jpg', 'JPEG')
            page_count += 1

        jarvis.say('Your images are saved successfully', Fore.GREEN)

    def get_parent_directory(self, path):
        """
        Removes the image name from the folder and returns
        the remaining path
        """
        path = path.split('/')
        path.pop()
        destination = '/'.join(path)
        return destination
