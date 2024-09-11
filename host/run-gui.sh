#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Enable xhost for the local machine only, safer than 'xhost +'
xhost local:

# Set SPECTRE_PARENT_PATH to the parent directory of this script
export SPECTRE_PARENT_PATH=$(dirname "$(dirname "$(realpath "$0")")")

# Check if the directory $SPECTRE_PARENT_PATH/chunks exists; if not, create it
if [ ! -d "$SPECTRE_PARENT_PATH/chunks" ]; then
    mkdir -p "$SPECTRE_PARENT_PATH/chunks"
fi

# Run the Docker container (no GUI support)
sudo docker run --name spectre-host-gui-container -it --rm \
    -v /dev/shm:/dev/shm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    spectre-host-gui

# Reset xhost
xhost -