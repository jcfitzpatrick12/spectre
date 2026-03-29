# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import time
import dataclasses

from gnuradio import spectre
from gnuradio import uhd

import spectre_server.core.fields

from ._base import Base, BaseModel
from ._constants import FlowgraphConstant


@dataclasses.dataclass(frozen=True)
class USRPWireFormat:
    """Indicates the form of the data over the bus/network."""

    SC8 = "sc8"
    SC12 = "sc12"
    SC16 = "sc16"


class USRPFixedCenterFrequencyModel(BaseModel):
    sample_rate: spectre_server.core.fields.Field.sample_rate = 600000
    batch_size: spectre_server.core.fields.Field.batch_size = 3
    center_frequency: spectre_server.core.fields.Field.center_frequency = 95.8e6
    bandwidth: spectre_server.core.fields.Field.bandwidth = 600000
    gain: spectre_server.core.fields.Field.gain = 35
    wire_format: spectre_server.core.fields.Field.wire_format = USRPWireFormat.SC12
    master_clock_rate: spectre_server.core.fields.Field.master_clock_rate = 60000000
    num_recv_frames: spectre_server.core.fields.Field.num_recv_frames = 32
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class USRPFixedCenterFrequency(Base[USRPFixedCenterFrequencyModel]):
    def configure(self, tag: str, model: USRPFixedCenterFrequencyModel) -> None:
        master_clock_rate = f"master_clock_rate={model.master_clock_rate}"
        num_recv_frames = f"num_recv_frames={model.num_recv_frames}"
        self.uhd_usrp_source = uhd.usrp_source(
            ",".join(("", "", master_clock_rate, num_recv_frames)),
            uhd.stream_args(
                cpu_format=model.output_type,
                otw_format=model.wire_format,
                args="",
                channels=[0],
            ),
        )
        self.uhd_usrp_source.set_samp_rate(model.sample_rate)
        self.uhd_usrp_source.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.uhd_usrp_source.set_center_freq(model.center_frequency, 0)
        self.uhd_usrp_source.set_bandwidth(model.bandwidth, 0)
        self.uhd_usrp_source.set_rx_agc(False, 0)
        self.uhd_usrp_source.set_auto_dc_offset(False, 0)
        self.uhd_usrp_source.set_auto_iq_balance(False, 0)
        self.uhd_usrp_source.set_gain(model.gain, 0)
        self.spectre_batched_file_sink = spectre.batched_file_sink(
            self._batches_dir_path,
            tag,
            model.output_type,
            model.batch_size,
            model.sample_rate,
            FlowgraphConstant.GROUP_BY_DATE,
        )
        self.connect((self.uhd_usrp_source, 0), (self.spectre_batched_file_sink, 0))


class USRPSweptCenterFrequencyModel(BaseModel):
    sample_rate: spectre_server.core.fields.Field.sample_rate = 2000000
    batch_size: spectre_server.core.fields.Field.batch_size = 3
    bandwidth: spectre_server.core.fields.Field.bandwidth = 2e6
    min_frequency: spectre_server.core.fields.Field.min_frequency = 95e6
    max_frequency: spectre_server.core.fields.Field.max_frequency = 101e6
    gain: spectre_server.core.fields.Field.gain = 35
    wire_format: spectre_server.core.fields.Field.wire_format = USRPWireFormat.SC12
    master_clock_rate: spectre_server.core.fields.Field.master_clock_rate = 60000000
    num_recv_frames: spectre_server.core.fields.Field.num_recv_frames = 32
    dwell_time: spectre_server.core.fields.Field.dwell_time = 0.15
    frequency_hop: spectre_server.core.fields.Field.frequency_hop = 2e6
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class USRPSweptCenterFrequency(Base[USRPSweptCenterFrequencyModel]):
    def configure(self, tag: str, model: USRPSweptCenterFrequencyModel) -> None:
        master_clock_rate = f"master_clock_rate={model.master_clock_rate}"
        num_recv_frames = f"num_recv_frames={model.num_recv_frames}"
        self.uhd_usrp_source = uhd.usrp_source(
            ",".join(("", "", master_clock_rate, num_recv_frames)),
            uhd.stream_args(
                cpu_format=model.output_type,
                otw_format=model.wire_format,
                args="",
                channels=[0],
            ),
        )
        self.uhd_usrp_source.set_samp_rate(model.sample_rate)
        self.uhd_usrp_source.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.uhd_usrp_source.set_center_freq(model.min_frequency, 0)
        self.uhd_usrp_source.set_bandwidth(model.bandwidth, 0)
        self.uhd_usrp_source.set_rx_agc(False, 0)
        self.uhd_usrp_source.set_auto_dc_offset(False, 0)
        self.uhd_usrp_source.set_auto_iq_balance(False, 0)
        self.uhd_usrp_source.set_gain(model.gain, 0)

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
        frequency_tag_key = "rx_freq"
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

        self.msg_connect(
            (self.spectre_frequency_sweeper, "retune_command"),
            (self.uhd_usrp_source, "command"),
        )
        self.connect((self.uhd_usrp_source, 0), (self.spectre_batched_file_sink, 0))
        self.connect((self.uhd_usrp_source, 0), (self.spectre_frequency_sweeper, 0))
