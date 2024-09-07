# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser
import os
import logging
from spectre.receivers.factory import get_receiver
from host.capture_session.processes import configure_subprocess_logging  # Import logging config

def main():
    # Configure logging for this subprocess (using its PID)
    pid = os.getpid()
    logger = configure_subprocess_logging(pid)  # Set up logging for the subprocess
    
    try:
        parser = ArgumentParser()
        parser.add_argument("--receiver", type=str, help="")
        parser.add_argument("--mode", type=str, help="")
        parser.add_argument("--tags", "--tag", type=str, nargs="+", help="")

        args = parser.parse_args()

        receiver_name = args.receiver
        mode = args.mode
        tags = args.tags

        # Log the input arguments
        logger.info(f"Starting capture with the receiver {receiver_name} in mode {mode} with tags {tags}.")

        # Get receiver and start capture
        receiver = get_receiver(receiver_name, mode=mode)
        logger.info(f"Receiver {receiver_name} successfully instantiated in mode {mode}.")

        receiver.start_capture(tags)
        logger.info(f"Capture started with tags {tags}")

    except Exception as e:
        # Log any unexpected errors
        logger.error(f"An exception occurred during capture: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
