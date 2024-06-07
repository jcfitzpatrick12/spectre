#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

git clone https://github.com/jcfitzpatrick12/gr-spectre.git
#cd into the cloned repo
cd gr-spectre
#built the OOT module
mkdir build && cd build && cmake .. && make
sudo make install

