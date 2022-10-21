#!/usr/bin/env python3
"""
Linux Python Script Compatibility maker
1. delete any pre-existing shell file
2. scan all python scripts in the same folder.
3. if the first line isn't '#!/usr/bin/env python3', inject the string at the start and save.
4. create a shell file, and for each script, add the lines 'chmod 755 [SCRIPT_ADDRESS]' and 'chmod +x [SCRIPT_ADDRESS]'pyth
5. print the scripts that did not have the first line
6. run the shell file
"""

import os
import sys

# get the current directory
current_dir = os.getcwd()

# get all files in the current directory
files = os.listdir(current_dir)

# delete any pre-existing shell file
for file in files:
    if file.endswith('.sh'):
        os.remove(file)

# create a shell file
shell_file = open('make_scripts_compatible.sh', 'w')

# scan all python scripts in the same folder.
for file in files:
    if file.endswith('.py'):
        # open the file
        f = open(file, 'r')
        # read the first line
        first_line = f.readline()
        # if the first line isn't '#!/usr/bin/env python3', inject the string at the start and save.
        if first_line != '#!/usr/bin/env python3\n':
            # close the file
            f.close()
            # open the file again
            f = open(file, 'r')
            # read all lines
            lines = f.readlines()
            # close the file
            f.close()
            # open the file again
            f = open(file, 'w')
            # write the first line
            f.write('#!/usr/bin/env python3\n')
            # write all lines
            for line in lines:
                f.write(line)
            # close the file
            f.close()
            # print the scripts that did not have the first line
            print(file)
        # add the lines 'chmod 755 [SCRIPT_ADDRESS]' and 'chmod +x [SCRIPT_ADDRESS]' to the shell file
        shell_file.write('chmod 755 ' + file + '\n')
        shell_file.write('chmod +x ' + file + '\n')

# close the shell file
shell_file.close()

# run the shell file
os.system('sh make_scripts_compatible.sh')
