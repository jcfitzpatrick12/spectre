#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# clone the message passing branch
git clone -b message-passing --single-branch https://github.com/fventuri/gr-sdrplay3.git
#cd into the cloned repo
cd gr-sdrplay3
#built the OOT module
mkdir build && cd build && cmake .. && make
sudo make install

