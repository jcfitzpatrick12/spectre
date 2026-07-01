# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import datetime
import os
import typing

import numpy as np
import numpy.typing as npt
import astropy.io.fits

import spectre_server.core.spectrograms

from ._base import Base, BatchFile

ADC_DIGIT_RANGE = np.float32(255)  # [1]
ADC_VOLTAGE_RANGE = np.float32(2500)  # [mV]
DETECTOR_CONVERSION_RATE = np.float32(25.4)  # [mv/dB]
MIN_LINEAR_AMPLITUDE = np.finfo(np.float32).tiny


def callisto_digits_from_linear(
    dynamic_spectra: npt.NDArray[np.float32],
) -> npt.NDArray[np.uint8]:
    """Transform from linearised CALLISTO digits back to digits.

    NOTE: The narrowing conversion introduces quantisation errors, but that's unavoidable since
    we must preserve compatibility with e-Callisto FITS files whose primary
    data array (effectively) encodes 8-bit unsigned integers.
    """
    # Values in (0, 1) are valid (negative dB), but non-positive values are undefined for log10.
    db = 10 * np.log10(np.maximum(dynamic_spectra, MIN_LINEAR_AMPLITUDE))
    # Transform the dB values to ADC digits, using hardware specifications from CALLISTO's logarithmic
    # detector and ADC.
    digits = ((db * DETECTOR_CONVERSION_RATE) / ADC_VOLTAGE_RANGE) * ADC_DIGIT_RANGE

    # Round to nearest ADC code before casting to avoid float32 truncation artifacts
    # (e.g. 0.9999999 becoming 0).
    digits = np.rint(digits)

    # Cast to unsigned 8-bit integers, clipping to avoid overflows.
    min_digit, max_digit = 0, 255
    return np.clip(digits, min_digit, max_digit).astype(dtype=np.uint8)


def callisto_digits_to_linear(
    digits: npt.NDArray[np.uint8],
) -> npt.NDArray[np.float32]:
    """Linearise CALLISTO ADC digits.

    NOTE: The widening conversion to float32 is required for compatibility with Spectre -
    dynamic spectra arrays use dtype np.float32.
    """
    db = (digits.astype(np.float32) / ADC_DIGIT_RANGE) * (
        ADC_VOLTAGE_RANGE / DETECTOR_CONVERSION_RATE
    )
    return 10 ** (db / 10)


@dataclasses.dataclass(frozen=True)
class CallistoBatchExtension:
    """Supported extensions for a `CallistoBatch`.

    :ivar FIT: Corresponds to the `.fit` file extension.
    :ivar FC32: Corresponds to the `.fc32` file extension.
    """

    FIT: str = "fit"
    FC32: str = "fc32"


class _Fc32File(BatchFile[npt.NDArray[np.complex64]]):
    def read(self) -> npt.NDArray[np.complex64]:
        """Read single-precision complex, interleaved I/Q samples in the binary format.

        :return: 64-bit complex IQ samples.
        """
        return np.fromfile(self.file_path, dtype=np.complex64)


class _FitFile(BatchFile[spectre_server.core.spectrograms.Spectrogram]):

    def read(self) -> spectre_server.core.spectrograms.Spectrogram:
        """Read the FIT file and create a spectrogram."""
        with astropy.io.fits.open(self.file_path, mode="readonly") as hdulist:
            primary_hdu = hdulist[0]
            bintable_hdu = hdulist[1]

            # e-Callisto stores the times and frequencies as double precision floating points,
            # so cast back to single precision. No concern for this narrowing conversion,
            # since the values started as single-precision anyway before being written to disk.
            times = np.asarray(bintable_hdu.data["TIME"][0], dtype=np.float32)

            # Same narrowing conversion, but also reverse the frequencies (e-Callisto stores them backwards) and convert from MHz to Hz.
            frequencies = (
                np.asarray(bintable_hdu.data["FREQUENCY"][0], dtype=np.float32)[::-1]
                * 1e6
            )

            linearised_digits = callisto_digits_to_linear(primary_hdu.data)

            return spectre_server.core.spectrograms.Spectrogram(
                # Reverse each spectrum in the spectrogram (as with the frequencies, e-Callisto stores them backwards).
                linearised_digits[::-1, :],
                times,
                frequencies,
                spectre_server.core.spectrograms.SpectrumUnit.CALLISTO,
                self.start_datetime,
            )


