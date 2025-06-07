#!/usr/bin/env python3
"""Add a text watermark to images."""
from PIL import Image, ImageDraw, ImageFont
import easygui
import os


def add_watermark(path: str, text: str, pos: tuple[int, int] = None) -> str:
    img = Image.open(path).convert('RGBA')
    watermark = Image.new('RGBA', img.size)
    draw = ImageDraw.Draw(watermark)
    font = ImageFont.load_default()
    if pos is None:
        pos = (img.width - 10 - font.getsize(text)[0], img.height - 10 - font.getsize(text)[1])
    draw.text(pos, text, fill=(255, 255, 255, 128), font=font)
    combined = Image.alpha_composite(img, watermark)
    out = os.path.splitext(path)[0] + '_watermark.png'
    combined.save(out)
    return out


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        text = easygui.enterbox(msg='Watermark text', default='sample')
        if text:
            for f in files:
                print(add_watermark(f, text))
