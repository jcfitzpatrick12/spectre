# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import typing

import numpy as np

import spectre_server.core.batches
import spectre_server.core.spectrograms
import spectre_server.core.fields

from ._base import Base, BaseModel
from ._stfft import (
    get_buffer,
    get_window,
    get_times,
    get_num_spectrums,
    get_frequencies,
    get_fftw_obj,
    stfft,
)

_LOGGER = logging.getLogger(__name__)

# CALLISTO 8-bit digit ratio: D / V * C, with D=255 digits, V=2500 mV ADC range,
# C=25.4 mV/dB detector slope (manual §4.2). Preserved so '1 digit ~= 0.1 dB' holds across stations.
CALLISTO_DIGIT_PER_DB = 255.0 * 25.4 / 2500.0


class ECallistoModel(BaseModel):
    window_size: spectre_server.core.fields.Field.window_size = 512
    window_hop: spectre_server.core.fields.Field.window_hop = 512
    window_type: spectre_server.core.fields.Field.window_type = (
        spectre_server.core.fields.WindowType.HANN
    )
    center_frequency: spectre_server.core.fields.Field.center_frequency = 32e6
    sample_rate: spectre_server.core.fields.Field.sample_rate = 64e6
    frequency_resolution: spectre_server.core.fields.Field.frequency_resolution = 0
    time_resolution: spectre_server.core.fields.Field.time_resolution = 0.25
    batch_size: spectre_server.core.fields.Field.batch_size = 900
    keep_signal: spectre_server.core.fields.Field.keep_signal = True
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )
    scaling_factor: spectre_server.core.fields.Field.scaling_factor = 1.0
    object: spectre_server.core.fields.Field.object_ = "Sun"


class ECallisto(Base[ECallistoModel, spectre_server.core.batches.ECallistoBatch]):
    def __init__(
        self,
        tag: str,
        model: ECallistoModel,
        batch_cls: typing.Type[spectre_server.core.batches.ECallistoBatch],
    ) -> None:
        super().__init__(tag, model, batch_cls)
        self.__model = model

        self.__window = get_window(self.__model.window_type, self.__model.window_size)
        self.__buffer = get_buffer(self.__model.window_size)
        # Defer the FFTW plan to the first batch (see FixedCenterFrequency for rationale).
        self.__fftw_obj = None
        self.__output_type = self.__model.output_type

    @property
    def _watch_extension(self) -> str:
        return self.__output_type

    def process(
        self, batch: spectre_server.core.batches.ECallistoBatch
    ) -> spectre_server.core.spectrograms.Spectrogram:
        """Compute an e-CALLISTO digit spectrogram from a batch of IQ samples.

        Mirrors the reference port (AlexandroRP99/e-Callisto_Py_RX-888_MK_II): integrate in
        linear amplitude via Spectre's time/frequency averaging, then convert amplitude -> dB
        -> 8-bit digits. Storage quantisation to uint8 happens at FITS write time.
        """
        _LOGGER.info("Reading the I/Q samples")
        iq_data = batch.read_iq(self.__output_type)

        if self.__fftw_obj is None:
            _LOGGER.info("Creating the FFTW plan")
            self.__fftw_obj = get_fftw_obj(self.__buffer)

        _LOGGER.info("Executing the short-time FFT")
        amplitude_spectra = stfft(
            self.__fftw_obj,
            self.__buffer,
            iq_data,
            self.__window,
            self.__model.window_hop,
        )
        amplitude_spectra = np.fft.fftshift(amplitude_spectra, axes=0)

        num_spectrums = get_num_spectrums(
            iq_data.size, self.__model.window_size, self.__model.window_hop
        )
        times = get_times(
            num_spectrums, self.__model.sample_rate, self.__model.window_hop
        )
        frequencies = (
            np.fft.fftshift(
                get_frequencies(self.__model.window_size, self.__model.sample_rate)
            )
            + self.__model.center_frequency
        )

        amplitude_spectrogram = spectre_server.core.spectrograms.Spectrogram(
            amplitude_spectra,
            times,
            frequencies,
            spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
            batch.start_datetime,
        )
        amplitude_spectrogram = spectre_server.core.spectrograms.time_average(
            amplitude_spectrogram,
            max(self.__model.time_resolution, amplitude_spectrogram.time_resolution),
        )
        amplitude_spectrogram = spectre_server.core.spectrograms.frequency_average(
            amplitude_spectrogram,
            max(
                self.__model.frequency_resolution,
                amplitude_spectrogram.frequency_resolution,
            ),
        )

        scaled = amplitude_spectrogram.dynamic_spectra * self.__model.scaling_factor
        dB = 10.0 * np.log10(np.maximum(scaled, np.finfo(np.float32).tiny))
        digits = np.clip(dB * CALLISTO_DIGIT_PER_DB, 0, 255).astype(np.float32)

        if not self.__model.keep_signal:
            _LOGGER.info("Deleting the I/Q samples")
            batch.delete_iq(self.__output_type)

        return spectre_server.core.spectrograms.Spectrogram(
            digits,
            amplitude_spectrogram.times,
            amplitude_spectrogram.frequencies,
            spectre_server.core.spectrograms.SpectrumUnit.CALLISTO_DIGITS,
            batch.start_datetime,
        )
