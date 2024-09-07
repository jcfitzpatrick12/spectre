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
        self.exception_queue = queue.Queue()  # A thread-safe queue for exceptions
        EventHandler = get_event_handler_from_tag(tag)
        self.event_handler = EventHandler(tag, self.exception_queue)

    def start(self):
        try:
            # Schedule the observer with the event handler
            self.observer.schedule(self.event_handler, CONFIG.path_to_chunks_dir, recursive=True)
            self.observer.start()
            print("Watcher started, observing directory...")

            # Monitor the observer and check for exceptions in the queue
            while True:
                try:
                    # Block and wait for exceptions with a 1-second timeout
                    exc = self.exception_queue.get(block=True, timeout=1)
                    print("Exception captured in background thread.")
                    raise exc  # Propagate the exception to the main thread
                except queue.Empty:
                    # No exceptions in queue, continue checking
                    pass

                # Stop if the observer thread stops running
                if not self.observer.is_alive():
                    print("Observer has stopped unexpectedly.")
                    break
        except Exception as e:
            print(f"Error occurred in Watcher: {e}")
            raise e
        finally:
            # Ensure the observer is properly stopped
            self.observer.stop()
            self.observer.join()
            print("Watcher stopped.")


