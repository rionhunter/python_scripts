import os
from tkinter import Tk, filedialog, Button, Label, Entry, Checkbutton, IntVar, messagebox
from natsort import natsorted


def natural_sort_key(s):
    """Sort filenames naturally (accounting for numbers and decimals)."""
    # natsort returns a sorted list, we take the first (and only) element
    return natsorted([s])[0]


class MergeApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Merge Text Files")
        self.root.geometry("500x200")

        # Checkbox: include pretty file names
        self.include_var = IntVar(value=0)
        self.chk_include = Checkbutton(
            self.root,
            text="Include filenames",
            variable=self.include_var
        )
        self.chk_include.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))

        # Input directory selection
        Label(self.root, text="Input Directory:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.dir_entry = Entry(self.root, width=40)
        self.dir_entry.grid(row=1, column=1, padx=5, pady=5)
        Button(
            self.root,
            text="Browse",
            command=self.browse_dir
        ).grid(row=1, column=2, padx=5, pady=5)

        # Output file selection
        Label(self.root, text="Output File:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.out_entry = Entry(self.root, width=40)
        self.out_entry.grid(row=2, column=1, padx=5, pady=5)
        Button(
            self.root,
            text="Browse",
            command=self.browse_out
        ).grid(row=2, column=2, padx=5, pady=5)

        # Merge button
        Button(
            self.root,
            text="Merge Files",
            width=15,
            command=self.merge_files
        ).grid(row=3, column=1, pady=15)

        self.root.mainloop()

    def browse_dir(self):
        directory = filedialog.askdirectory(title="Select a directory containing text files")
        if directory:
            self.dir_entry.delete(0, 'end')
            self.dir_entry.insert(0, directory)

    def browse_out(self):
        outfile = filedialog.asksaveasfilename(
            title="Save the merged file",
            defaultextension=".txt",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if outfile:
            self.out_entry.delete(0, 'end')
            self.out_entry.insert(0, outfile)

    def merge_files(self):
        input_dir = self.dir_entry.get()
        output_file = self.out_entry.get()

        if not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Please select a valid input directory.")
            return
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file.")
            return

        try:
            # Gather .txt and .md files
            files = [f for f in os.listdir(input_dir) if f.endswith(('.txt', '.md'))]
            sorted_files = natsorted(files, key=natural_sort_key)

            with open(output_file, 'w', encoding='utf-8') as outfile:
                for filename in sorted_files:
                    filepath = os.path.join(input_dir, filename)
                    # Optionally include a pretty header for each file
                    if self.include_var.get():
                        pretty_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                        outfile.write(f"=== {pretty_name} ===\n")

                    # Append the file content
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())

                    outfile.write("\n\n")  # Separation between files

            messagebox.showinfo("Success", f"Merged {len(sorted_files)} files into '{output_file}'.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    MergeApp()
