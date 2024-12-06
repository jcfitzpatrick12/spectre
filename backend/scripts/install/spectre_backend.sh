#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

pip install --upgrade pip

cd /home

# don't checkout HEAD when clone is complete
git clone --no-checkout https://github.com/jcfitzpatrick12/spectre.git && cd spectre

# Update the working directory with only required files
git sparse-checkout set backend/src backend/pyproject.toml
# git checkout v0.0.0
git checkout formal-installation

# install dependencies
cd backend
pip install .
