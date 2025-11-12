#!/usr/bin/env python3
"""
File Hash Calculator
Calculate and verify file hashes using various algorithms (MD5, SHA-1, SHA-256, SHA-512, etc.)
"""

import hashlib
import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, List


def calculate_hash(filepath: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file using specified algorithm.
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256, sha512, sha224, sha384)
        
    Returns:
        Hexadecimal hash string
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Get hash object
    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    # Read file in chunks to handle large files
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def calculate_multiple_hashes(filepath: str, algorithms: List[str]) -> Dict[str, str]:
    """
    Calculate multiple hashes for a file at once.
    
    Args:
        filepath: Path to file
        algorithms: List of hash algorithms
        
    Returns:
        Dictionary mapping algorithm names to hash values
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Initialize hash objects
    hash_objects = {}
    for algo in algorithms:
        try:
            hash_objects[algo] = hashlib.new(algo)
        except ValueError:
            print(f"Warning: Unsupported algorithm '{algo}', skipping...", file=sys.stderr)
    
    # Read file once and update all hashes
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            for hash_obj in hash_objects.values():
                hash_obj.update(chunk)
    
    # Return results
    return {algo: hash_obj.hexdigest() for algo, hash_obj in hash_objects.items()}


def verify_hash(filepath: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
    """
    Verify file hash matches expected value.
    
    Args:
        filepath: Path to file
        expected_hash: Expected hash value
        algorithm: Hash algorithm
        
    Returns:
        True if hash matches, False otherwise
    """
    actual_hash = calculate_hash(filepath, algorithm)
    return actual_hash.lower() == expected_hash.lower()


def hash_directory(directory: str, algorithm: str = 'sha256', 
                   recursive: bool = False) -> Dict[str, str]:
    """
    Calculate hashes for all files in a directory.
    
    Args:
        directory: Path to directory
        algorithm: Hash algorithm
        recursive: Process subdirectories recursively
        
    Returns:
        Dictionary mapping file paths to hash values
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")
    
    results = {}
    path = Path(directory)
    
    if recursive:
        files = path.rglob('*')
    else:
        files = path.glob('*')
    
    for file_path in files:
        if file_path.is_file():
            try:
                file_hash = calculate_hash(str(file_path), algorithm)
                results[str(file_path)] = file_hash
            except Exception as e:
                print(f"Error hashing {file_path}: {e}", file=sys.stderr)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Calculate and verify file hashes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.txt                           # SHA-256 hash (default)
  %(prog)s file.txt -a md5                    # MD5 hash
  %(prog)s file.txt -a sha512                 # SHA-512 hash
  %(prog)s file.txt -m md5 sha1 sha256        # Multiple hashes
  %(prog)s file.txt -v abc123...              # Verify hash
  %(prog)s directory/ -d                      # Hash all files in directory
  %(prog)s directory/ -d -r                   # Recursive directory hash
  
Supported algorithms: md5, sha1, sha224, sha256, sha384, sha512
        """
    )
    
    parser.add_argument('path', help='File or directory path')
    parser.add_argument('-a', '--algorithm', default='sha256',
                        choices=['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'],
                        help='Hash algorithm (default: sha256)')
    parser.add_argument('-m', '--multiple', nargs='+',
                        choices=['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'],
                        help='Calculate multiple hashes')
    parser.add_argument('-v', '--verify', metavar='HASH',
                        help='Verify file hash matches expected value')
    parser.add_argument('-d', '--directory', action='store_true',
                        help='Hash all files in directory')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Process directories recursively')
    
    args = parser.parse_args()
    
    try:
        if args.directory:
            # Hash directory
            results = hash_directory(args.path, args.algorithm, args.recursive)
            for filepath, file_hash in sorted(results.items()):
                print(f"{file_hash}  {filepath}")
        
        elif args.multiple:
            # Calculate multiple hashes
            results = calculate_multiple_hashes(args.path, args.multiple)
            for algo, file_hash in results.items():
                print(f"{algo.upper()}: {file_hash}")
        
        elif args.verify:
            # Verify hash
            if verify_hash(args.path, args.verify, args.algorithm):
                print(f"✓ Hash verified: {args.path}")
                return 0
            else:
                print(f"✗ Hash mismatch: {args.path}", file=sys.stderr)
                actual = calculate_hash(args.path, args.algorithm)
                print(f"  Expected: {args.verify}", file=sys.stderr)
                print(f"  Actual:   {actual}", file=sys.stderr)
                return 1
        
        else:
            # Calculate single hash
            file_hash = calculate_hash(args.path, args.algorithm)
            print(f"{file_hash}  {args.path}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
