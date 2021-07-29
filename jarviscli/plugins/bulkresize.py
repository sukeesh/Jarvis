import os

import cv2
from colorama import Fore

from plugin import plugin

IMAGE_FORMATS = ['.jpg', '.png', '.jpeg', '.svg']


def valid_path(path):
    """Checks if a given path leads to a valid directory

    Returns true if the path leads to valid dir, false otherwise

    Parameters
    ----------

    path: a path (str)
        a string variable that represents a path
    """
    return True if os.path.isdir(path) else False


def dir_exist(path):
    """Checks if a directory path exists

    Returns true if the dir path exists, false otherwise

    Parameters
    ----------

    path: a path (str)
        a string that represents a path
    """
    return True if os.path.exists(path) else False


def create_dir(path):
    """Creates a new directory

    Returns nothing. This function simply creates a new dir

    Parameters
    ----------

    path: a path (str)
        a string that represents the path of the dir that will be created
    """
    os.makedirs(path)


def list_contents(input_path):
    """Lists all the image files of a given path dirextory

    Returns a list that contains only the image files of given path directory

    Parameters
    ----------

    input_path: a path (str)
        a string that represents a path that leads to a valid dir
    """
    filepath = list()
    filename = os.listdir(input_path)

    for name in filename:
        path = input_path + "/" + name
        if os.path.isfile(path) and get_extension(path):
            filepath.append(path)
    return filepath


def remove_backslash(path):
    """Removes all the backslashes from a path and replace them with spaces

    Returns a new path without backslashes

    Parameters
    ----------

    path: a path (str)
        a string that represents a path that leads to a valid dir
    """
    if '\\ ' in path:
        path = path.replace('\\ ', ' ')
    return path


def get_extension(path):
    """Checks if an extension of a file path is an image using IMAGE_FORMATS list

    Returns true if the extension of the file path represents
    an image, false otherwise

    Parameters
    ----------

    path: a path (str)
        a string that leads to a file path
    """
    file_extension = os.path.splitext(path)[1]

    if file_extension in IMAGE_FORMATS:
        return True
    else:
        return False


def rename_img(path, number):
    """Renames a file path of an image

    Returns a new name of the file path for the resized images

    Parameters
    ----------

    path: a path (str)
        a string that leads to an existing file path
    number: a number (int)
        a number that is used in the concatination for the image rename
    """
    output_path = path + '/' + str(number) + '.jpg'
    return output_path


def output_path_concat(path, im_path):
    """Creates a file path of an image

    Returns an output file path for the resized images

    Parameters
    ----------
    path: a path (str)
        a string that lead to an existing file path
    im_path: an image path (str)
        a string that leads to an existing image file path
    """
    output_path = path + '/' + \
        os.path.splitext(os.path.basename(im_path))[0] + '.jpg'
    return output_path


def bulk_resizer(input_path, output_path, desired_size=32,
                 color=None, rename=True):
    if color is None:
        color = [0, 0, 0]
    filepath = list_contents(input_path)
    '''Resizes the images into a given size

    Creates a resized image for an existing image

    Parameters
    ----------

    input_path: an input_path (str)
        a path that leads to an existing dir that contains images
    output_path: an output_path (str)
        a path that will contain the resized images
    desired_size: a desired_size (int)
        a number that it is the size of the resized images
    color: list
        a list that represents the color of the border of the resized images.
        Color equal to [0, 0, 0] means that the border color will be black
    rename: bool
        if this variable is set to True then the resized images names will be
        set to an non repeating whole number series. If it is set to False the
        resized images will have the same name with the original ones.
    '''

    for im_pth in filepath:

        im = cv2.imread(im_pth)
        old_size = im.shape[:2]
        ratio = float(desired_size) / max(old_size)
        new_size = tuple([int(x * ratio) for x in old_size])

        # new_size should be in (width, height) format

        im = cv2.resize(im, (new_size[1], new_size[0]))

        delta_w = desired_size - new_size[1]
        delta_h = desired_size - new_size[0]
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)

        new_im = cv2.copyMakeBorder(im, top, bottom, left, right,
                                    cv2.BORDER_CONSTANT, value=color)
        if rename:
            output_path1 = rename_img(output_path, filepath.index(im_pth))
        else:
            output_path1 = output_path_concat(output_path, im_pth)
        cv2.imwrite(output_path1, new_im)


@plugin("bulkresizer")
def spin(jarvis, s):
    """
    This resizes all the images in a given directory
    to given size and renames them, Specially designed for Deep Leanring
    data collection process.

    """
    answer = ""
    jarvis.say(' ')
    jarvis.say(
        'This is bulk resizer. ' +
        'Bulkresizer is a plugin that resizes images' +
        'into a given size with padding!!!', Fore.BLUE)
    jarvis.say(
        'Specially designed for Deep Learning ' +
        'and data collection process.', Fore.BLUE)
    jarvis.say(' ')
    jarvis.say(
        'Enter the path of directory with images to be resized : ',
        Fore.BLUE)
    path1 = jarvis.input()
    path1 = remove_backslash(path1)
    while not valid_path(path1):
        jarvis.say(
            'The path ' + path1 +
            ' does not lead to a directory!', Fore.RED)
        jarvis.say(
            'Please enter a path that leads to an EXISTING DIRECTORY.',
            Fore.RED)
        path1 = jarvis.input()
    jarvis.say(
        'Should I rename them to non repeating whole number series?',
        Fore.YELLOW)
    jarvis.say('Press y for "YES" n for "NO"', Fore.YELLOW)
    rename = jarvis.input()
    jarvis.say('Enter the path of output directory :', Fore.YELLOW)
    path2 = jarvis.input()
    if not dir_exist(path2):
        jarvis.say(
            'The path ' + path2 + ' does not exist. Do you want to create it?',
            Fore.YELLOW)
        jarvis.say('Print y for "YES" n for "NO"', Fore.YELLOW)
        answer = jarvis.input()
    if answer == 'y':
        create_dir(path2)
    else:
        while not dir_exist(path2):
            jarvis.say(
                'The output path does not exist. ' +
                'Please type an existing path!',
                Fore.YELLOW)
            path2 = jarvis.input()
    jarvis.say("Enter the target size :", Fore.YELLOW)
    size = jarvis.input_number(rtype=int)
    if rename == 'y':
        bulk_resizer(path1, path2, size, [0, 0, 0], True)
    else:
        bulk_resizer(path1, path2, size, [0, 0, 0], False)
    jarvis.say("Resizing Completed!! Thank you for using jarvis", Fore.GREEN)
