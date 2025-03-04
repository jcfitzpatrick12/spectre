#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Cloning the freshest copy of the `spectre` and `spectre-core` repositories, and 
# pip installing them system-wide in editable mode.

git clone https://github.com/jcfitzpatrick12/spectre.git && cd spectre
git checkout main
pip install -e backend


cd ..
git clone https://github.com/jcfitzpatrick12/spectre-core.git && cd spectre-core
git checkout main
pip install -e .

