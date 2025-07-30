"""
quick_parse.py

Reads text from the clipboard, applies the same rescind/escape parsing logic
as escapade_parse.py (without any GUI), and writes the result back to the clipboard.
"""
import json
import os
import re
import string
import sys

import pyperclip

SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
        rescind_char = settings.get("rescind_char", ";")
        sentence_restart = settings.get("sentence_restart", "<.")
        paragraph_restart = settings.get(
            "paragraph_restart", rescind_char * 2 + "."
        )
    else:
        rescind_char = ";"
        sentence_restart = "<."
        paragraph_restart = rescind_char * 2 + "."
    return rescind_char, sentence_restart, paragraph_restart


def check_caps_sequence(text):
    words = text.split()
    count = 0
    for word in words:
        stripped = word.strip(string.punctuation)
        if (
            stripped
            and any(c.isalpha() for c in stripped)
            and stripped == stripped.upper()
        ):
            count += 1
            if count >= 10:
                return True
        else:
            count = 0
    return False


def reformat_caps_text(text):
    text = text.lower()
    if text:
        text = text[0].upper() + text[1:]
    text = re.sub(r'(?<=[.!?]\s)(\w)', lambda m: m.group(1).upper(), text)
    return text


def quick_parse(text, rescind_char, sentence_restart, paragraph_restart):
    paragraphs = text.split("\n")
    new_paragraphs = []
    for paragraph in paragraphs:
        words = paragraph.split()
        new_words = []
        skip_count = 0
        for word in words:
            if skip_count:
                skip_count -= 1
                continue
            if word.startswith(paragraph_restart):
                new_words = []
                continue
            if word.startswith(sentence_restart):
                while new_words and new_words[-1] not in [".", "!", "?"]:
                    new_words.pop()
                continue
            if word.startswith(rescind_char * 3):
                continue
            if word.startswith(rescind_char * 2):
                if len(new_words) >= 2:
                    new_words.pop()
                    new_words.pop()
                elif new_words:
                    new_words.pop()
                continue
            if word.startswith(rescind_char):
                if new_words:
                    new_words.pop()
                continue
            if rescind_char in word:
                last_part = word.rsplit(rescind_char, 1)[-1]
                if last_part:
                    new_words.append(last_part)
                continue
            new_words.append(word)
        new_paragraphs.append(" ".join(new_words))
    result = "\n".join(new_paragraphs)
    if check_caps_sequence(result):
        result = reformat_caps_text(result)
    return result


def main():
    rescind_char, sentence_restart, paragraph_restart = load_settings()
    text = pyperclip.paste()
    if not text:
        sys.exit("No text found in clipboard.")
    parsed = quick_parse(text, rescind_char, sentence_restart, paragraph_restart)
    pyperclip.copy(parsed)


if __name__ == "__main__":
    main()