import argparse
import os
import sys
from typing import List, Optional

# Import operations from existing modules
try:
    from .pdf_merge import merge_pdfs
    from .pdf_remove_pages import remove_pages
    from .pdf_reorder_pages import reorder_pages
except ImportError:
    # Fallback for running as a script from this folder
    from pdf_merge import merge_pdfs
    from pdf_remove_pages import remove_pages
    from pdf_reorder_pages import reorder_pages


def _safe_import_tkinter():
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
        return tk, filedialog, messagebox
    except Exception:
        return None, None, None


def ask_open_files_tk(multiple: bool = True) -> List[str]:
    tk, filedialog, _ = _safe_import_tkinter()
    if tk is None:
        return []
    root = tk.Tk()
    root.withdraw()
    filetypes = [("PDF files", "*.pdf"), ("All files", "*.*")]
    if multiple:
        paths = filedialog.askopenfilenames(title="Select PDF files", filetypes=filetypes)
        root.destroy()
        return list(paths)
    else:
        path = filedialog.askopenfilename(title="Select PDF file", filetypes=filetypes)
        root.destroy()
        return [path] if path else []


def ask_save_file_tk(default_name: str = "output.pdf") -> Optional[str]:
    tk, filedialog, _ = _safe_import_tkinter()
    if tk is None:
        return None
    root = tk.Tk()
    root.withdraw()
    filetypes = [("PDF files", "*.pdf"), ("All files", "*.*")]
    path = filedialog.asksaveasfilename(title="Save PDF as", defaultextension=".pdf", initialfile=default_name, filetypes=filetypes)
    root.destroy()
    return path or None


def _print_header():
    print("\n=== PDF Tools TUI ===")
    print("1) Merge PDFs")
    print("2) Remove Pages")
    print("3) Reorder Pages")
    print("q) Quit")


def _prompt_bool(label: str, default: bool = False) -> bool:
    d = "Y/n" if default else "y/N"
    ans = input(f"{label} ({d}): ").strip().lower()
    if not ans:
        return default
    return ans in ("y", "yes", "true", "1")


def _prompt_text(label: str, default: Optional[str] = None) -> str:
    if default is not None:
        ans = input(f"{label} [{default}]: ").strip()
        return ans if ans else default
    return input(f"{label}: ").strip()


def run_merge(use_dialogs: bool, overwrite_default: bool):
    print("\n-- Merge PDFs --")
    if use_dialogs:
        inputs = ask_open_files_tk(multiple=True)
        if not inputs:
            print("No input files selected.")
            return
        out = ask_save_file_tk("merged.pdf")
        if not out:
            print("No output path selected.")
            return
        overwrite = overwrite_default or _prompt_bool("Overwrite if output exists?", overwrite_default)
    else:
        paths = _prompt_text("Enter input PDF paths separated by ;")
        inputs = [p.strip() for p in paths.split(";") if p.strip()]
        out = _prompt_text("Enter output PDF path", "merged.pdf")
        overwrite = overwrite_default or _prompt_bool("Overwrite if output exists?", overwrite_default)

    try:
        total = merge_pdfs(inputs, out, overwrite=overwrite)
        print(f"Merged {len(inputs)} PDFs ({total} pages) -> {out}")
    except Exception as e:
        print(f"Error: {e}")


def run_remove(use_dialogs: bool, overwrite_default: bool):
    print("\n-- Remove/Keep Pages --")
    if use_dialogs:
        inp = ask_open_files_tk(multiple=False)
        if not inp:
            print("No input file selected.")
            return
        input_path = inp[0]
        out = ask_save_file_tk("output.pdf")
        if not out:
            print("No output path selected.")
            return
    else:
        input_path = _prompt_text("Enter input PDF path")
        out = _prompt_text("Enter output PDF path", "output.pdf")

    spec = _prompt_text("Page spec (1-based, e.g. 1,3-5,10-)")
    keep = _prompt_bool("Keep only specified pages?", False)
    overwrite = overwrite_default or _prompt_bool("Overwrite if output exists?", overwrite_default)

    try:
        count = remove_pages(input_path, out, spec, keep=keep, overwrite=overwrite)
        mode = "kept" if keep else "retained"
        print(f"Processed {input_path} -> {out} ({count} pages {mode})")
    except Exception as e:
        print(f"Error: {e}")


def run_reorder(use_dialogs: bool, overwrite_default: bool):
    print("\n-- Reorder Pages --")
    if use_dialogs:
        inp = ask_open_files_tk(multiple=False)
        if not inp:
            print("No input file selected.")
            return
        input_path = inp[0]
        out = ask_save_file_tk("output.pdf")
        if not out:
            print("No output path selected.")
            return
    else:
        input_path = _prompt_text("Enter input PDF path")
        out = _prompt_text("Enter output PDF path", "output.pdf")

    order = _prompt_text("Order spec (1-based, e.g. 3,1,2,4-7)")
    fill_unlisted = _prompt_bool("Append unlisted pages at end?", True)
    strict = _prompt_bool("Strict: list every page exactly once?", False)
    overwrite = overwrite_default or _prompt_bool("Overwrite if output exists?", overwrite_default)

    try:
        count = reorder_pages(input_path, out, order_spec=order, fill_unlisted=fill_unlisted, strict=strict, overwrite=overwrite)
        print(f"Reordered pages of {input_path} -> {out} ({count} pages)")
    except Exception as e:
        print(f"Error: {e}")


def main():
    ap = argparse.ArgumentParser(description="PDF Tools TUI (with optional Tk file dialogs)")
    ap.add_argument("--no-dialog", action="store_true", help="Disable Tk file dialogs; use text prompts instead")
    ap.add_argument("--operation", choices=["merge", "remove", "reorder"], help="Start directly in an operation")
    ap.add_argument("--overwrite", action="store_true", help="Default overwrite output if exists")
    args = ap.parse_args()

    use_dialogs = not args.no_dialog
    overwrite_default = args.overwrite

    if args.operation:
        op = args.operation
        if op == "merge":
            run_merge(use_dialogs, overwrite_default)
        elif op == "remove":
            run_remove(use_dialogs, overwrite_default)
        elif op == "reorder":
            run_reorder(use_dialogs, overwrite_default)
        return

    while True:
        _print_header()
        choice = input("Select an option: ").strip().lower()
        if choice == "1":
            run_merge(use_dialogs, overwrite_default)
        elif choice == "2":
            run_remove(use_dialogs, overwrite_default)
        elif choice == "3":
            run_reorder(use_dialogs, overwrite_default)
        elif choice in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        else:
            print("Unknown option. Please choose 1, 2, 3, or q.")


if __name__ == "__main__":
    main()
