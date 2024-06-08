# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser
import os

from spectre.watchdog.Watcher import Watcher
from cfg import CONFIG
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from host.utils import capture_session

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--tag", required=True, type=str, help="")
    args = parser.parse_args()
    tag = args.tag

    if not os.path.exists(CONFIG.chunks_dir):
        os.mkdir(CONFIG.chunks_dir)

    try:
        watcher = Watcher(tag)
        watcher.start()

    except Exception as e:
        capture_session.log_subprocess(os.getpid(), str(e))
