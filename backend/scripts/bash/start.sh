#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Update the shared library cache.
ldconfig

# Start the SDRplay API service in the background.
/opt/sdrplay_api/sdrplay_apiService &

# Start the spectre server
python3 -m spectre_server