# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from host.cli import spectre_cli, __app_name__

def main():
    spectre_cli.app(prog_name=__app_name__)

if __name__ == "__main__":
    import cProfile
    import pstats

    # Profile and store the results in a file
    with cProfile.Profile() as pr:
        main()
    
    # Create Stats object and sort by cumulative time
    stats = pstats.Stats(pr)
    stats.sort_stats("cumulative").print_stats(20)  # Prints top 20 slowest functions
    # main()