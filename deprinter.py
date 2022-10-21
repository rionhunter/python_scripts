#!/usr/bin/env python3
"""
Deprinter
1. using easyGUI, ask for a directory
2. ask for a filetype
3. recursively scan through the subsequent directories, reading each of the selected filetype, and delete each line that starts with 'print(' disregarding any whitespace or '#'
4. return a list of all the effected files
"""

import os
import easygui
import re

def deprinter(directory, filetype):
    """
    recursively scan through the subsequent directories, reading each of the selected filetype, and delete each line that starts with 'print(' disregarding any whitespace or '#'
    """
    # get a list of all the files in the directory
    files = os.listdir(directory)
    # create a list to store the effected files
    effected_files = []
    # iterate through the files
    for file in files:
        # if the file is a directory, recursively call the function
        if os.path.isdir(directory + '/' + file):
            effected_files.extend(deprinter(directory + '/' + file, filetype))
        # if the file is the correct filetype, open it and read it
        elif file.endswith(filetype):
            effected_files.append(directory + '/' + file)
            with open(directory + '/' + file, 'r') as f:
                lines = f.readlines()
            # iterate through the lines
            for i, line in enumerate(lines):
                # if the line starts with 'print(' disregarding any whitespace or '#', delete it
                if re.match(r'^\s*#?\s*print\(', line):
                    lines[i] = ''
            # write the lines back to the file
            with open(directory + '/' + file, 'w') as f:
                f.writelines(lines)
    return effected_files

if __name__ == '__main__':
    # ask for a directory
    directory = easygui.diropenbox()
    # ask for a filetype
    filetype = easygui.enterbox(msg='Enter a filetype', title='Filetype', default='py')
    # call the function
    effected_files = deprinter(directory, filetype)
    # print the effected files
    print('\n'.join(effected_files))
