import argparse
import hashlib
import logging
import sys
import time
import pyperclip
import os

MAX_CONSECUTIVE_FAILURES = 5


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
    """Monitors clipboard changes and logs them.

    The content already present at startup is taken as the silent
    baseline and is not logged. Later changes are logged only as a
    SHA256 digest and a character length. Clipboard text itself is
    never written to the log.
    """
    previous_clipboard_content = None
    baseline_set = False
    consecutive_failures = 0
    try:
        while True:
            try:
                current_clipboard_content = pyperclip.paste()
                consecutive_failures = 0
                if not baseline_set:
                    # The first successful read becomes the baseline whenever it
                    # happens. If the clipboard was unreadable for a while,
                    # everything copied during the outage is folded into that
                    # baseline in silence, and only changes after it are logged.
                    previous_clipboard_content = current_clipboard_content
                    baseline_set = True
                elif current_clipboard_content != previous_clipboard_content:
                    # A digest is not a redaction for short content. A copied PIN,
                    # a short password, a one word answer: anyone holding this
                    # log can guess the text and check the guess against the
                    # hash and the exact length beside it. The log is safer than
                    # plain text, and it is not safe to treat as harmless.
                    digest = hashlib.sha256(current_clipboard_content.encode("utf-8")).hexdigest()
                    if current_clipboard_content == "":
                        # An image copied to the clipboard reads as an empty string
                        # from pyperclip on the usual backends, so it is logged in
                        # this same cleared shape. I cannot tell a cleared clipboard
                        # from a picture, and my log does not pretend otherwise once
                        # you know the empty result covers both.
                        logging.info(
                            f"Clipboard changed: cleared or non-text clipboard "
                            f"(empty result) sha256={digest} length=0"
                        )
                    else:
                        logging.info(
                            f"Clipboard changed: sha256={digest} "
                            f"length={len(current_clipboard_content)}"
                        )
                    previous_clipboard_content = current_clipboard_content
            except pyperclip.PyperclipException as e:
                consecutive_failures += 1
                logging.error(f"Error accessing clipboard: {e}")
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    logging.error(
                        f"Clipboard unreadable after {MAX_CONSECUTIVE_FAILURES} "
                        f"consecutive failures."
                    )
                    sys.exit(1)
            except Exception as e:
                consecutive_failures += 1
                logging.error(f"An unexpected error occurred: {e}")
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    logging.error(
                        f"Clipboard unreadable after {MAX_CONSECUTIVE_FAILURES} "
                        f"consecutive failures."
                    )
                    sys.exit(1)
            # Polling at this interval is the whole detection method, so
            # a copy that is replaced again before the next check is
            # never seen. A fast A to B to A sequence logs nothing, and
            # the effective interval is this sleep plus whatever time
            # the paste call itself takes.
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Clipboard monitoring stopped.")


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
        print(f"Invalid argument value: {ve}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as e:
        print(f"An unrecoverable error occurred during setup: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
