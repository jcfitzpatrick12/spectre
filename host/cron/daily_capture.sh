#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

#Set SPECTREHOST as the parent directory of the package
export SPECTREPARENTPATH=/home/spectre
#add spectre to the python path so we can import modules properly
export PYTHONPATH="${SPECTREPARENTPATH}:${PYTHONPATH}"
# ensure that spectre is recognised as a command in the cron environment
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

spectre capture start-watcher -t sol
spectre capture start --receiver RSPduo --mode tuner-1-fixed --tag sol
sleep 36000s
spectre capture stop
