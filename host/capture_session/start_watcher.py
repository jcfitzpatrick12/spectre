# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser
import os
import logging
from spectre.watchdog.Watcher import Watcher
from cfg import CONFIG
from host.capture_session.processes import configure_subprocess_logging

if __name__ == "__main__":
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument("--tag", required=True, type=str, help="Tag for the file handler")
    args = parser.parse_args()
    tag = args.tag

    # Configure logging for this subprocess (using its PID)
    pid = os.getpid()
    logger = configure_subprocess_logging(pid)  # Ensure all logs go to the correct log file

    try:
        # Log that the process has started
        logger.info(f"Starting watcher with tag: {tag}")

        # Check if the chunks directory exists, and create if not
        if not os.path.exists(CONFIG.path_to_chunks_dir):
            os.mkdir(CONFIG.path_to_chunks_dir)
            logger.info(f"Created chunks directory at {CONFIG.path_to_chunks_dir}")

        # Start the watcher
        watcher = Watcher(tag)
        watcher.start()

    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Exception occurred in subprocess: {str(e)}", exc_info=True)
