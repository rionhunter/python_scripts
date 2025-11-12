#!/usr/bin/env python3
"""
Password Generator and Strength Checker
Generate secure passwords and check password strength
"""

import argparse
import random
import string
import sys
import re
from typing import Tuple, Dict


def generate_password(length: int = 16, 
                     use_uppercase: bool = True,
                     use_lowercase: bool = True,
                     use_digits: bool = True,
                     use_special: bool = True,
                     exclude_chars: str = '') -> str:
    """
    Generate a random password.
    
    Args:
        length: Password length
        use_uppercase: Include uppercase letters
        use_lowercase: Include lowercase letters
        use_digits: Include digits
        use_special: Include special characters
        exclude_chars: Characters to exclude
        
    Returns:
        Generated password string
    """
    if length < 4:
        raise ValueError("Password length must be at least 4")
    
    # Build character pool
    charset = ''
    if use_uppercase:
        charset += string.ascii_uppercase
    if use_lowercase:
        charset += string.ascii_lowercase
    if use_digits:
        charset += string.digits
    if use_special:
        charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not charset:
        raise ValueError("At least one character type must be enabled")
    
    # Remove excluded characters
    charset = ''.join(c for c in charset if c not in exclude_chars)
    
    if not charset:
        raise ValueError("No valid characters left after exclusions")
    
    # Generate password ensuring at least one character from each enabled type
    password_chars = []
    
    if use_uppercase:
        password_chars.append(random.choice([c for c in string.ascii_uppercase if c not in exclude_chars]))
    if use_lowercase:
        password_chars.append(random.choice([c for c in string.ascii_lowercase if c not in exclude_chars]))
    if use_digits:
        password_chars.append(random.choice([c for c in string.digits if c not in exclude_chars]))
    if use_special:
        special_chars = [c for c in "!@#$%^&*()_+-=[]{}|;:,.<>?" if c not in exclude_chars]
        if special_chars:
            password_chars.append(random.choice(special_chars))
    
    # Fill remaining length with random characters
    remaining = length - len(password_chars)
    password_chars.extend(random.choices(charset, k=remaining))
    
    # Shuffle to avoid predictable patterns
    random.shuffle(password_chars)
    
    return ''.join(password_chars)


def check_password_strength(password: str) -> Tuple[str, int, Dict[str, bool]]:
    """
    Check password strength.
    
    Args:
        password: Password to check
        
    Returns:
        Tuple of (strength_label, score, criteria_dict)
    """
    score = 0
    criteria = {
        'length': False,
        'uppercase': False,
        'lowercase': False,
        'digits': False,
        'special': False,
        'no_common': False,
        'no_repeated': False,
        'no_sequential': False
    }
    
    # Length check
    length = len(password)
    if length >= 8:
        criteria['length'] = True
        score += 20
    if length >= 12:
        score += 10
    if length >= 16:
        score += 10
    
    # Character type checks
    if re.search(r'[A-Z]', password):
        criteria['uppercase'] = True
        score += 10
    
    if re.search(r'[a-z]', password):
        criteria['lowercase'] = True
        score += 10
    
    if re.search(r'\d', password):
        criteria['digits'] = True
        score += 10
    
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        criteria['special'] = True
        score += 15
    
    # Common password patterns (basic check)
    common_patterns = [
        'password', '123456', 'qwerty', 'abc123', 'letmein',
        'monkey', 'dragon', 'master', 'sunshine', 'princess'
    ]
    is_common = any(pattern in password.lower() for pattern in common_patterns)
    if not is_common:
        criteria['no_common'] = True
        score += 10
    
    # Repeated characters check
    has_repeated = re.search(r'(.)\1{2,}', password)
    if not has_repeated:
        criteria['no_repeated'] = True
        score += 5
    
    # Sequential characters check (basic)
    has_sequential = False
    for i in range(len(password) - 2):
        if password[i:i+3].lower() in 'abcdefghijklmnopqrstuvwxyz':
            has_sequential = True
            break
        if password[i:i+3] in '0123456789':
            has_sequential = True
            break
    if not has_sequential:
        criteria['no_sequential'] = True
        score += 5
    
    # Character diversity bonus
    char_types = sum([
        bool(re.search(r'[A-Z]', password)),
        bool(re.search(r'[a-z]', password)),
        bool(re.search(r'\d', password)),
        bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password))
    ])
    if char_types >= 3:
        score += 5
    
    # Determine strength label
    if score >= 80:
        strength = 'Very Strong'
    elif score >= 60:
        strength = 'Strong'
    elif score >= 40:
        strength = 'Moderate'
    elif score >= 20:
        strength = 'Weak'
    else:
        strength = 'Very Weak'
    
    return strength, score, criteria


