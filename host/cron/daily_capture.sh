#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

#Set SPECTREHOST as the parent directory of the package
export SPECTRE_PARENT_PATH=/home/spectre
#add spectre to the python path so we can import modules properly
export PYTHONPATH="${SPECTRE_PARENT_PATH}:${PYTHONPATH}"
# ensure that spectre is recognised as a command in the cron environment
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

spectre capture session --receiver RSP1A --mode sweep --tag RSP1A-sweep-example --hours 8 --force-restart

