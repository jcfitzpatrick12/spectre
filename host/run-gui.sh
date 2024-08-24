#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Enable xhost for the local machine only, safer than 'xhost +'
xhost local:

# Set SPECTREPARENTPATH to the parent directory of this script
export SPECTREPARENTPATH=$(dirname "$(dirname "$(realpath "$0")")")

# Check if the directory $SPECTREPARENTPATH/chunks exists; if not, create it
if [ ! -d "$SPECTREPARENTPATH/chunks" ]; then
    mkdir -p "$SPECTREPARENTPATH/chunks"
fi

# Run the Docker container (no GUI support)
sudo docker run --name spectre-host-gui-container -it --rm \
    -v /dev/shm:/dev/shm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    spectre-host-gui

# Reset xhost
xhost -