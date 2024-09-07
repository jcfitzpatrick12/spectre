# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import queue
from watchdog.observers import Observer
from cfg import CONFIG
from spectre.watchdog.factory import get_event_handler_from_tag

class Watcher:
    def __init__(self, tag: str):
        self.observer = Observer()
        EventHandler = get_event_handler_from_tag(tag)
        self.event_handler = EventHandler(self, tag)
        self.exception_queue = queue.Queue()  # A thread-safe queue for exceptions

    def start(self):
        try:
            # Schedule the observer with the event handler
            self.observer.schedule(self.event_handler, CONFIG.path_to_chunks_dir, recursive=True)
            self.observer.start()
            print("Watching for new files...")

            # Monitor the observer and check for exceptions in the queue
            while True:
                try:
                    # Check if any exceptions were raised in the event handler
                    exc = self.exception_queue.get(block=False)  # Non-blocking
                    raise exc  # Raise the exception in the main thread
                except queue.Empty:
                    # No exceptions, continue checking
                    pass

                # Wait for the observer to finish
                self.observer.join(1)  # Use short join timeout for responsiveness
        except Exception as e:
            print(f"Error occurred in watcher: {e}")
            raise e
        finally:
            # Ensure the observer is properly stopped in case of an error
            self.observer.stop()
            self.observer.join()
            print("Observer stopped.")
