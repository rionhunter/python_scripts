#!/usr/bin/env python3
import pyperclip
import easygui

# get the clipboard contents
clipboard = pyperclip.paste()

# ask for the string to replace
replace_string = easygui.enterbox("Enter the string to replace:")

# ask for the string to replace it with
replace_with = easygui.enterbox("Enter the string to replace it with:")

# replace the string
clipboard = clipboard.replace(replace_string, replace_with)

# return the results to the clipboard
pyperclip.copy(clipboard)
