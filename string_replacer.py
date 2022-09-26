"""
string replacer
1. if all the variables aren't provided through system arguments, ask for them using easyGUI
2. the variables required are 'directory', 'filetype', 'old_string', and 'new_string'
3. recursively scan through the directory, parsing the files of the filetype, replacing the relvant strings.
4. display a list of files that had contained the old_string and has been formatted
"""

import os
import sys
import easygui

def main():
    # if all the variables aren't provided through system arguments, ask for them using easyGUI
    if len(sys.argv) < 5:
        directory = easygui.diropenbox(msg='Select the directory to scan', title='Directory')
        filetype = easygui.enterbox(msg='Enter the filetype to scan', title='Filetype')
        old_string = easygui.enterbox(msg='Enter the string to be replaced', title='Old String')
        new_string = easygui.enterbox(msg='Enter the string to replace with', title='New String')
    else:
        directory = sys.argv[1]
        filetype = sys.argv[2]
        old_string = sys.argv[3]
        new_string = sys.argv[4]

    # recursively scan through the directory, parsing the files of the filetype, replacing the relvant strings.
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(filetype):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                if old_string in content:
                    content = content.replace(old_string, new_string)
                    with open(file_path, 'w') as f:
                        f.write(content)
                    print(file_path)

if __name__ == '__main__':
    main()
