"""
Dynamic dictionary-based replacer GUI

Features:
- Dynamic add/remove key -> value rows in a Tkinter GUI
- Open a text file, preview replacements, and overwrite (with optional .bak backup)
- Save/load named profiles (JSON stored in user's config file)
- CLI --test mode demonstrates replacement logic

Profiles are stored at: %APPDATA%\tcl_replacer_profiles.json on Windows or
~/.tcl_replacer_profiles.json on other OSes.

"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import List, Tuple

try:
    # When run as a module inside the package
    from .dynamic_replacer_core import (
        apply_replacements,
        apply_replacements_with_counts,
        find_matches,
        ProfilesStore,
        SettingsStore,
    )
except ImportError:
    # When run directly as a script
    from dynamic_replacer_core import (
        apply_replacements,
        apply_replacements_with_counts,
        find_matches,
        ProfilesStore,
        SettingsStore,
    )


class DynamicReplacerApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title('Dynamic Replacer')

        self.profiles_store = ProfilesStore()
        self.settings = SettingsStore()

        # mapping_rows stores tuples: (key_entry, value_entry, ci_var, ww_var)
        self.mapping_rows: List[Tuple[tk.Entry, tk.Entry, tk.BooleanVar, tk.BooleanVar]] = []

        self.filepath_var = tk.StringVar()
        self.backup_var = tk.BooleanVar(value=True)

        top = tk.Frame(master, padx=8, pady=8)
        top.pack(fill='both', expand=True)

        file_frame = tk.Frame(top)
        file_frame.pack(fill='x')
        tk.Label(file_frame, text='File:').pack(side='left')
        tk.Entry(file_frame, textvariable=self.filepath_var, width=60).pack(side='left', padx=6)
        tk.Button(file_frame, text='Browse', command=self.browse_file).pack(side='left')
        tk.Button(file_frame, text='Add Files...', command=self.add_files).pack(side='left', padx=4)
        tk.Button(file_frame, text='Clear Files', command=self.clear_files).pack(side='left')

        controls = tk.Frame(top, pady=8)
        controls.pack(fill='x')
        tk.Button(controls, text='Add Row', command=self.add_row).pack(side='left')
        tk.Button(controls, text='Remove Last', command=self.remove_last).pack(side='left', padx=4)
        tk.Button(controls, text='Preview', command=self.preview).pack(side='left', padx=8)
        tk.Button(controls, text='Apply', command=self.apply).pack(side='left')
        tk.Button(controls, text='Restore .bak', command=self.restore_backup).pack(side='left', padx=6)
        tk.Checkbutton(controls, text='Create .bak', variable=self.backup_var).pack(side='right')

        profile_frame = tk.Frame(top)
        profile_frame.pack(fill='x', pady=6)
        tk.Label(profile_frame, text='Profiles:').pack(side='left')
        self.profile_var = tk.StringVar(value='')
        self.profile_menu = tk.OptionMenu(profile_frame, self.profile_var, *([''] + self.profiles_store.names()))
        self.profile_menu.pack(side='left')
        tk.Button(profile_frame, text='Save Profile', command=self.save_profile).pack(side='left', padx=4)
        tk.Button(profile_frame, text='Load Profile', command=self.load_profile).pack(side='left')
        tk.Button(profile_frame, text='Rename', command=self.rename_profile).pack(side='left', padx=4)
        tk.Button(profile_frame, text='Delete', command=self.delete_profile).pack(side='left')
        tk.Button(profile_frame, text='Import', command=self.import_profile).pack(side='left', padx=4)
        tk.Button(profile_frame, text='Export', command=self.export_profile).pack(side='left')

        # Scrollable area for rows
        canvas = tk.Canvas(top, height=260)
        canvas.pack(fill='both', expand=True)
        scrollbar = tk.Scrollbar(top, command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)
        self.rows_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.rows_frame, anchor='nw')
        self.rows_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # Files list (bulk)
        files_frame = tk.Frame(top)
        files_frame.pack(fill='both', expand=False, pady=8)
        tk.Label(files_frame, text='Files to process (optional):').pack(anchor='w')
        self.files_list = tk.Listbox(files_frame, height=5, selectmode='extended')
        self.files_list.pack(fill='x')

        # start with two rows
        self.add_row(key='Speaker1:', value='')
        self.add_row(key='Speaker2:', value='')

        # Restore window geometry
        geom = self.settings.get('geometry')
        if geom:
            try:
                master.geometry(geom)
            except Exception:
                pass
        master.protocol('WM_DELETE_WINDOW', self.on_close)

    def browse_file(self):
        p = filedialog.askopenfilename(title='Select file', filetypes=[('Text files', '*.txt'), ('All', '*.*')])
        if p:
            self.filepath_var.set(p)

    def add_files(self):
        paths = filedialog.askopenfilenames(title='Select files', filetypes=[('Text files', '*.txt'), ('All', '*.*')])
        for p in paths:
            self.files_list.insert('end', p)

    def clear_files(self):
        self.files_list.delete(0, 'end')

    def add_row(self, key: str = '', value: str = '', ci: bool = False, ww: bool = False):
        row = tk.Frame(self.rows_frame, pady=2)
        row.pack(fill='x')
        e1 = tk.Entry(row, width=30)
        e1.insert(0, key)
        e1.pack(side='left')
        tk.Label(row, text='→').pack(side='left', padx=6)
        e2 = tk.Entry(row, width=50)
        e2.insert(0, value)
        e2.pack(side='left', fill='x', expand=True)
        ci_var = tk.BooleanVar(value=ci)
        ww_var = tk.BooleanVar(value=ww)
        tk.Checkbutton(row, text='CI', variable=ci_var).pack(side='left', padx=4)
        tk.Checkbutton(row, text='Whole', variable=ww_var).pack(side='left')
        # Bind drag events for reordering
        def bind_drag(widget):
            widget.bind('<ButtonPress-1>', lambda ev, r=row: self._on_press(ev, r))
            widget.bind('<B1-Motion>', lambda ev, r=row: self._on_motion(ev, r))
            widget.bind('<ButtonRelease-1>', lambda ev, r=row: self._on_release(ev, r))

        bind_drag(row)
        bind_drag(e1)
        bind_drag(e2)

        self.mapping_rows.append((e1, e2, ci_var, ww_var))

    def _row_frames(self):
        return [k_ent.master for (k_ent, _, _, _) in self.mapping_rows]

    def _find_row_index(self, frame):
        frames = self._row_frames()
        try:
            return frames.index(frame)
        except ValueError:
            return -1

    def _on_press(self, event, frame):
        # Start dragging
        idx = self._find_row_index(frame)
        if idx < 0:
            return
        self._drag_data = {'frame': frame, 'index': idx}
        frame.lift()
        frame.config(relief='raised', bd=2)

    def _on_motion(self, event, frame):
        if not hasattr(self, '_drag_data'):
            return
        y = event.y_root - self.rows_frame.winfo_rooty()
        frames = self._row_frames()
        target = None
        for i, fr in enumerate(frames):
            if fr is self._drag_data['frame']:
                continue
            # compute center y of fr
            top = fr.winfo_rooty() - self.rows_frame.winfo_rooty()
            h = fr.winfo_height()
            center = top + h / 2
            if y < center:
                target = i
                break
        if target is None:
            target = len(frames) - 1

        src_idx = self._drag_data['index']
        # convert target to index within mapping_rows after removing src
        if target != src_idx:
            item = self.mapping_rows.pop(src_idx)
            # if moving downwards, and target > src_idx, insert after removing shifts index
            if target > src_idx:
                target = target
            self.mapping_rows.insert(target, item)
            self._drag_data['index'] = target
            self.repack_rows()

    def _on_release(self, event, frame):
        if not hasattr(self, '_drag_data'):
            return
        fr = self._drag_data['frame']
        fr.config(relief='flat', bd=0)
        del self._drag_data

    def repack_rows(self):
        # Re-pack frames in the order of self.mapping_rows
        for (k_ent, _, _, _) in self.mapping_rows:
            fr = k_ent.master
            fr.pack_forget()
        for (k_ent, _, _, _) in self.mapping_rows:
            fr = k_ent.master
            fr.pack(fill='x')

    def remove_last(self):
        if not self.mapping_rows:
            return
        e1, e2, ci, ww = self.mapping_rows.pop()
        parent = e1.master
        parent.destroy()

    def collect_mapping(self) -> List[Tuple[str, str, bool, bool]]:
        out: List[Tuple[str, str, bool, bool]] = []
        for k_ent, v_ent, ci_var, ww_var in self.mapping_rows:
            k = k_ent.get()
            v = v_ent.get()
            ci = bool(ci_var.get())
            ww = bool(ww_var.get())
            if k:
                out.append((k, v, ci, ww))
        return out

    def preview(self):
        path = self.filepath_var.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning('No file', 'Please select a valid file first.')
            return
        with open(path, 'r', encoding='utf-8') as f:
            src = f.read()
        items = self.collect_mapping()
        result = apply_replacements(src, items)
        # Show in a dialog with highlights using core find_matches
        PreviewDialog(self.master, src, result, items)

    def apply(self):
        path = self.filepath_var.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning('No file', 'Please select a valid file first.')
            return
        items = self.collect_mapping()
        if not items:
            messagebox.showwarning('No mappings', 'Please add at least one key to replace.')
            return
        # Bulk: if files list has entries, apply to all; else apply to single path
        targets: List[str] = list(self.files_list.get(0, 'end'))
        if not targets:
            if not path:
                messagebox.showwarning('No file', 'Please select a valid file first or add files to the list.')
                return
            targets = [path]
        total_files = 0
        total_replacements = 0
        per_file_counts = []
        try:
            for t in targets:
                if not os.path.isfile(t):
                    continue
                with open(t, 'r', encoding='utf-8') as f:
                    src = f.read()
                result, per_key, count = apply_replacements_with_counts(src, items)
                if self.backup_var.get():
                    shutil.copy2(t, t + '.bak')
                with open(t, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(result)
                total_files += 1
                total_replacements += count
                per_file_counts.append((t, count))
            if total_files == 0:
                messagebox.showwarning('No files written', 'No valid files to process.')
                return
            msg = f'Processed {total_files} file(s). Total replacements: {total_replacements}.'
            if len(per_file_counts) <= 5:
                detail = '\n'.join(f'- {fp}: {c}' for fp, c in per_file_counts)
                msg += f"\n\n{detail}"
            messagebox.showinfo('Saved', msg)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def restore_backup(self):
        path = self.filepath_var.get().strip()
        bak = path + '.bak'
        if not path or not os.path.isfile(bak):
            messagebox.showwarning('No backup', 'No .bak file found for the selected file')
            return
        if messagebox.askyesno('Restore', f'Restore {bak} over {path}?'):
            try:
                shutil.copy2(bak, path)
                messagebox.showinfo('Restored', f'Restored {path} from {bak}')
            except Exception as e:
                messagebox.showerror('Error', str(e))

    def save_profile(self):
        name = simpledialog.askstring('Profile name', 'Enter profile name:')
        if not name:
            return
        items = self.collect_mapping()
        mapping = {k: {'value': v, 'ci': ci, 'ww': ww} for k, v, ci, ww in items}
        self.profiles_store.set(name, mapping)
        self.refresh_profiles()
        messagebox.showinfo('Saved', f'Profile "{name}" saved')

    def load_profile(self):
        name = self.profile_var.get()
        if not name or name not in self.profiles_store.names():
            messagebox.showwarning('No profile', 'Select a profile first')
            return
        mapping = self.profiles_store.get(name)
        # clear existing rows
        while self.mapping_rows:
            self.remove_last()
        for k, info in mapping.items():
            if isinstance(info, dict):
                v = info.get('value', '')
                ci = bool(info.get('ci', False))
                ww = bool(info.get('ww', False))
            else:
                v = info
                ci = False
                ww = False
            self.add_row(key=k, value=v, ci=ci, ww=ww)

    def delete_profile(self):
        name = self.profile_var.get()
        if not name or name not in self.profiles_store.names():
            messagebox.showwarning('No profile', 'Select a profile first')
            return
        if messagebox.askyesno('Delete', f'Delete profile "{name}"?'):
            self.profiles_store.delete(name)
            self.refresh_profiles()

    def rename_profile(self):
        old = self.profile_var.get()
        if not old or old not in self.profiles_store.names():
            messagebox.showwarning('No profile', 'Select a profile first')
            return
        new = simpledialog.askstring('Rename profile', 'Enter new name:', initialvalue=old)
        if not new or new == old:
            return
        self.profiles_store.rename(old, new)
        self.profile_var.set(new)
        self.refresh_profiles()

    def import_profile(self):
        p = filedialog.askopenfilename(title='Import profile JSON', filetypes=[('JSON', '*.json'), ('All', '*.*')])
        if not p:
            return
        try:
            self.profiles_store.merge_from_file(p)
            self.refresh_profiles()
            messagebox.showinfo('Imported', f'Profiles imported from {p}')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def export_profile(self):
        name = self.profile_var.get()
        if not name or name not in self.profiles_store.names():
            messagebox.showwarning('No profile', 'Select a profile first')
            return
        p = filedialog.asksaveasfilename(title='Export profile as JSON', defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not p:
            return
        try:
            self.profiles_store.export_to_file(name, p)
            messagebox.showinfo('Exported', f'Profile exported to {p}')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def refresh_profiles(self):
        menu = self.profile_menu['menu']
        menu.delete(0, 'end')
        menu.add_command(label='', command=tk._setit(self.profile_var, ''))
        for k in self.profiles_store.names():
            menu.add_command(label=k, command=tk._setit(self.profile_var, k))

    def on_close(self):
        try:
            geom = self.master.winfo_geometry()
            self.settings.set('geometry', geom)
        finally:
            self.master.destroy()



class PreviewDialog(tk.Toplevel):
    def __init__(self, master: tk.Tk, original: str, replaced: str, mapping: List[Tuple[str, str, bool, bool]]):
        super().__init__(master)
        self.title('Preview Replacements')
        self.geometry('1000x700')
        left = tk.Text(self, wrap='word')
        left.insert('1.0', original)
        left.config(state='disabled')
        left.pack(side='left', fill='both', expand=True)
        right = tk.Text(self, wrap='word')
        right.insert('1.0', replaced)
        right.config(state='disabled')
        right.pack(side='left', fill='both', expand=True)

        # Simple highlighting on the right pane for each key (if non-empty)
        for i, (k, v, ci, ww) in enumerate(mapping):
            if not k:
                continue
            tag = f'tag{i}'
            right.tag_config(tag, background=['#ffff99', '#ffdd99', '#ddff99', '#99ffdd'][i % 4])
            # Find matches
            flags = re.IGNORECASE if ci else 0
            pat = (r"\b" + re.escape(k) + r"\b") if ww else re.escape(k)
            for m in re.finditer(pat, replaced, flags=flags):
                start = f"1.0+{m.start()}c"
                end = f"1.0+{m.end()}c"
                right.tag_add(tag, start, end)


def _test():
    src = 'Speaker1:\nHello Speaker1:\nThis is a test.\n'
    items = [
        ('Speaker1:', '', False, False),
        ('test', 'demo', False, False),
    ]
    print('Before:\n', src)
    print('After:\n', apply_replacements(src, items))


def main(argv=None):
    if argv and '--test' in argv:
        _test()
        return 0
    root = tk.Tk()
    app = DynamicReplacerApp(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
