#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.1.1

# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import spectre

from spectre.cfg import (
    CHUNKS_DIR_PATH
)

class cosine_signal_1(gr.top_block):

    def __init__(self, capture_config: dict[str, Any]):
        gr.top_block.__init__(self, "cosine-signal-1", catch_exceptions=True)

        ##################################################
        # Unpack capture config
        ##################################################
        samp_rate = capture_config['samp_rate']
        tag = capture_config['tag']
        chunk_size = capture_config['chunk_size']
        frequency = capture_config['frequency']
        amplitude = capture_config['amplitude']

        ##################################################
        # Blocks
        ##################################################
        self.spectre_batched_file_sink_0 = spectre.batched_file_sink(CHUNKS_DIR_PATH, tag, chunk_size, samp_rate)
        self.blocks_throttle_0_1 = blocks.throttle(gr.sizeof_float*1, samp_rate,True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*1, samp_rate,True)
        self.blocks_null_source_1 = blocks.null_source(gr.sizeof_float*1)
        self.blocks_float_to_complex_1 = blocks.float_to_complex(1)
        self.analog_sig_source_x_0 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, frequency, amplitude, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_float_to_complex_1, 0), (self.spectre_batched_file_sink_0, 0))
        self.connect((self.blocks_null_source_1, 0), (self.blocks_throttle_0_1, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_float_to_complex_1, 0))
        self.connect((self.blocks_throttle_0_1, 0), (self.blocks_float_to_complex_1, 1))


def main(capture_config: dict[str, Any], top_block_cls=cosine_signal_1, options=None):
    tb = top_block_cls(capture_config)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()
