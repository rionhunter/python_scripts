import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog


class JSONKeyExporter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('JSON Key Exporter')
        self.geometry('700x450')

        # Widgets
        self.open_btn = tk.Button(self, text='Open JSON...', command=self.open_json)
        self.open_btn.pack(padx=8, pady=8, anchor='nw')

        self.keys_listbox = tk.Listbox(self, width=40, height=20)
        self.keys_listbox.pack(side='left', padx=8, pady=8, fill='y')
        self.keys_listbox.bind('<<ListboxSelect>>', self.on_select)

        right_frame = tk.Frame(self)
        right_frame.pack(side='right', expand=True, fill='both', padx=8, pady=8)

        self.preview_text = tk.Text(right_frame, wrap='word')
        self.preview_text.pack(expand=True, fill='both')

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side='bottom', fill='x', padx=8, pady=8)

        self.export_btn = tk.Button(bottom_frame, text='Export Selected Key...', command=self.export_selected)
        self.export_btn.pack(side='right')

        self.status_var = tk.StringVar(value='No file loaded')
        status_label = tk.Label(bottom_frame, textvariable=self.status_var)
        status_label.pack(side='left')

        self.data = None
        self.json_path = None

    def open_json(self):
        path = filedialog.askopenfilename(title='Open JSON file', filetypes=[('JSON files', '*.json'), ('All files', '*.*')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to open JSON:\n{e}')
            return

        if not isinstance(self.data, dict):
            if isinstance(self.data, list):
                # offer to wrap or choose index
                if messagebox.askyesno('JSON root is array', 'Top-level JSON is a list/array. Do you want to select an index from it as the "key"?'):
                    self.pick_index_from_array(self.data)
                    self.json_path = path
                    self.status_var.set(f'Loaded: {os.path.basename(path)}')
                    return
            messagebox.showerror('Unsupported JSON', 'Top-level JSON is not an object/dictionary. This tool expects a JSON object at the root.')
            return

        self.json_path = path
        self.populate_keys()
        self.status_var.set(f'Loaded: {os.path.basename(path)}')

    def pick_index_from_array(self, arr):
        # show a simple dialog to pick index
        idx = simpledialog.askinteger('Pick index', f'Enter index (0 - {len(arr)-1}):', minvalue=0, maxvalue=len(arr)-1)
        if idx is None:
            return
        item = arr[idx]
        if isinstance(item, dict):
            self.data = item
            self.populate_keys()
        else:
            # not an object; set preview and allow export as raw
            self.data = {'_item': item}
            self.populate_keys()

    def populate_keys(self):
        self.keys_listbox.delete(0, tk.END)
        for k in sorted(self.data.keys(), key=str):
            self.keys_listbox.insert(tk.END, k)
        self.preview_text.delete('1.0', tk.END)

    def on_select(self, evt=None):
        sel = self.keys_listbox.curselection()
        if not sel:
            return
        key = self.keys_listbox.get(sel[0])
        value = self.data.get(key)
        try:
            pretty = json.dumps(value, indent=2, ensure_ascii=False)
        except Exception:
            pretty = str(value)
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert(tk.END, pretty)

    def export_selected(self):
        sel = self.keys_listbox.curselection()
        if not sel:
            messagebox.showinfo('No selection', 'Please select a key to export.')
            return
        key = self.keys_listbox.get(sel[0])
        value = self.data.get(key)

        export_path = filedialog.asksaveasfilename(title='Export value to file', defaultextension='.json', filetypes=[('JSON', '*.json'), ('Text', '*.txt'), ('All files', '*.*')])
        if not export_path:
            return
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                if isinstance(value, (dict, list)):
                    json.dump(value, f, indent=2, ensure_ascii=False)
                else:
                    f.write(str(value))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export file:\n{e}')
            return
        messagebox.showinfo('Exported', f'Key "{key}" exported to {export_path}')


if __name__ == '__main__':
    app = JSONKeyExporter()
    app.mainloop()
