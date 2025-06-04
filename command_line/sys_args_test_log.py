import sys
import os
import argparse
import logging

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

def parse_arguments():
    parser = argparse.ArgumentParser(description="System and argument testing script with logging.")
    parser.add_argument('--example', type=str, help="An example argument.")
    parser.add_argument('--number', type=int, help="A number argument.")
    parser.add_argument('--flag', action='store_true', help="A boolean flag.")
    return parser.parse_args()

def log_system_info():
    logging.info("### System Information ###")
    logging.info(f"Platform: {sys.platform}")
    logging.info(f"Python Version: {sys.version}")
    logging.info(f"Executable Path: {sys.executable}")
    logging.info("")

def log_environment_variables():
    logging.info("### Environment Variables ###")
    for key, value in os.environ.items():
        logging.info(f"{key}: {value}")
    logging.info("")

def log_arguments(args):
    logging.info("### Command Line Arguments ###")
    for arg in vars(args):
        logging.info(f"{arg}: {getattr(args, arg)}")
    logging.info("")

def log_input_data():
    logging.info("### Input Data ###")
    if not sys.stdin.isatty():
        input_data = sys.stdin.read()
        logging.info(f"Input Data: {input_data}")
    else:
        logging.info("No input data provided via stdin.")
    logging.info("")

def main():
    log_file = "system_test.log"
    setup_logging(log_file)

    log_system_info()
    log_environment_variables()

    args = parse_arguments()
    log_arguments(args)

    log_input_data()

    print(f"Results logged to {log_file}")

if __name__ == "__main__":
    main()
