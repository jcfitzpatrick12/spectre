# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from gnuradio import spectre
from gnuradio import soapy

import spectre_server.core.fields

from ._base import Base, BaseModel
from ._constants import FlowgraphConstant


class HackRFFixedCenterFrequencyModel(BaseModel):
    sample_rate: spectre_server.core.fields.Field.sample_rate = 2e6
    bandwidth: spectre_server.core.fields.Field.bandwidth = 2e6
    center_frequency: spectre_server.core.fields.Field.center_frequency = 95.8e6
    amp_on: spectre_server.core.fields.Field.amp_on = False
    lna_gain: spectre_server.core.fields.Field.lna_gain = 20
    vga_gain: spectre_server.core.fields.Field.vga_gain = 20
    batch_size: spectre_server.core.fields.Field.batch_size = 3
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class HackRFFixedCenterFrequency(Base[HackRFFixedCenterFrequencyModel]):
    def configure(self, tag: str, model: HackRFFixedCenterFrequencyModel) -> None:
        device = "driver=hackrf"
        type = model.output_type
        nchan = 1
        dev_args = ""
        stream_args = ""
        tune_args = [""]
        settings = [""]
        self.soapy_hackrf_source = soapy.source(
            device, type, nchan, dev_args, stream_args, tune_args, settings
        )
        self.soapy_hackrf_source.set_sample_rate(0, model.sample_rate)
        self.soapy_hackrf_source.set_bandwidth(0, model.bandwidth)
        self.soapy_hackrf_source.set_frequency(0, model.center_frequency)
        self.soapy_hackrf_source.set_gain(0, "AMP", model.amp_on)
        self.soapy_hackrf_source.set_gain(0, "LNA", model.lna_gain)
        self.soapy_hackrf_source.set_gain(0, "VGA", model.vga_gain)

        self.spectre_batched_file_sink = spectre.batched_file_sink(
            self._batches_dir_path,
            tag,
            model.output_type,
            model.batch_size,
            model.sample_rate,
            FlowgraphConstant.GROUP_BY_DATE,
        )
        self.connect((self.soapy_hackrf_source, 0), (self.spectre_batched_file_sink, 0))
