#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Clone the repository
git clone https://github.com/jcfitzpatrick12/spectre.git
# cd into the cloned repo
cd spectre
# Checkout a specific branch
# git checkout sweep-logic
# # Checkout a specific commit within the branch
# git checkout <commit hash>
# install the requirements for spectre-host
cd host/
pip install -r requirements.txt