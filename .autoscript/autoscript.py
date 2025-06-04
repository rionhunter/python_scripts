import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import openai

# Default values for command-line arguments
cli_args = {"api_key": None, "file_location": None, "prompt": None}

# Argument parsing
for arg in sys.argv[1:]:
    if "=" in arg:
        key, value = arg.split("=", 1)
        key = key.lstrip('-')
        if key in cli_args:
            cli_args[key] = value
        else:
            print(f"Unknown argument key: {key}")
            sys.exit(1)

api_key, file_location, prompt_text = cli_args["api_key"], cli_args["file_location"], cli_args["prompt"]

if file_location:
    try:
        with open(file_location, 'r') as file:
            file_contents = file.read()
            if prompt_text is None:
                prompt_text = file_contents
    except IOError:
        messagebox.showerror("File Error", f"Cannot open file: {file_location}")
        sys.exit(1)

# OpenAI Call Function
def call_openai_api(prompt, api_key):
    openai.api_key = api_key
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return None

# GUI Functions
def run():
    api_key_from_input = api_key_var.get()
    prompt_from_input = text_editor.get("1.0", tk.END).strip()

    if not api_key_from_input:
        messagebox.showerror("API Key Error", "Please enter your OpenAI API Key")
        return

    result = call_openai_api(prompt_from_input, api_key_from_input)
    if result:
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result)

def save_to_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as f:
            f.write(output_text.get("1.0", tk.END))

# GUI Setup
root = tk.Tk()
root.title("OpenAI Interaction App")

api_key_var = tk.StringVar(value=api_key)
prompt_var = tk.StringVar(value=prompt_text)

# API Key Entry
tk.Label(root, text="OpenAI API Key:").grid(row=0, column=0, sticky='w')
api_key_entry = tk.Entry(root, textvariable=api_key_var, width=50)
api_key_entry.grid(row=0, column=1)

# Text Editor (File contents / Prompt)
tk.Label(root, text="Edit your prompt:").grid(row=1, column=0, columnspan=2)
text_editor = scrolledtext.ScrolledText(root, height=10, width=60)
text_editor.grid(row=2, column=0, columnspan=2)
text_editor.insert(tk.END, prompt_text)

# Run Button
run_button = tk.Button(root, text="Run", command=run)
run_button.grid(row=3, column=1, sticky='e')

# Output Text Area
output_text = scrolledtext.ScrolledText(root, height=10, width=60)
output_text.grid(row=4, column=0, columnspan=2, pady=(0, 10))

# Save Button
save_button = tk.Button(root, text="Save to File", command=save_to_file)
save_button.grid(row=5, column=1, sticky='e')

root.mainloop()