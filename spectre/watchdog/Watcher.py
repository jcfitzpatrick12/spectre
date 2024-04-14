from watchdog.observers import Observer
import time
import threading

class Watcher:
    def __init__(self, watch_directory: str, tag: str, extension: str):
        self.observer = Observer()
        self.watch_directory = watch_directory
        self.tag = tag
        self.extension = extension
        self.stop_event = threading.Event()  # Event to signal an error and stop the watcher

    def run(self, event_handler):
        self.observer.schedule(event_handler, self.watch_directory, recursive=True)
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
