import os

json_configs_dir = os.path.join(os.environ['SPECTREPARENTPATH'],"host", "cfg", "json_configs")
chunks_dir = os.path.join(os.environ['SPECTREPARENTPATH'], 'host', 'chunks')
path_to_capture_log = os.path.join(os.environ['SPECTREPARENTPATH'], 'host', 'cfg', 'capture.log')

path_to_capture_scripts = os.path.join(os.environ['SPECTREPARENTPATH'], 'host', 'capture_scripts')
path_to_start_capture = os.path.join(path_to_capture_scripts, 'start_capture.py')
path_to_start_watcher = os.path.join(path_to_capture_scripts, 'start_watcher.py')
