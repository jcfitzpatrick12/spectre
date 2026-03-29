# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from gnuradio import sdrplay3
from gnuradio import spectre

import spectre_server.core.fields

from ._base import Base, BaseModel
from ._constants import FlowgraphConstant


class RSP1BFixedCenterFrequencyModel(BaseModel):
    sample_rate: spectre_server.core.fields.Field.sample_rate = 2e6
    batch_size: spectre_server.core.fields.Field.batch_size = 3
    center_frequency: spectre_server.core.fields.Field.center_frequency = 95.8e6
    bandwidth: spectre_server.core.fields.Field.bandwidth = 1.536e6
    if_gain: spectre_server.core.fields.Field.if_gain = -30
    rf_gain: spectre_server.core.fields.Field.rf_gain = 0
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class RSP1BFixedCenterFrequency(Base[RSP1BFixedCenterFrequencyModel]):
    def configure(self, tag: str, model: RSP1BFixedCenterFrequencyModel) -> None:
        self.spectre_batched_file_sink = spectre.batched_file_sink(
            self._batches_dir_path,
            tag,
            model.output_type,
            model.batch_size,
            model.sample_rate,
            FlowgraphConstant.GROUP_BY_DATE,
        )
        self.sdrplay3_rsp1b = sdrplay3.rsp1b(
            "",
            stream_args=sdrplay3.stream_args(
                output_type=model.output_type, channels_size=1
            ),
        )
        self.sdrplay3_rsp1b.set_sample_rate(model.sample_rate)
        self.sdrplay3_rsp1b.set_center_freq(model.center_frequency)
        self.sdrplay3_rsp1b.set_bandwidth(model.bandwidth)
        self.sdrplay3_rsp1b.set_gain_mode(False)
        self.sdrplay3_rsp1b.set_gain(model.if_gain, "IF")
        self.sdrplay3_rsp1b.set_gain(model.rf_gain, "RF")
        self.sdrplay3_rsp1b.set_freq_corr(0)
        self.sdrplay3_rsp1b.set_dc_offset_mode(False)
        self.sdrplay3_rsp1b.set_iq_balance_mode(False)
        self.sdrplay3_rsp1b.set_agc_setpoint(-30)
        self.sdrplay3_rsp1b.set_rf_notch_filter(False)
        self.sdrplay3_rsp1b.set_dab_notch_filter(False)
        self.sdrplay3_rsp1b.set_biasT(False)
        self.sdrplay3_rsp1b.set_debug_mode(False)
        self.sdrplay3_rsp1b.set_sample_sequence_gaps_check(False)
        self.sdrplay3_rsp1b.set_show_gain_changes(False)

        self.connect((self.sdrplay3_rsp1b, 0), (self.spectre_batched_file_sink, 0))
