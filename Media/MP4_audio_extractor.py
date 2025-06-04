import os
import subprocess
import tkinter as tk
from tkinter import filedialog

def split_and_export():
    # Get the input video file path
    input_file_path = filedialog.askopenfilename(title="Select Video File")
    if not input_file_path:
        return

    # Create a temporary directory to store the split files
    temp_dir = "temp_splits"
    os.makedirs(temp_dir, exist_ok=True)

    # Split the video into 10-second segments using ffmpeg
    for i in range(0, 100, 10):
        start_time = i
        end_time = i + 10
        output_file = f"{temp_dir}\\segment_{i}.mp4"  # Use backslash for path separator
        ffmpeg_cmd = f"ffmpeg -i '{input_file_path}' -ss {start_time} -to {end_time} -c copy '{output_file}'"
        subprocess.call(ffmpeg_cmd, shell=True)

    # Extract audio from each segment and save as MP3
    for segment_file in os.listdir(temp_dir):
        segment_path = os.path.join(temp_dir, segment_file)
        output_audio_file = f"segment_{segment_file[:-4]}.mp3"
        ffmpeg_cmd = f"ffmpeg -i '{segment_path}' -vn -acodec libmp3lame '{output_audio_file}'"
        subprocess.call(ffmpeg_cmd, shell=True)

    # Remove the temporary directory
    os.rmdir(temp_dir)

# Create the GUI
root = tk.Tk()
root.title("Video Splitter and Audio Extractor")

# Create a button to trigger the splitting and exporting process
button = tk.Button(root, text="Split and Export", command=split_and_export)
button.pack()

root.mainloop()