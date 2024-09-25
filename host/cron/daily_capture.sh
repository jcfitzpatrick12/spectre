#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

#Set SPECTREHOST as the parent directory of the package
export SPECTRE_DIR_PATH=/home/spectre
#add spectre to the python path so we can import modules properly
export PYTHONPATH="${SPECTRE_DIR_PATH}:${PYTHONPATH}"
# ensure that spectre is recognised as a command in the cron environment
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

spectre capture session --receiver RSP1A --mode sweep --tag RSP1A-sweeper --hours 8 --force-restart
spectre delete chunks --tag RSP1A-sweeper --ext bin --ext hdr

