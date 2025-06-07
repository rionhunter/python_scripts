#!/usr/bin/env python3
"""Flip images horizontally or vertically."""
from PIL import Image
import easygui
import os


def flip_image(path: str, direction: str = 'horizontal') -> str:
    img = Image.open(path)
    if direction == 'horizontal':
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
        suffix = '_fliph'
    else:
        flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
        suffix = '_flipv'
    out = os.path.splitext(path)[0] + suffix + '.png'
    flipped.save(out)
    return out


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        choice = easygui.choicebox(msg='Flip direction', choices=['horizontal', 'vertical'])
        if choice:
            for f in files:
                print(flip_image(f, choice))
