#!/usr/bin/env python3
"""
1. using easyGUI, ask the user for a directory, and a filetype
2. recursively scan the directories for all applicable files
3. if there are any lines that have been commented out, and then after any number of spaces begins with 'print(', delete that line
4. display a list of all affected files
"""

import os
import easygui
import re

def main():
    # get the directory and filetype from the user
    dir = easygui.diropenbox()
    filetype = easygui.enterbox("Enter the filetype to search for:")
    # get a list of all files in the directory
    files = os.listdir(dir)
    # create a list to store the files that will be affected
    affected_files = []
    # iterate through the files
    for file in files:
        # if the file is of the correct type
        if file.endswith(filetype):
            # open the file
            f = open(dir + "/" + file, "r")
            # read the file
            lines = f.readlines()
            # close the file
            f.close()
            # create a list to store the lines that will be written to the file
            new_lines = []
            # iterate through the lines
            for line in lines:
                # if the line is commented out, and then after any number of spaces begins with 'print(', delete that line
                if re.match("^#\s*print\(", line):
                    pass
                # otherwise, add the line to the list of lines to be written to the file
                else:
                    new_lines.append(line)
            # if the list of lines to be written to the file is not the same as the list of lines that were read from the file
            if new_lines != lines:
                # open the file
                f = open(dir + "/" + file, "w")
                # write the new lines to the file
                f.writelines(new_lines)
                # close the file
                f.close()
                # add the file to the list of affected files
                affected_files.append(file)
    # display a list of all affected files
    easygui.textbox("The following files were affected:", "Affected Files", affected_files)

main()
