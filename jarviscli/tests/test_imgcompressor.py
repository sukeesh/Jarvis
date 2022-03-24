import unittest
from tests import PluginTest
from plugins.imgcompressor import ImageCompressor

import requests
import os
import shutil

class ImgCompressorTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(ImageCompressor)

        self.image_folder = os.path.join(os.getcwd(), 'tests', 'images')

        # create folder with images
        self.create_image_folder()

    def tearDown(self):
        PluginTest.tearDown(self)
        shutil.rmtree(self.image_folder)
        

    def create_image_folder(self):
        os.mkdir(self.image_folder)

        image1 = requests.get('http://i.imgur.com/xZ8x9ES.jpg', stream=True)
        if image1.status_code == 200:
            with open(os.path.join(self.image_folder, 'image1.jpg'), 'wb') as f:
                shutil.copyfileobj(image1.raw, f)
            print('Image sucessfully Downloaded: ', 'image1.jpg')
        else:
            print('Image Couldn\'t be retrieved')
            # TODO fail test

        image2 = requests.get('https://i.imgur.com/UYrdDFI.jpg', stream=True)
        if image2.status_code == 200:
            with open(os.path.join(self.image_folder, 'image2.jpg'), 'wb') as f:
                shutil.copyfileobj(image2.raw, f)
            print('Image sucessfully Downloaded: ', 'image2.jpg')
        else:
            print('Image Couldn\'t be retrieved')

    def test_compress_single_image(self):
        # insert data to be retrieved by the jarvis input method
        # self.test.queue_input('1')      # select 1 on the menu

        # self.test.queue_input(30)       # chose 30 for image quality

        # self.test.queue_input('hello')

        # run code
        # self.test.run(TEST_STRING)

        # verify that code works
        # self.assertEqual(self.history_say().last_text(), EXPECTED_OUTPUT)
        # self.assertEqual('hello', 'hello')
        pass


if __name__ == '__main__':
    unittest.main()
