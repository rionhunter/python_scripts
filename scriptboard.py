#!/usr/bin/env python3
"""
Scriptboard
1. scan the immediate folder for other python scripts (discounting self)
2. using tkinter, create a vertical list of buttons that trigger each script respectively
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# get the current working directory
cwd = os.getcwd()

# get the list of files in the current working directory
files = os.listdir(cwd)

# filter out the files that are not python scripts
scripts = [f for f in files if f.endswith('.py')]

# remove the scriptboard script from the list of scripts
scripts.remove('scriptboard.py')

# create the tkinter window
root = tk.Tk()
root.title('Scriptboard')

# create a frame to hold the buttons
frame = ttk.Frame(root)
frame.pack()

# create a button for each script
for script in scripts:
    button = ttk.Button(frame, text=script, command=lambda script=script: os.system('python ' + script))
    button.pack()

# run the tkinter window
root.mainloop()
