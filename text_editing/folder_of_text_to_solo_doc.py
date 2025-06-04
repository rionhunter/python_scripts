import os
import re
from tkinter import Tk, filedialog
from natsort import natsorted

def natural_sort_key(s):
    """Sort filenames naturally (accounting for numbers and decimals)."""
    return natsorted([s])[0]

def get_directory():
    """Prompt the user to select a directory."""
    Tk().withdraw()  # Hide the root Tk window
    return filedialog.askdirectory(title="Select a directory containing text files")

def get_output_file():
    """Prompt the user to select an output file."""
    Tk().withdraw()  # Hide the root Tk window
    return filedialog.asksaveasfilename(
        title="Save the merged file",
        defaultextension=".txt",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )

def merge_files(input_dir, output_file):
    """Merge all text and Markdown files in the directory into one file."""
    try:
        files = [f for f in os.listdir(input_dir) if f.endswith(('.txt', '.md'))]
        sorted_files = natsorted(files, key=natural_sort_key)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            for filename in sorted_files:
                filepath = os.path.join(input_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")  # Add separation between files
        print(f"Merged {len(sorted_files)} files into '{output_file}'.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_dir = get_directory()
    if not input_dir:
        print("No directory selected. Exiting.")
        exit()

    output_file = get_output_file()
    if not output_file:
        print("No output file specified. Exiting.")
        exit()

    merge_files(input_dir, output_file)
