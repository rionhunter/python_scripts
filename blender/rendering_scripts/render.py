import tkinter as tk
from tkinter import Label, filedialog, simpledialog
import subprocess
import os
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import Label, filedialog, simpledialog
import subprocess
import os
from PIL import Image, ImageTk

def get_blender_path():
    config_file = 'blender_path.txt'
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            blender_path = file.read().strip()
            if os.path.exists(blender_path):
                return blender_path
    root = tk.Tk()
    root.withdraw()
    blender_path = filedialog.askopenfilename(title="Select Blender Executable", filetypes=[("Executable files", "*.exe")])
    if blender_path:
        with open(config_file, 'w') as file:
            file.write(blender_path)
        return blender_path
    else:
        print("Blender executable not selected. Exiting...")
        root.destroy()
        exit()

def get_start_frame(blend_file, blender_path):
    blender_script = "import bpy; print('StartFrame:', bpy.context.scene.frame_start)"
    command = [
        blender_path,
        "-b", blend_file,
        "--python-expr", blender_script
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    if result.stderr:
        print("Error running Blender:", result.stderr)
    
    # Look for the expected output in stdout
    lines = result.stdout.split('\n')
    for line in lines:
        if "StartFrame:" in line:
            _, start_frame = line.split(':')
            return int(start_frame.strip())

    return None



def select_blend_file(blender_path):
    root = tk.Tk()
    root.title("Render Setup")
    root.geometry("400x300")
    label = Label(root, text="Select the .blend file and output directory:")
    label.pack(pady=10)

    btn_blend = tk.Button(root, text="Select .blend File", command=lambda: select_file(root, blender_path))
    btn_blend.pack(pady=10)

    root.mainloop()

def select_file(root, blender_path):
    file_path = filedialog.askopenfilename(filetypes=[("Blender files", "*.blend")])
    if file_path:
        output_directory = filedialog.askdirectory()
        if output_directory:
            start_frame = get_start_frame(file_path, blender_path)
            if start_frame is not None:
                root.destroy()
                run_blender_instances(file_path, blender_path, output_directory, start_frame)
            else:
                print("Failed to read the start frame from the Blender file.")
                root.destroy()


def run_blender_instances(blend_file, blender_path, output_directory, start_frame):
    frame_end = 100
    gpus = [0, 1, 2, 3]  # Assume 4 GPUs indexed from 0 to 3

    for i in range(4):
        frame_step = 4
        command = [
            blender_path, 
            "-b", blend_file,
            "-s", str(start_frame + i),
            "-e", str(frame_end),
            "-j", str(frame_step),
            "-o", os.path.join(output_directory, f"frame_####_{i}"),
            "--", "--cycles-device", "CUDA",
            "--cycles-device-index", str(gpus[i]),
            "-a"
        ]
        subprocess.Popen(command)
    monitor_output(output_directory, start_frame)

def monitor_output(output_directory, start_frame):
    root = tk.Tk()
    root.title("Rendering Monitor")
    label = Label(root, text=f"Most Recent Rendered Frame (Starting from {start_frame}):")
    label.pack(pady=20)
    img_label = Label(root)
    img_label.pack()
    update_image(img_label, output_directory)
    root.mainloop()

def update_image(img_label, output_directory):
    try:
        latest_file = max([os.path.join(output_directory, f) for f in os.listdir(output_directory)], key=os.path.getmtime)
        img = Image.open(latest_file)
        img.thumbnail((400, 400))  # Resize to fit within 400x400 pixels
        photo = ImageTk.PhotoImage(img)
        img_label.config(image=photo)
        img_label.image = photo
    except ValueError:
        img_label.config(text="No frames rendered yet.")
    img_label.after(1000, lambda: update_image(img_label, output_directory))

if __name__ == "__main__":
    blender_path = get_blender_path()
    select_blend_file(blender_path)
