# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cfg import CONFIG
from spectre.watchdog.factory import get_event_handler_from_tag

class Watcher:
    def __init__(self, tag: str):
        self.observer = Observer()
        EventHandler = get_event_handler_from_tag(tag)
        self.event_handler = EventHandler(self, tag)  # Initialize with the appropriate handler

    def start(self):
        try:
            # Schedule the observer with the event handler
            self.observer.schedule(self.event_handler, CONFIG.path_to_chunks_dir, recursive=True)
            self.observer.start()
            print("Watching for new files...")

            # Observer runs asynchronously, just wait for it to complete or fail
            self.observer.join()  # This will block until the observer is stopped
        except Exception as e:
            # Propagate the error upwards
            print(f"Error occurred in watcher: {e}")
            raise e
        finally:
            # Ensure the observer is properly stopped in the event of an error
            self.observer.stop()
            self.observer.join()
            print("Observer stopped.")
