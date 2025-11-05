#!/usr/bin/env python3
"""
Data Format Converter
Convert between XML, JSON, YAML, CSV, and other data formats
Supports batch processing and bidirectional conversions
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union
import xml.etree.ElementTree as ET
from xml.dom import minidom

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: YAML support not available. Install with: pip install pyyaml")


class DataConverter:
    """Main data format conversion class"""
    
    @staticmethod
    def json_to_xml(data: Union[Dict, List], root_name: str = 'root') -> str:
        """
        Convert JSON/dict to XML string
        
        Args:
            data: JSON data (dict or list)
            root_name: Name for root element
            
        Returns:
            Formatted XML string
        """
        def build_xml(parent, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    # Sanitize key for XML element name
                    key = str(key).replace(' ', '_')
                    child = ET.SubElement(parent, key)
                    build_xml(child, value)
            
            elif isinstance(data, list):
                for item in data:
                    child = ET.SubElement(parent, 'item')
                    build_xml(child, item)
            
            else:
                parent.text = str(data)
        
        root = ET.Element(root_name)
        build_xml(root, data)
        
        # Pretty print
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
    
    @staticmethod
    def xml_to_json(xml_string: str) -> Union[Dict, str]:
        """
        Convert XML string to JSON/dict
        
        Args:
            xml_string: XML content
            
        Returns:
            Dictionary representation
        """
        def parse_element(element):
            result = {}
            
            # Add attributes
            if element.attrib:
                result['@attributes'] = element.attrib
            
            # Parse children
            children = list(element)
            if children:
                child_dict = {}
                for child in children:
                    child_data = parse_element(child)
                    tag = child.tag
                    
                    # Handle multiple children with same tag
                    if tag in child_dict:
                        if not isinstance(child_dict[tag], list):
                            child_dict[tag] = [child_dict[tag]]
                        child_dict[tag].append(child_data)
                    else:
                        child_dict[tag] = child_data
                
                result.update(child_dict)
            
            # Add text content
            if element.text and element.text.strip():
                if result:
                    result['#text'] = element.text.strip()
                else:
                    return element.text.strip()
            
            return result if result else None
        
        try:
            root = ET.fromstring(xml_string)
            return {root.tag: parse_element(root)}
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            return {}
    
    @staticmethod
    def json_to_yaml(data: Union[Dict, List]) -> str:
        """
        Convert JSON/dict to YAML string
        
        Args:
            data: JSON data
            
        Returns:
            YAML string
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
        
        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    @staticmethod
    def yaml_to_json(yaml_string: str) -> Union[Dict, List]:
        """
        Convert YAML string to JSON/dict
        
        Args:
            yaml_string: YAML content
            
        Returns:
            Dictionary or list
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
        
        return yaml.safe_load(yaml_string)
    
    @staticmethod
    def csv_to_json(csv_content: str, delimiter: str = ',') -> List[Dict]:
        """
        Convert CSV to JSON (list of dicts)
        
        Args:
            csv_content: CSV content
            delimiter: CSV delimiter
            
        Returns:
            List of dictionaries
        """
        import csv
        from io import StringIO
        
        reader = csv.DictReader(StringIO(csv_content), delimiter=delimiter)
        return list(reader)
    
    @staticmethod
    def json_to_csv(data: List[Dict], delimiter: str = ',') -> str:
        """
        Convert JSON (list of dicts) to CSV
        
        Args:
            data: List of dictionaries
            delimiter: CSV delimiter
            
        Returns:
            CSV string
        """
        import csv
        from io import StringIO
        
        if not data:
            return ""
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys(), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    @staticmethod
    def csv_to_sql(csv_content: str, table_name: str, delimiter: str = ',') -> str:
        """
        Convert CSV to SQL INSERT statements
        
        Args:
            csv_content: CSV content
            table_name: SQL table name
            delimiter: CSV delimiter
            
        Returns:
            SQL INSERT statements
        """
        import csv
        from io import StringIO
        
        reader = csv.DictReader(StringIO(csv_content), delimiter=delimiter)
        rows = list(reader)
        
        if not rows:
            return ""
        
        # Generate SQL
        columns = list(rows[0].keys())
        sql_lines = []
        
        for row in rows:
            values = []
            for col in columns:
                value = row[col]
                # Escape single quotes and wrap in quotes
                value = value.replace("'", "''")
                values.append(f"'{value}'")
            
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
            sql_lines.append(sql)
        
        return '\n'.join(sql_lines)
    
    @staticmethod
    def json_to_python_dict(data: Union[Dict, List]) -> str:
        """
        Convert JSON to Python dict literal string
        
        Args:
            data: JSON data
            
        Returns:
            Python dict/list string representation
        """
        import pprint
        return pprint.pformat(data, width=100, sort_dicts=False)


def convert_file(input_path: str, output_path: str, from_format: str, 
                 to_format: str, **kwargs):
    """
    Convert file from one format to another
    
    Args:
        input_path: Input file path
        output_path: Output file path
        from_format: Source format
        to_format: Target format
        **kwargs: Additional conversion parameters
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # Read input
    with open(input_path, 'r', encoding='utf-8') as f:
        input_content = f.read()
    
    converter = DataConverter()
    
    # Parse input format
    if from_format == 'json':
        data = json.loads(input_content)
    elif from_format == 'xml':
        data = converter.xml_to_json(input_content)
    elif from_format == 'yaml':
        data = converter.yaml_to_json(input_content)
    elif from_format == 'csv':
        data = converter.csv_to_json(input_content, kwargs.get('delimiter', ','))
    else:
        raise ValueError(f"Unsupported input format: {from_format}")
    
    # Convert to output format
    if to_format == 'json':
        output_content = json.dumps(data, indent=2, ensure_ascii=False)
    elif to_format == 'xml':
        root_name = kwargs.get('root_name', 'root')
        output_content = converter.json_to_xml(data, root_name)
    elif to_format == 'yaml':
        output_content = converter.json_to_yaml(data)
    elif to_format == 'csv':
        if not isinstance(data, list):
            raise ValueError("CSV output requires list of dictionaries")
        output_content = converter.json_to_csv(data, kwargs.get('delimiter', ','))
    elif to_format == 'sql':
        if not isinstance(data, list):
            raise ValueError("SQL output requires list of dictionaries")
        csv_temp = converter.json_to_csv(data)
        table_name = kwargs.get('table_name', 'table')
        output_content = converter.csv_to_sql(csv_temp, table_name)
    elif to_format == 'python':
        output_content = converter.json_to_python_dict(data)
    else:
        raise ValueError(f"Unsupported output format: {to_format}")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"Converted {input_path} ({from_format}) -> {output_path} ({to_format})")


