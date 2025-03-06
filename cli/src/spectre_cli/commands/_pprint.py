# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml

def pprint_dict(
    d: dict
) -> None:
    print( yaml.dump(d, sort_keys=True, default_flow_style=False) )