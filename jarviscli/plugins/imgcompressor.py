from PIL import Image
import os
from plugin import plugin, alias
from colorama import Fore


@alias('image compressor')
@plugin('imgcompressor')
class ImageCompressor:
    """
    A tool to compress images
    """

    def __init__(self):
        self.quality = None
        self.formats = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG'}

    def __call__(self, jarvis, s):
        self.img_compressor(jarvis)

    def img_compressor(self, jarvis):
        jarvis.say('')
        jarvis.say('This tool will help you compress a image')
        jarvis.say(
            'The given images will be compressed and saved on the same directory with a prefix "compressed_"')
        while True:

            self.quality = self.quality_option(jarvis)

            self.available_options(jarvis)
            user_input = jarvis.input('Your choice: ')
            user_input = user_input.lower()

            if user_input == 'q' or user_input == 'quit' or user_input == '3':
                jarvis.say("See you next time :D", Fore.CYAN)
                break

            # For single image to be compressed
            elif user_input == '1':
                while True:
                    image_path = jarvis.input(
                        'Enter the full path of the image: ')
                    if os.path.isfile(image_path) and image_path.endswith(tuple(self.formats)):
                        break
                    else:
                        jarvis.say(
                            'Opps! Looks like you entered an invalid path. Kindly Re-enter', Fore.RED)
                self.img_compress(jarvis, image_path)

            # For multiple images in a folder to be compressed
            elif user_input == '2':
                while True:
                    folder_path = jarvis.input(
                        'Enter the full path of a folder: ')
                    if os.path.isdir(folder_path):
                        break
                    else:
                        jarvis.say(
                            'Opps! Looks like you entered an invalid path. Kindly Re-enter', Fore.RED)
                self.folder_images_compress(jarvis, folder_path)

            # For an incorrectly entered option
            else:
                jarvis.incorrect_option()
                continue

    def available_options(self, jarvis):
        """
        Message displayed to prompt the user about compressing
        images.
        """
        jarvis.say('Select one of the following options:')
        jarvis.say('1: Compress a single image')
        jarvis.say('2: Compress all images of a folder')
        jarvis.say('3: Quit')

    def quality_option(self, jarvis):
        """
        Message displayed to prompt the user about the quality
        of compression.
        """
        return abs(jarvis.input_number(prompt='\nEnter desired quality of compressions (0-100 where 100 is maximum compression): ', rtype=int, rmin=0, rmax=100)-100)

    def folder_images_compress(self, jarvis, folder_path):
        """
        This function is used to compress all the images
        in a given folder path.
        """
        os.chdir(folder_path)
        for image in os.listdir(os.getcwd()):
            if image.endswith(tuple(self.formats)):
                self.img_compress(
                    jarvis, os.path.join(os.getcwd(), image), from_folder=True)

        jarvis.say(
            'Your images in the provided folder were compressed successfully', Fore.GREEN)

    def img_compress(self, jarvis, img_path, from_folder=False):
        """
        Save the pdf to the thus supplied location
        or prompt the user to choose a new location
        """
        picture = Image.open(img_path, mode='r')

        picture.save(os.path.join(os.path.dirname(img_path), "compressed_" + os.path.basename(img_path)),
                     self.formats.get(os.path.splitext(img_path)[1]),
                     optimize=True,
                     quality=self.quality)

        if not from_folder:
            jarvis.say('Your image was compressed successfully', Fore.GREEN)
