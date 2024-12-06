#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Enable xhost for the local machine only
xhost local:

docker run --rm \
           --publish 127.0.0.1:5000:5000 \
           --name spectre-dev-server \
           --volume /dev/shm:/dev/shm \
           --volume $SPECTRE_DATA_DIR_PATH:/home/spectre/.spectre-data \
            -e DISPLAY=$DISPLAY \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            --interactive \
            --tty \
            spectre-dev-server \
            /bin/bash

# Reset xhost
xhost -
