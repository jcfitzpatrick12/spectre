#!/bin/bash
# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Start the SDRplay API service in the background.
sdrplay_apiService &

# Start the spectre server.
python3 -m gunicorn -c gunicorn.conf.py "spectre_server.__main__:make_app()"
