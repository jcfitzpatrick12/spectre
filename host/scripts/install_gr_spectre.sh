#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Clone the repository
git clone https://github.com/jcfitzpatrick12/gr-spectre.git
# cd into the cloned repo
cd gr-spectre
# Checkout a specific branch
git checkout sweep-logic
# Checkout a specific commit within the branch
git checkout 0a4414cc5fcf91ab55039e519ff4398cf182399e
# Build the OOT module
mkdir build && cd build && cmake .. && make
# Install the module
sudo make install
