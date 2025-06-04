import tkinter as tk
from tkinter import scrolledtext, messagebox

def convert_to_zim():
    input_text = input_text_area.get("1.0", tk.END)
    output_text = ""
    lines = input_text.splitlines()
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith("```"):
            if in_code_block:
                # End the verbatim block if we're currently in one
                output_text += "'''\n"
                in_code_block = False
            else:
                # Start a verbatim block, skipping the language line
                output_text += "'''\n"
                in_code_block = True
        elif in_code_block:
            # Add lines as part of the verbatim text
            output_text += line + "\n"
        else:
            if line.startswith("#"):
                # Convert markdown headers to Zim headers
                level = len(line) - len(line.lstrip('#'))
                title = line.strip('# ')
                output_text += f"{'=' * level} {title} {'=' * level}\n"
            else:
                output_text += line + "\n"

    if in_code_block:
        # Close any unclosed verbatim blocks
        output_text += "'''\n"

    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", output_text)
    messagebox.showinfo("Conversion Status", "Conversion to Zim format completed!")

# Set up the main window
root = tk.Tk()
root.title("GPT to Zim Format Converter")

# Set up the input text area
input_text_area = scrolledtext.ScrolledText(root, width=70, height=20)
input_text_area.pack(padx=10, pady=5)

# Set up the convert button
convert_button = tk.Button(root, text="Convert to Zim Format", command=convert_to_zim)
convert_button.pack(pady=10)

# Set up the output text area
output_text_area = scrolledtext.ScrolledText(root, width=70, height=20)
output_text_area.pack(padx=10, pady=5)

root.mainloop()
