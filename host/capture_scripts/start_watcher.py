# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser
import os

from spectre.watchdog.Watcher import Watcher
from cfg import CONFIG

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--tag", required=True, type=str, help="")
    args = parser.parse_args()
    tag = args.tag

    if not os.path.exists(CONFIG.path_to_chunks_dir):
        os.mkdir(CONFIG.path_to_chunks_dir)

    watcher = Watcher(tag)
    watcher.start()

