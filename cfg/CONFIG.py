# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

SPECTREPARENTPATH = os.environ.get("SPECTREPARENTPATH")
if SPECTREPARENTPATH is None:
    raise ValueError("The environment variable SPECTREPARENTPATH has not been set.")


default_time_format = "%Y-%m-%dT%H:%M:%S"
# chunks_dir
path_to_chunks_dir = os.path.join(SPECTREPARENTPATH, 'chunks')
# path_to_capture_log
path_to_capture_log = os.path.join(SPECTREPARENTPATH, 'host', 'logs','capture.log')
# json_configs_dir
path_to_json_configs_dir = os.path.join(SPECTREPARENTPATH, "cfg", "json_configs")

# path_to_capture_scripts
path_to_capture_scripts_dir = os.path.join(SPECTREPARENTPATH, 'host', 'capture_scripts')
# path_to_start_capture
path_to_start_capture = os.path.join(path_to_capture_scripts_dir, 'start_capture.py')
# path_to_start_watcher
path_to_start_watcher = os.path.join(path_to_capture_scripts_dir, 'start_watcher.py')

