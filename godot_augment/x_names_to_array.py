import tkinter as tk
from tkinter import scrolledtext

def process_input():
    try:
        # Getting the input from the text box
        input_content = text_input.get('1.0', tk.END)

        # Process the input to find signal names
        signal_names = []
        parts = input_content.split('}, {')
        for part in parts:
            name_start_idx = part.find('"name": "') + len('"name": "')
            if name_start_idx > -1:
                name_end_idx = part.find('"', name_start_idx)
                signal_name = part[name_start_idx:name_end_idx]
                signal_names.append(f"'{signal_name}'")

        # Creating the final string representation of the list
        result = f"[{', '.join(signal_names)}]"

        # Displaying the result in the result window
        result_display.delete('1.0', tk.END)
        result_display.insert(tk.INSERT, result)
    except Exception as e:
        result_display.delete('1.0', tk.END)
        result_display.insert(tk.INSERT, f"Error: {e}")

# Setting up the main window
root = tk.Tk()
root.title("Godot Signal Name Extractor")

# Text input area
text_input = scrolledtext.ScrolledText(root, height=10)
text_input.pack(padx=10, pady=5)

# Process button
process_button = tk.Button(root, text="Process", command=process_input)
process_button.pack(pady=5)

# Result display area
result_display = scrolledtext.ScrolledText(root, height=10)
result_display.pack(padx=10, pady=5)

# Run the application
root.mainloop()
