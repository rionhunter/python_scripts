import os
import sys
import argparse
import pickle
import re
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:  # pragma: no cover - optional GUI dependency
    tk = None
    filedialog = None
    messagebox = None
from pytube import YouTube
try:
    # MoviePy <2.0
    from moviepy.editor import AudioFileClip  # type: ignore
except Exception:  # pragma: no cover - compatibility path
    # MoviePy >=2.0
    from moviepy.audio.io.AudioFileClip import AudioFileClip  # type: ignore

# Constants
SAVE_FILE = "last_save_path.pkl"

def sanitize_filename(name):
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", str(name or ""))
    sanitized = sanitized.rstrip(" .")
    return sanitized or "output"

def load_last_save_path():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'rb') as f:
            return pickle.load(f)
    return ""

def save_last_save_path(path):
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(path, f)

def convert_to_seconds(time_str):
    time_str = str(time_str).strip()
    if not time_str:
        raise ValueError("Empty time string")
    parts = [p.strip() for p in time_str.split(':')]
    parts = list(map(int, parts))
    if len(parts) == 1:
        return parts[0]  # seconds
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]  # minutes:seconds
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]  # hours:minutes:seconds
    else:
        raise ValueError("Invalid time format")


def _choose_audio_stream(streams, quality_kbps=None):
    """Choose an audio-only stream, optionally near desired quality in kbps.

    If quality_kbps is provided, pick the highest stream <= desired; if none,
    pick the closest higher one; otherwise fall back to first available.
    """
    audio_streams = [s for s in streams.filter(only_audio=True)]
    if not audio_streams:
        return None
    if quality_kbps is None:
        # Best available abr by numeric value
        def abr_num(s):
            try:
                return int((s.abr or "0kbps").replace("kbps", "").strip())
            except Exception:
                return 0
        return sorted(audio_streams, key=abr_num, reverse=True)[0]

    # Parse quality and select
    try:
        desired = int(str(quality_kbps).lower().replace("kbps", "").replace("k", "").strip())
    except Exception:
        desired = None

    if desired is None:
        return audio_streams[0]

    def abr_num(s):
        try:
            return int((s.abr or "0kbps").replace("kbps", "").strip())
        except Exception:
            return 0

    sorted_streams = sorted(audio_streams, key=abr_num)
    # Try highest <= desired
    leq = [s for s in sorted_streams if abr_num(s) <= desired]
    if leq:
        return leq[-1]
    # Otherwise, lowest above desired
    return sorted_streams[0]

def download_audio(youtube_url, start_time, end_time, file_format,
                   output_path=None, quality=None, show_ui=True):
    """Download a YouTube audio snippet and save to output_path.

    - youtube_url: str
    - start_time, end_time: str in SS, MM:SS, or HH:MM:SS
    - file_format: 'mp3' | 'ogg' | 'wav'
    - output_path: full file path to save to; if None and show_ui True, opens a save dialog; if None and show_ui False, defaults to 'output.<ext>' in CWD
    - quality: desired audio bitrate (e.g., 128 or '128k'), best effort
    - show_ui: whether to show filedialog/messagebox UI
    """
    output_file = None
    audio_file = None
    try:
        yt = YouTube(youtube_url)
        stream = _choose_audio_stream(yt.streams, quality)
        if stream is None:
            raise RuntimeError("No audio streams available for this video")
        audio_file = stream.download(filename='temp_audio')

        start_seconds = convert_to_seconds(start_time)
        end_seconds = convert_to_seconds(end_time)
        if end_seconds <= start_seconds:
            raise ValueError("End time must be greater than start time")

        audio_clip = AudioFileClip(audio_file).subclip(start_seconds, end_seconds)

        ext = file_format.lower()
        if ext not in {"mp3", "ogg", "wav"}:
            raise ValueError("Unsupported file format. Use mp3, ogg, or wav")

        # Determine target temp output
        output_file = f"output.{ext}"
        if ext == 'mp3':
            audio_clip.write_audiofile(output_file, codec='mp3')
        elif ext == 'ogg':
            audio_clip.write_audiofile(output_file, codec='libvorbis')
        elif ext == 'wav':
            audio_clip.write_audiofile(output_file, codec='pcm_s16le')

        audio_clip.close()  # Ensure the audio clip is closed before deleting the file

        final_path = output_path
        if not final_path:
            if show_ui:
                initialdir = load_last_save_path() or os.getcwd()
                final_path = filedialog.asksaveasfilename(
                    defaultextension=f".{ext}", initialfile=output_file, initialdir=initialdir
                )
            else:
                final_path = os.path.abspath(output_file)

        if final_path:
            if os.path.abspath(output_file) != os.path.abspath(final_path):
                # Ensure directory exists
                os.makedirs(os.path.dirname(final_path) or '.', exist_ok=True)
                # Move/rename
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.replace(output_file, final_path)
            # Persist last directory
            try:
                save_last_save_path(os.path.dirname(final_path) or os.getcwd())
            except Exception:
                pass
            if show_ui:
                messagebox.showinfo("Success", f"File saved successfully: {final_path}")
        else:
            # User canceled save dialog: remove temp
            if os.path.exists(output_file):
                os.remove(output_file)
        return final_path
    except Exception as e:
        if show_ui:
            if messagebox is not None:
                messagebox.showerror("Error", str(e))
            return None
        raise
    finally:
        try:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
        except Exception:
            pass

def on_download():
    youtube_url = url_entry.get()
    start_time = start_time_entry.get()
    end_time = end_time_entry.get()
    file_format = file_format_var.get()
    if youtube_url and start_time and end_time and file_format:
        download_audio(youtube_url, start_time, end_time, file_format, show_ui=True)
    else:
        messagebox.showwarning("Input Error", "Please fill all fields")

def run_gui():
    global root, url_entry, start_time_entry, end_time_entry, file_format_var
    if tk is None:
        raise RuntimeError("Tkinter is not available. Install Python with Tk support or run with --no-gui.")
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


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="YouTube audio snippet downloader (GUI/CLI)")
    p.add_argument('--url', help='YouTube video URL')
    p.add_argument('--start', help='Start time (SS | MM:SS | HH:MM:SS)')
    p.add_argument('--end', help='End time (SS | MM:SS | HH:MM:SS)')
    p.add_argument('--format', dest='format', default='mp3', help='Output format: mp3 | ogg | wav')
    p.add_argument('--output', help='Output file path (full path). If directory, name is inferred from title.')
    p.add_argument('--quality', help='Desired audio quality (e.g., 128, 128k)')
    p.add_argument('--no-gui', action='store_true', help='Force CLI mode (no GUI)')
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Decide mode: GUI if no CLI args and not forced no-gui
    cli_params = [args.url, args.start, args.end]
    if not args.no_gui and not any(cli_params):
        run_gui()
        return 0

    # CLI mode: validate
    if not (args.url and args.start and args.end):
        print("Error: --url, --start, and --end are required in CLI mode", file=sys.stderr)
        return 2

    output_path = args.output
    if output_path and os.path.isdir(output_path):
        # If a directory was provided, infer file name from title
        try:
            yt = YouTube(args.url)
            base = sanitize_filename(yt.title)
        except Exception:
            base = 'output'
        output_path = os.path.join(output_path, f"{base}.{args.format}")

    try:
        final_path = download_audio(
            args.url, args.start, args.end, args.format,
            output_path=output_path, quality=args.quality, show_ui=False
        )
        if final_path:
            print(final_path)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
