import argparse
import os
import sys
from pypdf import PdfReader, PdfWriter


def merge_pdfs(inputs, output, overwrite=False):
    if not inputs:
        raise ValueError("No input PDFs provided.")
    if os.path.exists(output) and not overwrite:
        raise FileExistsError(f"Output file exists: {output}. Use --overwrite.")

    writer = PdfWriter()
    total_pages = 0

    for path in inputs:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Input not found: {path}")
        with open(path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
                total_pages += 1

    with open(output, "wb") as f:
        writer.write(f)

    return total_pages


def main():
    ap = argparse.ArgumentParser(description="Merge multiple PDFs into one.")
    ap.add_argument("inputs", nargs="+", help="Input PDF files in desired order.")
    ap.add_argument("-o", "--output", required=True, help="Output PDF path.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite output if exists.")
    args = ap.parse_args()

    try:
        total = merge_pdfs(args.inputs, args.output, args.overwrite)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Merged {len(args.inputs)} PDFs ({total} pages) -> {args.output}")


if __name__ == "__main__":
    main()
