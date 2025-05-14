#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Update the shared library cache.
ldconfig

# Change ownership of the /app directory (including the mounted volume) so that our non-root user can write to it.
chown -R appuser:appgroup /app

# Drop root privileges and execute the provided command as appuser.
exec runuser -u appuser "$@"