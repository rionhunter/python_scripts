#!/usr/bin/env python3
"""
Text Comparison and Diff Tool
Compare text files and strings with various output formats
"""

import argparse
import sys
import difflib
from pathlib import Path
from typing import List, Tuple, Optional


def read_file_lines(filepath: str) -> List[str]:
    """Read file and return lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()


def unified_diff(file1: str, file2: str, context: int = 3) -> str:
    """
    Generate unified diff output.
    
    Args:
        file1: Path to first file
        file2: Path to second file
        context: Number of context lines
        
    Returns:
        Unified diff string
    """
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=file1,
        tofile=file2,
        lineterm='',
        n=context
    )
    
    return '\n'.join(diff)


def context_diff(file1: str, file2: str, context: int = 3) -> str:
    """Generate context diff output."""
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    
    diff = difflib.context_diff(
        lines1, lines2,
        fromfile=file1,
        tofile=file2,
        lineterm='',
        n=context
    )
    
    return '\n'.join(diff)


def html_diff(file1: str, file2: str, output: Optional[str] = None) -> str:
    """
    Generate HTML side-by-side diff.
    
    Args:
        file1: Path to first file
        file2: Path to second file
        output: Optional output file path
        
    Returns:
        HTML diff string
    """
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    
    differ = difflib.HtmlDiff()
    html = differ.make_file(
        lines1, lines2,
        fromdesc=file1,
        todesc=file2,
        context=True,
        numlines=3
    )
    
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ HTML diff saved to: {output}")
    
    return html


def side_by_side_diff(file1: str, file2: str, width: int = 80) -> str:
    """
    Generate side-by-side text diff.
    
    Args:
        file1: Path to first file
        file2: Path to second file
        width: Width of each column
        
    Returns:
        Side-by-side diff string
    """
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    
    # Ensure same length
    max_len = max(len(lines1), len(lines2))
    lines1 += [''] * (max_len - len(lines1))
    lines2 += [''] * (max_len - len(lines2))
    
    output = []
    output.append(f"{'File 1: ' + file1:{width}} | {'File 2: ' + file2}")
    output.append('=' * (width * 2 + 3))
    
    for i, (line1, line2) in enumerate(zip(lines1, lines2), 1):
        line1 = line1.rstrip('\n')
        line2 = line2.rstrip('\n')
        
        # Mark differences
        marker = '|' if line1 != line2 else ' '
        
        # Truncate if needed
        line1 = line1[:width-1].ljust(width)
        line2 = line2[:width-1]
        
        output.append(f"{line1} {marker} {line2}")
    
    return '\n'.join(output)


def get_diff_stats(file1: str, file2: str) -> dict:
    """
    Get statistics about differences between files.
    
    Args:
        file1: Path to first file
        file2: Path to second file
        
    Returns:
        Dictionary with diff statistics
    """
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    
    differ = difflib.Differ()
    diff = list(differ.compare(lines1, lines2))
    
    stats = {
        'added': sum(1 for line in diff if line.startswith('+ ')),
        'removed': sum(1 for line in diff if line.startswith('- ')),
        'changed': 0,
        'unchanged': sum(1 for line in diff if line.startswith('  ')),
        'total_lines_1': len(lines1),
        'total_lines_2': len(lines2)
    }
    
    # Estimate changed lines (removed + added in close proximity)
    stats['changed'] = min(stats['added'], stats['removed'])
    stats['added'] -= stats['changed']
    stats['removed'] -= stats['changed']
    
    return stats


def calculate_similarity(file1: str, file2: str) -> float:
    """
    Calculate similarity ratio between two files.
    
    Args:
        file1: Path to first file
        file2: Path to second file
        
    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    
    # Use SequenceMatcher for similarity
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    return matcher.ratio()


def find_matching_blocks(file1: str, file2: str) -> List[Tuple[int, int, int]]:
    """
    Find matching blocks between two files.
    
    Returns:
        List of tuples (pos1, pos2, length)
    """
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    return matcher.get_matching_blocks()


def main():
    parser = argparse.ArgumentParser(
        description='Compare text files and show differences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file1.txt file2.txt                    # Unified diff
  %(prog)s file1.txt file2.txt -f context         # Context diff
  %(prog)s file1.txt file2.txt -f html -o diff.html  # HTML diff
  %(prog)s file1.txt file2.txt -f side            # Side-by-side
  %(prog)s file1.txt file2.txt --stats            # Show statistics
  %(prog)s file1.txt file2.txt --similarity       # Similarity score
  
Formats:
  unified  - Standard unified diff (default)
  context  - Context diff format
  html     - HTML side-by-side diff
  side     - Text side-by-side diff
        """
    )
    
    parser.add_argument('file1', help='First file to compare')
    parser.add_argument('file2', help='Second file to compare')
    parser.add_argument('-f', '--format', default='unified',
                        choices=['unified', 'context', 'html', 'side'],
                        help='Diff format (default: unified)')
    parser.add_argument('-o', '--output', metavar='FILE',
                        help='Output file (for HTML format)')
    parser.add_argument('-c', '--context', type=int, default=3,
                        help='Number of context lines (default: 3)')
    parser.add_argument('-w', '--width', type=int, default=80,
                        help='Column width for side-by-side (default: 80)')
    parser.add_argument('--stats', action='store_true',
                        help='Show diff statistics')
    parser.add_argument('--similarity', action='store_true',
                        help='Show similarity score')
    parser.add_argument('--quiet', action='store_true',
                        help='Only show if files differ (exit code)')
    
    args = parser.parse_args()
    
    try:
        # Check if files exist
        if not Path(args.file1).exists():
            print(f"Error: File not found: {args.file1}", file=sys.stderr)
            return 1
        if not Path(args.file2).exists():
            print(f"Error: File not found: {args.file2}", file=sys.stderr)
            return 1
        
        # Quick check if files are identical
        lines1 = read_file_lines(args.file1)
        lines2 = read_file_lines(args.file2)
        
        if lines1 == lines2:
            if not args.quiet:
                print("Files are identical")
            return 0
        
        if args.quiet:
            return 1
        
        # Show statistics
        if args.stats:
            stats = get_diff_stats(args.file1, args.file2)
            print("\nDiff Statistics:")
            print(f"  Lines in file 1: {stats['total_lines_1']}")
            print(f"  Lines in file 2: {stats['total_lines_2']}")
            print(f"  Unchanged:       {stats['unchanged']}")
            print(f"  Changed:         {stats['changed']}")
            print(f"  Added:           {stats['added']}")
            print(f"  Removed:         {stats['removed']}")
            print()
        
        # Show similarity
        if args.similarity:
            similarity = calculate_similarity(args.file1, args.file2)
            print(f"\nSimilarity: {similarity * 100:.2f}%\n")
        
        # Generate diff
        if args.format == 'unified':
            diff_output = unified_diff(args.file1, args.file2, args.context)
            print(diff_output)
        
        elif args.format == 'context':
            diff_output = context_diff(args.file1, args.file2, args.context)
            print(diff_output)
        
        elif args.format == 'html':
            output_file = args.output or 'diff.html'
            html_diff(args.file1, args.file2, output_file)
        
        elif args.format == 'side':
            diff_output = side_by_side_diff(args.file1, args.file2, args.width)
            print(diff_output)
        
        return 1  # Files differ
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
