import cv2
import os
import glob

from plugin import plugin
from colorama import Fore

IMAGE_FORMATS = ['.jpg', '.png', '.jpeg', '.svg']

def valid_path(path):
    return True if os.path.isdir(path) else False

def dir_exist(path):
    return True if os.path.exists(path) else False

def create_dir(path):
    os.makedirs(path)

def list_contents(input_path):
    filepath = list()
    filename = os.listdir(input_path)

    for name in filename:
        path = input_path + "/" + name
        if os.path.isfile(path) and get_extension(path):
            filepath.append(path)
    return filepath

def remove_backslash(path):
    if '\ ' in path:
        path = path.replace('\ ', ' ')
    return path

def get_extension(path):
    file_extension = os.path.splitext(path)[1]
    
    if file_extension in IMAGE_FORMATS:
        return True
    else:
        return False

def rename_img(path, number):
    output_path = path + '/' + str(number) + '.jpg'
    return output_path

def output_path_concat(path, im_path):
    output_path = path + '/' + \
        os.path.splitext(os.path.basename(im_path))[0] + '.jpg'
    
    return output_path

def bulk_resizer(input_path, output_path, desired_size=32,
                 color=[0, 0, 0], rename=True):
    filepath = list_contents(input_path)

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
    jarvis.say('This is bulk resizer. Bulkresizer is a plugin that resizes images into a given size with padding!!!', Fore.BLUE)
    jarvis.say('Specially designed for Deep Learning and data collection process.', Fore.BLUE)
    jarvis.say(' ')
    jarvis.say('Enter the path of directory with images to be resized : ', Fore.BLUE)
    path1 = jarvis.input()
    while not valid_path(path1):
        jarvis.say('The path ' + path1 + ' does not lead to a directory!', Fore.RED)
        jarvis.say('Please enter a path that leads to an EXISTING DIRECTORY.', Fore.RED)
        path1 = jarvis.input()
    jarvis.say('Should I rename them to non repeating whole number series?', Fore.YELLOW)
    jarvis.say('Press y for "YES" n for "NO"', Fore.YELLOW)
    rename = jarvis.input()
    jarvis.say('Enter the path of output directory :', Fore.YELLOW)
    path2 = jarvis.input()
    if not dir_exist(path2):
        jarvis.say('The path ' + path2 + ' does not exist. Do you want to create it?', Fore.YELLOW)
        jarvis.say('Print y for "YES" n for "NO"', Fore.YELLOW)
        answer = jarvis.input()
    if answer is 'y':
        create_dir(path2)
    else:
        while not dir_exist(path2):
            jarvis.say('The output path does not exist. Please type an existing path!', Fore.YELLOW)
            path2 = jarvis.input()
    jarvis.say("Enter the target size :", Fore.YELLOW)
    size = jarvis.input_number(rtype=int)
    if rename == 'y':
        bulk_resizer(path1, path2, size, [0, 0, 0], True)
    else:
        bulk_resizer(path1, path2, size, [0, 0, 0], False)
    jarvis.say("Resizing Compleated!! Thank you for using jarvis", Fore.GREEN)
