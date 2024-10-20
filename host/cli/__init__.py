# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.logging import PROCESS_TYPES

__app_name__ = "spectre"
__version__ = "0.0.0"


RECEIVER_NAME_HELP = "The name of the receiver"
MODE_HELP = "The operating mode for the receiver"

TAG_HELP = "The capture config tag"
TAGS_HELP = "The capture config tags"

SECONDS_HELP = "Seconds component of the session duration"
MINUTES_HELP = "Minutes component of the session duration"
HOURS_HELP = "Hours component of the session duration"

DAY_HELP = "Day of the month (numeric)"
MONTH_HELP = "Month of the year (numeric)"
YEAR_HELP = "Year (numeric)"

FORCE_RESTART_HELP = "If a worker process stops unexpectedly, terminate all subprocesses and restart the capture session"
PARAMS_HELP = "Pass arbitrary key-value pairs"
PROCESS_TYPE_HELP = f"Processes may be one of {PROCESS_TYPES}"

EXTENSIONS_HELP = "File extensions"

SUPPRESS_DOUBLECHECK_HELP = "Suppress doublecheck prompts on file operations"

PID_HELP = "Process ID"
FILE_NAME_HELP = "File name (specified without extension)"
AS_COMMAND_HELP = "Output is expressed as a runnable command"

INSTRUMENT_CODE_HELP = "The case-sensitive CALLISTO instrument code"