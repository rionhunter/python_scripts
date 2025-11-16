#!/usr/bin/env python3
"""
File Encryption and Decryption Tool
Encrypt and decrypt files using AES-256 encryption
"""

import argparse
import os
import sys
import getpass
import hashlib
from pathlib import Path

# Check for cryptography library
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derive an encryption key from a password using PBKDF2.
    
    Args:
        password: User password
        salt: Salt bytes
        
    Returns:
        Derived key bytes
    """
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_file(input_path: str, output_path: str, password: str) -> None:
    """
    Encrypt a file using AES-256.
    
    Args:
        input_path: Path to input file
        output_path: Path to output encrypted file
        password: Encryption password
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Generate a random salt
    salt = os.urandom(16)
    
    # Derive key from password
    key = derive_key_from_password(password, salt)
    
    # Create Fernet cipher with derived key (base64 encoded)
    import base64
    fernet_key = base64.urlsafe_b64encode(key)
    cipher = Fernet(fernet_key)
    
    # Read input file
    with open(input_path, 'rb') as f:
        plaintext = f.read()
    
    # Encrypt
    ciphertext = cipher.encrypt(plaintext)
    
    # Write salt + ciphertext to output file
    with open(output_path, 'wb') as f:
        f.write(salt)
        f.write(ciphertext)
    
    print(f"✓ Encrypted: {input_path} -> {output_path}")


def decrypt_file(input_path: str, output_path: str, password: str) -> None:
    """
    Decrypt a file encrypted with encrypt_file.
    
    Args:
        input_path: Path to encrypted file
        output_path: Path to output decrypted file
        password: Decryption password
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Read encrypted file
    with open(input_path, 'rb') as f:
        salt = f.read(16)
        ciphertext = f.read()
    
    # Derive key from password
    key = derive_key_from_password(password, salt)
    
    # Create Fernet cipher with derived key
    import base64
    fernet_key = base64.urlsafe_b64encode(key)
    cipher = Fernet(fernet_key)
    
    try:
        # Decrypt
        plaintext = cipher.decrypt(ciphertext)
        
        # Write decrypted data
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        print(f"✓ Decrypted: {input_path} -> {output_path}")
    
    except Exception as e:
        raise ValueError("Decryption failed. Incorrect password or corrupted file.")


def encrypt_directory(directory: str, password: str, recursive: bool = False) -> None:
    """
    Encrypt all files in a directory.
    
    Args:
        directory: Path to directory
        password: Encryption password
        recursive: Process subdirectories recursively
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")
    
    path = Path(directory)
    
    if recursive:
        files = path.rglob('*')
    else:
        files = path.glob('*')
    
    encrypted_count = 0
    for file_path in files:
        if file_path.is_file() and not file_path.name.endswith('.encrypted'):
            try:
                output_path = str(file_path) + '.encrypted'
                encrypt_file(str(file_path), output_path, password)
                encrypted_count += 1
            except Exception as e:
                print(f"Error encrypting {file_path}: {e}", file=sys.stderr)
    
    print(f"\n✓ Encrypted {encrypted_count} files")


def decrypt_directory(directory: str, password: str, recursive: bool = False) -> None:
    """
    Decrypt all .encrypted files in a directory.
    
    Args:
        directory: Path to directory
        password: Decryption password
        recursive: Process subdirectories recursively
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")
    
    path = Path(directory)
    
    if recursive:
        files = path.rglob('*.encrypted')
    else:
        files = path.glob('*.encrypted')
    
    decrypted_count = 0
    for file_path in files:
        if file_path.is_file():
            try:
                output_path = str(file_path)[:-10]  # Remove .encrypted extension
                decrypt_file(str(file_path), output_path, password)
                decrypted_count += 1
            except Exception as e:
                print(f"Error decrypting {file_path}: {e}", file=sys.stderr)
    
    print(f"\n✓ Decrypted {decrypted_count} files")


def main():
    if not CRYPTO_AVAILABLE:
        print("Error: 'cryptography' library not installed", file=sys.stderr)
        print("Install with: pip install cryptography", file=sys.stderr)
        return 1
    
    parser = argparse.ArgumentParser(
        description='Encrypt and decrypt files using AES-256',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -e file.txt -o file.txt.encrypted       # Encrypt a file
  %(prog)s -d file.txt.encrypted -o file.txt       # Decrypt a file
  %(prog)s -e document.pdf                         # Encrypt (auto output name)
  %(prog)s -d document.pdf.encrypted               # Decrypt (auto output name)
  %(prog)s -e /path/to/dir --directory             # Encrypt directory
  %(prog)s -d /path/to/dir --directory -r          # Decrypt directory recursively
  
Note: You will be prompted for a password. Keep it safe!
      Encrypted files use AES-256 with PBKDF2 key derivation.
        """
    )
    
    parser.add_argument('-e', '--encrypt', metavar='PATH',
                        help='Path to file or directory to encrypt')
    parser.add_argument('-d', '--decrypt', metavar='PATH',
                        help='Path to file or directory to decrypt')
    parser.add_argument('-o', '--output', metavar='PATH',
                        help='Output path (default: auto-generated)')
    parser.add_argument('-p', '--password', metavar='PASS',
                        help='Password (not recommended, use prompt instead)')
    parser.add_argument('--directory', action='store_true',
                        help='Process entire directory')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Process directories recursively')
    
    args = parser.parse_args()
    
    if not args.encrypt and not args.decrypt:
        parser.print_help()
        return 1
    
    if args.encrypt and args.decrypt:
        print("Error: Cannot use both -e and -d options", file=sys.stderr)
        return 1
    
    try:
        # Get password
        if args.password:
            password = args.password
        else:
            password = getpass.getpass("Enter password: ")
            if args.encrypt:
                confirm = getpass.getpass("Confirm password: ")
                if password != confirm:
                    print("Error: Passwords do not match", file=sys.stderr)
                    return 1
        
        if not password:
            print("Error: Password cannot be empty", file=sys.stderr)
            return 1
        
        # Perform operation
        if args.encrypt:
            input_path = args.encrypt
            
            if args.directory:
                encrypt_directory(input_path, password, args.recursive)
            else:
                output_path = args.output or (input_path + '.encrypted')
                encrypt_file(input_path, output_path, password)
        
        elif args.decrypt:
            input_path = args.decrypt
            
            if args.directory:
                decrypt_directory(input_path, password, args.recursive)
            else:
                if args.output:
                    output_path = args.output
                elif input_path.endswith('.encrypted'):
                    output_path = input_path[:-10]
                else:
                    output_path = input_path + '.decrypted'
                
                decrypt_file(input_path, output_path, password)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
