# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from watchdog.observers import Observer
import time
import threading


from cfg import CONFIG
from spectre.watchdog.factory import get_event_handler_from_tag
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler

class Watcher:
    def __init__(self, tag: str):
        self.observer = Observer()
        self.tag = tag

        # Event handler based on tag
        EventHandler = get_event_handler_from_tag(tag)
        self.event_handler = EventHandler(self, tag)

        self.stop_event = threading.Event()  # Event to signal an error and stop the watcher

    def start(self):
        self.observer.schedule(self.event_handler, CONFIG.path_to_chunks_dir, recursive=True)
        self.observer.start()
        print("Watching for new files...")

        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except Exception as e:
            # Propagate the error upwards to the caller
            raise e  # This will propagate the error to where watcher.start() is called
        finally:
            # Ensure the observer is properly stopped even in the case of an error
            self.observer.stop()
            self.observer.join()
            print("Observer Stopped")

    def stop(self):
        self.stop_event.set()  # Signal to stop the observer


