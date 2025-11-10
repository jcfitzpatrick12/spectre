# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import spectre_core.logs
import spectre_core.wgetting


@spectre_core.logs.log_call
def get_instrument_codes() -> list[str]:
    """Get all defined e-Callisto network station codes."""
    return [code.value for code in spectre_core.wgetting.CallistoInstrumentCode]


@spectre_core.logs.log_call
def download_callisto_data(
    instrument_codes: list[str],
    year: int,
    month: int,
    day: int,
) -> list[str]:
    """Download and decompress e-Callisto FITS files, and save them as batch files.

    :param instrument_codes: A list of e-Callisto station instrument codes.
    :param year: Year of the observation.
    :param month: Month of the observation.
    :param day: Day of the observation.
    :return: A list of file paths of all newly created batch files, as absolute paths within the container's file system.
    """
    codes = [
        spectre_core.wgetting.CallistoInstrumentCode(code) for code in instrument_codes
    ]

    batch_file_paths = []
    for code in codes:
        new_batch_files = spectre_core.wgetting.download_callisto_data(
            code, year, month, day
        )
        batch_file_paths += new_batch_files
    return batch_file_paths
