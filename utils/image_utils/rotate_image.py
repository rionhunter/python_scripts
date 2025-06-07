#!/usr/bin/env python3
"""Rotate images by a specified angle."""
from PIL import Image
import easygui
import os


def rotate_image(path: str, angle: int, expand: bool = True) -> str:
    img = Image.open(path)
    rotated = img.rotate(angle, expand=expand)
    out = os.path.splitext(path)[0] + f'_rot{angle}.png'
    rotated.save(out)
    return out


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        angle = easygui.integerbox(msg='Rotation angle', title='Rotate', lowerbound=0, upperbound=360)
        if angle is not None:
            for f in files:
                print(rotate_image(f, angle))
