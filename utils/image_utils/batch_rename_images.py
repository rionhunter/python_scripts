#!/usr/bin/env python3
"""Rename images in sequence with a prefix."""
import easygui
import os


def batch_rename(paths: list[str], prefix: str = 'img') -> list[str]:
    renamed = []
    for idx, path in enumerate(paths, start=1):
        ext = os.path.splitext(path)[1]
        new_name = f"{prefix}_{idx}{ext}"
        new_path = os.path.join(os.path.dirname(path), new_name)
        os.rename(path, new_path)
        renamed.append(new_path)
    return renamed


if __name__ == '__main__':
    files = easygui.fileopenbox(msg='Select images', default='*.png', multiple=True)
    if files:
        prefix = easygui.enterbox(msg='Filename prefix', default='img')
        if prefix:
            for new_path in batch_rename(files, prefix):
                print(new_path)
