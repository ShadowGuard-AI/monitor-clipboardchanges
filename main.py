import argparse
import logging
import time
import pyperclip
import os


def setup_argparse():
    """Sets up the command line argument parser."""
    parser = argparse.ArgumentParser(description="Monitors clipboard changes and logs them.")
    parser.add_argument(
        "--log-file",
        type=str,
        default="clipboard_monitor.log",
        help="Path to the log file.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1,
        help="Interval in seconds to check clipboard changes.",
    )
    return parser.parse_args()


def setup_logging(log_file, log_level):
    """Sets up the logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(
        filename=log_file,
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def monitor_clipboard(interval):
    """Monitors clipboard changes and logs them."""
    previous_clipboard_content = None
    try:
        while True:
            try:
                current_clipboard_content = pyperclip.paste()
                if current_clipboard_content != previous_clipboard_content:
                    logging.info(f"Clipboard changed: {current_clipboard_content}")
                    previous_clipboard_content = current_clipboard_content
            except pyperclip.PyperclipException as e:
                logging.error(f"Error accessing clipboard: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Clipboard monitoring stopped.")
    except Exception as e:
        logging.critical(f"An unrecoverable error occurred: {e}")


def validate_args(args):
    """Validates CLI arguments."""
    if args.interval <= 0:
        raise ValueError("Interval must be a positive value.")
    if not os.path.isdir(os.path.dirname(os.path.abspath(args.log_file))):
         raise ValueError("Log file directory doesn't exists.")


def main():
    """Main function to orchestrate the clipboard monitoring."""
    try:
        args = setup_argparse()
        validate_args(args)
        setup_logging(args.log_file, args.log_level)
        logging.info("Clipboard monitoring started.")
        monitor_clipboard(args.interval)
    except ValueError as ve:
        logging.error(f"Invalid argument value: {ve}")
    except Exception as e:
        logging.critical(f"An unrecoverable error occurred during setup: {e}")


if __name__ == "__main__":
    """Entry point of the script."""
    main()

# Usage Example:
# 1. Default usage: python main.py
# This will log clipboard changes to clipboard_monitor.log with INFO level and 1 second interval.
#
# 2. Custom log file: python main.py --log-file my_clipboard.log
# This will log to my_clipboard.log file.
#
# 3. Custom log level: python main.py --log-level DEBUG
# This will log at DEBUG level.
#
# 4. Custom interval: python main.py --interval 0.5
# This will check the clipboard every 0.5 seconds.
#
# 5. Combination: python main.py --log-file my_clipboard.log --log-level DEBUG --interval 2
# This will log to my_clipboard.log, at DEBUG level, every 2 seconds