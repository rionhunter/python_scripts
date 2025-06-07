#!/usr/bin/env python3
"""Convert images to a specified format."""
from PIL import Image
import easygui
import os


def convert_format(path: str, fmt: str) -> str:
    img = Image.open(path)
    out = os.path.splitext(path)[0] + '.' + fmt.lower()
    if fmt.lower() in ('jpg', 'jpeg'):
        img.convert('RGB').save(out)
    else:
        img.save(out)
    return out


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        fmt = easygui.choicebox(msg='Choose format', choices=['png', 'jpg', 'bmp', 'gif'])
        if fmt:
            for f in files:
                print(convert_format(f, fmt))
