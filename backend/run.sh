#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

docker run --interactive \
           --tty \
           --rm \
           --publish 127.0.0.1:5000:5000 \
           --name spectre-backend \
           --volume /dev/shm:/dev/shm \
           --volume $SPECTRE_DATA_DIR_PATH:/home/spectre/spectre-data \
           spectre-server \
           /bin/bash
