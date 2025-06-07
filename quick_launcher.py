import json
import subprocess
import sys
from pathlib import Path
import tkinter as tk

TAG_FILE = Path('script_tags.json')

if not TAG_FILE.exists():
    print('Tag file not found. Run generate_tags.py first.')
    sys.exit(1)

data = json.loads(TAG_FILE.read_text())
root_path = Path(__file__).parent


def run_script(rel_path):
    path = root_path / rel_path
    if rel_path.endswith('.py'):
        subprocess.Popen([sys.executable, str(path)])
    elif rel_path.endswith('.sh'):
        subprocess.Popen(['bash', str(path)])
    else:
        subprocess.Popen([str(path)])
    info = data.get(rel_path, {})
    info['usage'] = info.get('usage', 0) + 1
    data[rel_path] = info
    TAG_FILE.write_text(json.dumps(data, indent=2))
    root.quit()


def search(query):
    query = query.lower()
    matches = []
    for path, info in data.items():
        text = path.lower() + ' ' + ' '.join(info.get('tags', []))
        if query in text:
            matches.append((path, info))
    matches.sort(key=lambda x: (-x[1].get('usage', 0), x[0]))
    return matches


def update_list(*_):
    query = entry.get()
    listbox.delete(0, tk.END)
    for path, info in search(query):
        deps = ' '.join(f'[{d}]' for d in info.get('deps', []))
        listbox.insert(tk.END, f"{Path(path).name} {deps}")


def on_select(event):
    selection = listbox.curselection()
    if selection:
        idx = selection[0]
        path = search(entry.get())[idx][0]
        run_script(path)


root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.bind('<Escape>', lambda e: root.destroy())

entry = tk.Entry(root)
entry.pack(fill='x')
entry.bind('<KeyRelease>', update_list)

listbox = tk.Listbox(root, activestyle='none')
listbox.pack(fill='both', expand=True)
listbox.bind('<Return>', on_select)
listbox.bind('<Double-Button-1>', on_select)

root.update_idletasks()
width, height = 500, 300
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.geometry(f"{width}x{height}+{int((screen_w-width)/2)}+{int((screen_h-height)/2)}")

update_list()
entry.focus_set()
root.mainloop()
