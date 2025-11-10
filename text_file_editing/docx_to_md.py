"""Convert .docx files to Markdown and save alongside the original.

When run as a script, opens a GUI file selector to pick a .docx file and
saves the converted markdown to the same directory with the same base name
and a .md extension.

This implementation uses python-docx to read paragraph text and basic
handling for headings and lists. It intentionally keeps dependencies minimal
and focuses on a usable default conversion for simple documents.
"""

from __future__ import annotations

import os
import sys
from typing import List

try:
    from docx import Document
except Exception:
    Document = None  # lazily handle when running tests or environment missing


def docx_paragraphs_to_markdown(doc: Document) -> str:
    """Convert a python-docx Document to a markdown string.

    This is a best-effort conversion: paragraphs, runs, headings, and simple
    lists are handled. Complex elements (tables, images, footnotes) are not
    converted.
    """
    lines: List[str] = []

    for p in doc.paragraphs:
        style = p.style.name.lower() if p.style is not None else ''

        text = p.text.strip()
        if not text:
            # preserve paragraph breaks
            lines.append('')
            continue

        # Headings (common Word styles start with 'heading')
        if 'heading' in style:
            # try to extract the level number from style name
            level = 1
            for part in style.split():
                if part.isdigit():
                    try:
                        level = int(part)
                    except Exception:
                        pass
            lines.append('#' * level + ' ' + text)
            continue

        # Simple bullet list detection: if style contains 'list' or bullet char
        if 'list' in style or p.text.lstrip().startswith(('•', '-', '*')):
            # normalize leading bullet
            stripped = text.lstrip('•- *')
            lines.append(f'- {stripped}')
            continue

        # Fallback: plain paragraph
        lines.append(text)

    # Join lines with double newlines for paragraph separation
    md = '\n\n'.join(lines)
    return md


def convert_docx_to_md(input_path: str, output_path: str | None = None) -> str:
    """Read a .docx file and write markdown to output_path.

    Returns the markdown string. If output_path is None, returns the markdown
    without writing to disk.
    """
    if Document is None:
        raise RuntimeError("python-docx is required. Install with: pip install python-docx")

    if not input_path.lower().endswith('.docx'):
        raise ValueError('Input file must have a .docx extension')

    doc = Document(input_path)
    md = docx_paragraphs_to_markdown(doc)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)

    return md


def choose_file_via_tk(initialdir: str | None = None) -> str | None:
    """Open a simple GUI file picker for .docx files and return selected path.

    Uses tkinter.filedialog so this function is safe to import on systems with
    a display. On headless systems it will raise.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as e:
        raise RuntimeError('tkinter is required for the GUI file picker') from e

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title='Select a .docx file to convert',
        filetypes=[('Word Documents', '*.docx')],
        initialdir=initialdir or os.path.expanduser('~')
    )
    root.destroy()
    return file_path or None


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. If run without args, opens the GUI file selector.

    Usage:
        python -m text_file_editing.docx_to_md [input.docx] [output.md]
    """
    argv = argv if argv is not None else sys.argv[1:]

    if len(argv) == 0:
        # Launch GUI to choose file
        try:
            input_path = choose_file_via_tk()
        except Exception as e:
            print(f'GUI file picker failed: {e}', file=sys.stderr)
            return 2
        if not input_path:
            print('No file selected.')
            return 0
    else:
        input_path = argv[0]

    if not os.path.isfile(input_path):
        print(f'Input file not found: {input_path}', file=sys.stderr)
        return 2

    base, _ = os.path.splitext(input_path)
    output_path = argv[1] if len(argv) > 1 else f'{base}.md'

    try:
        md = convert_docx_to_md(input_path, output_path)
        print(f'Converted: {input_path} -> {output_path}')
        return 0
    except Exception as e:
        print(f'Error converting file: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
