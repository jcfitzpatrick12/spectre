# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple
from scipy.signal import ShortTimeFFT, get_window
import matplotlib.pyplot as plt

from spectre.chunks.SPECTREChunk import SPECTREChunk
from spectre.chunks.chunk_register import register_chunk
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.chunks.library.sweep.HdrChunk import HdrChunk
from spectre.chunks.library.default.BinChunk import BinChunk
from spectre.chunks.library.default.FitsChunk import FitsChunk

@register_chunk('sweep')
class Chunk(SPECTREChunk):
    def __init__(self, chunk_start_time, tag):
        super().__init__(chunk_start_time, tag)

        self.bin = BinChunk(chunk_start_time, tag)
        self.fits = FitsChunk(chunk_start_time, tag)
        self.hdr = HdrChunk(chunk_start_time, tag)


    # ! TO BE IMPLEMENTED ! # 
    def build_spectrogram(self) -> Spectrogram:
        return