from fpdf import FPDF
import img2pdf 
from PIL import Image
import os 
from plugin import plugin
from colorama import Fore


@plugin('image to pdf')
class ImageToPDF:
    """
    A tool to converrt images to pdf file
    """

    def __init__(self):
        #Path of the folder or image to be converted
        self.path = None
        self.image = None
        self.pdf = None

    def __call__(self, jarvis, s):
        self.imgtopdf(jarvis)

    def imgtopdf(self, jarvis):
        jarvis.say('')
        jarvis.say('This tool will help you convert image to pdf')
        while True:

            self.available_options(jarvis)
            user_input = jarvis.input('Your choice: ')
            user_input = user_input.lower()

            if user_input == 'q' or user_input == 'quit' or user_input == '3':
                jarvis.say("See you next time :D", Fore.CYAN)
                break

            elif user_input == '1':
                image_path = jarvis.input('Enter the full path of the image: ')
                pdf_bytes = self.single_image_to_pdf(jarvis, image_path)

            elif user_input == '2':
                self.folder_to_pdf(jarvis)

            else:
                self.incorrect_option(jarvis)
                # For skipping the code written after else
                continue

            user_choice = jarvis.input('Would you like to save the file in the same folder?[y/n] ')
            user_choice = user_choice.lower()
            if user_choice == 'yes' or user_choice == 'y':
                destination = self.getParentDirectory(self.path)
            elif user_choice == 'no' or user_choice == 'n':
                destination = jarvis.input('Enter the folder destination: ')

            file_name = jarvis.input('What would you like to name your pdf? ')
            destination = destination + '/'+ file_name + '.pdf'
            print('Final Destination ' + destination)
            self.save_pdf(jarvis, pdf_bytes, destination)

    def available_options(self, jarvis):
        """
        Message displayed to prompt the user about converting
        images to pdf
        """
        jarvis.say('Select one of the two options:')
        jarvis.say('1: Convert a single image')
        jarvis.say('2: Convert all images of the folder')
        jarvis.say('3: Quit')

    def single_image_to_pdf(self, jarvis, image_path):
        """
        This function is used to convert a single image 
        with a given path to a pdf file.
        """
        self.path = image_path
        self.image = Image.open(image_path) 
        pdf_bytes = img2pdf.convert(self.image.filename)
        return pdf_bytes

    def folder_to_pdf(self, jarvis):
        """
        This function is used to convert all the images
        in a given folder path to a single PDF file
        """
        pass

    def incorrect_option(self, jarvis):
        """
        A function to notify the user that an incorrect option 
        has been entered and prompting him to enter a correct one
        """
        jarvis.say("Oops! Looks like you entered an incorrect option", Fore.RED)
        jarvis.say("Look at the options once again:", Fore.GREEN)

    def save_pdf(self, jarvis, pdf_bytes, destination):
        """
        Save the pdf to the thus supplied location
        or prompt the user to choose a new location
        """
        pdf_file = open(destination, 'wb')
        pdf_file.write(pdf_bytes)
        self.image.close()
        pdf_file.close()
        jarvis.say('Your pdf is created successfully', Fore.GREEN)

    def getParentDirectory(self, path):
        """
        Removes the image name from the folder and returns 
        the remaining path. 
        """
        path = path.split('/')
        path.pop()
        destination = '/'.join(path)
        return destination
