#!/usr/bin/env python3
"""
Archive Tool
Create, extract, and manage ZIP, TAR, and 7Z archives
"""

import argparse
import os
import sys
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import List, Optional


def create_zip(source_path: str, output_path: str, compression: int = zipfile.ZIP_DEFLATED) -> None:
    """
    Create a ZIP archive.
    
    Args:
        source_path: Path to file or directory to archive
        output_path: Output ZIP file path
        compression: Compression method
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source not found: {source_path}")
    
    with zipfile.ZipFile(output_path, 'w', compression) as zipf:
        if os.path.isfile(source_path):
            zipf.write(source_path, os.path.basename(source_path))
            print(f"✓ Added: {source_path}")
        else:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                    zipf.write(file_path, arcname)
                    print(f"✓ Added: {arcname}")
    
    file_size = os.path.getsize(output_path)
    print(f"\n✓ Created: {output_path} ({file_size:,} bytes)")


def extract_zip(archive_path: str, output_dir: str, password: Optional[str] = None) -> None:
    """
    Extract a ZIP archive.
    
    Args:
        archive_path: Path to ZIP file
        output_dir: Directory to extract to
        password: Optional password for encrypted archives
    """
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    with zipfile.ZipFile(archive_path, 'r') as zipf:
        # Convert password to bytes if provided
        pwd = password.encode() if password else None
        
        members = zipf.namelist()
        print(f"Extracting {len(members)} files...")
        
        for member in members:
            try:
                zipf.extract(member, output_dir, pwd=pwd)
                print(f"✓ Extracted: {member}")
            except Exception as e:
                print(f"✗ Error extracting {member}: {e}", file=sys.stderr)
    
    print(f"\n✓ Extracted to: {output_dir}")


def list_zip_contents(archive_path: str) -> None:
    """
    List contents of a ZIP archive.
    
    Args:
        archive_path: Path to ZIP file
    """
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    
    with zipfile.ZipFile(archive_path, 'r') as zipf:
        print(f"\nArchive: {archive_path}")
        print(f"{'Name':<50} {'Size':>15} {'Compressed':>15}")
        print("-" * 82)
        
        total_size = 0
        total_compressed = 0
        
        for info in zipf.filelist:
            print(f"{info.filename:<50} {info.file_size:>15,} {info.compress_size:>15,}")
            total_size += info.file_size
            total_compressed += info.compress_size
        
        print("-" * 82)
        print(f"{'Total:':<50} {total_size:>15,} {total_compressed:>15,}")
        
        if total_size > 0:
            ratio = (1 - total_compressed / total_size) * 100
            print(f"\nCompression ratio: {ratio:.1f}%")


def create_tar(source_path: str, output_path: str, compression: str = 'gz') -> None:
    """
    Create a TAR archive.
    
    Args:
        source_path: Path to file or directory to archive
        output_path: Output TAR file path
        compression: Compression method ('', 'gz', 'bz2', 'xz')
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source not found: {source_path}")
    
    mode = f'w:{compression}' if compression else 'w'
    
    with tarfile.open(output_path, mode) as tarf:
        if os.path.isfile(source_path):
            tarf.add(source_path, arcname=os.path.basename(source_path))
            print(f"✓ Added: {source_path}")
        else:
            tarf.add(source_path, arcname=os.path.basename(source_path))
            print(f"✓ Added directory: {source_path}")
    
    file_size = os.path.getsize(output_path)
    print(f"\n✓ Created: {output_path} ({file_size:,} bytes)")


def extract_tar(archive_path: str, output_dir: str) -> None:
    """
    Extract a TAR archive.
    
    Args:
        archive_path: Path to TAR file
        output_dir: Directory to extract to
    """
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    with tarfile.open(archive_path, 'r:*') as tarf:
        members = tarf.getmembers()
        print(f"Extracting {len(members)} items...")
        
        for member in members:
            tarf.extract(member, output_dir)
            print(f"✓ Extracted: {member.name}")
    
    print(f"\n✓ Extracted to: {output_dir}")


