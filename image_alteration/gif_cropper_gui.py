"""
gif_cropper_gui.py

A small Tkinter GUI tool to load animated GIFs, draw a crop rectangle, preview the cropped animation
and export the cropped GIF while preserving timing/loop information as much as possible.

Dependencies: Pillow
    pip install pillow

Usage: Run this script. Open a GIF, drag on the preview to select crop area, press "Crop Preview" to view
the cropped animation and "Export Cropped GIF" to save.

This tool attempts to export without quality loss by cropping frames in their original mode and
saving with Pillow's save_all=True, preserving duration and loop information.
"""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Tuple

from PIL import Image, ImageTk


class GifCropperGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("GIF Cropper")
        self.geometry("900x700")

        # State
        self.original_frames: List[Image.Image] = []
        self.frame_durations: List[int] = []
        self.loop: int | None = None
        self.current_index = 0
        self.preview_frames_tk: List[ImageTk.PhotoImage] = []
        self.preview_job = None
        self.crop_box: Tuple[int, int, int, int] | None = None

        # UI
        ctrl = tk.Frame(self)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        tk.Button(ctrl, text="Open GIF", command=self.open_gif).pack(side=tk.LEFT)
        tk.Button(ctrl, text="Crop Preview", command=self.crop_preview).pack(side=tk.LEFT, padx=6)
        tk.Button(ctrl, text="Export Cropped GIF", command=self.export_cropped).pack(side=tk.LEFT)
        tk.Button(ctrl, text="Reset Selection", command=self.reset_selection).pack(side=tk.LEFT, padx=6)

        # Numeric controls for crop box (original image coordinates)
        num_ctrl = tk.Frame(self)
        num_ctrl.pack(side=tk.TOP, fill=tk.X, padx=6)
        self.var_x0 = tk.IntVar(value=0)
        self.var_y0 = tk.IntVar(value=0)
        self.var_x1 = tk.IntVar(value=0)
        self.var_y1 = tk.IntVar(value=0)

        tk.Label(num_ctrl, text="X0").pack(side=tk.LEFT)
        tk.Spinbox(num_ctrl, from_=0, to=99999, textvariable=self.var_x0, width=6).pack(side=tk.LEFT)
        tk.Label(num_ctrl, text="Y0").pack(side=tk.LEFT)
        tk.Spinbox(num_ctrl, from_=0, to=99999, textvariable=self.var_y0, width=6).pack(side=tk.LEFT)
        tk.Label(num_ctrl, text="X1").pack(side=tk.LEFT, padx=(8,0))
        tk.Spinbox(num_ctrl, from_=0, to=99999, textvariable=self.var_x1, width=6).pack(side=tk.LEFT)
        tk.Label(num_ctrl, text="Y1").pack(side=tk.LEFT)
        tk.Spinbox(num_ctrl, from_=0, to=99999, textvariable=self.var_y1, width=6).pack(side=tk.LEFT)
        tk.Button(num_ctrl, text="Apply Coordinates", command=self.apply_coords).pack(side=tk.LEFT, padx=8)

        self.coord_label = tk.Label(ctrl, text="Select an area by dragging on the image")
        self.coord_label.pack(side=tk.LEFT, padx=12)

        # Main preview canvas
        self.canvas = tk.Canvas(self, bg="#222", width=800, height=540)
        self.canvas.pack(padx=6, pady=6)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # status bar
        self.status = tk.Label(self, text="No GIF loaded.", anchor=tk.W)
        self.status.pack(fill=tk.X)

        # selection visuals
        self._start_xy = None
        self._rect_id = None
        # tag used for selection so we can always raise it above frames
        self._sel_tag = "sel_rect"

    def open_gif(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("GIF files", "*.gif"), ("All files", "*")])
        if not path:
            return
        try:
            im = Image.open(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")
            return

        # Load frames
        frames = []
        durations = []
        loop = im.info.get("loop", 0)
        try:
            i = 0
            while True:
                im.seek(i)
                frame = im.copy()
                frames.append(frame)
                durations.append(im.info.get("duration", 100))
                i += 1
        except EOFError:
            pass

        if not frames:
            messagebox.showerror("Error", "No frames found in GIF")
            return

        self.original_frames = frames
        self.frame_durations = durations
        self.loop = loop
        self.current_index = 0
        self.status.config(text=f"Loaded: {os.path.basename(path)} - {len(frames)} frames")
        self.reset_selection()
        self.build_preview_frames(self.original_frames)
        self.start_preview()

    def build_preview_frames(self, frames: List[Image.Image]) -> None:
        # Resize frames to fit canvas while keeping aspect ratio for preview
        cw = int(self.canvas.cget("width"))
        ch = int(self.canvas.cget("height"))
        self.preview_frames_tk = []
        for f in frames:
            # convert to RGBA for consistent preview
            pf = f.convert("RGBA")
            fw, fh = pf.size
            scale = min(cw / fw, ch / fh, 1.0)
            nw, nh = max(1, int(fw * scale)), max(1, int(fh * scale))
            pf_resized = pf.resize((nw, nh), Image.LANCZOS)
            self.preview_frames_tk.append(ImageTk.PhotoImage(pf_resized))
        # keep selection rectangle if present; remove only image frames
        try:
            self.canvas.delete("frame")
        except Exception:
            # canvas may not be created yet
            pass

    def start_preview(self) -> None:
        self.stop_preview()
        if not self.preview_frames_tk:
            return
        self._animate()

    def stop_preview(self) -> None:
        if self.preview_job:
            self.after_cancel(self.preview_job)
            self.preview_job = None

    def _animate(self) -> None:
        if not self.preview_frames_tk:
            return
        frame = self.preview_frames_tk[self.current_index]
        self.canvas.delete("frame")
        # center frame
        cw = int(self.canvas.cget("width"))
        ch = int(self.canvas.cget("height"))
        iw = frame.width()
        ih = frame.height()
        x = (cw - iw) // 2
        y = (ch - ih) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=frame, tags=("frame",))
        # keep reference
        self.canvas.image = frame

        # ensure selection rectangle (if any) is above the image
        try:
            self.canvas.tag_raise(self._sel_tag)
        except Exception:
            pass

        dur = self.frame_durations[self.current_index] if self.current_index < len(self.frame_durations) else 100
        self.current_index = (self.current_index + 1) % len(self.preview_frames_tk)
        self.preview_job = self.after(max(20, dur), self._animate)

    def on_mouse_down(self, event) -> None:
        self._start_xy = (event.x, event.y)
        if self._rect_id:
            self.canvas.delete(self._rect_id)
            self._rect_id = None

    def on_mouse_drag(self, event) -> None:
        if not self._start_xy:
            return
        x0, y0 = self._start_xy
        x1, y1 = event.x, event.y
        if self._rect_id:
            self.canvas.coords(self._rect_id, x0, y0, x1, y1)
        else:
            self._rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2, tags=(self._sel_tag,))
        self.coord_label.config(text=f"Select: ({x0},{y0}) -> ({x1},{y1})")

    def on_mouse_up(self, event) -> None:
        if not self._start_xy:
            return
        x0, y0 = self._start_xy
        x1, y1 = event.x, event.y
        self._start_xy = None
        if abs(x1 - x0) < 5 or abs(y1 - y0) < 5:
            # too small
            self.coord_label.config(text="Selection too small")
            return

        # convert selection on canvas back to coordinates on original frames
        bbox = self._canvas_coords_to_image_box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        self.crop_box = bbox
        self.coord_label.config(text=f"Crop box (original image coords): {bbox}")
        # update numeric entries
        self.update_entries_from_crop_box()
        # draw selection rectangle snapped to canvas coords
        cx0, cy0, cx1, cy1 = self._image_box_to_canvas_coords(*bbox)
        if self._rect_id:
            self.canvas.coords(self._rect_id, cx0, cy0, cx1, cy1)
        else:
            self._rect_id = self.canvas.create_rectangle(cx0, cy0, cx1, cy1, outline="red", width=2, tags=(self._sel_tag,))
        # ensure selection above image
        try:
            self.canvas.tag_raise(self._sel_tag)
        except Exception:
            pass

    def _canvas_coords_to_image_box(self, x0, y0, x1, y1) -> Tuple[int, int, int, int]:
        # Map canvas coords back to original frame coords using current preview scale
        if not self.original_frames:
            return (0, 0, 0, 0)
        frame = self.original_frames[0]
        fw, fh = frame.size
        cw = int(self.canvas.cget("width"))
        ch = int(self.canvas.cget("height"))
        scale = min(cw / fw, ch / fh, 1.0)
        iw = int(fw * scale)
        ih = int(fh * scale)
        offset_x = (cw - iw) // 2
        offset_y = (ch - ih) // 2
        # clamp selection to displayed image area
        sx0 = max(0, min(iw, x0 - offset_x))
        sy0 = max(0, min(ih, y0 - offset_y))
        sx1 = max(0, min(iw, x1 - offset_x))
        sy1 = max(0, min(ih, y1 - offset_y))
        # map to original coords
        ox0 = int(sx0 / scale)
        oy0 = int(sy0 / scale)
        ox1 = int(sx1 / scale)
        oy1 = int(sy1 / scale)
        # ensure inside image
        ox0 = max(0, min(fw, ox0))
        oy0 = max(0, min(fh, oy0))
        ox1 = max(0, min(fw, ox1))
        oy1 = max(0, min(fh, oy1))
        if ox1 == ox0:
            ox1 = min(fw, ox0 + 1)
        if oy1 == oy0:
            oy1 = min(fh, oy0 + 1)
        return (ox0, oy0, ox1, oy1)

    def _image_box_to_canvas_coords(self, ox0: int, oy0: int, ox1: int, oy1: int) -> Tuple[int, int, int, int]:
        """Map an original image bbox to canvas coordinates used for drawing selection."""
        if not self.original_frames:
            return (ox0, oy0, ox1, oy1)
        frame = self.original_frames[0]
        fw, fh = frame.size
        cw = int(self.canvas.cget("width"))
        ch = int(self.canvas.cget("height"))
        scale = min(cw / fw, ch / fh, 1.0)
        iw = int(fw * scale)
        ih = int(fh * scale)
        offset_x = (cw - iw) // 2
        offset_y = (ch - ih) // 2
        cx0 = offset_x + int(ox0 * scale)
        cy0 = offset_y + int(oy0 * scale)
        cx1 = offset_x + int(ox1 * scale)
        cy1 = offset_y + int(oy1 * scale)
        return (cx0, cy0, cx1, cy1)

    def update_entries_from_crop_box(self) -> None:
        if not self.crop_box:
            return
        x0, y0, x1, y1 = self.crop_box
        self.var_x0.set(x0)
        self.var_y0.set(y0)
        self.var_x1.set(x1)
        self.var_y1.set(y1)

    def apply_coords(self) -> None:
        """Apply numeric coordinates to update the selection and preview."""
        if not self.original_frames:
            messagebox.showinfo("Info", "Open a GIF first.")
            return
        try:
            x0 = int(self.var_x0.get())
            y0 = int(self.var_y0.get())
            x1 = int(self.var_x1.get())
            y1 = int(self.var_y1.get())
        except Exception:
            messagebox.showerror("Error", "Invalid coordinate values")
            return
        # clamp to image
        fw, fh = self.original_frames[0].size
        x0 = max(0, min(fw, x0))
        x1 = max(0, min(fw, x1))
        y0 = max(0, min(fh, y0))
        y1 = max(0, min(fh, y1))
        if x1 == x0 or y1 == y0:
            messagebox.showerror("Error", "Zero-size selection")
            return
        self.crop_box = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        # draw on canvas
        cx0, cy0, cx1, cy1 = self._image_box_to_canvas_coords(*self.crop_box)
        if self._rect_id:
            self.canvas.coords(self._rect_id, cx0, cy0, cx1, cy1)
        else:
            self._rect_id = self.canvas.create_rectangle(cx0, cy0, cx1, cy1, outline="red", width=2, tags=(self._sel_tag,))
        try:
            self.canvas.tag_raise(self._sel_tag)
        except Exception:
            pass

    def crop_preview(self) -> None:
        if not self.original_frames:
            messagebox.showinfo("Info", "Open a GIF first.")
            return
        if not self.crop_box:
            messagebox.showinfo("Info", "Make a selection first by dragging on the preview.")
            return

        cropped = [f.crop(self.crop_box) for f in self.original_frames]
        # rebuild preview frames
        self.build_preview_frames(cropped)
        # swap the frames used for preview (but keep original_frames intact)
        self.start_preview()
        self.status.config(text=f"Previewing cropped area {self.crop_box}")

    def reset_selection(self) -> None:
        self.crop_box = None
        self.coord_label.config(text="Select an area by dragging on the image")
        if self._rect_id:
            self.canvas.delete(self._rect_id)
            self._rect_id = None

    def export_cropped(self) -> None:
        if not self.original_frames:
            messagebox.showinfo("Info", "Open a GIF first.")
            return
        if not self.crop_box:
            messagebox.showinfo("Info", "Make a selection first by dragging on the preview.")
            return

        out_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
        if not out_path:
            return

        try:
            # Crop frames in original mode to avoid additional quantization steps where possible
            cropped_frames = [f.crop(self.crop_box) for f in self.original_frames]

            # If frames are palette-based ('P') try to preserve that palette by saving directly.
            # Pillow will handle converting modes if needed.
            first = cropped_frames[0]
            append = cropped_frames[1:]

            save_kwargs = {
                "save_all": True,
                "append_images": append,
                "loop": self.loop if self.loop is not None else 0,
                "duration": self.frame_durations,
                "disposal": 2,
            }

            # Ensure the first frame has the same mode as original first frame when possible
            try:
                first.save(out_path, format="GIF", **save_kwargs)
            except Exception:
                # fallback: convert to RGBA then save (may re-quantize)
                rgba_frames = [f.convert("RGBA") for f in cropped_frames]
                first = rgba_frames[0]
                append = rgba_frames[1:]
                first.save(out_path, format="GIF", save_all=True, append_images=append,
                           loop=self.loop or 0, duration=self.frame_durations)

            messagebox.showinfo("Saved", f"Cropped GIF saved to {out_path}")
            self.status.config(text=f"Saved cropped GIF: {out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save cropped GIF: {e}")


def main() -> None:
    app = GifCropperGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
