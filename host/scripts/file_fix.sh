#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

######## Note ##########
# file fix is required on both raspberry pi and standard x86 architectures
# but the directory where we need to move the files from is system dependent
# this script detects the architecture and changes the suffix directory dynamically
########################

# Define source and destination directories
source_dir="/usr/local/lib/$(uname -m)-linux-gnu"
dest_dir="/usr/lib/${lib_dir_suffix}"

# Move files
mv "${source_dir}/"* "${dest_dir}/"
