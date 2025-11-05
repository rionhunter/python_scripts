#!/usr/bin/env python3
"""
Data Generator Suite
Generate UUID, Lorem Ipsum, Random Data, and Fake Data for testing
"""

import argparse
import sys
import uuid
import random
import string
from typing import List, Optional
from datetime import datetime, timedelta

# Faker is optional
FAKER_AVAILABLE = False
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    pass


class DataGenerator:
    """Generate various types of test data"""
    
    # Lorem Ipsum text
    LOREM_WORDS = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", 
        "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore",
        "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam",
        "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "aliquip",
        "ex", "ea", "commodo", "consequat", "duis", "aute", "irure", "in",
        "reprehenderit", "voluptate", "velit", "esse", "cillum", "fugiat", "nulla",
        "pariatur", "excepteur", "sint", "occaecat", "cupidatat", "non", "proident",
        "sunt", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id",
        "est", "laborum"
    ]
    
    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", 
        "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan",
        "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher",
        "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret",
        "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul",
        "Emily", "Andrew", "Donna", "Joshua", "Michelle"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
        "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
        "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
    ]
    
    STREET_NAMES = [
        "Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington", "Lake",
        "Hill", "Park", "River", "First", "Second", "Third", "Fourth", "Fifth",
        "Walnut", "Sunset", "Forest", "Spring", "Highland", "Church", "Valley",
        "Market", "Madison", "Adams", "Jefferson", "Franklin", "Lincoln"
    ]
    
    STREET_TYPES = ["St", "Ave", "Blvd", "Rd", "Dr", "Ln", "Ct", "Way", "Pl"]
    
    CITIES = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
        "Seattle", "Denver", "Washington", "Boston", "Nashville", "Detroit",
        "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore", "Milwaukee"
    ]
    
    STATES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
        "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
        "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
        "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
        "WI", "WY"
    ]
    
    DOMAINS = [
        "example.com", "test.com", "mail.com", "email.com", "demo.com",
        "sample.org", "fake.net", "dummy.io", "placeholder.dev"
    ]
    
    COMPANIES = [
        "Tech Corp", "Data Systems", "Global Solutions", "Innovation Labs",
        "Digital Services", "Cloud Computing Inc", "Software Partners",
        "Network Solutions", "Enterprise Systems", "Smart Technologies"
    ]
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for reproducibility"""
        if seed is not None:
            random.seed(seed)
        
        self.faker = None
        if FAKER_AVAILABLE:
            self.faker = Faker()
            if seed is not None:
                Faker.seed(seed)
    
    def generate_uuid(self, version: int = 4, count: int = 1) -> List[str]:
        """Generate UUID(s)"""
        results = []
        for _ in range(count):
            if version == 1:
                results.append(str(uuid.uuid1()))
            elif version == 4:
                results.append(str(uuid.uuid4()))
            else:
                raise ValueError(f"Unsupported UUID version: {version}")
        return results
    
    def generate_lorem_ipsum(self, words: int = 50, paragraphs: int = 1) -> str:
        """Generate Lorem Ipsum text"""
        result = []
        for _ in range(paragraphs):
            para_words = random.choices(self.LOREM_WORDS, k=words)
            # Capitalize first word
            para_words[0] = para_words[0].capitalize()
            paragraph = ' '.join(para_words) + '.'
            result.append(paragraph)
        
        return '\n\n'.join(result)
    
    def generate_name(self, count: int = 1) -> List[str]:
        """Generate random full names"""
        return [f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}"
                for _ in range(count)]
    
    def generate_email(self, count: int = 1) -> List[str]:
        """Generate random email addresses"""
        emails = []
        for _ in range(count):
            first = random.choice(self.FIRST_NAMES).lower()
            last = random.choice(self.LAST_NAMES).lower()
            domain = random.choice(self.DOMAINS)
            separator = random.choice(['.', '_', ''])
            email = f"{first}{separator}{last}@{domain}"
            emails.append(email)
        return emails
    
    def generate_phone(self, count: int = 1, format: str = 'us') -> List[str]:
        """Generate random phone numbers"""
        phones = []
        for _ in range(count):
            if format == 'us':
                area = random.randint(200, 999)
                prefix = random.randint(200, 999)
                line = random.randint(1000, 9999)
                phones.append(f"({area}) {prefix}-{line}")
            else:
                # International format
                phones.append(f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}")
        return phones
    
    def generate_address(self, count: int = 1) -> List[str]:
        """Generate random addresses"""
        addresses = []
        for _ in range(count):
            number = random.randint(1, 9999)
            street = random.choice(self.STREET_NAMES)
            street_type = random.choice(self.STREET_TYPES)
            city = random.choice(self.CITIES)
            state = random.choice(self.STATES)
            zip_code = random.randint(10000, 99999)
            
            addresses.append(f"{number} {street} {street_type}, {city}, {state} {zip_code}")
        return addresses
    
    def generate_company(self, count: int = 1) -> List[str]:
        """Generate random company names"""
        return [random.choice(self.COMPANIES) for _ in range(count)]
    
    def generate_username(self, count: int = 1) -> List[str]:
        """Generate random usernames"""
        usernames = []
        for _ in range(count):
            first = random.choice(self.FIRST_NAMES).lower()
            last = random.choice(self.LAST_NAMES).lower()
            num = random.randint(1, 999)
            pattern = random.choice([
                f"{first}{last}",
                f"{first}.{last}",
                f"{first}_{last}",
                f"{first}{num}",
                f"{first}{last}{num}"
            ])
            usernames.append(pattern)
        return usernames
    
    def generate_password(self, length: int = 12, count: int = 1, 
                         include_special: bool = True) -> List[str]:
        """Generate random passwords"""
        passwords = []
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        for _ in range(count):
            password = ''.join(random.choice(chars) for _ in range(length))
            passwords.append(password)
        return passwords
    
    def generate_date(self, start_date: Optional[str] = None, 
                     end_date: Optional[str] = None, count: int = 1) -> List[str]:
        """Generate random dates"""
        if start_date is None:
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.fromisoformat(start_date)
        
        if end_date is None:
            end = datetime.now()
        else:
            end = datetime.fromisoformat(end_date)
        
        dates = []
        delta = (end - start).days
        for _ in range(count):
            random_days = random.randint(0, delta)
            random_date = start + timedelta(days=random_days)
            dates.append(random_date.strftime('%Y-%m-%d'))
        return dates
    
    def generate_number(self, min_val: float = 0, max_val: float = 100,
                       decimals: int = 0, count: int = 1) -> List[float]:
        """Generate random numbers"""
        numbers = []
        for _ in range(count):
            num = random.uniform(min_val, max_val)
            if decimals == 0:
                numbers.append(int(num))
            else:
                numbers.append(round(num, decimals))
        return numbers
    
    def generate_color_hex(self, count: int = 1) -> List[str]:
        """Generate random hex color codes"""
        return [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(count)]
    
    def generate_ip_address(self, count: int = 1, version: int = 4) -> List[str]:
        """Generate random IP addresses"""
        ips = []
        for _ in range(count):
            if version == 4:
                ip = '.'.join(str(random.randint(0, 255)) for _ in range(4))
            else:  # IPv6
                ip = ':'.join(f'{random.randint(0, 65535):x}' for _ in range(8))
            ips.append(ip)
        return ips
    
    def generate_mac_address(self, count: int = 1) -> List[str]:
        """Generate random MAC addresses"""
        return [':'.join(f'{random.randint(0, 255):02x}' for _ in range(6))
                for _ in range(count)]
    
    def generate_credit_card(self, count: int = 1) -> List[str]:
        """Generate fake credit card numbers (Luhn algorithm compliant)"""
        cards = []
        for _ in range(count):
            # Generate 15 digits
            digits = [random.randint(0, 9) for _ in range(15)]
            
            # Calculate Luhn check digit
            checksum = 0
            for i, digit in enumerate(digits):
                if i % 2 == 0:
                    doubled = digit * 2
                    checksum += doubled if doubled < 10 else doubled - 9
                else:
                    checksum += digit
            
            check_digit = (10 - (checksum % 10)) % 10
            digits.append(check_digit)
            
            # Format as credit card
            card = ''.join(map(str, digits))
            formatted = f"{card[0:4]} {card[4:8]} {card[8:12]} {card[12:16]}"
            cards.append(formatted)
        
        return cards
    
    def generate_json_dataset(self, count: int = 10) -> List[dict]:
        """Generate complete fake dataset with multiple fields"""
        dataset = []
        for i in range(count):
            record = {
                'id': i + 1,
                'uuid': self.generate_uuid()[0],
                'name': self.generate_name()[0],
                'email': self.generate_email()[0],
                'phone': self.generate_phone()[0],
                'address': self.generate_address()[0],
                'company': self.generate_company()[0],
                'username': self.generate_username()[0],
                'created_date': self.generate_date()[0],
                'is_active': random.choice([True, False])
            }
            dataset.append(record)
        return dataset


def main():
    parser = argparse.ArgumentParser(
        description='Data Generator - Generate test data, UUIDs, Lorem Ipsum, and more',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate UUIDs
  python data_generator.py uuid -n 5
  
  # Generate Lorem Ipsum (100 words, 3 paragraphs)
  python data_generator.py lorem --words 100 --paragraphs 3
  
  # Generate names
  python data_generator.py name -n 10
  
  # Generate email addresses
  python data_generator.py email -n 5
  
  # Generate complete dataset (JSON)
  python data_generator.py dataset -n 20 -o data.json
  
  # Generate passwords
  python data_generator.py password -n 5 --length 16
  
  # Generate phone numbers
  python data_generator.py phone -n 10
        """
    )
    
    parser.add_argument('type', choices=[
        'uuid', 'lorem', 'name', 'email', 'phone', 'address', 'company',
        'username', 'password', 'date', 'number', 'color', 'ip', 'mac',
        'credit-card', 'dataset'
    ], help='Type of data to generate')
    
    parser.add_argument('-n', '--count', type=int, default=1,
                        help='Number of items to generate (default: 1)')
    parser.add_argument('-o', '--output', help='Output file (JSON format)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    
    # Lorem Ipsum options
    parser.add_argument('--words', type=int, default=50,
                        help='Words per paragraph for Lorem Ipsum (default: 50)')
    parser.add_argument('--paragraphs', type=int, default=1,
                        help='Number of paragraphs for Lorem Ipsum (default: 1)')
    
    # Password options
    parser.add_argument('--length', type=int, default=12,
                        help='Password length (default: 12)')
    parser.add_argument('--no-special', action='store_true',
                        help='Exclude special characters from passwords')
    
    # Number options
    parser.add_argument('--min', type=float, default=0,
                        help='Minimum value for numbers (default: 0)')
    parser.add_argument('--max', type=float, default=100,
                        help='Maximum value for numbers (default: 100)')
    parser.add_argument('--decimals', type=int, default=0,
                        help='Decimal places for numbers (default: 0)')
    
    # Date options
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    # IP version
    parser.add_argument('--ipv6', action='store_true', help='Generate IPv6 addresses')
    
    args = parser.parse_args()
    
    # Create generator
    gen = DataGenerator(seed=args.seed)
    
    # Generate data
    if args.type == 'uuid':
        results = gen.generate_uuid(count=args.count)
    elif args.type == 'lorem':
        results = [gen.generate_lorem_ipsum(words=args.words, paragraphs=args.paragraphs)]
    elif args.type == 'name':
        results = gen.generate_name(count=args.count)
    elif args.type == 'email':
        results = gen.generate_email(count=args.count)
    elif args.type == 'phone':
        results = gen.generate_phone(count=args.count)
    elif args.type == 'address':
        results = gen.generate_address(count=args.count)
    elif args.type == 'company':
        results = gen.generate_company(count=args.count)
    elif args.type == 'username':
        results = gen.generate_username(count=args.count)
    elif args.type == 'password':
        results = gen.generate_password(
            length=args.length, count=args.count, 
            include_special=not args.no_special
        )
    elif args.type == 'date':
        results = gen.generate_date(
            start_date=args.start_date, end_date=args.end_date, count=args.count
        )
    elif args.type == 'number':
        results = gen.generate_number(
            min_val=args.min, max_val=args.max,
            decimals=args.decimals, count=args.count
        )
    elif args.type == 'color':
        results = gen.generate_color_hex(count=args.count)
    elif args.type == 'ip':
        version = 6 if args.ipv6 else 4
        results = gen.generate_ip_address(count=args.count, version=version)
    elif args.type == 'mac':
        results = gen.generate_mac_address(count=args.count)
    elif args.type == 'credit-card':
        results = gen.generate_credit_card(count=args.count)
    elif args.type == 'dataset':
        results = gen.generate_json_dataset(count=args.count)
    else:
        print(f"Unknown type: {args.type}")
        return 1
    
    # Output results
    if args.output:
        import json
        from pathlib import Path
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Generated {len(results) if isinstance(results, list) else 1} items -> {output_path}")
    else:
        if isinstance(results, list):
            for item in results:
                print(item)
        else:
            print(results)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
