#!/usr/bin/env python3
"""Convert images to grayscale."""
from PIL import Image
import easygui
import os

def to_grayscale(path: str) -> str:
    img = Image.open(path)
    gray = img.convert('L')
    out = os.path.splitext(path)[0] + '_gray.png'
    gray.save(out)
    return out

if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        for f in files:
            print(to_grayscale(f))
