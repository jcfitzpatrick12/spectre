#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

pip install --upgrade pip

cd /home
# don't checkout HEAD when clone is complete
# install the latest version of spectre available
git clone --no-checkout https://github.com/jcfitzpatrick12/spectre.git && cd spectre

# Update the working directory with only required files
git sparse-checkout set backend/src backend/pyproject.toml
git checkout bug-fixes
# install dependencies in editable mode
cd backend
pip install -e .


cd /home
# Overwrite spectre-core with the latest available from git
git clone https://github.com/jcfitzpatrick12/spectre-core.git && cd spectre-core
pip install -e .
