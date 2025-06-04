#!/usr/bin/env python3
import easygui
import os
from PIL import Image

# get the file names
files = easygui.fileopenbox(msg='Select .png files', default='*.png', multiple=True)

# loop through the files
for file in files:
    # open the file
    img = Image.open(file)
    # get the size of the image
    width, height = img.size
    # create a new image of the same size
    new_img = Image.new('RGBA', (width, height))
    # loop through the pixels
    for x in range(width):
        for y in range(height):
            # get the pixel
            pixel = img.getpixel((x, y))
            # get the colour values
            r, g, b, a = pixel
            # invert the colours
            r = 255 - r
            g = 255 - g
            b = 255 - b
            # create a new pixel
            new_pixel = (r, g, b, a)
            # put the pixel in the new image
            new_img.putpixel((x, y), new_pixel)
    # save the new image
    new_img.save(os.path.splitext(file)[0] + '_inverted.png')
d.png')
