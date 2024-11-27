#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Clone the repository
git clone https://github.com/jcfitzpatrick12/gr-spectre.git
# cd into the cloned repo
cd gr-spectre
# Checkout a specific branch
# git checkout <branch name>
# Checkout a specific commit within the branch
# git checkout <commit hash>
# Build the OOT module
mkdir build && cd build && cmake .. && make
# Install the module
sudo make install