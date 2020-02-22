import cv2
import os
import glob

from plugin import plugin


def bulk_resizer(input_path, output_path, desired_size=32,
                 color=[0, 0, 0], rename=True):
    img_no = 0

    onlyfiles = os.listdir(input_path)
    # print(onlyfiles)
    for im_pth in onlyfiles:
        try:
            im = cv2.imread(im_pth)
            old_size = im.shape[:2]
        except:
            continue

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
            output_path1 = output_path + "/" + str(img_no) + ".jpg"
            img_no += 1
        else:
            output_path1 = output_path + "/" + \
                os.path.splitext(os.path.basename(im_pth))[0] + ".jpg"

        cv2.imwrite(output_path1, new_im)


@plugin("bulkresizer")
def spin(jarvis, s):
    """
    \nThis resizes all the images in a given directory
    to given size and renames them, Specially designed for Deep Leanring
    data collection process. 

    """
    jarvis.say(' ')
    jarvis.say('This is bulk resizer it will resize the image into given',
               'size with padding !!!! Specially designed for Deep Leanring',
               ' data collection process')
    jarvis.say('Enter the path of directory with images to be resized :')
    path1 = jarvis.input()
    jarvis.say('Should I rename them to non repeating whole number series?',
               ' y/n :')
    rename = jarvis.input()
    jarvis.say('Enter the path of output directory :')
    path2 = jarvis.input()
    jarvis.say("Enter the target size :")
    size = jarvis.input_number()
    if rename == 'y':
        bulk_resizer(path1, path2, size, [0, 0, 0], True)
    else:
        bulk_resizer(path1, path2, size, [0, 0, 0], False)
    jarvis.say("Resizing Compleated!! Thank you for using jarvis")
