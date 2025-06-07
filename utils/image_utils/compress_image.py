#!/usr/bin/env python3
"""Compress JPEG images by adjusting quality."""
from PIL import Image
import easygui
import os


def compress_image(path: str, quality: int = 75) -> str:
    img = Image.open(path)
    out = os.path.splitext(path)[0] + f'_q{quality}.jpg'
    img.convert('RGB').save(out, quality=quality)
    return out


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.jpg', multiple=True)
    if files:
        quality = easygui.integerbox(msg='JPEG quality (1-95)', lowerbound=1, upperbound=95)
        if quality:
            for f in files:
                print(compress_image(f, quality))
