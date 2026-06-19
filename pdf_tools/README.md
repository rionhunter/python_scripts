# PDF Tools

Utilities for common PDF actions: merging documents, removing pages, and reordering pages. Built with the `pypdf` library and simple CLI interfaces.

## Installation

Option 1: Install only the dependency

```bash
pip install pypdf
```

Option 2: Install from this folder

```bash
pip install -r pdf_tools/requirements.txt
```

## Commands

- Merge PDFs:
  ```bash
  python pdf_tools/pdf_merge.py input1.pdf input2.pdf -o merged.pdf --overwrite
  ```

- Remove pages (remove listed pages):
  ```bash
  python pdf_tools/pdf_remove_pages.py -i input.pdf -o output.pdf --pages "1,3-5,10-" --overwrite
  ```
  The pages spec uses 1-based indices and supports ranges:
  - Single pages: `1, 7`
  - Ranges: `3-5` (inclusive)
  - Open start: `-5` (from first page through page 5)
  - Open end: `10-` (from page 10 to the last page)
  To keep only the specified pages, add `--keep`.

- Reorder pages:
  ```bash
  python pdf_tools/pdf_reorder_pages.py -i input.pdf -o output.pdf --order "3,1,2,4-7" --overwrite
  ```
  By default, pages not listed are appended at the end in their original order. Use `--no-fill-unlisted` to avoid appending. Use `--strict` to require that all pages are listed exactly once.

## TUI (with file dialogs)

Launch an interactive menu that uses native file selection dialogs (Tk) when available. Add `--no-dialog` to use text prompts instead.

```bash
C:/Python313/python.exe pdf_tools/pdf_tui.py
```

On Windows, you can use the batch launcher:

```bat
pdf_tools\run_pdf_tools.bat
```

Arguments pass through, e.g.:

```bat
pdf_tools\run_pdf_tools.bat --operation merge --overwrite
```

Start directly in an operation:

```bash
C:/Python313/python.exe pdf_tools/pdf_tui.py --operation merge
C:/Python313/python.exe pdf_tools/pdf_tui.py --operation remove
C:/Python313/python.exe pdf_tools/pdf_tui.py --operation reorder
```

## Notes

- Encrypted PDFs may require a password and are not handled in these simple scripts.
- For very large PDFs, operations may take time and memory.
- These scripts are intended for quick CLI usage; integrate the modules into larger apps if needed.
