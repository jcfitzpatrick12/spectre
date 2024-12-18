#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# start the capture session
spectre start session --tag rsp1a-fixed-example --hours 8 --force-restart
# deletes all remnant bin and hdr chunk files in all chunks subdirectories
spectre delete chunk-files --tag rsp1a-fixed-example --extension bin --extension hdr --force