def list_tar_contents(archive_path: str) -> None:
    """
    List contents of a TAR archive.
    
    Args:
        archive_path: Path to TAR file
    """
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    
    with tarfile.open(archive_path, 'r:*') as tarf:
        print(f"\nArchive: {archive_path}")
        print(f"{'Name':<50} {'Size':>15} {'Type':>10}")
        print("-" * 77)
        
        total_size = 0
        
        for member in tarf.getmembers():
            type_str = 'DIR' if member.isdir() else 'FILE'
            print(f"{member.name:<50} {member.size:>15,} {type_str:>10}")
            total_size += member.size
        
        print("-" * 77)
        print(f"{'Total:':<50} {total_size:>15,}")


def batch_create_archives(directory: str, output_dir: str, format: str = 'zip') -> None:
    """
    Create individual archives for each item in a directory.
    
    Args:
        directory: Source directory
        output_dir: Output directory for archives
        format: Archive format ('zip' or 'tar')
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    created = 0
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        
        if format == 'zip':
            output_path = os.path.join(output_dir, f"{item}.zip")
            try:
                create_zip(item_path, output_path)
                created += 1
            except Exception as e:
                print(f"Error archiving {item}: {e}", file=sys.stderr)
        
        elif format == 'tar':
            output_path = os.path.join(output_dir, f"{item}.tar.gz")
            try:
                create_tar(item_path, output_path, 'gz')
                created += 1
            except Exception as e:
                print(f"Error archiving {item}: {e}", file=sys.stderr)
    
    print(f"\n✓ Created {created} archives in {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Create, extract, and manage archives',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # ZIP operations
  %(prog)s -c file.txt -o archive.zip              # Create ZIP
  %(prog)s -c directory/ -o archive.zip            # ZIP directory
  %(prog)s -x archive.zip -o output_dir/           # Extract ZIP
  %(prog)s -l archive.zip                          # List contents
  
  # TAR operations
  %(prog)s -c directory/ -o archive.tar.gz --tar   # Create TAR.GZ
  %(prog)s -x archive.tar.gz -o output_dir/ --tar  # Extract TAR
  %(prog)s -l archive.tar.bz2 --tar                # List TAR contents
  
  # Batch operations
  %(prog)s --batch source_dir/ -o archives_dir/    # Archive each item
  
Supported formats: ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ
        """
    )
    
    parser.add_argument('-c', '--create', metavar='PATH',
                        help='Create archive from file or directory')
    parser.add_argument('-x', '--extract', metavar='ARCHIVE',
                        help='Extract archive')
    parser.add_argument('-l', '--list', metavar='ARCHIVE',
                        help='List archive contents')
    parser.add_argument('-o', '--output', metavar='PATH',
                        help='Output path (file for create, directory for extract)')
    parser.add_argument('--tar', action='store_true',
                        help='Use TAR format instead of ZIP')
    parser.add_argument('--compression', choices=['none', 'gz', 'bz2', 'xz'],
                        default='gz', help='TAR compression (default: gz)')
    parser.add_argument('-p', '--password', metavar='PASS',
                        help='Password for encrypted ZIP archives')
    parser.add_argument('--batch', metavar='DIR',
                        help='Batch create archives for each item in directory')
    
    args = parser.parse_args()
    
    try:
        if args.batch:
            # Batch archive creation
            output_dir = args.output or './archives'
            format = 'tar' if args.tar else 'zip'
            batch_create_archives(args.batch, output_dir, format)
        
        elif args.create:
            # Create archive
            if not args.output:
                # Auto-generate output name
                basename = os.path.basename(args.create.rstrip('/'))
                if args.tar:
                    ext = f'.tar.{args.compression}' if args.compression != 'none' else '.tar'
                else:
                    ext = '.zip'
                args.output = basename + ext
            
            if args.tar:
                compression = '' if args.compression == 'none' else args.compression
                create_tar(args.create, args.output, compression)
            else:
                create_zip(args.create, args.output)
        
        elif args.extract:
            # Extract archive
            if not args.output:
                # Extract to current directory
                args.output = '.'
            
            if args.tar or args.extract.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2')):
                extract_tar(args.extract, args.output)
            else:
                extract_zip(args.extract, args.output, args.password)
        
        elif args.list:
            # List archive contents
            if args.tar or args.list.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2')):
                list_tar_contents(args.list)
            else:
                list_zip_contents(args.list)
        
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
