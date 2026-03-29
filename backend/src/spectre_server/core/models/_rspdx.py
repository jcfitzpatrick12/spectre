# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.events
import spectre_server.core.flowgraphs

from ._validators import (
    skip_validator,
    validate_window_size,
    validate_window_type,
    validate_one_of,
    validate_non_overlapping_steps,
    validate_num_samples_per_step,
    validate_nyquist_criterion,
    validate_num_steps_per_sweep,
)
from ._sdrplay_validators import (
    validate_bandwidth,
    validate_center_frequency,
    validate_if_gain,
    validate_low_if_sample_rate,
    validate_rf_gain,
    validate_sample_rate,
    validate_constant_lna_state,
    validate_output_type,
)


def _get_rf_gains(center_frequency: float) -> list[int]:
    # Assume HDR mode is false.
    # Some nasty black formatting, but we move.
    if center_frequency <= 12e6:
        return [
            0,
            -3,
            -6,
            -9,
            -12,
            -15,
            -24,
            -27,
            -30,
            -33,
            -36,
            -39,
            -42,
            -45,
            -48,
            -51,
            -54,
            -57,
            -60,
        ]
    elif center_frequency <= 50e6:
        return [
            0,
            -3,
            -6,
            -9,
            -12,
            -15,
            -18,
            -24,
            -27,
            -30,
            -33,
            -36,
            -39,
            -42,
            -45,
            -48,
            -51,
            -54,
            -57,
            -60,
        ]
    elif center_frequency <= 60e6:
        return [
            0,
            -3,
            -6,
            -9,
            -12,
            -20,
            -23,
            -26,
            -29,
            -32,
            -35,
            -38,
            -44,
            -47,
            -50,
            -53,
            -56,
            -59,
            -62,
            -65,
            -68,
            -71,
            -74,
            -77,
            -80,
        ]
    elif center_frequency <= 250e6:
        return [
            0,
            -3,
            -6,
            -9,
            -12,
            -15,
            -24,
            -27,
            -30,
            -33,
            -36,
            -39,
            -42,
            -45,
            -48,
            -51,
            -54,
            -57,
            -60,
            -63,
            -66,
            -69,
            -72,
            -75,
            -78,
            -81,
            -84,
        ]
    elif center_frequency <= 420e6:
        return [
            0,
            -3,
            -6,
            -9,
            -12,
            -15,
            -18,
            -24,
            -27,
            -30,
            -33,
            -36,
            -39,
            -42,
            -45,
            -48,
            -51,
            -54,
            -57,
            -60,
            -63,
            -66,
            -69,
            -72,
            -75,
            -78,
            -81,
            -84,
        ]
    elif center_frequency <= 1000e6:
        return [
            0,
            -7,
            -10,
            -13,
            -16,
            -19,
            -22,
            -25,
            -31,
            -34,
            -37,
            -40,
            -43,
            -46,
            -49,
            -52,
            -55,
            -58,
            -61,
            -64,
            -67,
        ]
    elif center_frequency <= 2000e6:
        return [
            0,
            -5,
            -8,
            -11,
            -14,
            -17,
            -20,
            -32,
            -35,
            -38,
            -41,
            -44,
            -47,
            -50,
            -53,
            -56,
            -59,
            -62,
            -65,
        ]
    else:
        return []


class RSPdxFixedCenterFrequency(
    spectre_server.core.flowgraphs.RSPdxFixedCenterFrequencyModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_one_of(
            self.antenna_port,
            [
                spectre_server.core.flowgraphs.RSPdxPort.ANT_A,
                spectre_server.core.flowgraphs.RSPdxPort.ANT_B,
            ],
            name="antenna_port",
        )
        validate_nyquist_criterion(self.sample_rate, self.bandwidth)
        validate_center_frequency(self.center_frequency)
        validate_window_size(self.window_size)
        validate_window_type(self.window_type)
        validate_sample_rate(self.sample_rate)
        validate_bandwidth(self.bandwidth)
        validate_if_gain(self.if_gain)
        validate_output_type(self.output_type)
        validate_low_if_sample_rate(self.sample_rate)
        validate_rf_gain(self.rf_gain, _get_rf_gains(self.center_frequency))
        return self


class RSPdxSweptCenterFrequency(
    spectre_server.core.flowgraphs.RSPdxSweptCenterFrequencyModel,
    spectre_server.core.events.SweptCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_one_of(
            self.antenna_port,
            [
                spectre_server.core.flowgraphs.RSPdxPort.ANT_A,
                spectre_server.core.flowgraphs.RSPdxPort.ANT_B,
            ],
            name="antenna_port",
        )
        validate_center_frequency(self.min_frequency)
        validate_center_frequency(self.max_frequency)
        validate_window_size(self.window_size)
        validate_window_type(self.window_type)
        validate_sample_rate(self.sample_rate)
        validate_bandwidth(self.bandwidth)
        validate_if_gain(self.if_gain)
        validate_output_type(self.output_type)
        validate_low_if_sample_rate(self.sample_rate)
        validate_non_overlapping_steps(self.frequency_hop, self.sample_rate)
        validate_num_samples_per_step(
            self.window_size, self.dwell_time, self.sample_rate
        )
        validate_num_steps_per_sweep(
            self.min_frequency, self.max_frequency, self.frequency_hop
        )
        validate_constant_lna_state(
            self.min_frequency, self.max_frequency, _get_rf_gains
        )
        return self