def batch_convert(input_dir: str, output_dir: str, from_format: str, 
                  to_format: str, pattern: str = '*', **kwargs):
    """
    Batch convert files in directory
    
    Args:
        input_dir: Input directory
        output_dir: Output directory
        from_format: Source format
        to_format: Target format
        pattern: File pattern to match
        **kwargs: Additional conversion parameters
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find files
    if from_format == 'json':
        files = list(input_dir.glob(f"{pattern}.json"))
    elif from_format == 'xml':
        files = list(input_dir.glob(f"{pattern}.xml"))
    elif from_format == 'yaml':
        files = list(input_dir.glob(f"{pattern}.yaml")) + list(input_dir.glob(f"{pattern}.yml"))
    elif from_format == 'csv':
        files = list(input_dir.glob(f"{pattern}.csv"))
    else:
        files = []
    
    if not files:
        print(f"No {from_format} files found in {input_dir}")
        return
    
    # Convert each file
    for input_file in files:
        # Determine output extension
        ext_map = {
            'json': '.json',
            'xml': '.xml',
            'yaml': '.yaml',
            'csv': '.csv',
            'sql': '.sql',
            'python': '.py'
        }
        output_file = output_dir / (input_file.stem + ext_map.get(to_format, '.txt'))
        
        try:
            convert_file(input_file, output_file, from_format, to_format, **kwargs)
        except Exception as e:
            print(f"Error converting {input_file}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Data Format Converter - Convert between XML, JSON, YAML, CSV, SQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file
  python data_converter.py input.json output.xml --from json --to xml
  
  # JSON to YAML
  python data_converter.py data.json data.yaml --from json --to yaml
  
  # CSV to SQL INSERT statements
  python data_converter.py data.csv data.sql --from csv --to sql --table users
  
  # Batch convert directory
  python data_converter.py input_dir output_dir --from json --to yaml --batch
  
  # XML to JSON
  python data_converter.py config.xml config.json --from xml --to json
        """
    )
    
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('output', help='Output file or directory')
    parser.add_argument('--from', dest='from_format', required=True,
                        choices=['json', 'xml', 'yaml', 'csv'],
                        help='Source format')
    parser.add_argument('--to', dest='to_format', required=True,
                        choices=['json', 'xml', 'yaml', 'csv', 'sql', 'python'],
                        help='Target format')
    parser.add_argument('--batch', action='store_true',
                        help='Batch convert directory')
    parser.add_argument('--pattern', default='*',
                        help='File pattern for batch mode (default: *)')
    parser.add_argument('--delimiter', default=',',
                        help='CSV delimiter (default: ,)')
    parser.add_argument('--table', dest='table_name', default='table',
                        help='SQL table name (for SQL output)')
    parser.add_argument('--root', dest='root_name', default='root',
                        help='XML root element name (for XML output)')
    
    args = parser.parse_args()
    
    kwargs = {
        'delimiter': args.delimiter,
        'table_name': args.table_name,
        'root_name': args.root_name
    }
    
    try:
        if args.batch:
            batch_convert(args.input, args.output, args.from_format, 
                         args.to_format, args.pattern, **kwargs)
        else:
            convert_file(args.input, args.output, args.from_format, 
                        args.to_format, **kwargs)
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