def generate_memorable_password(words: int = 4, separator: str = '-',
                                capitalize: bool = True, 
                                add_number: bool = True) -> str:
    """
    Generate a memorable passphrase using random words.
    
    Args:
        words: Number of words
        separator: Separator between words
        capitalize: Capitalize first letter of each word
        add_number: Add a number at the end
        
    Returns:
        Generated passphrase
    """
    # Simple word list (in practice, you'd use a larger word list file)
    word_list = [
        'apple', 'banana', 'cherry', 'dragon', 'eagle', 'forest', 'garden',
        'happy', 'island', 'jungle', 'knight', 'lemon', 'mountain', 'ocean',
        'palace', 'queen', 'river', 'sunset', 'tiger', 'universe', 'valley',
        'wizard', 'yellow', 'zebra', 'cloud', 'diamond', 'emerald', 'flame',
        'glacier', 'horizon', 'crystal', 'thunder', 'rainbow', 'phoenix',
        'shadow', 'meadow', 'cascade', 'nebula', 'aurora', 'comet'
    ]
    
    selected_words = random.sample(word_list, min(words, len(word_list)))
    
    if capitalize:
        selected_words = [word.capitalize() for word in selected_words]
    
    passphrase = separator.join(selected_words)
    
    if add_number:
        passphrase += str(random.randint(10, 99))
    
    return passphrase


def main():
    parser = argparse.ArgumentParser(
        description='Password generator and strength checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Generate 16-char password
  %(prog)s -l 20                              # Generate 20-char password
  %(prog)s -l 12 --no-special                 # No special characters
  %(prog)s --memorable                        # Generate memorable passphrase
  %(prog)s -n 5                               # Generate 5 passwords
  %(prog)s -c "MyPassword123!"                # Check password strength
        """
    )
    
    parser.add_argument('-l', '--length', type=int, default=16,
                        help='Password length (default: 16)')
    parser.add_argument('-n', '--count', type=int, default=1,
                        help='Number of passwords to generate (default: 1)')
    parser.add_argument('--no-uppercase', action='store_true',
                        help='Exclude uppercase letters')
    parser.add_argument('--no-lowercase', action='store_true',
                        help='Exclude lowercase letters')
    parser.add_argument('--no-digits', action='store_true',
                        help='Exclude digits')
    parser.add_argument('--no-special', action='store_true',
                        help='Exclude special characters')
    parser.add_argument('--exclude', default='',
                        help='Characters to exclude from password')
    parser.add_argument('--memorable', action='store_true',
                        help='Generate memorable passphrase')
    parser.add_argument('-c', '--check', metavar='PASSWORD',
                        help='Check password strength')
    
    args = parser.parse_args()
    
    try:
        if args.check:
            # Check password strength
            strength, score, criteria = check_password_strength(args.check)
            
            print(f"\nPassword Strength: {strength} ({score}/100)")
            print("\nCriteria:")
            print(f"  {'✓' if criteria['length'] else '✗'} Length ≥ 8 characters")
            print(f"  {'✓' if criteria['uppercase'] else '✗'} Contains uppercase letters")
            print(f"  {'✓' if criteria['lowercase'] else '✗'} Contains lowercase letters")
            print(f"  {'✓' if criteria['digits'] else '✗'} Contains digits")
            print(f"  {'✓' if criteria['special'] else '✗'} Contains special characters")
            print(f"  {'✓' if criteria['no_common'] else '✗'} Not a common password")
            print(f"  {'✓' if criteria['no_repeated'] else '✗'} No repeated characters (3+)")
            print(f"  {'✓' if criteria['no_sequential'] else '✗'} No sequential characters")
            
            return 0
        
        # Generate passwords
        for i in range(args.count):
            if args.memorable:
                password = generate_memorable_password()
            else:
                password = generate_password(
                    length=args.length,
                    use_uppercase=not args.no_uppercase,
                    use_lowercase=not args.no_lowercase,
                    use_digits=not args.no_digits,
                    use_special=not args.no_special,
                    exclude_chars=args.exclude
                )
            
            print(password)
            
            # Show strength for single password generation
            if args.count == 1:
                strength, score, _ = check_password_strength(password)
                print(f"Strength: {strength} ({score}/100)")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
