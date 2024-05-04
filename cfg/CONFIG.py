import os

default_time_format = "%Y-%m-%dT%H:%M:%S"
chunks_dir = os.path.join(os.environ['SPECTREPARENTPATH'], 'chunks')
path_to_capture_log = os.path.join(os.environ['SPECTREPARENTPATH'], 'logs', 'capture.log')
json_configs_dir = os.path.join(os.environ['SPECTREPARENTPATH'], "cfg", "json_configs")

path_to_capture_scripts = os.path.join(os.environ['SPECTREPARENTPATH'], 'host', 'capture_scripts')
path_to_start_capture = os.path.join(path_to_capture_scripts, 'start_capture.py')
path_to_start_watcher = os.path.join(path_to_capture_scripts, 'start_watcher.py')

