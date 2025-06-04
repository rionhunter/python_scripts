import keyboard
import pyperclip
import time
import threading

# Configurable characters
RESCIND_KEY = ';'
RESET_SEQUENCE = '/.'

# State tracking
typed_chars = []
current_sentence = []
rescind_count = 0

# Helpers
def delete_word():
    keyboard.press_and_release('ctrl+backspace')

def delete_n_words(n):
    for _ in range(n):
        delete_word()
        time.sleep(0.01)  # Slight delay to allow proper deletion

def reset_sentence():
    while current_sentence:
        delete_word()
        current_sentence.pop()
        time.sleep(0.01)

def handle_key(event):
    global typed_chars, current_sentence, rescind_count
    name = event.name

    if len(name) == 1 and name.isprintable():
        typed_chars.append(name)
        current_sentence.append(name)

    elif name == 'space':
        typed_chars.append(' ')
        current_sentence.append(' ')
        rescind_count = 0  # Reset rescind tracking after word

    elif name == RESCIND_KEY:
        rescind_count += 1
        typed_chars.append(RESCIND_KEY)

    elif name == 'backspace':
        if typed_chars:
            typed_chars.pop()
        if current_sentence:
            current_sentence.pop()

    elif name == 'enter':
        typed_chars.clear()
        current_sentence.clear()
        rescind_count = 0

    # Rescind logic (triggered only if no space after rescind)
    if rescind_count > 0:
        if len(typed_chars) >= rescind_count and all(c == RESCIND_KEY for c in typed_chars[-rescind_count:]):
            delete_n_words(rescind_count)
            rescind_count = 0
            typed_chars = typed_chars[:-rescind_count]
            current_sentence = current_sentence[:-rescind_count]

    # Check for reset sequence
    if len(current_sentence) >= len(RESET_SEQUENCE):
        if ''.join(current_sentence[-len(RESET_SEQUENCE):]) == RESET_SEQUENCE:
            reset_sentence()
            current_sentence.clear()
            rescind_count = 0
            typed_chars.clear()

# Start background listener
def start_listener():
    keyboard.on_press(handle_key)
    print("[Rescind listener active] Press ESC to exit.")
    keyboard.wait('esc')

threading.Thread(target=start_listener, daemon=True).start()

# Keep script alive
while True:
    time.sleep(1)
