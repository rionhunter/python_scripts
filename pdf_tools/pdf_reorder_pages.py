import argparse
import os
import sys
from pypdf import PdfReader, PdfWriter

try:
    from .utils import parse_order_spec
except ImportError:
    from utils import parse_order_spec


def reorder_pages(input_path, output_path, order_spec, fill_unlisted=True, strict=False, overwrite=False):
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input not found: {input_path}")
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file exists: {output_path}. Use --overwrite.")

    with open(input_path, "rb") as f_in:
        reader = PdfReader(f_in)
        num = len(reader.pages)
        order = parse_order_spec(order_spec, num, fill_unlisted=fill_unlisted, strict=strict)
        writer = PdfWriter()

        for i in order:
            writer.add_page(reader.pages[i])

        with open(output_path, "wb") as f_out:
            writer.write(f_out)

    return len(order)


def main():
    ap = argparse.ArgumentParser(description="Reorder pages in a PDF.")
    ap.add_argument("-i", "--input", required=True, help="Input PDF path.")
    ap.add_argument("-o", "--output", required=True, help="Output PDF path.")
    ap.add_argument("--order", required=True, help="Order spec, e.g. '3,1,2,4-7' (1-based).")
    ap.add_argument("--fill-unlisted", action="store_true", help="Append pages not listed at the end (default).")
    ap.add_argument("--no-fill-unlisted", dest="fill_unlisted", action="store_false", help="Do not append unlisted pages.")
    ap.add_argument("--strict", action="store_true", help="Require listing every page exactly once.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite output if exists.")
    ap.set_defaults(fill_unlisted=True)
    args = ap.parse_args()

    try:
        count = reorder_pages(args.input, args.output, args.order, args.fill_unlisted, args.strict, args.overwrite)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Reordered pages of {args.input} -> {args.output} ({count} pages)")


if __name__ == "__main__":
    main()
