# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import multiprocessing

SPECTRE_BIND_HOST  = os.environ.get("SPECTRE_BIND_HOST", "0.0.0.0")
SPECTRE_BIND_PORT  = int( os.environ.get("SPECTRE_BIND_PORT", "5000") )


bind = f"{SPECTRE_BIND_HOST}:{SPECTRE_BIND_PORT}"
workers = multiprocessing.cpu_count() * 2 + 1 
timeout=0
