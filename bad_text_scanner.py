"""
1. using easyGUI, ask for a directory, and then for a filetype
2. recursively scan all the files of the filetype in the directory
3. track each file that doesn't have compliant characters (UTF-8)
4. display the file paths with easyGUI
"""

import os
import easygui
import codecs

def get_file_paths(directory, filetype):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            if filepath.endswith(filetype):
                file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

def check_file_encoding(file_path):
    """
    This function will check the encoding of a file and return True if it is UTF-8
    """
    try:
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            f.read()
            return True
    except UnicodeDecodeError:
        return False

def main():
    """
    This is the main function
    """
    # get the directory and filetype from the user
    directory = easygui.diropenbox()
    filetype = easygui.enterbox(msg='Enter the filetype to check (e.g. .txt)')

    # get all the files in the directory
    file_paths = get_file_paths(directory, filetype)

    # check the encoding of each file
    bad_files = []
    for file_path in file_paths:
        if not check_file_encoding(file_path):
            bad_files.append(file_path)

    # display the bad files
    easygui.textbox(msg='The following files are not UTF-8', title='Bad Files', text='\n'.join(bad_files))

if __name__ == "__main__":
    main()
