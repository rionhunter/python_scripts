#!/usr/bin/env python3
"""Convert images to JPEG format."""
from PIL import Image
import easygui
import os

def convert_to_jpg(path: str) -> str:
    img = Image.open(path)
    new_path = os.path.splitext(path)[0] + '.jpg'
    img.convert('RGB').save(new_path)
    return new_path

if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        for f in files:
            print(convert_to_jpg(f))
