# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Tuple
from datetime import date

from spectre_core.logs import log_call
from spectre_core import wgetting

@log_call
def get_instrument_codes(
) -> list[str]:
    """Get all defined e-Callisto network station codes."""
    return [code.value for code in wgetting.CallistoInstrumentCode]


@log_call
def download_callisto_data(
    instrument_code: str,
    year: int, 
    month: int,
    day: int,
) -> Tuple[list[str], date]:
    """Download and decompress e-Callisto FITS files, saving them as `spectre` batch files.

    :param instrument_code: e-Callisto station instrument code.
    :param year: Year of the observation.
    :param month: Month of the observation.
    :param day: Day of the observation.
    :return: A list of file paths of all newly created batch files, as absolute paths within 
    the container's file system. Additionally, return the start date shared by all batch files.
    """
    instr_code = wgetting.CallistoInstrumentCode(instrument_code)
    return wgetting.download_callisto_data(instr_code, 
                                           year,
                                           month,
                                           day)
