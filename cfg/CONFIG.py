import os


SPECTREPARENTPATH = os.environ.get("SPECTREPARENTPATH")
if SPECTREPARENTPATH is None:
    raise ValueError("The environment variable SPECTREPARENTPATH has not been set.")


default_time_format = "%Y-%m-%dT%H:%M:%S"
chunks_dir = os.path.join(SPECTREPARENTPATH, 'chunks')
path_to_capture_log = os.path.join(SPECTREPARENTPATH, 'host', 'logs','capture.log')
json_configs_dir = os.path.join(SPECTREPARENTPATH, "cfg", "json_configs")

path_to_capture_scripts = os.path.join(SPECTREPARENTPATH, 'host', 'capture_scripts')
path_to_start_capture = os.path.join(path_to_capture_scripts, 'start_capture.py')
path_to_start_watcher = os.path.join(path_to_capture_scripts, 'start_watcher.py')

