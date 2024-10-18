# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

import queue
from watchdog.observers import Observer

from spectre.watchdog.factory import get_event_handler_from_tag

from spectre.cfg import (
    CHUNKS_DIR_PATH
)

class Watcher:
    def __init__(self, tag: str):
        self.observer = Observer()
        self.exception_queue = queue.Queue()  # A thread-safe queue for exceptions
        EventHandler = get_event_handler_from_tag(tag)
        self.event_handler = EventHandler(tag, self.exception_queue)


    def start(self):
        _LOGGER.info("Starting watcher...")

        # Schedule and start the observer
        self.observer.schedule(self.event_handler, CHUNKS_DIR_PATH, recursive=True)
        self.observer.start()

        try:
            # Monitor the observer and handle exceptions
            while self.observer.is_alive():
                try:
                    exc = self.exception_queue.get(block=True, timeout=0.25)
                    if exc:
                        raise exc  # Propagate the exception
                except queue.Empty:
                    pass  # Continue looping if no exception in queue
        finally:
            # Ensure the observer is properly stopped
            self.observer.stop()
            self.observer.join()


