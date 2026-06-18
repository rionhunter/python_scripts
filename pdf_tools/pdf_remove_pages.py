import argparse
import os
import sys
from pypdf import PdfReader, PdfWriter

try:
    from .utils import parse_pages_spec
except ImportError:
    from utils import parse_pages_spec


def remove_pages(input_path, output_path, pages_spec, keep=False, overwrite=False):
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input not found: {input_path}")
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file exists: {output_path}. Use --overwrite.")

    with open(input_path, "rb") as f_in:
        reader = PdfReader(f_in)
        num = len(reader.pages)
        selected = set(parse_pages_spec(pages_spec, num))
        writer = PdfWriter()

        if keep:
            indices = sorted(selected)
        else:
            indices = [i for i in range(num) if i not in selected]

        for i in indices:
            writer.add_page(reader.pages[i])

        with open(output_path, "wb") as f_out:
            writer.write(f_out)

    return len(indices)


def main():
    ap = argparse.ArgumentParser(description="Remove or keep specified pages from a PDF.")
    ap.add_argument("-i", "--input", required=True, help="Input PDF path.")
    ap.add_argument("-o", "--output", required=True, help="Output PDF path.")
    ap.add_argument("--pages", required=True, help="Page spec, e.g. '1,3-5,10-' (1-based).")
    ap.add_argument("--keep", action="store_true", help="Keep only specified pages instead of removing them.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite output if exists.")
    args = ap.parse_args()

    try:
        count = remove_pages(args.input, args.output, args.pages, args.keep, args.overwrite)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    mode = "kept" if args.keep else "retained"
    print(f"Processed {args.input} -> {args.output} ({count} pages {mode})")


if __name__ == "__main__":
    main()
