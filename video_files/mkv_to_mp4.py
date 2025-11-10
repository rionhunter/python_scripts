"""
Simple GUI: pick an MKV file and convert to MP4 using ffmpeg.

Usage:
 - Requires ffmpeg available on PATH.
 - Run: python mkv_to_mp4.py

This script opens a small tkinter window. Select an .mkv file, click Convert.
Conversion runs in a background thread and shows ffmpeg output in the GUI.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import threading
import queue
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox


def find_ffmpeg() -> str | None:
	"""Return path to ffmpeg executable or None if not found."""
	return shutil.which("ffmpeg")


def choose_output_path(input_path: Path) -> Path:
	"""Return a non-colliding output path in same directory with .mp4 extension."""
	base = input_path.with_suffix("")
	out = base.with_suffix(".mp4")
	counter = 1
	while out.exists():
		out = base.with_name(f"{base.name}_converted{counter}").with_suffix(".mp4")
		counter += 1
	return out


class ConverterApp(tk.Tk):
	def __init__(self) -> None:
		super().__init__()
		self.title("MKV → MP4 Converter")
		self.geometry("640x360")
		self.resizable(False, False)

		self.file_path: Path | None = None
		self.ffmpeg = find_ffmpeg()

		self._build_ui()

		# queue for subprocess output
		self._q: queue.Queue[str] = queue.Queue()
		self._worker: threading.Thread | None = None

	def _build_ui(self) -> None:
		frm = ttk.Frame(self, padding=12)
		frm.pack(fill=tk.BOTH, expand=True)

		# File selector
		btn_select = ttk.Button(frm, text="Select MKV file…", command=self.select_file)
		btn_select.grid(row=0, column=0, sticky=tk.W)

		self.lbl_selected = ttk.Label(frm, text="No file selected", wraplength=480)
		self.lbl_selected.grid(row=1, column=0, columnspan=3, pady=(8, 12), sticky=tk.W)

		# Convert button
		self.btn_convert = ttk.Button(frm, text="Convert to MP4", command=self.start_conversion)
		self.btn_convert.grid(row=2, column=0, sticky=tk.W)
		self.btn_convert.state(["disabled"])

		# Open folder after conversion
		self.open_after_var = tk.BooleanVar(value=True)
		chk = ttk.Checkbutton(frm, text="Open folder after conversion", variable=self.open_after_var)
		chk.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

		# Log area
		lbl_log = ttk.Label(frm, text="ffmpeg output:")
		lbl_log.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(12, 0))

		self.txt_log = tk.Text(frm, height=12, width=76, wrap=tk.NONE)
		self.txt_log.grid(row=4, column=0, columnspan=3, pady=(6, 0))
		self.txt_log.configure(state=tk.DISABLED)

		# status
		self.status_var = tk.StringVar(value=("ffmpeg not found" if not self.ffmpeg else "ready"))
		lbl_status = ttk.Label(frm, textvariable=self.status_var)
		lbl_status.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))

	def select_file(self) -> None:
		file = filedialog.askopenfilename(title="Select MKV file", filetypes=[("MKV files", "*.mkv"), ("All files", "*")])
		if not file:
			return
		p = Path(file)
		if p.suffix.lower() != ".mkv":
			messagebox.showwarning("File type", "Selected file does not have .mkv extension. Continuing anyway.")
		self.file_path = p
		self.lbl_selected.config(text=str(p))
		if self.ffmpeg:
			self.btn_convert.state(["!disabled"])
		else:
			self.btn_convert.state(["disabled"])
			messagebox.showerror("ffmpeg not found", "ffmpeg was not found on your PATH. Please install ffmpeg and try again.")

	def start_conversion(self) -> None:
		if not self.file_path:
			messagebox.showinfo("No file", "Please select a file first.")
			return
		if not self.ffmpeg:
			messagebox.showerror("ffmpeg missing", "ffmpeg is required but was not found.")
			return

		out_path = choose_output_path(self.file_path)
		cmd = [self.ffmpeg, "-y", "-i", str(self.file_path), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_path)]

		# disable UI while running
		self.btn_convert.state(["disabled"])
		self.status_var.set("converting…")
		self._append_log(f"Running: {' '.join(cmd)}\n")

		# run ffmpeg in background thread, stream stderr to queue
		def worker() -> None:
			try:
				# Use text mode with explicit encoding and error replacement so
				# ffmpeg output containing bytes outside the local codepage
				# won't raise UnicodeDecodeError when iterating stderr.
				proc = subprocess.Popen(
					cmd,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True,
					encoding="utf-8",
					errors="replace",
				)
			except Exception as e:
				self._q.put(f"ERROR: failed to start ffmpeg: {e}\n")
				self._q.put("__DONE__")
				return

			# read stderr
			assert proc.stderr is not None
			for line in proc.stderr:
				self._q.put(line)
			proc.wait()
			if proc.returncode == 0:
				self._q.put("__SUCCESS__")
			else:
				self._q.put(f"__ERROR__ returncode={proc.returncode}\n")
			self._q.put("__DONE__")

		self._worker = threading.Thread(target=worker, daemon=True)
		self._worker.start()
		self.after(100, lambda: self._poll_queue(out_path))

	def _poll_queue(self, out_path: Path) -> None:
		try:
			while True:
				line = self._q.get_nowait()
				if line == "__DONE__":
					# re-enable UI
					self.btn_convert.state(["!disabled"])
					self.status_var.set("ready")
					return
				if line == "__SUCCESS__":
					self._append_log("Conversion finished successfully.\n")
					if self.open_after_var.get():
						try:
							if sys.platform == "win32":
								os.startfile(out_path.parent)
							else:
								subprocess.Popen(["xdg-open", str(out_path.parent)])
						except Exception:
							pass
					continue
				if line.startswith("__ERROR__"):
					self._append_log("Conversion failed: " + line + "\n")
					continue
				self._append_log(line)
		except queue.Empty:
			# nothing to read now
			pass
		# keep polling while worker still alive
		if self._worker and self._worker.is_alive():
			self.after(100, lambda: self._poll_queue(out_path))
		else:
			# ensure button state
			self.btn_convert.state(["!disabled"])
			self.status_var.set("ready")

	def _append_log(self, text: str) -> None:
		self.txt_log.configure(state=tk.NORMAL)
		self.txt_log.insert(tk.END, text)
		self.txt_log.see(tk.END)
		self.txt_log.configure(state=tk.DISABLED)


def main() -> None:
	app = ConverterApp()
	app.mainloop()


if __name__ == "__main__":
	main()

