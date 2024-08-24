#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Clone the repository
git clone https://github.com/fventuri/gr-sdrplay3.git
# cd into the cloned repo
cd gr-sdrplay3
# Checkout a specific branch
git checkout message-passing
# Checkout a specific commit within the branch
# git checkout <commit hash>
# Build the OOT module
mkdir build && cd build && cmake .. && make
# Install the module
sudo make install

