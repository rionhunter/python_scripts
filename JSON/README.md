# JSON Key Exporter (GUI)

A small Tkinter GUI to open a JSON file, pick a top-level key, preview its value, and export that value to a file.

Usage

1. Run the GUI:

   python JSON/json_key_exporter_gui.py

2. Click "Open JSON..." and choose a JSON file.
3. Select a key from the left list to preview it.
4. Click "Export Selected Key..." to save the value to a file.

Notes

- If the top-level JSON is an array, you will be prompted to select an index and then keys will be taken from that item if it's an object. If it's not an object the item will be exported as the special key `_item`.
- Exports use `.json` by default for objects/arrays, otherwise plain text is written.
