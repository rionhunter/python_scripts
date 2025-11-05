#!/usr/bin/env python3
"""
Regex Tools Suite
Test, build, and manage regular expressions with explanations
"""

import argparse
import sys
import re
from typing import List, Dict, Optional, Tuple
import json
from pathlib import Path


class RegexTester:
    """Test regular expressions against text"""
    
    def __init__(self, pattern: str, flags: int = 0):
        """
        Initialize regex tester
        
        Args:
            pattern: Regular expression pattern
            flags: Regex flags (re.IGNORECASE, etc.)
        """
        self.pattern = pattern
        self.flags = flags
        try:
            self.regex = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
    
    def test(self, text: str) -> Dict:
        """
        Test regex against text
        
        Returns:
            Dictionary with match information
        """
        results = {
            'pattern': self.pattern,
            'text': text,
            'matches': [],
            'match_count': 0,
            'has_match': False
        }
        
        # Find all matches
        for match in self.regex.finditer(text):
            match_info = {
                'match': match.group(0),
                'start': match.start(),
                'end': match.end(),
                'groups': match.groups(),
                'groupdict': match.groupdict()
            }
            results['matches'].append(match_info)
        
        results['match_count'] = len(results['matches'])
        results['has_match'] = results['match_count'] > 0
        
        return results
    
    def search(self, text: str) -> Optional[re.Match]:
        """Find first match"""
        return self.regex.search(text)
    
    def findall(self, text: str) -> List[str]:
        """Find all matches"""
        return self.regex.findall(text)
    
    def split(self, text: str) -> List[str]:
        """Split text by pattern"""
        return self.regex.split(text)
    
    def sub(self, replacement: str, text: str, count: int = 0) -> str:
        """Replace matches with replacement"""
        return self.regex.sub(replacement, text, count=count)
    
    def highlight_matches(self, text: str, color: bool = False) -> str:
        """Highlight matches in text"""
        if not color:
            # Simple brackets
            offset = 0
            result = text
            for match in self.regex.finditer(text):
                start = match.start() + offset
                end = match.end() + offset
                result = result[:start] + '[' + result[start:end] + ']' + result[end:]
                offset += 2
            return result
        else:
            # ANSI color codes
            offset = 0
            result = text
            for match in self.regex.finditer(text):
                start = match.start() + offset
                end = match.end() + offset
                highlighted = f"\033[1;31m{result[start:end]}\033[0m"  # Red bold
                result = result[:start] + highlighted + result[end:]
                offset += len(highlighted) - (end - start)
            return result


class RegexLibrary:
    """Common regex patterns library"""
    
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'url': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
        'phone_us': r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        'ip_v4': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        'ip_v6': r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}',
        'date_iso': r'\d{4}-\d{2}-\d{2}',
        'date_us': r'\d{1,2}/\d{1,2}/\d{4}',
        'time_24h': r'([01]?[0-9]|2[0-3]):[0-5][0-9]',
        'time_12h': r'(1[0-2]|0?[1-9]):([0-5][0-9])\s?(AM|PM|am|pm)',
        'hex_color': r'#(?:[0-9a-fA-F]{3}){1,2}',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'zip_code': r'\b\d{5}(?:-\d{4})?\b',
        'mac_address': r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})',
        'uuid': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
        'username': r'^[a-zA-Z0-9_-]{3,16}$',
        'password_strong': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
        'html_tag': r'<([a-z]+)([^>]*)>.*?</\1>',
        'markdown_link': r'\[([^\]]+)\]\(([^\)]+)\)',
        'number_integer': r'-?\d+',
        'number_decimal': r'-?\d+\.?\d*',
        'word': r'\b\w+\b',
        'whitespace': r'\s+',
        'python_variable': r'[a-zA-Z_][a-zA-Z0-9_]*',
        'json_string': r'"(?:[^"\\]|\\.)*"',
    }
    
    DESCRIPTIONS = {
        'email': 'Email address',
        'url': 'HTTP/HTTPS URL',
        'phone_us': 'US phone number',
        'ip_v4': 'IPv4 address',
        'ip_v6': 'IPv6 address',
        'date_iso': 'ISO date format (YYYY-MM-DD)',
        'date_us': 'US date format (MM/DD/YYYY)',
        'time_24h': '24-hour time format',
        'time_12h': '12-hour time format with AM/PM',
        'hex_color': 'Hexadecimal color code',
        'credit_card': 'Credit card number',
        'ssn': 'Social Security Number',
        'zip_code': 'US ZIP code',
        'mac_address': 'MAC address',
        'uuid': 'UUID/GUID',
        'username': 'Username (3-16 chars, alphanumeric, dash, underscore)',
        'password_strong': 'Strong password (min 8 chars, upper, lower, digit, special)',
        'html_tag': 'HTML tag with content',
        'markdown_link': 'Markdown link',
        'number_integer': 'Integer number',
        'number_decimal': 'Decimal number',
        'word': 'Word boundary',
        'whitespace': 'Whitespace characters',
        'python_variable': 'Python variable name',
        'json_string': 'JSON string',
    }
    
    @classmethod
    def get_pattern(cls, name: str) -> Optional[str]:
        """Get pattern by name"""
        return cls.PATTERNS.get(name)
    
    @classmethod
    def get_description(cls, name: str) -> Optional[str]:
        """Get pattern description"""
        return cls.DESCRIPTIONS.get(name)
    
    @classmethod
    def list_patterns(cls) -> List[Tuple[str, str, str]]:
        """List all patterns with descriptions"""
        return [(name, pattern, cls.DESCRIPTIONS.get(name, ''))
                for name, pattern in cls.PATTERNS.items()]
    
    @classmethod
    def search(cls, query: str) -> List[Tuple[str, str, str]]:
        """Search patterns by name or description"""
        query = query.lower()
        results = []
        for name, pattern in cls.PATTERNS.items():
            desc = cls.DESCRIPTIONS.get(name, '').lower()
            if query in name.lower() or query in desc:
                results.append((name, pattern, cls.DESCRIPTIONS.get(name, '')))
        return results


