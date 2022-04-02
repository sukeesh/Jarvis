import unittest
from tests import PluginTest
from plugins.imgcompressor import ImageCompressor

import requests
import os
import shutil

"""Instructions to run this test.

source env/bin/activate
cd jarviscli/
python -m unittest tests/test_imgcompressor.py
"""


class ImgCompressorTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(ImageCompressor)

        self.image_folder = os.path.join(os.getcwd(), 'tests', 'images')

        self.prefix = 'compressed_'
        self.image1 = 'image1.jpg'
        self.image2 = 'image2.jpg'

        self.create_image_folder()

    def tearDown(self):
        PluginTest.tearDown(self)
        # remove directory with the dummy images
        shutil.rmtree(self.image_folder)

    def create_image_folder(self):
        """Create a folder with two dummy images.

        This images will be used to test the two functionalities
        of the ImgCompressor plugin
        """

        os.mkdir(self.image_folder)

        image1 = requests.get('http://i.imgur.com/xZ8x9ES.jpg', stream=True)
        if image1.status_code == 200:
            with open(os.path.join(self.image_folder, self.image1), 'wb') as f:
                shutil.copyfileobj(image1.raw, f)
            print('Image sucessfully Downloaded: ', self.image1)
        else:
            print('Image Couldn\'t be retrieved')
            self.fail('Image Couldn\'t be retrieved')

        image2 = requests.get('https://i.imgur.com/UYrdDFI.jpg', stream=True)
        if image2.status_code == 200:
            with open(os.path.join(self.image_folder, self.image2), 'wb') as f:
                shutil.copyfileobj(image2.raw, f)
            print('Image sucessfully Downloaded: ', self.image2)
        else:
            print('Image Couldn\'t be retrieved')
            self.fail('Image Couldn\'t be retrieved')

    def test_compress_single_image(self):
        """Test workflow to compress a single image."""

        # insert data to be retrieved by jarvis.input()
        self.queue_input('1')           # select 1 on the menu
        self.queue_input('30')          # chose 30 for image quality

        # specify the image path when jarvis.input() is called
        self.queue_input(os.path.join(self.image_folder, self.image1))

        self.queue_input('3')           # quit from the main menu

        # run code
        self.test.run('')

        # verify that a compressed image was created in the specified folder
        self.assertTrue(
            any(
                image.startswith(self.prefix)
                for image in os.listdir(self.image_folder)
            )
        )

        # verify that the compressed image is in fact compressed
        original_image_size = os.stat(
            os.path.join(self.image_folder, self.image1)
        ).st_size

        compressed_image_size = os.stat(
            os.path.join(self.image_folder, self.prefix + self.image1)
        ).st_size

        self.assertGreater(
            original_image_size, compressed_image_size
        )

        # verify that the client quited the menu
        self.assertEqual(self.history_say().last_text(),
                         'See you next time :D')

    def test_compress_multiple_images(self):
        """Test workflow to compress multiple images."""

        # insert data to be retrieved by jarvis.input()
        self.queue_input('2')           # select 1 on the menu
        self.queue_input('30')          # chose 30 for image quality

        # specify the image path when jarvis.input() is called
        self.queue_input(self.image_folder)

        self.queue_input('3')           # quit from the main menu

        # run code
        self.test.run('')

        # verify that, there are 4 images, 2 original and other 2 compressed
        images_on_folder = os.listdir(self.image_folder)

        self.assertEqual(len(images_on_folder), 4)

        self.assertEqual(
            len(
                [
                    image
                    for image in images_on_folder
                    if image.startswith(self.prefix)
                ]
            ), 2
        )

        # check if the compressed images have the right size
        image1, image1_compressed = (
            os.stat(
                os.path.join(self.image_folder, self.image1)
            ).st_size,
            os.stat(
                os.path.join(self.image_folder, self.prefix + self.image1)
            ).st_size
        )

        image2, image2_compressed = (
            os.stat(
                os.path.join(self.image_folder, self.image2)
            ).st_size,
            os.stat(
                os.path.join(self.image_folder, self.prefix + self.image2)
            ).st_size
        )

        self.assertGreater(
            image1, image1_compressed
        )

        self.assertGreater(
            image2, image2_compressed
        )

        # verify that the client quited the menu
        self.assertEqual(self.history_say().last_text(),
                         'See you next time :D')


if __name__ == '__main__':
    unittest.main()
