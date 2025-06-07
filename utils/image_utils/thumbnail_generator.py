#!/usr/bin/env python3
"""Generate thumbnails for images."""
from PIL import Image
import easygui
import os


def create_thumbnail(path: str, size: int = 128) -> str:
    img = Image.open(path)
    img.thumbnail((size, size))
    out = os.path.splitext(path)[0] + f'_thumb{size}.png'
    img.save(out)
    return out


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        size = easygui.integerbox(msg='Thumbnail size', lowerbound=16, upperbound=1024)
        if size:
            for f in files:
                print(create_thumbnail(f, size))