class CallistoBatch(Base):

    def __init__(self, batches_dir_path: str, start_time: str, tag: str) -> None:
        """A batch containing spectrograms compatible with the e-Callisto network.

        Supports the following extensions:
        - `.fit`
        - `.fc32`

        :param batches_dir_path: The shared parent directory for each batch file.
        :param start_time: The start time of the batch.
        :param tag: The batch name tag.
        """
        super().__init__(batches_dir_path, start_time, tag)

        self.add_file(_FitFile, CallistoBatchExtension.FIT)
        self.add_file(_Fc32File, CallistoBatchExtension.FC32)

    @property
    def fit_file(self) -> _FitFile:
        """The batch file corresponding to the `.fit` extension."""
        return typing.cast(_FitFile, self.get_file(CallistoBatchExtension.FIT))

    @property
    def fc32_file(self) -> _Fc32File:
        """The batch file corresponding to the `.fc32` extension."""
        return typing.cast(_Fc32File, self.get_file(CallistoBatchExtension.FC32))

    @property
    def spectrogram_file(self) -> _FitFile:
        return self.fit_file

    def read_iq(self, extension: str) -> npt.NDArray[np.complex64]:
        """Read I/Q samples from the batch."""
        if extension == CallistoBatchExtension.FC32:
            return self.fc32_file.read()
        else:
            raise ValueError(f"Unsupported output type: {extension}")

    def delete_iq(self, extension: str) -> None:
        """Delete I/Q samples from the batch."""
        if extension == CallistoBatchExtension.FC32:
            self.fc32_file.delete()

    def write_spectrogram(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        origin: str,
        instrume: str,
        observer: str,
        object_: str,
        telescop: str,
        obsgeo_b: float,
        obsgeo_l: float,
        obsgeo_h: float,
    ) -> None:
        """Write spectrogram data to disk compatible with the e-Callisto network."""

        digits = callisto_digits_from_linear(spectrogram.dynamic_spectra)

        # Create the primary HDU (the basic keywords are set by Astropy).
        # Reverse each spectrum in the spectrogram (as with the frequencies, e-Callisto stores them backwards).
        primary_hdu = astropy.io.fits.PrimaryHDU(data=digits[::-1, :])

        # All data in the batch should have the same start time.
        if self.start_datetime != spectrogram.start_datetime.astype(datetime.datetime):
            raise ValueError(
                "Start time of the spectrogram must coincide with the start time of the batch. "
                f"Expected: {self.start_datetime}. Got: {spectrogram.start_datetime}."
            )

        start_datetime = spectrogram.datetimes[0].astype(datetime.datetime)
        end_datetime = spectrogram.datetimes[-1].astype(datetime.datetime)

        date = datetime.datetime.strftime(start_datetime, "%Y-%m-%d")
        date_obs = datetime.datetime.strftime(start_datetime, "%Y/%m/%d")
        date_end = datetime.datetime.strftime(end_datetime, "%Y/%m/%d")
        time_obs = datetime.datetime.strftime(start_datetime, "%H:%M:%S.%f")[:-3]
        time_end = datetime.datetime.strftime(end_datetime, "%H:%M:%S")

        primary_hdu.header.set("DATE", date)
        primary_hdu.header.set("ORIGIN", origin)
        primary_hdu.header.set("TELESCOP", telescop)
        primary_hdu.header.set("INSTRUME", instrume)
        primary_hdu.header.set("OBSERVER", observer)
        primary_hdu.header.set("OBJECT", object_)

        primary_hdu.header.set("BZERO", 0)
        primary_hdu.header.set("BSCALE", 1)
        primary_hdu.header.set("DATAMIN", int(np.nanmin(primary_hdu.data)))
        primary_hdu.header.set("DATAMAX", int(np.nanmax(primary_hdu.data)))
        primary_hdu.header.set("BUNIT", "digits")

        primary_hdu.header.set("DATE-OBS", date_obs)
        primary_hdu.header.set("DATE-END", date_end)
        primary_hdu.header.set("TIME-OBS", time_obs)
        primary_hdu.header.set("TIME-END", time_end)

        # ----------------------------------------------------------------------- #
        # In the e-Callisto FITS files, the values assumed by the world coordinate
        # system keywords don't appear to be consistent with the data in the binary
        # table extension or the spectrogram. We prioritise making them consistent
        # with e-Callisto, rather than the FITS standard.
        # ----------------------------------------------------------------------- #
        seconds_since_midnight = (
            start_datetime.hour * 3600
            + start_datetime.minute * 60
            + start_datetime.second
        )
        primary_hdu.header.set("CRVAL1", seconds_since_midnight)
        primary_hdu.header.set("CRPIX1", 0)
        primary_hdu.header.set("CTYPE1", "Time [UT]")
        primary_hdu.header.set("CDELT1", spectrogram.time_resolution)
        primary_hdu.header.set("CRVAL2", 200)
        primary_hdu.header.set("CRPIX2", 0)
        primary_hdu.header.set("CRTYPE2", "Frequency [MHz]")
        primary_hdu.header.set("CDELT2", -1)

        primary_hdu.header.set("OBS_LAT", obsgeo_b)
        primary_hdu.header.set("OBS_LAC", "N")
        primary_hdu.header.set("OBS_LON", obsgeo_l)
        primary_hdu.header.set("OBS_LOC", "E")
        primary_hdu.header.set("OBS_ALT", obsgeo_h)
        primary_hdu.header.set(
            "CONTENT",
            f"{date_obs}  Radio flux density, e-CALLISTO ({instrume})",
        )
        # These keywords do not carry over in any meaningful way, so set them to empty.
        primary_hdu.header.set("FRQFILE", "")
        primary_hdu.header.set("PWM_VAL", "")

        bintable_hdu = astropy.io.fits.BinTableHDU.from_columns(
            [
                astropy.io.fits.Column(
                    name="TIME",
                    format=f"{spectrogram.num_times}D8.3",
                    array=[spectrogram.times.astype(np.float64)],
                ),
                astropy.io.fits.Column(
                    name="FREQUENCY",
                    format=f"{spectrogram.num_frequencies}D8.3",
                    # Reverse, and convert to MHz.
                    array=[spectrogram.frequencies.astype(np.float64)[::-1] * 1e-6],
                ),
            ]
        )
        bintable_hdu.header.set("TSCAL1", 1)
        bintable_hdu.header.set("TSCAL2", 1)
        bintable_hdu.header.set("TZERO1", 0)
        bintable_hdu.header.set("TZERO2", 0)

        os.makedirs(self.fit_file.parent_dir_path, exist_ok=True)
        astropy.io.fits.HDUList([primary_hdu, bintable_hdu]).writeto(
            self.fit_file.file_path,
            overwrite=True,
        )
