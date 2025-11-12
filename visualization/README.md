# Data Visualization Tools

Create professional plots and charts from CSV and JSON data files.

## Features

- **Multiple Plot Types**: Line, bar, scatter, histogram, pie, box plots
- **Data Formats**: CSV and JSON support
- **Customization**: Colors, labels, titles, markers
- **High Quality**: 300 DPI output for publications
- **Easy to Use**: Simple command-line interface

## Installation

Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Plot Tool (`plot_tool.py`)

#### Line Plots

```bash
# Basic line plot from CSV
python plot_tool.py -t line -f data.csv -o output.png

# With custom labels and title
python plot_tool.py -t line -f data.csv -o sales.png \
    --title "Monthly Sales" --xlabel "Month" --ylabel "Revenue ($)"

# With markers
python plot_tool.py -t line -f data.csv -o output.png --marker o --color red
```

#### Bar Charts

```bash
# Vertical bar chart
python plot_tool.py -t bar -f data.csv -o chart.png \
    --title "Product Sales" --color steelblue

# Horizontal bar chart
python plot_tool.py -t bar -f data.csv -o chart.png --horizontal
```

#### Scatter Plots

```bash
# Basic scatter plot
python plot_tool.py -t scatter -f data.csv -o scatter.png

# Custom color and from JSON
python plot_tool.py -t scatter -f data.json -o scatter.png \
    --x-key temperature --y-key humidity --color red
```

#### Histograms

```bash
# Distribution histogram
python plot_tool.py -t histogram -f values.csv -o hist.png --bins 50

# Custom styling
python plot_tool.py -t histogram -f values.csv -o hist.png \
    --title "Value Distribution" --xlabel "Value" --ylabel "Count" --color green
```

#### Pie Charts

```bash
# Pie chart from CSV
python plot_tool.py -t pie -f categories.csv -o pie.png \
    --title "Market Share"
```

#### Box Plots

```bash
# Box plot for distribution
python plot_tool.py -t box -f data.csv -o box.png \
    --title "Data Distribution"
```

## Data Formats

### CSV Format

Simple two-column format (or specify columns):
```csv
Month,Sales
January,1000
February,1200
March,1500
```

Usage:
```bash
# With header
python plot_tool.py -t line -f data.csv --has-header

# Specify columns
python plot_tool.py -t line -f data.csv --x-column 0 --y-column 2
```

### JSON Format

Two formats supported:

**List of objects:**
```json
[
  {"x": 1, "y": 10},
  {"x": 2, "y": 20},
  {"x": 3, "y": 30}
]
```

**Dictionary with arrays:**
```json
{
  "x": [1, 2, 3, 4, 5],
  "y": [10, 20, 15, 25, 30]
}
```

Usage:
```bash
python plot_tool.py -t line -f data.json --x-key time --y-key value
```

## Examples

### Sales Data Visualization

```bash
# Create sample data
cat > sales.csv << EOF
Month,Revenue
Jan,45000
Feb,52000
Mar,48000
Apr,61000
May,58000
Jun,67000
EOF

# Create bar chart
python plot_tool.py -t bar -f sales.csv --has-header \
    --title "Monthly Revenue 2024" \
    --xlabel "Month" --ylabel "Revenue ($)" \
    --color "#4a90e2" -o monthly_sales.png
```

### Scientific Data Plot

```bash
# Line plot with markers
python plot_tool.py -t line -f experiment.csv --has-header \
    --title "Temperature vs Time" \
    --xlabel "Time (minutes)" --ylabel "Temperature (°C)" \
    --marker o --color red -o temperature_plot.png
```

### Distribution Analysis

```bash
# Histogram of values
python plot_tool.py -t histogram -f measurements.csv \
    --title "Measurement Distribution" \
    --xlabel "Value" --ylabel "Frequency" \
    --bins 30 --color green -o distribution.png
```

## Customization Options

### Colors
Use any matplotlib color name or hex code:
- Named: `blue`, `red`, `green`, `steelblue`, `coral`
- Hex: `#FF5733`, `#4a90e2`

### Markers (Line Plots)
- `o` - Circle
- `s` - Square
- `^` - Triangle up
- `v` - Triangle down
- `*` - Star
- `+` - Plus
- `x` - X mark

### Plot Sizes
All plots are 10x6 inches at 300 DPI by default, suitable for:
- Reports and presentations
- Academic papers
- Web content

## Tips

1. **CSV Headers**: Use `--has-header` when your CSV has column names
2. **Large Datasets**: Histograms and scatter plots handle large data well
3. **File Formats**: Save as PNG for web, or modify code for PDF/SVG
4. **Color Schemes**: Use consistent colors across related plots
5. **Labels**: Always add descriptive labels and titles

## Common Use Cases

### Business Analytics
- Sales trends
- Revenue comparisons
- Market share visualization

### Scientific Research
- Experimental data plots
- Distribution analysis
- Correlation studies

### Data Exploration
- Quick data visualization
- Outlier detection
- Pattern identification

## Advanced Usage

### Creating Multiple Plots

```bash
# Script to create multiple views of data
for type in line bar scatter; do
    python plot_tool.py -t $type -f data.csv -o plot_$type.png
done
```

### Batch Processing

```bash
# Plot all CSV files in directory
for file in *.csv; do
    python plot_tool.py -t line -f "$file" -o "${file%.csv}.png"
done
```

## Dependencies

- **matplotlib**: Plotting library
- **numpy**: Numerical operations
- Python 3.7+

## Limitations

- Box plots currently support single data series
- Pie charts work best with small number of categories
- Very large datasets (>100K points) may be slow

## Future Enhancements

- Multiple series on same plot
- 3D plotting
- Interactive plots (Plotly backend)
- More chart types (violin, heatmap, etc.)
