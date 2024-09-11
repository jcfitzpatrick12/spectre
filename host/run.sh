#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Set SPECTRE_DIR_PATH to the parent directory of this script
export SPECTRE_DIR_PATH=$(dirname "$(dirname "$(realpath "$0")")")

# Check if the directory $SPECTRE_DIR_PATH/chunks exists; if not, create it
if [ ! -d "$SPECTRE_DIR_PATH/chunks" ]; then
    mkdir -p "$SPECTRE_DIR_PATH/chunks"
fi

# Run the Docker container (no GUI support)
sudo docker run --name spectre-host-container -it --rm \
    -v $SPECTRE_DIR_PATH/cfg:/home/spectre/cfg \
    -v $SPECTRE_DIR_PATH/host/logs:/home/spectre/host/logs \
    -v $SPECTRE_DIR_PATH/chunks:/home/spectre/chunks \
    -v /dev/shm:/dev/shm \
    spectre-host