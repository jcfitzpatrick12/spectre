# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from gnuradio import spectre
from gnuradio import soapy

import spectre_server.core.fields

from ._base import Base, BaseModel
from ._constants import FlowgraphConstant


class RTLSDRFixedCenterFrequencyModel(BaseModel):
    sample_rate: spectre_server.core.fields.Field.sample_rate = 1536000
    center_frequency: spectre_server.core.fields.Field.center_frequency = 95.8e6
    rf_gain: spectre_server.core.fields.Field.rf_gain = 30
    batch_size: spectre_server.core.fields.Field.batch_size = 3
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class RTLSDRFixedCenterFrequency(Base[RTLSDRFixedCenterFrequencyModel]):
    def configure(self, tag: str, model: RTLSDRFixedCenterFrequencyModel) -> None:
        device = "driver=rtlsdr"
        type = model.output_type
        nchan = 1
        dev_args = ""
        stream_args = ""
        tune_args = [""]
        settings = [""]
        self.soapy_rtlsdr_source = soapy.source(
            device, type, nchan, dev_args, stream_args, tune_args, settings
        )
        self.soapy_rtlsdr_source.set_sample_rate(0, model.sample_rate)
        self.soapy_rtlsdr_source.set_gain_mode(0, False)
        self.soapy_rtlsdr_source.set_frequency(0, model.center_frequency)
        self.soapy_rtlsdr_source.set_frequency_correction(0, 0)
        self.soapy_rtlsdr_source.set_gain(0, model.rf_gain)
        self.spectre_batched_file_sink = spectre.batched_file_sink(
            self._batches_dir_path,
            tag,
            model.output_type,
            model.batch_size,
            model.sample_rate,
            FlowgraphConstant.GROUP_BY_DATE,
        )
        self.connect((self.soapy_rtlsdr_source, 0), (self.spectre_batched_file_sink, 0))
