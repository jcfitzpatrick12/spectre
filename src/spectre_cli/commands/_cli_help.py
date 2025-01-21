# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

@dataclass(frozen=True)
class CliHelp:
    RECEIVER_NAME       = "The name of the receiver."
    MODE                = "The operating mode for the receiver."
    TAG                 = "The tag identifier for the data."
    SECONDS             = "Seconds component of the session duration."
    MINUTES             = "Minutes component of the session duration."
    HOURS               = "Hours component of the session duration."
    DAY                 = "Numeric day of the month."
    MONTH               = "Numeric month of the year."
    YEAR                = "Numeric year."
    FORCE_RESTART       = (
        "When a worker process stops unexpectedly, terminate all workers "
        "and restart."
    )
    FORCE_UPDATE        = (
        "Force configuration files to update, even if batches exist under "
        "the given tag."
    )
    PARAM               = "Capture config parameters as key-value pairs."
    PROCESS_TYPE        = "Specifies one of 'worker' or 'user'."
    EXTENSIONS          = "The file extension."
    FORCE               = "Forcibly ignore user warnings."
    PID                 = "The process ID."
    INSTRUMENT_CODE     = "The case-sensitive e-Callisto station instrument codes."
    ABSOLUTE_TOLERANCE  = (
        "The absolute tolerance to which we consider 'agreement' with the "
        "analytical solution for each spectral component. See the 'atol' "
        "keyword argument for np.isclose."
    )
    PER_SPECTRUM        = "Show validated status per spectrum."
    PARAMETER_NAME      = "The name of the parameter."