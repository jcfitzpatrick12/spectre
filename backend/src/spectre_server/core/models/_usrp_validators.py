# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import spectre_server.core.flowgraphs
import spectre_server.core.fields

from ._validators import validate_one_of

EXPECTED_OUTPUT_TYPES = ["fc32", "sc16"]


def validate_wire_format(wire_format: str) -> None:
    validate_one_of(
        wire_format,
        [
            spectre_server.core.flowgraphs.USRPWireFormat.SC8,
            spectre_server.core.flowgraphs.USRPWireFormat.SC12,
            spectre_server.core.flowgraphs.USRPWireFormat.SC16,
        ],
        "wire_format",
    )


def validate_output_type(output_type: str) -> None:
    """Checks the output type is supported."""
    validate_one_of(output_type, EXPECTED_OUTPUT_TYPES, "output_type")


def validate_sample_rate_with_master_clock_rate(
    sample_rate: float, master_clock_rate: int
) -> None:
    """Ensure that the master clock rate is an integer multiple of the sample rate."""
    if master_clock_rate % sample_rate != 0:
        raise ValueError(
            f"The master clock rate of {master_clock_rate} [Hz] is not an integer "
            f"multiple of the sample rate {sample_rate} [Hz]."
        )
