#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Create the named `spectre-group` inside the container.
if ! getent group "$SPECTRE_GID" >/dev/null; then
    echo "Creating group 'spectre-group' inside container with GID $SPECTRE_GID"
    groupadd -g "$SPECTRE_GID" spectre-group
fi

# Add out non-root user to the `spectre-group`, so that it can access USB devices.
usermod -aG spectre-group appuser

# Change ownership of the /app directory (including the mounted volume) so that our non-root user can write to it.
chown -R appuser:spectre-group /app

# Drop root privileges when running the application.
exec gosu appuser "$@"