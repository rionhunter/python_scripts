#!/usr/bin/env python3
"""Crop images to specified bounding box."""
from PIL import Image
import easygui
import os


def crop_image(path: str, left: int, top: int, right: int, bottom: int) -> str:
    img = Image.open(path)
    cropped = img.crop((left, top, right, bottom))
    out = os.path.splitext(path)[0] + f'_crop.png'
    cropped.save(out)
    return out


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        l = easygui.integerbox(msg='Left', lowerbound=0, upperbound=10000)
        t = easygui.integerbox(msg='Top', lowerbound=0, upperbound=10000)
        r = easygui.integerbox(msg='Right', lowerbound=0, upperbound=10000)
        b = easygui.integerbox(msg='Bottom', lowerbound=0, upperbound=10000)
        if None not in (l, t, r, b):
            for f in files:
                print(crop_image(f, l, t, r, b))
