# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from host.cli import spectre_cli, __app_name__

def main():
    spectre_cli.app(prog_name=__app_name__)

if __name__ == "__main__":
    main()