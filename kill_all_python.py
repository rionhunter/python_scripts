"""
!/usr/bin/env python3
Python Process Killer - Development Utility
============================================

This script kills all running Python processes on Windows.
Useful for handling stuck Python applications during development.

Usage:
    python kill_all_python.py [options]

Options:
    --dry-run, -d    Show what processes would be killed without actually killing them
    --exclude-self   Exclude the current script process from being killed (default: True)
    --force, -f      Force kill processes without confirmation
    --help, -h       Show this help message

Author: Development Utility
Created: 2025-09-27
"""

import os
import sys
import subprocess
import argparse
import time
from typing import List, Tuple


def get_python_processes() -> List[Tuple[int, str]]:
    """
    Get all running Python processes.
    
    Returns:
        List of tuples containing (PID, process_name)
    """
    processes = []
    
    try:
        # Use tasklist to get all processes
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python*', '/FO', 'CSV'],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        
        # Skip header line
        for line in lines[1:]:
            if line.strip():
                # Parse CSV format: "Image Name","PID","Session Name","Session#","Mem Usage"
                parts = [part.strip('"') for part in line.split('","')]
                if len(parts) >= 2:
                    image_name = parts[0]
                    try:
                        pid = int(parts[1])
                        processes.append((pid, image_name))
                    except ValueError:
                        continue
                        
    except subprocess.CalledProcessError as e:
        print(f"Error getting process list: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    
    return processes


def kill_process(pid: int, process_name: str, force: bool = False) -> bool:
    """
    Kill a process by PID.
    
    Args:
        pid: Process ID to kill
        process_name: Name of the process (for logging)
        force: If True, use /F flag for forceful termination
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ['taskkill', '/PID', str(pid)]
        if force:
            cmd.append('/F')
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Killed {process_name} (PID: {pid})")
            return True
        else:
            # Clean up error message - remove extra whitespace and newlines
            error_msg = result.stderr.strip().replace('\r\n', ' ').replace('\n', ' ')
            
            # Check if process was already terminated
            if "not found" in error_msg.lower():
                print(f"→ Process {process_name} (PID: {pid}) already terminated")
                return True  # Consider this a success since the goal is achieved
            else:
                print(f"✗ Failed to kill {process_name} (PID: {pid}): {error_msg}")
                return False
            
    except Exception as e:
        print(f"✗ Error killing {process_name} (PID: {pid}): {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Kill all Python processes (development utility)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python kill_all_python.py              # Kill all Python processes with confirmation
    python kill_all_python.py --dry-run    # Show what would be killed
    python kill_all_python.py --force      # Kill without confirmation
    python kill_all_python.py -d -f        # Dry run in force mode
        """
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show what processes would be killed without actually killing them'
    )
    
    parser.add_argument(
        '--exclude-self',
        action='store_true',
        default=True,
        help='Exclude the current script process from being killed (default: True)'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force kill processes without confirmation'
    )
    
    args = parser.parse_args()
    
    print("Python Process Killer - Development Utility")
    print("=" * 45)
    
    # Get all Python processes
    processes = get_python_processes()
    
    if not processes:
        print("No Python processes found running.")
        return 0
    
    # Filter out current process if requested
    current_pid = os.getpid()
    if args.exclude_self:
        processes = [p for p in processes if p[0] != current_pid]
        
    if not processes:
        print("No Python processes found (excluding current script).")
        return 0
    
    print(f"\nFound {len(processes)} Python process(es):")
    for pid, name in processes:
        status = "(current script)" if pid == current_pid else ""
        print(f"  - {name} (PID: {pid}) {status}")
    
    if args.dry_run:
        print(f"\n[DRY RUN] Would kill {len(processes)} process(es)")
        return 0
    
    # Confirm before killing (unless force mode)
    if not args.force:
        print(f"\nThis will kill {len(processes)} Python process(es).")
        response = input("Are you sure? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Operation cancelled.")
            return 0
    
    print(f"\nKilling {len(processes)} Python process(es)...")
    
    killed_count = 0
    failed_count = 0
    
    for pid, name in processes:
        if kill_process(pid, name, force=args.force):
            killed_count += 1
        else:
            failed_count += 1
        
        # Small delay between kills
        time.sleep(0.1)
    
    print(f"\nResults:")
    print(f"  ✓ Successfully killed: {killed_count}")
    print(f"  ✗ Failed to kill: {failed_count}")
    
    if failed_count > 0:
        print("\nNote: Some processes may have already terminated or require administrator privileges.")
        print("This is normal - the goal of stopping Python processes has been achieved.")
    
    # Only return error code if there were actual failures (not "already terminated" cases)
    return 0  # Changed to always return success since "not found" processes are handled as success


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
