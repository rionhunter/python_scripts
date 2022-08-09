"""
1. using easyGUI, ask for a directory, filetype, and phrase
2. recursively scan the directory for files of the selected filetype, then read thefiles for the phrase.
3. return a list of all the files it shows up in, and at what line.
4. clicking a result in the list launches the file with the Operating System's default program
"""

import os
import easygui
import re

def get_file_list(directory, filetype):
    """
    returns a list of all files in the directory with the given filetype
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(filetype):
                file_list.append(os.path.join(root, file))
    return file_list

def search_files(file_list, phrase):
    """
    returns a list of tuples of the form (file, line_number)
    """
    results = []
    for file in file_list:
        with open(file, 'r') as f:
            for i, line in enumerate(f):
                if re.search(phrase, line):
                    results.append((file, i))
    return results

def main():
    directory = easygui.diropenbox()
    filetype = easygui.enterbox(msg='Enter filetype to search for')
    phrase = easygui.enterbox(msg='Enter phrase to search for')
    file_list = get_file_list(directory, filetype)
    results = search_files(file_list, phrase)
    easygui.textbox(msg='Results', text='\n'.join(['{}:{}'.format(result[0], result[1]) for result in results]))

if __name__ == '__main__':
    main()
