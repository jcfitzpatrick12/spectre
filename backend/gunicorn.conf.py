# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import multiprocessing

SPECTRE_SERVICE_HOST = os.environ.get("SPECTRE_SERVICE_HOST", "0.0.0.0")
SPECTRE_SERVICE_PORT = int(os.environ.get("SPECTRE_SERVICE_PORT", "5000"))

bind = f"{SPECTRE_SERVICE_HOST}:{SPECTRE_SERVICE_PORT}"
workers = multiprocessing.cpu_count() * 2 + 1 
