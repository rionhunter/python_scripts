import easygui
import os

def list_files(startpath):
    output_filename = os.path.basename(startpath) + '.txt'
    with open(output_filename, 'w') as f:
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            f.write('{}{}/\n'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                f.write('{}{}\n'.format(subindent, file))

# Ask for directory
directory = easygui.diropenbox(msg="Please select a directory")

# Write all directories and files to a .txt file named after the selected directory
list_files(directory)