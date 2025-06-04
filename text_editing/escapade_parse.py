import tkinter as tk
from tkinter import simpledialog, filedialog, scrolledtext
import pyperclip
import json
import os
import re
import string

SETTINGS_FILE = "settings.json"

class RescindTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Rescind Text Editor")
        
        self.load_settings()
        
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(fill='x', padx=10, pady=5)
        
        self.process_button = tk.Button(self.control_frame, text="Process Text", command=self.process_text)
        self.process_button.pack(side='left', padx=5)
        
        self.save_button = tk.Button(self.control_frame, text="Save", command=self.save_text)
        self.save_button.pack(side='left', padx=5)
        
        self.copy_button = tk.Button(self.control_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side='left', padx=5)
        
        self.express_button = tk.Button(self.control_frame, text="Express Edit", command=self.express_edit)
        self.express_button.pack(side='left', padx=5)
        
        self.set_rescind_button = tk.Button(self.control_frame, text="Set Rescind Character", command=self.set_rescind_char)
        self.set_rescind_button.pack(side='left', padx=5)
        
        self.set_sentence_restart_button = tk.Button(self.control_frame, text="Set Sentence Restart", command=self.set_sentence_restart)
        self.set_sentence_restart_button.pack(side='left', padx=5)
        
        self.set_paragraph_restart_button = tk.Button(self.control_frame, text="Set Paragraph Restart", command=self.set_paragraph_restart)
        self.set_paragraph_restart_button.pack(side='left', padx=5)
        
        self.resolved_text = ""
    
    def express_edit(self):
        text = pyperclip.paste()
        self.text_area.insert("1.0", text)
        self.process_text()
        pyperclip.copy(self.resolved_text)
        self.root.quit()
    
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                settings = json.load(file)
                self.rescind_char = settings.get("rescind_char", ";")
                self.sentence_restart = settings.get("sentence_restart", "<.")
                self.paragraph_restart = settings.get("paragraph_restart", self.rescind_char * 2 + '.')
        else:
            self.rescind_char = ';'
            self.sentence_restart = '<.'
            self.paragraph_restart = self.rescind_char * 2 + '.'
    
    def save_settings(self):
        settings = {
            "rescind_char": self.rescind_char,
            "sentence_restart": self.sentence_restart,
            "paragraph_restart": self.paragraph_restart
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file)
    
    def set_rescind_char(self):
        char = simpledialog.askstring("Rescind Character", "Enter rescind character:", initialvalue=self.rescind_char)
        if char:
            self.rescind_char = char
            self.paragraph_restart = self.rescind_char * 2 + '.'
            self.save_settings()
    
    def set_sentence_restart(self):
        char = simpledialog.askstring("Sentence Restart", "Enter sentence restart sequence:", initialvalue=self.sentence_restart)
        if char:
            self.sentence_restart = char
            self.save_settings()
    
    def set_paragraph_restart(self):
        char = simpledialog.askstring("Paragraph Restart", "Enter paragraph restart sequence:", initialvalue=self.paragraph_restart)
        if char:
            self.paragraph_restart = char
            self.save_settings()
    
    def check_caps_sequence(self, text):
        """Check for 10 or more consecutive ALL CAPS words (to fix accidental capslock abuse)."""
        words = text.split()
        count = 0
        for word in words:
            stripped = word.strip(string.punctuation)
            if stripped and any(c.isalpha() for c in stripped) and stripped == stripped.upper():
                count += 1
                if count >= 10:
                    return True
            else:
                count = 0
        return False
    
    def reformat_caps_text(self, text):
        """Convert the whole text to lowercase, then capitalize the first letter of each sentence."""
        text = text.lower()
        if text:
            text = text[0].upper() + text[1:]
        # Capitalize letter following a period, exclamation mark, or question mark plus whitespace.
        text = re.sub(r'(?<=[.!?]\s)(\w)', lambda m: m.group(1).upper(), text)
        return text
    
    def process_text(self):
        text = self.text_area.get("1.0", tk.END).strip()
        paragraphs = text.split('\n')
        new_paragraphs = []
        
        for paragraph in paragraphs:
            words = paragraph.split()
            new_words = []
            skip_count = 0
            
            for i, word in enumerate(words):
                if skip_count:
                    skip_count -= 1
                    continue
                
                if word.startswith(self.paragraph_restart):
                    new_words = []  # Restart paragraph
                    continue
                
                if word.startswith(self.sentence_restart):
                    while new_words and new_words[-1] not in ['.', '!', '?']:
                        new_words.pop()
                    continue
                
                if word.startswith(self.rescind_char * 3):
                    continue  # Ignore triple rescind characters
                
                if word.startswith(self.rescind_char * 2):
                    if len(new_words) >= 2:
                        new_words.pop()
                        new_words.pop()
                    elif new_words:
                        new_words.pop()
                    continue
                
                if word.startswith(self.rescind_char):
                    if new_words:
                        new_words.pop()
                    continue
                
                if self.rescind_char in word:
                    last_part = word.rsplit(self.rescind_char, 1)[-1]
                    if last_part:
                        new_words.append(last_part)
                    continue
                
                new_words.append(word)
            
            new_paragraphs.append(' '.join(new_words))
        
        self.resolved_text = '\n'.join(new_paragraphs)
        
        # New feature: If there are 10+ consecutive ALL CAPS words, fix your accidental capslock.
        if self.check_caps_sequence(self.resolved_text):
            self.resolved_text = self.reformat_caps_text(self.resolved_text)
        
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", self.resolved_text)
    
    def save_text(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.resolved_text)
    
    def copy_to_clipboard(self):
        pyperclip.copy(self.resolved_text)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = RescindTextEditor(root)
    root.mainloop()
