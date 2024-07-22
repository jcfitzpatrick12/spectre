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

        EventHandler = get_event_handler_from_tag(tag)
        # create an instance of the event handler
        self.event_handler = EventHandler(self, tag)

        self.stop_event = threading.Event()  # Event to signal an error and stop the watcher

    def start(self):
        self.observer.schedule(self.event_handler, CONFIG.chunks_dir, recursive=True)
        self.observer.start()
        print("Watching for new files...")
        try:
            while not self.stop_event.is_set():  # Check if the stop event is set
                time.sleep(1)
        except KeyboardInterrupt:
            print("Watcher manually interrupted.")
        finally:
            self.observer.stop()
            self.observer.join()
            print("Observer Stopped")


    def stop(self):
        self.stop_event.set()  # External method to stop the observer
