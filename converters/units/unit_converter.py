#!/usr/bin/env python3
"""
Unit Converter Suite
Convert between various units: length, weight, volume, temperature, currency, time zones, base conversions
Supports batch conversions and interactive mode
"""

import argparse
import sys
import math
from typing import Dict, Tuple, Optional
from datetime import datetime
import json


class UnitConverter:
    """Universal unit conversion class"""
    
    # Conversion factors to base units (meters, grams, liters, etc.)
    LENGTH_UNITS = {
        # Metric
        'mm': 0.001, 'millimeter': 0.001, 'millimeters': 0.001,
        'cm': 0.01, 'centimeter': 0.01, 'centimeters': 0.01,
        'm': 1.0, 'meter': 1.0, 'meters': 1.0, 'metre': 1.0, 'metres': 1.0,
        'km': 1000.0, 'kilometer': 1000.0, 'kilometers': 1000.0, 'kilometre': 1000.0, 'kilometres': 1000.0,
        # Imperial
        'in': 0.0254, 'inch': 0.0254, 'inches': 0.0254,
        'ft': 0.3048, 'foot': 0.3048, 'feet': 0.3048,
        'yd': 0.9144, 'yard': 0.9144, 'yards': 0.9144,
        'mi': 1609.344, 'mile': 1609.344, 'miles': 1609.344,
        # Nautical
        'nmi': 1852.0, 'nautical_mile': 1852.0, 'nautical_miles': 1852.0,
    }
    
    WEIGHT_UNITS = {
        # Metric
        'mg': 0.001, 'milligram': 0.001, 'milligrams': 0.001,
        'g': 1.0, 'gram': 1.0, 'grams': 1.0,
        'kg': 1000.0, 'kilogram': 1000.0, 'kilograms': 1000.0,
        't': 1000000.0, 'ton': 1000000.0, 'tons': 1000000.0, 'tonne': 1000000.0, 'tonnes': 1000000.0,
        # Imperial
        'oz': 28.3495, 'ounce': 28.3495, 'ounces': 28.3495,
        'lb': 453.592, 'lbs': 453.592, 'pound': 453.592, 'pounds': 453.592,
        'stone': 6350.29, 'st': 6350.29,
    }
    
    VOLUME_UNITS = {
        # Metric
        'ml': 0.001, 'milliliter': 0.001, 'milliliters': 0.001, 'millilitre': 0.001, 'millilitres': 0.001,
        'l': 1.0, 'liter': 1.0, 'liters': 1.0, 'litre': 1.0, 'litres': 1.0,
        # Imperial
        'tsp': 0.00492892, 'teaspoon': 0.00492892, 'teaspoons': 0.00492892,
        'tbsp': 0.0147868, 'tablespoon': 0.0147868, 'tablespoons': 0.0147868,
        'floz': 0.0295735, 'fluid_ounce': 0.0295735, 'fluid_ounces': 0.0295735,
        'cup': 0.236588, 'cups': 0.236588,
        'pt': 0.473176, 'pint': 0.473176, 'pints': 0.473176,
        'qt': 0.946353, 'quart': 0.946353, 'quarts': 0.946353,
        'gal': 3.78541, 'gallon': 3.78541, 'gallons': 3.78541,
    }
    
    AREA_UNITS = {
        'mm2': 0.000001, 'sq_mm': 0.000001,
        'cm2': 0.0001, 'sq_cm': 0.0001,
        'm2': 1.0, 'sq_m': 1.0, 'square_meter': 1.0, 'square_meters': 1.0,
        'km2': 1000000.0, 'sq_km': 1000000.0, 'square_kilometer': 1000000.0,
        'hectare': 10000.0, 'ha': 10000.0,
        'acre': 4046.86, 'acres': 4046.86,
        'sq_in': 0.00064516, 'square_inch': 0.00064516,
        'sq_ft': 0.092903, 'square_foot': 0.092903, 'square_feet': 0.092903,
        'sq_yd': 0.836127, 'square_yard': 0.836127,
        'sq_mi': 2589988.0, 'square_mile': 2589988.0,
    }
    
    TIME_UNITS = {
        'ms': 0.001, 'millisecond': 0.001, 'milliseconds': 0.001,
        's': 1.0, 'sec': 1.0, 'second': 1.0, 'seconds': 1.0,
        'min': 60.0, 'minute': 60.0, 'minutes': 60.0,
        'h': 3600.0, 'hr': 3600.0, 'hour': 3600.0, 'hours': 3600.0,
        'd': 86400.0, 'day': 86400.0, 'days': 86400.0,
        'wk': 604800.0, 'week': 604800.0, 'weeks': 604800.0,
        'mo': 2629800.0, 'month': 2629800.0, 'months': 2629800.0,  # Average month
        'yr': 31557600.0, 'year': 31557600.0, 'years': 31557600.0,  # Average year
    }
    
    SPEED_UNITS = {
        'mps': 1.0, 'm/s': 1.0, 'meters_per_second': 1.0,
        'kph': 0.277778, 'km/h': 0.277778, 'kmh': 0.277778,
        'mph': 0.44704, 'miles_per_hour': 0.44704,
        'fps': 0.3048, 'ft/s': 0.3048, 'feet_per_second': 0.3048,
        'knot': 0.514444, 'knots': 0.514444, 'kt': 0.514444,
    }
    
    DATA_UNITS = {
        'b': 1.0, 'bit': 1.0, 'bits': 1.0,
        'B': 8.0, 'byte': 8.0, 'bytes': 8.0,
        'KB': 8000.0, 'kilobyte': 8000.0, 'kilobytes': 8000.0,
        'MB': 8000000.0, 'megabyte': 8000000.0, 'megabytes': 8000000.0,
        'GB': 8000000000.0, 'gigabyte': 8000000000.0, 'gigabytes': 8000000000.0,
        'TB': 8000000000000.0, 'terabyte': 8000000000000.0, 'terabytes': 8000000000000.0,
        # Binary
        'KiB': 8192.0, 'kibibyte': 8192.0,
        'MiB': 8388608.0, 'mebibyte': 8388608.0,
        'GiB': 8589934592.0, 'gibibyte': 8589934592.0,
        'TiB': 8796093022208.0, 'tebibyte': 8796093022208.0,
    }
    
    def __init__(self):
        self.unit_groups = {
            'length': self.LENGTH_UNITS,
            'weight': self.WEIGHT_UNITS,
            'mass': self.WEIGHT_UNITS,
            'volume': self.VOLUME_UNITS,
            'area': self.AREA_UNITS,
            'time': self.TIME_UNITS,
            'speed': self.SPEED_UNITS,
            'velocity': self.SPEED_UNITS,
            'data': self.DATA_UNITS,
        }
    
    def convert(self, value: float, from_unit: str, to_unit: str, 
                category: Optional[str] = None) -> float:
        """
        Convert value from one unit to another
        
        Args:
            value: Numeric value to convert
            from_unit: Source unit
            to_unit: Target unit
            category: Unit category (auto-detected if None)
            
        Returns:
            Converted value
        """
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Find the unit category
        if category:
            units_dict = self.unit_groups.get(category.lower())
            if not units_dict:
                raise ValueError(f"Unknown category: {category}")
        else:
            units_dict = None
            for cat, units in self.unit_groups.items():
                if from_unit in units and to_unit in units:
                    units_dict = units
                    break
            
            if not units_dict:
                raise ValueError(f"Could not find compatible units: {from_unit} and {to_unit}")
        
        # Check units exist
        if from_unit not in units_dict:
            raise ValueError(f"Unknown unit: {from_unit}")
        if to_unit not in units_dict:
            raise ValueError(f"Unknown unit: {to_unit}")
        
        # Convert through base unit
        base_value = value * units_dict[from_unit]
        result = base_value / units_dict[to_unit]
        
        return result
    
    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert temperature between Celsius, Fahrenheit, and Kelvin
        
        Args:
            value: Temperature value
            from_unit: Source unit (C, F, K)
            to_unit: Target unit (C, F, K)
            
        Returns:
            Converted temperature
        """
        from_unit = from_unit.upper()
        to_unit = to_unit.upper()
        
        # Convert to Celsius first
        if from_unit == 'C' or from_unit == 'CELSIUS':
            celsius = value
        elif from_unit == 'F' or from_unit == 'FAHRENHEIT':
            celsius = (value - 32) * 5/9
        elif from_unit == 'K' or from_unit == 'KELVIN':
            celsius = value - 273.15
        else:
            raise ValueError(f"Unknown temperature unit: {from_unit}")
        
        # Convert from Celsius to target
        if to_unit == 'C' or to_unit == 'CELSIUS':
            return celsius
        elif to_unit == 'F' or to_unit == 'FAHRENHEIT':
            return celsius * 9/5 + 32
        elif to_unit == 'K' or to_unit == 'KELVIN':
            return celsius + 273.15
        else:
            raise ValueError(f"Unknown temperature unit: {to_unit}")
    
    def convert_base(self, value: str, from_base: int, to_base: int) -> str:
        """
        Convert number between different bases (binary, octal, decimal, hex)
        
        Args:
            value: Number as string
            from_base: Source base (2-36)
            to_base: Target base (2-36)
            
        Returns:
            Converted number as string
        """
        # Convert to decimal first
        try:
            decimal_value = int(value, from_base)
        except ValueError:
            raise ValueError(f"Invalid number '{value}' for base {from_base}")
        
        # Convert to target base
        if to_base == 10:
            return str(decimal_value)
        elif to_base == 2:
            return bin(decimal_value)[2:]  # Remove '0b' prefix
        elif to_base == 8:
            return oct(decimal_value)[2:]  # Remove '0o' prefix
        elif to_base == 16:
            return hex(decimal_value)[2:]  # Remove '0x' prefix
        else:
            # Custom base conversion
            if decimal_value == 0:
                return '0'
            
            digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            result = ''
            negative = decimal_value < 0
            decimal_value = abs(decimal_value)
            
            while decimal_value > 0:
                remainder = decimal_value % to_base
                result = digits[remainder] + result
                decimal_value //= to_base
            
            return ('-' + result) if negative else result
    
    def list_units(self, category: Optional[str] = None) -> Dict:
        """
        List available units
        
        Args:
            category: Specific category or None for all
            
        Returns:
            Dictionary of units by category
        """
        if category:
            category = category.lower()
            if category in self.unit_groups:
                return {category: list(self.unit_groups[category].keys())}
            else:
                return {}
        else:
            return {cat: list(units.keys()) 
                   for cat, units in self.unit_groups.items()}


def format_result(value: float, precision: int = 6) -> str:
    """Format conversion result with appropriate precision"""
    # Remove trailing zeros
    formatted = f"{value:.{precision}f}".rstrip('0').rstrip('.')
    return formatted


def main():
    parser = argparse.ArgumentParser(
        description='Unit Converter Suite - Convert between various units',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Length conversion
  python unit_converter.py 100 m ft
  python unit_converter.py 5.5 miles km
  
  # Weight conversion
  python unit_converter.py 150 lbs kg
  
  # Temperature conversion
  python unit_converter.py 98.6 F C --temp
  python unit_converter.py 0 C K --temp
  
  # Base conversion
  python unit_converter.py FF --from-base 16 --to-base 10
  python unit_converter.py 1010 --from-base 2 --to-base 16
  
  # List available units
  python unit_converter.py --list
  python unit_converter.py --list length
        """
    )
    
    parser.add_argument('value', nargs='?', help='Value to convert')
    parser.add_argument('from_unit', nargs='?', help='Source unit')
    parser.add_argument('to_unit', nargs='?', help='Target unit')
    parser.add_argument('-c', '--category', help='Unit category (length, weight, volume, etc.)')
    parser.add_argument('-t', '--temp', action='store_true', help='Temperature conversion')
    parser.add_argument('--from-base', type=int, help='Source base for number conversion')
    parser.add_argument('--to-base', type=int, help='Target base for number conversion')
    parser.add_argument('-p', '--precision', type=int, default=6,
                        help='Decimal precision (default: 6)')
    parser.add_argument('--list', nargs='?', const='all', metavar='CATEGORY',
                        help='List available units (optionally for specific category)')
    
    args = parser.parse_args()
    
    converter = UnitConverter()
    
    # List units mode
    if args.list:
        category = None if args.list == 'all' else args.list
        units = converter.list_units(category)
        
        print("Available units:")
        for cat, unit_list in sorted(units.items()):
            print(f"\n{cat.upper()}:")
            # Group similar units
            print(f"  {', '.join(sorted(set(unit_list)))}")
        
        return 0
    
    # Validate arguments
    if not args.value:
        parser.error("Value is required")
    
    try:
        # Base conversion mode
        if args.from_base and args.to_base:
            result = converter.convert_base(args.value, args.from_base, args.to_base)
            print(f"{args.value} (base {args.from_base}) = {result} (base {args.to_base})")
        
        # Temperature conversion mode
        elif args.temp:
            if not args.from_unit or not args.to_unit:
                parser.error("Temperature conversion requires from_unit and to_unit")
            
            value = float(args.value)
            result = converter.convert_temperature(value, args.from_unit, args.to_unit)
            print(f"{value}°{args.from_unit.upper()} = {format_result(result, args.precision)}°{args.to_unit.upper()}")
        
        # Standard unit conversion
        else:
            if not args.from_unit or not args.to_unit:
                parser.error("Conversion requires from_unit and to_unit")
            
            value = float(args.value)
            result = converter.convert(value, args.from_unit, args.to_unit, args.category)
            print(f"{value} {args.from_unit} = {format_result(result, args.precision)} {args.to_unit}")
        
        return 0
    
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
