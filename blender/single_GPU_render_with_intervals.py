import subprocess
import sys
import os
import tempfile

def setup_blender_render(blender_exe, blend_file, output_path, start_frame, end_frame, frame_step, gpu_index, compute_device):
    # Python code to configure Blender to use only the specified GPU
    python_code = f"""
import bpy
bpy.context.preferences.addons['cycles'].preferences.get_devices()
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = '{compute_device.upper()}'
for device in bpy.context.preferences.addons['cycles'].preferences.devices:
    device.use = (device.id == {gpu_index})

bpy.context.scene.render.filepath = r'{output_path}'
bpy.context.scene.frame_start = {start_frame}
bpy.context.scene.frame_end = {end_frame}
bpy.context.scene.frame_step = {frame_step}
bpy.ops.render.render(animation=True)
"""

    # Write the Python code to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_py_file:
        temp_py_file.write(python_code.encode('utf-8'))
        temp_py_file_path = temp_py_file.name

    # Build the command for rendering
    render_cmd = [
        blender_exe,
        "-b", blend_file,
        "--python", temp_py_file_path
    ]

    # Debug: Print the full command
    print("Running Blender with command:")
    print(" ".join(render_cmd))

    # Execute the render command and capture output in real-time
    with subprocess.Popen(render_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True) as process:
        for line in process.stdout:
            print(line, end='')
        for line in process.stderr:
            print(line, end='')
        process.wait()

    # Clean up temporary file
    os.remove(temp_py_file_path)

if __name__ == "__main__":
    if len(sys.argv) != 9:
        print("Usage: python script.py <blender_exe> <blend_file> <output_path> <start_frame> <end_frame> <frame_step> <gpu_index> <compute_device>")
        sys.exit(1)

    blender_exe, blend_file, output_path, start_frame, end_frame, frame_step, gpu_index, compute_device = sys.argv[1:]
    setup_blender_render(blender_exe, blend_file, output_path, int(start_frame), int(end_frame), int(frame_step), int(gpu_index), compute_device)
