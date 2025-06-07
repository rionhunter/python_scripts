#!/usr/bin/env python3
"""Merge two images side by side."""
from PIL import Image
import easygui
import os


def merge_images(left_path: str, right_path: str) -> str:
    left = Image.open(left_path)
    right = Image.open(right_path)
    out_img = Image.new('RGBA', (left.width + right.width, max(left.height, right.height)))
    out_img.paste(left, (0, 0))
    out_img.paste(right, (left.width, 0))
    out_path = os.path.splitext(left_path)[0] + '_merged.png'
    out_img.save(out_path)
    return out_path


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select two images', default='*.png', multiple=True)
    if files and len(files) >= 2:
        print(merge_images(files[0], files[1]))
