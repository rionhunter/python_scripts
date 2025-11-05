# Converters Suite

Comprehensive data format and unit conversion utilities.

## Data Format Converter

Convert between XML, JSON, YAML, CSV, SQL, and Python dict formats.

### Features
- Bidirectional conversions between popular data formats
- Batch processing for entire directories
- CSV to SQL INSERT statement generation
- Preserves data structure and types
- Pretty-printed output

### Usage Examples

```bash
# JSON to XML
python data_formats/data_converter.py input.json output.xml --from json --to xml

# CSV to JSON
python data_formats/data_converter.py data.csv data.json --from csv --to json

# CSV to SQL INSERT statements
python data_formats/data_converter.py users.csv users.sql --from csv --to sql --table users

# XML to YAML
python data_formats/data_converter.py config.xml config.yaml --from xml --to yaml

# Batch convert directory (JSON to YAML)
python data_formats/data_converter.py input_dir output_dir --from json --to yaml --batch
```

### Supported Conversions
- **Input formats**: JSON, XML, YAML, CSV
- **Output formats**: JSON, XML, YAML, CSV, SQL, Python dict literal

### Installation
```bash
cd data_formats
pip install -r requirements.txt
```

## Unit Converter

Convert between various measurement units including length, weight, volume, temperature, speed, time, area, and data sizes.

### Features
- Length: metric, imperial, nautical
- Weight/Mass: grams, pounds, ounces, tons
- Volume: liters, gallons, cups, tablespoons
- Temperature: Celsius, Fahrenheit, Kelvin
- Area: square meters, acres, hectares
- Speed: m/s, km/h, mph, knots
- Time: seconds to years
- Data: bytes to terabytes (decimal and binary)
- Base conversions: binary, octal, decimal, hexadecimal (base 2-36)

### Usage Examples

```bash
# Length conversions
python units/unit_converter.py 100 m ft
python units/unit_converter.py 5.5 miles km

# Weight conversions
python units/unit_converter.py 150 lbs kg
python units/unit_converter.py 2.5 kg oz

# Temperature conversions
python units/unit_converter.py 98.6 F C --temp
python units/unit_converter.py 25 C F --temp
python units/unit_converter.py 0 C K --temp

# Volume conversions
python units/unit_converter.py 2 gallons liters
python units/unit_converter.py 500 ml cups

# Speed conversions
python units/unit_converter.py 100 kph mph
python units/unit_converter.py 55 mph mps

# Data size conversions
python units/unit_converter.py 1024 MB GB
python units/unit_converter.py 1 GiB MiB

# Base conversions (number systems)
python units/unit_converter.py FF --from-base 16 --to-base 10
python units/unit_converter.py 255 --from-base 10 --to-base 2
python units/unit_converter.py 1010 --from-base 2 --to-base 16

# List available units
python units/unit_converter.py --list
python units/unit_converter.py --list length
python units/unit_converter.py --list temperature
```

### Advanced Options
- `--precision N`: Set decimal precision (default: 6)
- `--category CAT`: Specify unit category explicitly
- `--list [CATEGORY]`: List all available units or units in specific category

### No external dependencies required for unit converter!

## Quick Reference

### Common Conversions

**Temperature**
- Celsius to Fahrenheit: `python units/unit_converter.py 25 C F --temp`
- Fahrenheit to Celsius: `python units/unit_converter.py 77 F C --temp`

**Length**
- Meters to feet: `python units/unit_converter.py 100 m ft`
- Miles to kilometers: `python units/unit_converter.py 10 miles km`

**Weight**
- Pounds to kilograms: `python units/unit_converter.py 150 lbs kg`
- Kilograms to pounds: `python units/unit_converter.py 70 kg lbs`

**Data Formats**
- JSON to XML: `python data_formats/data_converter.py file.json file.xml --from json --to xml`
- CSV to JSON: `python data_formats/data_converter.py data.csv data.json --from csv --to json`
