# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from queue import Queue, Empty

from watchdog.observers import Observer

from spectre.watchdog.factory import get_event_handler_from_tag
from spectre.cfg import CHUNKS_DIR_PATH

class Watcher:
    def __init__(self, 
                 tag: str):
        self._observer: Observer = Observer()
        self._exception_queue: Queue = Queue()  # A thread-safe queue for exceptions

        EventHandler = get_event_handler_from_tag(tag)
        self._event_handler = EventHandler(tag, 
                                           self._exception_queue,
                                           "bin")


    def start(self):
        _LOGGER.info("Starting watcher...")

        # Schedule and start the observer
        self._observer.schedule(self._event_handler, 
                               CHUNKS_DIR_PATH, 
                               recursive=True)
        self._observer.start()

        try:
            # Monitor the observer and handle exceptions
            while self._observer.is_alive():
                try:
                    exc = self._exception_queue.get(block=True, timeout=0.25)
                    if exc:
                        raise exc  # Propagate the exception
                except Empty:
                    pass  # Continue looping if no exception in queue
        finally:
            # Ensure the observer is properly stopped
            self._observer.stop()
            self._observer.join()


