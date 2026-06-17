# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import datetime
import typing

import numpy as np
import numpy.typing as npt
import astropy.io.fits

import spectre_server.core.spectrograms

from ._base import Base, BatchFile


@dataclasses.dataclass(frozen=True)
class ECallistoBatchExtension:
    """Supported extensions for an `ECallistoBatch`."""

    FITS: str = "fits"
    FC32: str = "fc32"


class _Fc32File(BatchFile[npt.NDArray[np.complex64]]):
    def read(self) -> npt.NDArray[np.complex64]:
        """Read single-precision complex, interleaved I/Q samples in the binary format.

        :return: 64-bit complex IQ samples.
        """
        return np.fromfile(self.file_path, dtype=np.complex64)


class _ECallistoFitsFile(BatchFile[spectre_server.core.spectrograms.Spectrogram]):
    """Reader for e-CALLISTO-shaped FITS, inverting the transforms in `_save_callisto`.

    On disk the image is uint8 with frequency descending; we cast back to float32 and
    re-order to ascending frequency so the in-memory `Spectrogram` invariant holds.
    """

    def read(self) -> spectre_server.core.spectrograms.Spectrogram:
        with astropy.io.fits.open(self.file_path, mode="readonly") as hdulist:
            primary_hdu = hdulist["PRIMARY"]
            digits_descending = primary_hdu.data
            bunit = primary_hdu.header["BUNIT"]

            date_obs = primary_hdu.header["DATE-OBS"]
            time_obs = primary_hdu.header["TIME-OBS"]
            start_datetime = datetime.datetime.strptime(
                f"{date_obs} {time_obs}", "%Y/%m/%d %H:%M:%S.%f"
            )

            bintable_hdu = hdulist[1]
            times = np.asarray(bintable_hdu.data["TIME"][0], dtype=np.float32)
            frequencies_descending_MHz = bintable_hdu.data["FREQUENCY"][0]

        dynamic_spectra = np.asarray(digits_descending[::-1, :], dtype=np.float32)
        frequencies = np.asarray(
            frequencies_descending_MHz[::-1] * 1e6, dtype=np.float32
        )

        return spectre_server.core.spectrograms.Spectrogram(
            dynamic_spectra,
            times,
            frequencies,
            spectre_server.core.spectrograms.SpectrumUnit(bunit),
            start_datetime,
        )


class ECallistoBatch(Base):
    def __init__(self, batches_dir_path: str, start_time: str, tag: str) -> None:
        """A batch of data derived from a stream of IQ samples, producing e-CALLISTO-shaped FITS.

        Supports the following extensions:
        - `.fits`
        - `.fc32`
        """
        super().__init__(batches_dir_path, start_time, tag)

        self.add_file(_ECallistoFitsFile, ECallistoBatchExtension.FITS)
        self.add_file(_Fc32File, ECallistoBatchExtension.FC32)

    @property
    def fits_file(self) -> _ECallistoFitsFile:
        """The batch file corresponding to the `.fits` extension."""
        return typing.cast(
            _ECallistoFitsFile, self.get_file(ECallistoBatchExtension.FITS)
        )

    @property
    def fc32_file(self) -> _Fc32File:
        """The batch file corresponding to the `.fc32` extension."""
        return typing.cast(_Fc32File, self.get_file(ECallistoBatchExtension.FC32))

    @property
    def spectrogram_file(self) -> _ECallistoFitsFile:
        return self.fits_file

    def read_iq(self, extension: str) -> npt.NDArray[np.complex64]:
        """Read I/Q samples from the batch."""
        if extension == ECallistoBatchExtension.FC32:
            return self.fc32_file.read()
        raise ValueError(f"Unsupported output type: {extension}")

    def delete_iq(self, extension: str) -> None:
        """Delete I/Q samples from the batch."""
        if extension == ECallistoBatchExtension.FC32:
            self.fc32_file.delete()
            return
        raise ValueError(f"Unsupported output type: {extension}")
