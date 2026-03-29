# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
from gnuradio import spectre

import spectre_server.core.fields

from ._base import Base, BaseModel
from ._constants import FlowgraphConstant


class SignalGeneratorCosineWaveModel(BaseModel):
    sample_rate: spectre_server.core.fields.Field.sample_rate = 128e3
    batch_size: spectre_server.core.fields.Field.batch_size = 1
    frequency: spectre_server.core.fields.Field.frequency = 32e3
    amplitude: spectre_server.core.fields.Field.amplitude = 1
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class SignalGeneratorCosineWave(Base[SignalGeneratorCosineWaveModel]):
    def configure(self, tag: str, model: SignalGeneratorCosineWaveModel) -> None:
        """Record a complex-valued cosine signal."""
        self.spectre_batched_file_sink = spectre.batched_file_sink(
            self._batches_dir_path,
            tag,
            model.output_type,
            model.batch_size,
            model.sample_rate,
            FlowgraphConstant.GROUP_BY_DATE,
        )
        self.blocks_throttle_0 = blocks.throttle(
            gr.sizeof_float * 1, model.sample_rate, True
        )
        self.blocks_throttle_1 = blocks.throttle(
            gr.sizeof_float * 1, model.sample_rate, True
        )
        self.blocks_null_source = blocks.null_source(gr.sizeof_float * 1)
        self.blocks_float_to_complex = blocks.float_to_complex(1)

        self.analog_sig_source = analog.sig_source_f(
            model.sample_rate,
            analog.GR_COS_WAVE,
            model.frequency,
            model.amplitude,
        )

        self.connect((self.analog_sig_source, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_null_source, 0), (self.blocks_throttle_1, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_float_to_complex, 0))
        self.connect((self.blocks_throttle_1, 0), (self.blocks_float_to_complex, 1))
        self.connect(
            (self.blocks_float_to_complex, 0), (self.spectre_batched_file_sink, 0)
        )


class SignalGeneratorConstantStaircaseModel(BaseModel):
    step_increment: spectre_server.core.fields.Field.step_increment = 200
    sample_rate: spectre_server.core.fields.Field.sample_rate = 128000
    min_samples_per_step: spectre_server.core.fields.Field.min_samples_per_step = 4000
    max_samples_per_step: spectre_server.core.fields.Field.max_samples_per_step = 5000
    frequency_hop: spectre_server.core.fields.Field.frequency_hop = 128000
    batch_size: spectre_server.core.fields.Field.batch_size = 1
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class SignalGeneratorConstantStaircase(Base[SignalGeneratorConstantStaircaseModel]):
    def configure(self, tag: str, model: SignalGeneratorConstantStaircaseModel) -> None:
        """Record a constant signal that periodically increments in value.
        Each step increases in duration, up to a maximum, before resetting."""
        self.spectre_constant_staircase = spectre.tagged_staircase(
            model.min_samples_per_step,
            model.max_samples_per_step,
            model.frequency_hop,
            model.step_increment,
            model.sample_rate,
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
            FlowgraphConstant.NO_INITIAL_TAG_VALUE,
        )
        self.blocks_throttle = blocks.throttle(
            gr.sizeof_gr_complex * 1, model.sample_rate
        )

        self.connect((self.spectre_constant_staircase, 0), (self.blocks_throttle, 0))
        self.connect((self.blocks_throttle, 0), (self.spectre_batched_file_sink, 0))
