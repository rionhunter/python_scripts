import sys
import os
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="System and argument testing script.")
    parser.add_argument('--example', type=str, help="An example argument.")
    parser.add_argument('--number', type=int, help="A number argument.")
    parser.add_argument('--flag', action='store_true', help="A boolean flag.")
    return parser.parse_args()

def print_system_info():
    print("### System Information ###")
    print(f"Platform: {sys.platform}")
    print(f"Python Version: {sys.version}")
    print(f"Executable Path: {sys.executable}")
    print()

def print_environment_variables():
    print("### Environment Variables ###")
    for key, value in os.environ.items():
        print(f"{key}: {value}")
    print()

def print_arguments(args):
    print("### Command Line Arguments ###")
    for arg in vars(args):
        print(f"{arg}: {getattr(args, arg)}")
    print()

def print_input_data():
    print("### Input Data ###")
    if not sys.stdin.isatty():
        input_data = sys.stdin.read()
        print(f"Input Data: {input_data}")
    else:
        print("No input data provided via stdin.")
    print()

def main():
    print_system_info()
    print_environment_variables()

    args = parse_arguments()
    print_arguments(args)

    print_input_data()

if __name__ == "__main__":
    main()
