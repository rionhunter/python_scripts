#!/usr/bin/env python3
"""
1. expect multiple image files to be dragged onto the script as incoming args
    - if no scripts present, use easyGUI to ask the user for image files
2. ask the user what scale images they want using a slider, with the first image used as examples of the outputs
    - 25%
    - 33%
    - 50%
    - 66%
    - 75%
    - 90%
3. save the new file in the same location, with its new dimensions as its suffix
"""

import sys
import os
import easygui
from PIL import Image

# ~~~~~~~~ PROCESSING IMAGE FILES ~~~~~~~~~~

# check sys.args for incoming files
if len(sys.argv) > 1:
    # if there are incoming files, use them
    incoming_files = sys.argv[1:]
else:
    # if there are no incoming files, ask the user for them
    incoming_files = easygui.fileopenbox(msg="Select image files to resize", multiple=True)

# check if the user cancelled the file selection
if incoming_files is None:
    sys.exit()

# check if the user wants to resize the images
resize_images = easygui.ynbox(msg="Do you want to resize the images?", title="Resize Images")

# if the user wants to resize the images, ask them what scale they want
if resize_images:
    scale_percent = easygui.integerbox(msg="What scale percent do you want the images to be resized to?",
                                       title="Resize Images", lowerbound=1, upperbound=100)
    # check if the user cancelled the scale selection
    if scale_percent is None:
        sys.exit()

# iterate through the incoming files
for file in incoming_files:
    # check if the file is an image
    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        # open the image
        img = Image.open(file)
        # if the user wants to resize the images, resize them
        if resize_images:
            # resize the image
            img = img.resize((int(img.width * scale_percent / 100), int(img.height * scale_percent / 100)))
        # get the new file name
        new_file_name = os.path.splitext(file)[0] + "_" + str(scale_percent) + os.path.splitext(file)[1]
        # save the image
        img.save(new_file_name)
        # close the image
        img.close()
    else:
        # if the file is not an image, print an error message
        print("Error: " + file + " is not an image file.")
