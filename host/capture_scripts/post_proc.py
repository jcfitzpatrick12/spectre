# from argparse import ArgumentParser
# import os
# import time
# from datetime import datetime
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# from cfg import CONFIG
# from utils import capture_session 
# from spectre.chunks.get_chunk import get_chunk
# from spectre.cfg.json_config.CaptureConfig import CaptureConfig
# from spectre.utils.datetime_helpers import date_dir


# class StationaryFileHandler(FileSystemEventHandler):
#     def on_created(self, event):
#         # Ignore directories; only process files
#         if not event.is_directory:
#             self.process_if_stationary(event.src_path)

#     def process_if_stationary(self, path):
#         # Check if the file is not being written to (stationary)
#         if self.is_stationary(path):
#             file = os.path.basename(path)
#             chunk_name, ext = 
#             print(f"Processing stationary file: {path}")
#             self.post_process_file(path)
#             # Delete the file after processing
#             os.remove(path)
#         else:
#             print(f"File is currently being written to: {path}")

#     def is_stationary(self, path):
#         initial_size = os.path.getsize(path)
#         time.sleep(1)  # Wait for a bit to see if the file is still being written to
#         final_size = os.path.getsize(path)
#         return initial_size == final_size

#     def post_process_file(self, path):
#         # Placeholder for your post-processing logic
#         print(f"placeholder processing for {path}")


# def main():
#     try:
#         date_dir = date_dir(datetime.now())
#         path_to_watch = os.path.join(CONFIG.chunks_dir, date_dir)

#         if not os.path.exists(path_to_watch):
#             raise NotADirectoryError(f"The path to watch {path_to_watch} does not exist.")

#         event_handler = StationaryFileHandler()
#         observer = Observer()
#         observer.schedule(event_handler, path_to_watch, recursive=False)
#         observer.start()

#         try:
#             while True:
#                 time.sleep(10)
#         except KeyboardInterrupt:
#             observer.stop()
#         observer.join()

#     except Exception as e:
#         capture_session.log_subprocess(os.getpid(), str(e))

#     # try:
#     #     # find which type of chunk to use with the current tag
#     #     capture_config_instance = CaptureConfig(tag, CONFIG.json_configs_dir)
#     #     capture_config = capture_config_instance.load_as_dict()
#     #     chunk_key = capture_config.get("chunk_key")
#     #     Chunk = get_chunk(chunk_key)

#     # except Exception as e:
#     #     capture_session.log_subprocess(os.getpid(), str(e))

# if __name__ == "__main__":
#     main()







