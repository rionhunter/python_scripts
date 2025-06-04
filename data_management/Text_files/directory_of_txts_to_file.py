import os
import tkinter as tk
from tkinter import filedialog

def compile_txt_files(directory_path):
    # Check if the given directory exists
    if not os.path.isdir(directory_path):
        print(f"The directory '{directory_path}' does not exist.")
        return

    # Get the name of the directory and create the output file name
    directory_name = os.path.basename(directory_path)
    output_file_name = os.path.join(os.path.dirname(directory_path), directory_name + ".txt")

    # Open the output file in write mode to overwrite if it already exists
    with open(output_file_name, 'w') as output_file:
        # Iterate over all files in the given directory
        for file in os.listdir(directory_path):
            # Process only txt files
            if file.endswith(".txt"):
                file_path = os.path.join(directory_path, file)
                # Write the file name (formatted) as a header in the output file
                formatted_file_name = file.replace('_', ' ').rsplit('.', 1)[0]
                output_file.write(f"\n--- {formatted_file_name} ---\n\n")
                # Read and write the contents of the txt file to the output file
                with open(file_path, 'r') as input_file:
                    output_file.write(input_file.read() + "\n")

    print(f"All txt files have been compiled into '{output_file_name}'.")

def ask_directory():
    # Set up the root Tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open the directory selection dialog
    directory_path = filedialog.askdirectory()
    root.destroy()  # Close the Tkinter window after selection

    # If a directory was selected, proceed to compile files
    if directory_path:
        compile_txt_files(directory_path)
    else:
        print("No directory selected. Exiting.")

ask_directory()
