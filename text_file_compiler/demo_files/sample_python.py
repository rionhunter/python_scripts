#!/usr/bin/env python3
"""
Sample Python script for demonstration.

This script shows how the text file compiler handles Python code
with proper syntax highlighting and formatting.
"""

import os
import sys
from datetime import datetime


class DemoClass:
    """A demonstration class."""
    
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
    
    def greet(self) -> str:
        """Return a greeting message."""
        return f"Hello from {self.name}! Created at {self.created_at}"
    
    def calculate_fibonacci(self, n: int) -> int:
        """Calculate the nth Fibonacci number."""
        if n <= 1:
            return n
        return self.calculate_fibonacci(n - 1) + self.calculate_fibonacci(n - 2)


def main():
    """Main function demonstrating the class usage."""
    demo = DemoClass("PyQt6 Text Compiler Demo")
    print(demo.greet())
    
    # Calculate some Fibonacci numbers
    for i in range(10):
        fib = demo.calculate_fibonacci(i)
        print(f"Fibonacci({i}) = {fib}")


if __name__ == "__main__":
    main()