#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Clone the repository
git clone https://github.com/jcfitzpatrick12/gr-spectre.git
# cd into the cloned repo
cd gr-spectre
# Checkout a specific version
git checkout v0.0.1
# Build the OOT module
mkdir build && cd build && cmake .. && make
# Install the module
sudo make install
