import tkinter as tk
from tkinter import filedialog, messagebox

def purge_duplicates(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Remove duplicate lines while maintaining order
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)

        with open(file_path, 'w') as file:
            file.writelines(unique_lines)

        messagebox.showinfo("Success", "Duplicate lines removed successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select a text file",
        filetypes=[("Text Files", "*.txt *.md *.py"), ("All Files", "*.*")]
    )
    if file_path:
        purge_duplicates(file_path)

def main():
    root = tk.Tk()
    root.title("Duplicate Line Remover")

    select_button = tk.Button(root, text="Select File", command=select_file)
    select_button.pack(pady=20)

    root.geometry("300x100")
    root.mainloop()

if __name__ == "__main__":
    main()