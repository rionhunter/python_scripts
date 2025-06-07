#!/usr/bin/env python3
"""Resize images to a specific width and height."""
from PIL import Image
import easygui
import os


def resize_image(path: str, width: int, height: int) -> str:
    img = Image.open(path)
    resized = img.resize((width, height))
    out = os.path.splitext(path)[0] + f'_{width}x{height}.png'
    resized.save(out)
    return out


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        w = easygui.integerbox(msg='Width', lowerbound=1, upperbound=10000)
        h = easygui.integerbox(msg='Height', lowerbound=1, upperbound=10000)
        if w and h:
            for f in files:
                print(resize_image(f, w, h))
