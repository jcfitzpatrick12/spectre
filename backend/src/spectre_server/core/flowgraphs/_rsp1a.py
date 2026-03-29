# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from gnuradio import sdrplay3
from gnuradio import spectre

import spectre_server.core.fields

from ._base import Base, BaseModel
from ._constants import FlowgraphConstant


class RSP1AFixedCenterFrequencyModel(BaseModel):
    sample_rate: spectre_server.core.fields.Field.sample_rate = 2e6
    batch_size: spectre_server.core.fields.Field.batch_size = 3
    center_frequency: spectre_server.core.fields.Field.center_frequency = 95.8e6
    bandwidth: spectre_server.core.fields.Field.bandwidth = 1.536e6
    if_gain: spectre_server.core.fields.Field.if_gain = -30
    rf_gain: spectre_server.core.fields.Field.rf_gain = 0
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class RSP1AFixedCenterFrequency(Base[RSP1AFixedCenterFrequencyModel]):
    def configure(self, tag: str, model: RSP1AFixedCenterFrequencyModel) -> None:
        self.spectre_batched_file_sink = spectre.batched_file_sink(
            self._batches_dir_path,
            tag,
            model.output_type,
            model.batch_size,
            model.sample_rate,
            FlowgraphConstant.GROUP_BY_DATE,
        )
        self.sdrplay3_rsp1a = sdrplay3.rsp1a(
            "",
            stream_args=sdrplay3.stream_args(
                output_type=model.output_type, channels_size=1
            ),
        )
        self.sdrplay3_rsp1a.set_sample_rate(model.sample_rate)
        self.sdrplay3_rsp1a.set_center_freq(model.center_frequency)
        self.sdrplay3_rsp1a.set_bandwidth(model.bandwidth)
        self.sdrplay3_rsp1a.set_gain_mode(False)
        self.sdrplay3_rsp1a.set_gain(model.if_gain, "IF")
        self.sdrplay3_rsp1a.set_gain(model.rf_gain, "RF")
        self.sdrplay3_rsp1a.set_freq_corr(0)
        self.sdrplay3_rsp1a.set_dc_offset_mode(False)
        self.sdrplay3_rsp1a.set_iq_balance_mode(False)
        self.sdrplay3_rsp1a.set_agc_setpoint(-30)
        self.sdrplay3_rsp1a.set_rf_notch_filter(False)
        self.sdrplay3_rsp1a.set_dab_notch_filter(False)
        self.sdrplay3_rsp1a.set_biasT(False)
        self.sdrplay3_rsp1a.set_debug_mode(False)
        self.sdrplay3_rsp1a.set_sample_sequence_gaps_check(False)
        self.sdrplay3_rsp1a.set_show_gain_changes(False)

        self.connect((self.sdrplay3_rsp1a, 0), (self.spectre_batched_file_sink, 0))


class RSP1ASweptCenterFrequencyModel(BaseModel):
    sample_rate: spectre_server.core.fields.Field.sample_rate = 2e6
    batch_size: spectre_server.core.fields.Field.batch_size = 3
    bandwidth: spectre_server.core.fields.Field.bandwidth = 1.536e6
    if_gain: spectre_server.core.fields.Field.if_gain = -30
    rf_gain: spectre_server.core.fields.Field.rf_gain = 0
    min_frequency: spectre_server.core.fields.Field.min_frequency = 95e6
    max_frequency: spectre_server.core.fields.Field.max_frequency = 100e6
    dwell_time: spectre_server.core.fields.Field.dwell_time = 0.15
    frequency_hop: spectre_server.core.fields.Field.frequency_hop = 2e6
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class RSP1ASweptCenterFrequency(Base[RSP1ASweptCenterFrequencyModel]):
    def configure(self, tag: str, model: RSP1ASweptCenterFrequencyModel) -> None:

        retune_cmd_name = "freq"
        self.spectre_frequency_sweeper = spectre.frequency_sweeper(
            model.min_frequency,
            model.max_frequency,
            model.frequency_hop,
            model.dwell_time,
            model.sample_rate,
            retune_cmd_name,
            model.output_type,
        )

        is_tagged = True
        frequency_tag_key = "freq"
        self.spectre_batched_file_sink = spectre.batched_file_sink(
            self._batches_dir_path,
            tag,
            model.output_type,
            model.batch_size,
            model.sample_rate,
            FlowgraphConstant.GROUP_BY_DATE,
            is_tagged,
            frequency_tag_key,
            model.min_frequency,
        )
        self.sdrplay3_rsp1a = sdrplay3.rsp1a(
            "",
            stream_args=sdrplay3.stream_args(
                output_type=model.output_type, channels_size=1
            ),
        )
        self.sdrplay3_rsp1a.set_sample_rate(model.sample_rate, True)
        self.sdrplay3_rsp1a.set_center_freq(model.min_frequency, True)
        self.sdrplay3_rsp1a.set_bandwidth(model.bandwidth)
        self.sdrplay3_rsp1a.set_gain_mode(False)
        self.sdrplay3_rsp1a.set_gain(model.if_gain, "IF", True)
        self.sdrplay3_rsp1a.set_gain(model.rf_gain, "RF", True)
        self.sdrplay3_rsp1a.set_freq_corr(0)
        self.sdrplay3_rsp1a.set_dc_offset_mode(False)
        self.sdrplay3_rsp1a.set_iq_balance_mode(False)
        self.sdrplay3_rsp1a.set_agc_setpoint(-30)
        self.sdrplay3_rsp1a.set_rf_notch_filter(False)
        self.sdrplay3_rsp1a.set_dab_notch_filter(False)
        self.sdrplay3_rsp1a.set_biasT(False)
        self.sdrplay3_rsp1a.set_stream_tags(True)
        self.sdrplay3_rsp1a.set_debug_mode(False)
        self.sdrplay3_rsp1a.set_sample_sequence_gaps_check(False)
        self.sdrplay3_rsp1a.set_show_gain_changes(False)

        self.msg_connect(
            (self.spectre_frequency_sweeper, "retune_command"),
            (self.sdrplay3_rsp1a, "command"),
        )
        self.connect((self.sdrplay3_rsp1a, 0), (self.spectre_batched_file_sink, 0))
        self.connect((self.sdrplay3_rsp1a, 0), (self.spectre_frequency_sweeper, 0))
