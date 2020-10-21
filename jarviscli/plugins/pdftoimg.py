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
                while True:
                    pdf_path = jarvis.input('Enter the full path of the pdf: ')
                    if os.path.exists(pdf_path) and (pdf_path.endswith('.pdf')):
                        break
                    else:
                        jarvis.say(
                            'Opps! Looks like you entered an invalid path. Kindly Re-enter', Fore.RED)
                pages = self.convert_to_images(pdf_path, jarvis)

            # For an incorrectly entered option
            else:
                jarvis.incorrect_option()
                continue

            destination = jarvis.get_saving_directory(self.path)
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
