"""
Core logic for dynamic replacer GUI.

Provides:
- apply_replacements(items) and apply_replacements_with_counts
- find_matches for highlighting
- ProfilesStore and SettingsStore for persistence
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# Storage locations
PROFILE_FILENAME = os.path.join(
    os.getenv('APPDATA') or os.path.expanduser('~'), 'tcl_replacer_profiles.json'
)
SETTINGS_FILENAME = os.path.join(
    os.getenv('APPDATA') or os.path.expanduser('~'), 'tcl_replacer_settings.json'
)


def apply_replacements(text: str, items: List[Tuple[str, str, bool, bool]]) -> str:
    return apply_replacements_with_counts(text, items)[0]


def apply_replacements_with_counts(text: str, items: List[Tuple[str, str, bool, bool]]) -> Tuple[str, Dict[str, int], int]:
    """Apply replacements sequentially and return (result, per_key_count, total_count)."""
    out = text
    per_key: Dict[str, int] = {}
    total = 0
    for key, val, ci, ww in items:
        if not key:
            continue
        pat = r"\b" + re.escape(key) + r"\b" if ww else re.escape(key)
        flags = re.IGNORECASE if ci else 0
        out, count = re.subn(pat, val, out, flags=flags)
        per_key[key] = per_key.get(key, 0) + count
        total += count
    return out, per_key, total


def find_matches(text: str, items: List[Tuple[str, str, bool, bool]]) -> List[Tuple[int, int, int]]:
    """Return a list of (start, end, item_index) for matches in text."""
    spans: List[Tuple[int, int, int]] = []
    for i, (key, _val, ci, ww) in enumerate(items):
        if not key:
            continue
        pat = r"\b" + re.escape(key) + r"\b" if ww else re.escape(key)
        flags = re.IGNORECASE if ci else 0
        for m in re.finditer(pat, text, flags=flags):
            spans.append((m.start(), m.end(), i))
    return spans


class ProfilesStore:
    def __init__(self, path: Optional[str] = None):
        self.path = path or PROFILE_FILENAME
        self._profiles: Dict[str, Dict[str, Dict[str, object]]] = {}
        self.load()

    def load(self) -> None:
        if not os.path.isfile(self.path):
            self._profiles = {}
            return
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self._profiles = json.load(f)
        except Exception:
            self._profiles = {}

    def save(self) -> None:
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self._profiles, f, indent=2, ensure_ascii=False)

    def names(self) -> List[str]:
        return list(self._profiles.keys())

    def get(self, name: str) -> Dict[str, Dict[str, object]]:
        return self._profiles.get(name, {})

    def set(self, name: str, mapping: Dict[str, Dict[str, object]]) -> None:
        self._profiles[name] = mapping
        self.save()

    def delete(self, name: str) -> None:
        if name in self._profiles:
            del self._profiles[name]
            self.save()

    def rename(self, old: str, new: str) -> None:
        if old in self._profiles and new:
            self._profiles[new] = self._profiles.pop(old)
            self.save()

    def merge_from_file(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._profiles.update(data)
        self.save()

    def export_to_file(self, name: str, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({name: self._profiles.get(name, {})}, f, indent=2, ensure_ascii=False)


class SettingsStore:
    def __init__(self, path: Optional[str] = None):
        self.path = path or SETTINGS_FILENAME
        self.data: Dict[str, object] = {}
        self.load()

    def load(self) -> None:
        if not os.path.isfile(self.path):
            self.data = {}
            return
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception:
            self.data = {}

    def save(self) -> None:
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value) -> None:
        self.data[key] = value
        self.save()
