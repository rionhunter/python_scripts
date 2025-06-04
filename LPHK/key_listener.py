from pynput import keyboard
import tkinter as tk

# To keep track of currently pressed keys
current_keys = set()

# Define the translation function for individual keys
def translate_key_to_lphk(key):
    key_mapping = {
        'Key.esc': 'esc',
        'Key.space': 'space',
        'Key.enter': 'enter',
        'Key.tab': 'tab',
        'Key.shift': 'shift',
        'Key.shift_r': 'shift_r',
        'Key.ctrl_l': 'ctrl',
        'Key.ctrl_r': 'ctrl',
        'Key.alt_l': 'alt',
        'Key.alt_r': 'alt_gr',
        'Key.caps_lock': 'caps_lock',
        'Key.backspace': 'backspace',
        'Key.delete': 'delete',
        'Key.up': 'up',
        'Key.down': 'down',
        'Key.left': 'left',
        'Key.right': 'right',
        'Key.page_up': 'page_up',
        'Key.page_down': 'page_down',
        'Key.home': 'home',
        'Key.end': 'end',
        'Key.insert': 'insert',
        'Key.menu': 'menu',
        'Key.num_lock': 'num_lock',
        'Key.print_screen': 'print_screen',
        'Key.scroll_lock': 'scroll_lock',
        'Key.pause': 'pause',
        'Key.f1': 'f1',
        'Key.f2': 'f2',
        'Key.f3': 'f3',
        'Key.f4': 'f4',
        'Key.f5': 'f5',
        'Key.f6': 'f6',
        'Key.f7': 'f7',
        'Key.f8': 'f8',
        'Key.f9': 'f9',
        'Key.f10': 'f10',
        'Key.f11': 'f11',
        'Key.f12': 'f12',
        'Key.media_volume_up': 'vol_up',
        'Key.media_volume_down': 'vol_down',
        'Key.media_mute': 'mute',
        'Key.media_next': 'next_track',
        'Key.media_previous': 'prev_track',
        'Key.media_play_pause': 'play_pause',
    }

    if hasattr(key, 'char') and key.char is not None:
        return key.char
    else:
        return key_mapping.get(str(key), str(key))

# Initialize the tkinter GUI
root = tk.Tk()
root.title("Macro Script Output")
text_output = tk.Text(root, wrap='word', height=20, width=50)
text_output.pack()

def update_gui_output(command):
    text_output.insert(tk.END, f'{command}\n')
    text_output.see(tk.END)

def on_press(key):
    if key not in current_keys:
        current_keys.add(key)
        translated_key = translate_key_to_lphk(key)
        if translated_key not in ["ctrl", "shift", "alt", "alt_gr"]:
            # First, press all modifiers
            for mod_key in current_keys:
                mod_translated = translate_key_to_lphk(mod_key)
                if mod_translated in ["ctrl", "shift", "alt", "alt_gr"]:
                    update_gui_output(f'PRESS {mod_translated}')
            # Then, tap the non-modifier key
            update_gui_output(f'TAP {translated_key}')

def on_release(key):
    translated_key = translate_key_to_lphk(key)
    if key in current_keys:
        current_keys.remove(key)
        if translated_key in ["ctrl", "shift", "alt", "alt_gr"]:
            update_gui_output(f'RELEASE {translated_key}')
        elif len(current_keys) == 0:
            # Release all modifiers when no more keys are pressed
            for mod_key in current_keys:
                mod_translated = translate_key_to_lphk(mod_key)
                if mod_translated in ["ctrl", "shift", "alt", "alt_gr"]:
                    update_gui_output(f'RELEASE {mod_translated}')
    if key == keyboard.Key.esc:
        return False

def main():
    print("Listening for key presses... Press 'esc' to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        root.mainloop()
        listener.join()

if __name__ == "__main__":
    main()