class RegexExplainer:
    """Explain regex patterns in plain English"""
    
    EXPLANATIONS = {
        r'\d': 'digit (0-9)',
        r'\D': 'non-digit',
        r'\w': 'word character (a-z, A-Z, 0-9, _)',
        r'\W': 'non-word character',
        r'\s': 'whitespace',
        r'\S': 'non-whitespace',
        r'.': 'any character (except newline)',
        r'^': 'start of string',
        r'$': 'end of string',
        r'\b': 'word boundary',
        r'\B': 'non-word boundary',
        r'*': 'zero or more times',
        r'+': 'one or more times',
        r'?': 'zero or one time (optional)',
        r'{n}': 'exactly n times',
        r'{n,}': 'n or more times',
        r'{n,m}': 'between n and m times',
        r'[abc]': 'any of a, b, or c',
        r'[^abc]': 'not a, b, or c',
        r'[a-z]': 'any lowercase letter',
        r'[A-Z]': 'any uppercase letter',
        r'[0-9]': 'any digit',
        r'(...)': 'capture group',
        r'(?:...)': 'non-capturing group',
        r'(?=...)': 'positive lookahead',
        r'(?!...)': 'negative lookahead',
        r'(?<=...)': 'positive lookbehind',
        r'(?<!...)': 'negative lookbehind',
        r'|': 'OR operator',
        r'\\': 'escape character',
    }
    
    @classmethod
    def explain(cls, pattern: str) -> str:
        """Provide basic explanation of pattern"""
        explanations = []
        
        # Look for common patterns
        if r'\d' in pattern:
            explanations.append("- Matches digits")
        if r'\w' in pattern:
            explanations.append("- Matches word characters")
        if r'\s' in pattern:
            explanations.append("- Matches whitespace")
        if '+' in pattern:
            explanations.append("- Uses '+' (one or more repetitions)")
        if '*' in pattern:
            explanations.append("- Uses '*' (zero or more repetitions)")
        if '^' in pattern:
            explanations.append("- Anchored to start of string (^)")
        if '$' in pattern:
            explanations.append("- Anchored to end of string ($)")
        if '(' in pattern:
            explanations.append("- Contains capture groups ()")
        if '[' in pattern:
            explanations.append("- Contains character class []")
        
        if not explanations:
            explanations.append("- Simple pattern")
        
        return '\n'.join(explanations)


