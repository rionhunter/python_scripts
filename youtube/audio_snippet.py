import os
import pickle
import tkinter as tk
from tkinter import filedialog, messagebox
from pytube import YouTube
from moviepy.editor import AudioFileClip

# Constants
SAVE_FILE = "last_save_path.pkl"

def load_last_save_path():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'rb') as f:
            return pickle.load(f)
    return ""

def save_last_save_path(path):
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(path, f)

def convert_to_seconds(time_str):
    parts = list(map(int, time_str.split(':')))
    if len(parts) == 1:
        return parts[0]  # seconds
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]  # minutes:seconds
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]  # hours:minutes:seconds
    else:
        raise ValueError("Invalid time format")

def download_audio(youtube_url, start_time, end_time, file_format):
    try:
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(only_audio=True).first()
        audio_file = stream.download(filename='temp_audio')

        start_seconds = convert_to_seconds(start_time)
        end_seconds = convert_to_seconds(end_time)
        audio_clip = AudioFileClip(audio_file).subclip(start_seconds, end_seconds)
        
        if file_format == 'mp3':
            output_file = 'output.mp3'
            audio_clip.write_audiofile(output_file, codec='mp3')
        elif file_format == 'ogg':
            output_file = 'output.ogg'
            audio_clip.write_audiofile(output_file, codec='libvorbis')
        elif file_format == 'wav':
            output_file = 'output.wav'
            audio_clip.write_audiofile(output_file, codec='pcm_s16le')

        audio_clip.close()  # Ensure the audio clip is closed before deleting the file
        
        save_path = filedialog.asksaveasfilename(defaultextension=f".{file_format}", initialfile=output_file)
        if save_path:
            os.rename(output_file, save_path)
            save_last_save_path(os.path.dirname(save_path))
            messagebox.showinfo("Success", f"File saved successfully: {save_path}")
        os.remove(audio_file)
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_download():
    youtube_url = url_entry.get()
    start_time = start_time_entry.get()
    end_time = end_time_entry.get()
    file_format = file_format_var.get()
    if youtube_url and start_time and end_time and file_format:
        download_audio(youtube_url, start_time, end_time, file_format)
    else:
        messagebox.showwarning("Input Error", "Please fill all fields")

# GUI Setup
root = tk.Tk()
root.title("YouTube Audio Downloader")

tk.Label(root, text="YouTube URL:").grid(row=0, column=0)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1)

tk.Label(root, text="Start Time (HH:MM:SS or MM:SS or SS):").grid(row=1, column=0)
start_time_entry = tk.Entry(root, width=10)
start_time_entry.grid(row=1, column=1)

tk.Label(root, text="End Time (HH:MM:SS or MM:SS or SS):").grid(row=2, column=0)
end_time_entry = tk.Entry(root, width=10)
end_time_entry.grid(row=2, column=1)

tk.Label(root, text="File Format:").grid(row=3, column=0)
file_format_var = tk.StringVar(value='mp3')
tk.Radiobutton(root, text="MP3", variable=file_format_var, value='mp3').grid(row=3, column=1)
tk.Radiobutton(root, text="OGG", variable=file_format_var, value='ogg').grid(row=3, column=2)
tk.Radiobutton(root, text="WAV", variable=file_format_var, value='wav').grid(row=3, column=3)

download_button = tk.Button(root, text="Download", command=on_download)
download_button.grid(row=4, column=1)

root.mainloop()
