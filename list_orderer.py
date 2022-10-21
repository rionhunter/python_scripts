#!/usr/bin/env python3
"""
LINE RENUMBERER - replace original numbers at start of lines with order they appeared ine
1. if most lines of the string in the clipboard don't start with a number, quit
2. with the confirmed string, scan each line and count its placement it if it starts with a number (integer or float)
3. replace the number (up to the first space) with its placement amongst numbered lines,  followed by a '.
6. don't add numbers to the beginning of lines that didn't have numbers to begin with, but include all unaltered lines in output
7. send the results to the clipboard and close
"""

import pyperclip
import re

# get text from clipboard
text = pyperclip.paste()

# check if most lines start with a number
lines = text.split('\n')
num_lines = len(lines)
num_lines_with_num = 0
for line in lines:
    if re.match(r'^\d+', line):
        num_lines_with_num += 1

if num_lines_with_num / num_lines < 0.5:
    print('Most lines do not start with a number. Quitting.')
    quit()

# scan each line and count its placement it if it starts with a number (integer or float)
# replace the number (up to the first space) with its placement amongst numbered lines,  followed by a '.
# don't add numbers to the beginning of lines that didn't have numbers to begin with, but include all unaltered lines in output

new_lines = []
line_num = 0
for line in lines:
    if re.match(r'^\d+', line):
        line_num += 1
        new_lines.append(str(line_num) + '. ' + line[line.find(' ') + 1:])
    else:
        new_lines.append(line)

# send the results to the clipboard and close
pyperclip.copy('\n'.join(new_lines))
print('Done.')
