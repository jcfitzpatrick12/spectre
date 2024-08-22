#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import sdrplay3
from gnuradio import spectre

from cfg import CONFIG




class tuner_1_sweep(gr.top_block):
    def __init__(self, capture_config: dict):
        gr.top_block.__init__(self, "tuner-1-sweep", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        samp_rate = capture_config['samp_rate']
        bandwidth = capture_config['bandwidth']
        min_freq = capture_config['min_freq']
        max_freq = capture_config['max_freq']
        freq_step = capture_config['freq_step']
        samples_per_step = capture_config['samples_per_step']
        IF_gain = capture_config['IF_gain']
        RF_gain = capture_config['RF_gain']
        chunk_size = capture_config['chunk_size']
        start_freq = min_freq + samp_rate/2


        ##################################################
        # Blocks
        ##################################################
        self.spectre_sweep_driver_0 = spectre.sweep_driver(min_freq, 
                                                           max_freq, 
                                                           freq_step, 
                                                           samp_rate, 
                                                           samples_per_step,
                                                           'freq')
        self.spectre_batched_file_sink_0 = spectre.batched_file_sink(CONFIG.path_to_chunks_dir, 
                                                                     'sweep-test', 
                                                                     chunk_size, 
                                                                     samp_rate, 
                                                                     True, 
                                                                     'freq', 
                                                                     start_freq)
        self.sdrplay3_rspduo_0 = sdrplay3.rspduo(
            '',
            rspduo_mode="Single Tuner",
            antenna="Tuner 1 50 ohm",
            stream_args=sdrplay3.stream_args(
                output_type='fc32',
                channels_size=1
            ),
        )
        self.sdrplay3_rspduo_0.set_sample_rate(samp_rate, True)
        self.sdrplay3_rspduo_0.set_center_freq(start_freq, True)
        self.sdrplay3_rspduo_0.set_bandwidth(bandwidth)
        self.sdrplay3_rspduo_0.set_antenna("Tuner 1 50 ohm")
        self.sdrplay3_rspduo_0.set_gain_mode(False)
        self.sdrplay3_rspduo_0.set_gain(IF_gain, 'IF', True)
        self.sdrplay3_rspduo_0.set_gain(RF_gain, 'RF', True)
        self.sdrplay3_rspduo_0.set_freq_corr(0)
        self.sdrplay3_rspduo_0.set_dc_offset_mode(False)
        self.sdrplay3_rspduo_0.set_iq_balance_mode(False)
        self.sdrplay3_rspduo_0.set_agc_setpoint(-30)
        self.sdrplay3_rspduo_0.set_rf_notch_filter(False)
        self.sdrplay3_rspduo_0.set_dab_notch_filter(True)
        self.sdrplay3_rspduo_0.set_am_notch_filter(False)
        self.sdrplay3_rspduo_0.set_biasT(False)
        self.sdrplay3_rspduo_0.set_stream_tags(True)
        self.sdrplay3_rspduo_0.set_debug_mode(False)
        self.sdrplay3_rspduo_0.set_sample_sequence_gaps_check(False)
        self.sdrplay3_rspduo_0.set_show_gain_changes(False)
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_gr_complex*1, 'freq', "freq")
        self.blocks_tag_debug_0.set_display(True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.spectre_sweep_driver_0, 'freq'), (self.sdrplay3_rspduo_0, 'freq'))
        self.connect((self.sdrplay3_rspduo_0, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.sdrplay3_rspduo_0, 0), (self.spectre_batched_file_sink_0, 0))
        self.connect((self.sdrplay3_rspduo_0, 0), (self.spectre_sweep_driver_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.sdrplay3_rspduo_0.set_sample_rate(self.samp_rate, True)




def main(capture_config: dict, top_block_cls=tuner_1_sweep, options=None):
    tb = top_block_cls(capture_config)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()

