# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.receivers.Receiver import Receiver
from argparse import ArgumentParser
from cfg import CONFIG
from host.utils import capture_session
import os

def main():
    parser = ArgumentParser()
    parser.add_argument("--receiver", type=str, help="")
    parser.add_argument("--mode", type=str, help="")
    parser.add_argument("--tags", "--tag", type=str, nargs="+", help="")

    args = parser.parse_args()

    receiver_name = args.receiver
    mode = args.mode
    tags = args.tags

    try:
        receiver = Receiver(receiver_name)
        receiver.set_mode(mode)
        receiver.start_capture(tags)

    except Exception as e:
        capture_session.log_subprocess(os.getpid(), str(e))

if __name__ == "__main__":
    main()






