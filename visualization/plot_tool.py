#!/usr/bin/env python3
"""
Data Visualization Tool
Create various types of plots and charts from data files or command-line data
"""

import argparse
import sys
import json
import csv
from typing import List, Dict, Any, Optional

# Check for matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False


def read_csv_data(filepath: str, x_column: int = 0, y_column: int = 1, 
                  has_header: bool = False) -> tuple:
    """
    Read data from CSV file.
    
    Args:
        filepath: Path to CSV file
        x_column: Column index for x-axis data
        y_column: Column index for y-axis data
        has_header: Whether first row is header
        
    Returns:
        Tuple of (x_data, y_data, header)
    """
    x_data = []
    y_data = []
    header = None
    
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        
        if has_header:
            header = next(reader)
        
        for row in reader:
            try:
                x_data.append(float(row[x_column]))
                y_data.append(float(row[y_column]))
            except (ValueError, IndexError):
                continue
    
    return x_data, y_data, header


def read_json_data(filepath: str, x_key: str = 'x', y_key: str = 'y') -> tuple:
    """
    Read data from JSON file.
    
    Args:
        filepath: Path to JSON file
        x_key: Key for x-axis data
        y_key: Key for y-axis data
        
    Returns:
        Tuple of (x_data, y_data)
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        x_data = [item.get(x_key, i) for i, item in enumerate(data)]
        y_data = [item.get(y_key, 0) for item in data]
    elif isinstance(data, dict):
        x_data = data.get(x_key, [])
        y_data = data.get(y_key, [])
    else:
        raise ValueError("JSON must be a list or dict")
    
    return x_data, y_data


def create_line_plot(x_data: List, y_data: List, title: str = "Line Plot",
                    xlabel: str = "X", ylabel: str = "Y", 
                    output: str = "plot.png", style: str = '-',
                    color: str = 'blue', marker: Optional[str] = None) -> None:
    """Create a line plot."""
    plt.figure(figsize=(10, 6))
    plt.plot(x_data, y_data, style, color=color, marker=marker, linewidth=2, markersize=6)
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output}")


def create_bar_plot(x_data: List, y_data: List, title: str = "Bar Plot",
                   xlabel: str = "X", ylabel: str = "Y",
                   output: str = "plot.png", color: str = 'steelblue',
                   horizontal: bool = False) -> None:
    """Create a bar plot."""
    plt.figure(figsize=(10, 6))
    
    if horizontal:
        plt.barh(x_data, y_data, color=color, edgecolor='black', linewidth=0.5)
    else:
        plt.bar(x_data, y_data, color=color, edgecolor='black', linewidth=0.5)
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output}")


def create_scatter_plot(x_data: List, y_data: List, title: str = "Scatter Plot",
                       xlabel: str = "X", ylabel: str = "Y",
                       output: str = "plot.png", color: str = 'red',
                       size: int = 50) -> None:
    """Create a scatter plot."""
    plt.figure(figsize=(10, 6))
    plt.scatter(x_data, y_data, s=size, c=color, alpha=0.6, edgecolors='black', linewidth=0.5)
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output}")


def create_histogram(data: List, title: str = "Histogram",
                    xlabel: str = "Value", ylabel: str = "Frequency",
                    output: str = "plot.png", bins: int = 30,
                    color: str = 'green') -> None:
    """Create a histogram."""
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=bins, color=color, edgecolor='black', linewidth=0.5, alpha=0.7)
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output}")


def create_pie_chart(labels: List, values: List, title: str = "Pie Chart",
                    output: str = "plot.png", explode: Optional[List] = None) -> None:
    """Create a pie chart."""
    plt.figure(figsize=(10, 8))
    
    colors = plt.cm.Set3(range(len(labels)))
    
    if explode is None:
        explode = [0.05 if i == values.index(max(values)) else 0 for i in range(len(values))]
    
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=colors, explode=explode, shadow=True)
    plt.title(title, fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output}")


def create_box_plot(data_groups: List[List], labels: List[str],
                   title: str = "Box Plot", ylabel: str = "Value",
                   output: str = "plot.png") -> None:
    """Create a box plot."""
    plt.figure(figsize=(10, 6))
    bp = plt.boxplot(data_groups, labels=labels, patch_artist=True,
                     notch=True, showmeans=True)
    
    # Color boxes
    colors = plt.cm.Set2(range(len(data_groups)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output}")


def main():
    if not MPL_AVAILABLE:
        print("Error: matplotlib not installed", file=sys.stderr)
        print("Install with: pip install matplotlib", file=sys.stderr)
        return 1
    
    parser = argparse.ArgumentParser(
        description='Create various types of plots and charts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Line plot from CSV
  %(prog)s -t line -f data.csv -o output.png --title "My Data"
  
  # Bar chart with custom labels
  %(prog)s -t bar -f data.csv --xlabel "Month" --ylabel "Sales"
  
  # Scatter plot from JSON
  %(prog)s -t scatter -f data.json --x-key time --y-key value
  
  # Histogram from values
  %(prog)s -t histogram -f values.csv --bins 50
  
  # Pie chart from CSV
  %(prog)s -t pie -f categories.csv --has-header
  
Supported plot types: line, bar, scatter, histogram, pie, box
        """
    )
    
    parser.add_argument('-t', '--type', required=True,
                        choices=['line', 'bar', 'scatter', 'histogram', 'pie', 'box'],
                        help='Plot type')
    parser.add_argument('-f', '--file', metavar='FILE',
                        help='Input data file (CSV or JSON)')
    parser.add_argument('-o', '--output', default='plot.png',
                        help='Output file path (default: plot.png)')
    parser.add_argument('--title', default='Plot',
                        help='Plot title')
    parser.add_argument('--xlabel', default='X',
                        help='X-axis label')
    parser.add_argument('--ylabel', default='Y',
                        help='Y-axis label')
    parser.add_argument('--x-column', type=int, default=0,
                        help='CSV column index for x-axis (default: 0)')
    parser.add_argument('--y-column', type=int, default=1,
                        help='CSV column index for y-axis (default: 1)')
    parser.add_argument('--x-key', default='x',
                        help='JSON key for x-axis data')
    parser.add_argument('--y-key', default='y',
                        help='JSON key for y-axis data')
    parser.add_argument('--has-header', action='store_true',
                        help='CSV file has header row')
    parser.add_argument('--color', default='blue',
                        help='Plot color')
    parser.add_argument('--bins', type=int, default=30,
                        help='Number of bins for histogram')
    parser.add_argument('--horizontal', action='store_true',
                        help='Create horizontal bar chart')
    parser.add_argument('--marker', default=None,
                        help='Marker style for line plot (o, s, ^, etc.)')
    
    args = parser.parse_args()
    
    try:
        if not args.file:
            print("Error: Input file required", file=sys.stderr)
            return 1
        
        # Read data
        if args.file.endswith('.json'):
            x_data, y_data = read_json_data(args.file, args.x_key, args.y_key)
        else:
            x_data, y_data, header = read_csv_data(
                args.file, args.x_column, args.y_column, args.has_header
            )
            
            # Use header for labels if available
            if header and args.has_header:
                if not args.xlabel or args.xlabel == 'X':
                    args.xlabel = header[args.x_column] if len(header) > args.x_column else 'X'
                if not args.ylabel or args.ylabel == 'Y':
                    args.ylabel = header[args.y_column] if len(header) > args.y_column else 'Y'
        
        # Create plot
        if args.type == 'line':
            create_line_plot(x_data, y_data, args.title, args.xlabel, args.ylabel,
                           args.output, color=args.color, marker=args.marker)
        
        elif args.type == 'bar':
            create_bar_plot(x_data, y_data, args.title, args.xlabel, args.ylabel,
                          args.output, color=args.color, horizontal=args.horizontal)
        
        elif args.type == 'scatter':
            create_scatter_plot(x_data, y_data, args.title, args.xlabel, args.ylabel,
                              args.output, color=args.color)
        
        elif args.type == 'histogram':
            # For histogram, use y_data or combine both
            data = y_data if y_data else x_data
            create_histogram(data, args.title, args.xlabel, args.ylabel,
                           args.output, bins=args.bins, color=args.color)
        
        elif args.type == 'pie':
            create_pie_chart(x_data, y_data, args.title, args.output)
        
        elif args.type == 'box':
            # For box plot, treat x_data as labels and y_data as single group
            # (More complex multi-group support would need different input format)
            create_box_plot([y_data], ['Data'], args.title, args.ylabel, args.output)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