def main():
    parser = argparse.ArgumentParser(
        description='Regex Tools Suite - Test, build, and manage regular expressions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test regex pattern
  python regex_tool.py test "\d+" "abc 123 def 456"
  
  # Test with highlighting
  python regex_tool.py test "\w+@\w+\.\w+" "Contact: user@example.com" --highlight
  
  # Replace matches
  python regex_tool.py replace "\d+" "NUMBER" "I have 5 apples and 3 oranges"
  
  # List common patterns
  python regex_tool.py library
  
  # Search pattern library
  python regex_tool.py library --search email
  
  # Use library pattern
  python regex_tool.py test --pattern email "Contact me at user@example.com"
  
  # Explain pattern
  python regex_tool.py explain "\d{3}-\d{2}-\d{4}"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test regex pattern')
    test_parser.add_argument('pattern', nargs='?', help='Regex pattern')
    test_parser.add_argument('text', nargs='?', help='Text to test against')
    test_parser.add_argument('--pattern', dest='pattern_name', help='Use pattern from library')
    test_parser.add_argument('-i', '--ignore-case', action='store_true',
                            help='Ignore case')
    test_parser.add_argument('-m', '--multiline', action='store_true',
                            help='Multiline mode')
    test_parser.add_argument('--highlight', action='store_true',
                            help='Highlight matches')
    test_parser.add_argument('--color', action='store_true',
                            help='Use color highlighting')
    test_parser.add_argument('--json', action='store_true',
                            help='Output as JSON')
    
    # Replace command
    replace_parser = subparsers.add_parser('replace', help='Replace matches')
    replace_parser.add_argument('pattern', help='Regex pattern')
    replace_parser.add_argument('replacement', help='Replacement text')
    replace_parser.add_argument('text', help='Text to process')
    replace_parser.add_argument('-i', '--ignore-case', action='store_true')
    replace_parser.add_argument('--count', type=int, default=0,
                               help='Max replacements (0 = all)')
    
    # Library command
    lib_parser = subparsers.add_parser('library', help='Browse pattern library')
    lib_parser.add_argument('--search', help='Search patterns')
    lib_parser.add_argument('--get', help='Get specific pattern')
    
    # Explain command
    explain_parser = subparsers.add_parser('explain', help='Explain regex pattern')
    explain_parser.add_argument('pattern', help='Regex pattern to explain')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Test command
        if args.command == 'test':
            # Get pattern
            if args.pattern_name:
                pattern = RegexLibrary.get_pattern(args.pattern_name)
                if not pattern:
                    print(f"Pattern '{args.pattern_name}' not found in library")
                    return 1
            elif args.pattern:
                pattern = args.pattern
            else:
                print("Error: pattern required")
                return 1
            
            if not args.text:
                print("Error: text required")
                return 1
            
            # Set flags
            flags = 0
            if args.ignore_case:
                flags |= re.IGNORECASE
            if args.multiline:
                flags |= re.MULTILINE
            
            # Test
            tester = RegexTester(pattern, flags)
            results = tester.test(args.text)
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"Pattern: {pattern}")
                print(f"Text: {args.text}")
                print(f"\nMatches: {results['match_count']}")
                
                if results['has_match']:
                    if args.highlight:
                        print(f"\nHighlighted:\n{tester.highlight_matches(args.text, args.color)}")
                    else:
                        for i, match in enumerate(results['matches'], 1):
                            print(f"\nMatch #{i}:")
                            print(f"  Text: {match['match']}")
                            print(f"  Position: {match['start']}-{match['end']}")
                            if match['groups']:
                                print(f"  Groups: {match['groups']}")
                else:
                    print("No matches found")
        
        # Replace command
        elif args.command == 'replace':
            flags = re.IGNORECASE if args.ignore_case else 0
            tester = RegexTester(args.pattern, flags)
            result = tester.sub(args.replacement, args.text, count=args.count)
            print(result)
        
        # Library command
        elif args.command == 'library':
            if args.get:
                pattern = RegexLibrary.get_pattern(args.get)
                desc = RegexLibrary.get_description(args.get)
                if pattern:
                    print(f"Name: {args.get}")
                    print(f"Description: {desc}")
                    print(f"Pattern: {pattern}")
                else:
                    print(f"Pattern '{args.get}' not found")
            
            elif args.search:
                results = RegexLibrary.search(args.search)
                if results:
                    print(f"Found {len(results)} pattern(s):\n")
                    for name, pattern, desc in results:
                        print(f"{name}:")
                        print(f"  Description: {desc}")
                        print(f"  Pattern: {pattern}\n")
                else:
                    print(f"No patterns found for: {args.search}")
            
            else:
                patterns = RegexLibrary.list_patterns()
                print("Available patterns:\n")
                for name, pattern, desc in patterns:
                    print(f"{name}:")
                    print(f"  {desc}")
                    print(f"  Pattern: {pattern}\n")
        
        # Explain command
        elif args.command == 'explain':
            print(f"Pattern: {args.pattern}")
            print("\nExplanation:")
            print(RegexExplainer.explain(args.pattern))
        
        return 0
    
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
