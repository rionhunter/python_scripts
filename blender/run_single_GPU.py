import tkinter as tk
from tkinter import filedialog
import os
import json
import subprocess

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def select_blender_exe():
    file_path = filedialog.askopenfilename(title="Select Blender Executable", filetypes=[("Blender Executable", "*.exe" if os.name == "nt" else "")])
    blender_exe_var.set(file_path)

def select_blend_file():
    file_path = filedialog.askopenfilename(title="Select Blender File", filetypes=[("Blender Files", "*.blend")])
    blend_file_var.set(file_path)

def select_output_folder():
    folder_path = filedialog.askdirectory(title="Select Output Folder")
    output_folder_var.set(folder_path)

def start_render():
    config['blender_exe'] = blender_exe_var.get()
    config['blend_file'] = blend_file_var.get()
    config['output_folder'] = output_folder_var.get()
    config['start_frame'] = start_frame_var.get()
    config['end_frame'] = end_frame_var.get()
    config['frame_step'] = frame_step_var.get()
    config['gpu_index'] = gpu_index_var.get()
    config['compute_device'] = compute_device_var.get()
    save_config(config)

    output_path = os.path.join(output_folder_var.get(), "frame_####.png")
    start_frame = int(start_frame_var.get())
    end_frame = int(end_frame_var.get())
    frame_step = int(frame_step_var.get())
    gpu_index = int(gpu_index_var.get())
    compute_device = compute_device_var.get()

    command = [
        "python", "single_GPU_render_with_intervals.py",
        config['blender_exe'],
        config['blend_file'],
        output_path,
        str(start_frame),
        str(end_frame),
        str(frame_step),
        str(gpu_index),
        compute_device
    ]
    print("Executing command:", " ".join(command))
    subprocess.run(command)

# Load configuration
config = load_config()

# Set up the main window
root = tk.Tk()
root.title("Blender Render Setup")

# Variables to store user input
blender_exe_var = tk.StringVar(value=config.get('blender_exe', ''))
blend_file_var = tk.StringVar(value=config.get('blend_file', ''))
output_folder_var = tk.StringVar(value=config.get('output_folder', ''))
start_frame_var = tk.StringVar(value=config.get('start_frame', ''))
end_frame_var = tk.StringVar(value=config.get('end_frame', ''))
frame_step_var = tk.StringVar(value=config.get('frame_step', ''))
gpu_index_var = tk.StringVar(value=config.get('gpu_index', ''))
compute_device_var = tk.StringVar(value=config.get('compute_device', 'CUDA'))

# Layout
tk.Label(root, text="Blender Executable:").grid(row=0, column=0, sticky='e')
tk.Entry(root, textvariable=blender_exe_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Browse", command=select_blender_exe).grid(row=0, column=2)

tk.Label(root, text="Blend File:").grid(row=1, column=0, sticky='e')
tk.Entry(root, textvariable=blend_file_var, width=50).grid(row=1, column=1)
tk.Button(root, text="Browse", command=select_blend_file).grid(row=1, column=2)

tk.Label(root, text="Output Folder:").grid(row=2, column=0, sticky='e')
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=2, column=1)
tk.Button(root, text="Browse", command=select_output_folder).grid(row=2, column=2)

tk.Label(root, text="Start Frame:").grid(row=3, column=0, sticky='e')
tk.Entry(root, textvariable=start_frame_var).grid(row=3, column=1)

tk.Label(root, text="End Frame:").grid(row=4, column=0, sticky='e')
tk.Entry(root, textvariable=end_frame_var).grid(row=4, column=1)

tk.Label(root, text="Frame Step:").grid(row=5, column=0, sticky='e')
tk.Entry(root, textvariable=frame_step_var).grid(row=5, column=1)

tk.Label(root, text="GPU Index:").grid(row=6, column=0, sticky='e')
tk.Entry(root, textvariable=gpu_index_var).grid(row=6, column=1)

tk.Label(root, text="Compute Device:").grid(row=7, column=0, sticky='e')
tk.Entry(root, textvariable=compute_device_var).grid(row=7, column=1)

tk.Button(root, text="Start Render", command=start_render).grid(row=8, columnspan=3)

# Run the main loop
root.mainloop()
