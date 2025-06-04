import tkinter as tk
from tkinter.scrolledtext import ScrolledText

def parse_input_and_convert():
    input_data = text_input.get('1.0', tk.END)
    lines = input_data.split('\n')
    result_dict = {}

    for line in lines:
        if '\t' in line:  # Looking for tabs that separate our key-value pairs
            key, value = line.split('\t', 1)
            result_dict[key] = value.strip()

    # Now, let's beautify that dictionary into a string representation
    pretty_dict_string = "{\n" + ",\n".join(f'"{k}": "{v}"' for k, v in result_dict.items()) + "\n}"

    text_output.delete('1.0', tk.END)  # Clear previous output
    text_output.insert('1.0', pretty_dict_string)  # Voila, insert new prettified dictionary

# Setting up the UI because we're fancy like that
root = tk.Tk()
root.title("Spreadsheet Despair Converter")

text_input = ScrolledText(root, height=15, width=75)
text_input.pack(padx=10, pady=5)

convert_button = tk.Button(root, text="Convert", command=parse_input_and_convert)
convert_button.pack(pady=5)

text_output = ScrolledText(root, height=15, width=75)
text_output.pack(padx=10, pady=5)

root.mainloop()
