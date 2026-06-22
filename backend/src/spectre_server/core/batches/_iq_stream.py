# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import dataclasses
import typing
import os

import numpy as np
import numpy.typing as npt
import astropy.io.fits
import astropy.wcs

import spectre_server.core.config
import spectre_server.core.spectrograms

from ._base import Base, BatchFile


@dataclasses.dataclass(frozen=True)
class IQStreamBatchExtension:
    """Supported extensions for a `IQStreamBatch`.

    :ivar FITS: Corresponds to the `.fits` file extension.
    :ivar FC32: Corresponds to the `.fc32` file extension.
    :ivar FC64: Corresponds to the `.fc64` file extension.
    :ivar SC8: Corresponds to the `.sc8` file extension.
    :ivar SC16: Corresponds to the `.sc16` file extension.
    :ivar HDR: Corresponds to the `.hdr` file extension.
    """

    FITS: str = "fits"
    FC32: str = "fc32"
    FC64: str = "fc64"
    SC8: str = "sc8"
    SC16: str = "sc16"
    HDR: str = "hdr"


class _Fc32File(BatchFile[npt.NDArray[np.complex64]]):
    def read(self) -> npt.NDArray[np.complex64]:
        """Read single-precision complex, interleaved I/Q samples in the binary format.

        :return: 64-bit complex IQ samples.
        """
        return np.fromfile(self.file_path, dtype=np.complex64)


class _Fc64File(BatchFile[npt.NDArray[np.complex64]]):
    def read(self) -> npt.NDArray[np.complex64]:
        """Read double-precision complex, interleaved I/Q samples in the binary format. A narrowing
        conversion is applied.

        :return: 64-bit complex IQ samples.
        """
        return np.fromfile(self.file_path, dtype=np.complex128).astype(np.complex64)


class _Sc8File(BatchFile[npt.NDArray[np.complex64]]):
    def read(self) -> npt.NDArray[np.complex64]:
        """Read single-precision complex, interleaved I/Q samples in the binary format. A promotional
        conversion is applied.

        :return: 64-bit complex IQ samples.
        """
        data = np.fromfile(self.file_path, dtype=np.int8)
        return (data[0::2] + 1j * data[1::2]).astype(np.complex64)


class _Sc16File(BatchFile[npt.NDArray[np.complex64]]):
    def read(self) -> npt.NDArray[np.complex64]:
        """Read double-precision complex, interleaved I/Q samples in the binary format. A promotional
        conversion is applied.

        :return: 64-bit complex IQ samples.
        """
        data = np.fromfile(self.file_path, dtype=np.int16)
        return (data[0::2] + 1j * data[1::2]).astype(np.complex64)


@dataclasses.dataclass
class IQMetadata:
    """Stores metadata produced by the batched file sink block.

    :ivar center_frequencies: Center frequencies for each I/Q sample.
    :ivar num_samples: The number of I/Q samples at each center frequency.
    """

    center_frequencies: npt.NDArray[np.float32]
    num_samples: npt.NDArray[np.uint64]


class _HdrFile(BatchFile[IQMetadata]):
    def read(self) -> IQMetadata:
        """Read metadata produced by the batched file sink block by parsing the interleaved
        center frequencies and the number of samples corresponding to each.

        :return: A container for the metadata
        """
        dt = np.dtype([("value", np.float32), ("num_samples", np.uint64)])
        metadata = np.fromfile(self.file_path, dtype=dt)
        return IQMetadata(metadata["value"], metadata["num_samples"])


class _FitsFile(BatchFile[spectre_server.core.spectrograms.Spectrogram]):

    def read(self) -> spectre_server.core.spectrograms.Spectrogram:
        """Read the FITS file and create a spectrogram."""
        with astropy.io.fits.open(self.file_path, mode="readonly") as hdulist:
            primary_hdu = hdulist[0]
            dynamic_spectra = primary_hdu.data

            wcs = astropy.wcs.WCS(primary_hdu.header, fix=False, relax=False)

            pixel_coordinates = (
                np.indices(
                    (
                        primary_hdu.header.get("NAXIS1"),
                        primary_hdu.header.get("NAXIS2"),
                    ),
                    dtype=np.float32,
                )
                + 1
            )  # Pixel coordinates are 1-indexed in the FITS standard.

            # The time coordinates are identical for any spectral bin, so just pick the first.
            times = wcs.wcs_pix2world(pixel_coordinates[:, :, 0].T, 1)[:, 0]

            # The frequency coordinates for every spectrum are identical, so just pick the first.
            frequencies = wcs.wcs_pix2world(pixel_coordinates[:, 0, :].T, 1)[:, 1]

            return spectre_server.core.spectrograms.Spectrogram(
                dynamic_spectra,
                times,
                frequencies,
                spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
                self.start_datetime,
            )


class IQStreamBatch(Base):

    def __init__(self, batches_dir_path: str, start_time: str, tag: str) -> None:
        """A batch of data derived from a stream of IQ samples from some receiver.

        Supports the following extensions:
        - `.fits`
        - `.fc32`
        - `.fc64`
        - `.sc8`
        - `.sc16`
        - `.hdr`

        :param batches_dir_path: The shared parent directory for each batch file.
        :param start_time: The start time of the batch.
        :param tag: The batch name tag.
        """
        super().__init__(batches_dir_path, start_time, tag)

        self.add_file(_FitsFile, IQStreamBatchExtension.FITS)
        self.add_file(_Fc32File, IQStreamBatchExtension.FC32)
        self.add_file(_Fc64File, IQStreamBatchExtension.FC64)
        self.add_file(_Sc8File, IQStreamBatchExtension.SC8)
        self.add_file(_Sc16File, IQStreamBatchExtension.SC16)
        self.add_file(_HdrFile, IQStreamBatchExtension.HDR)

    @property
    def fits_file(self) -> _FitsFile:
        """The batch file corresponding to the `.fits` extension."""
        return typing.cast(_FitsFile, self.get_file(IQStreamBatchExtension.FITS))

    @property
    def fc32_file(self) -> _Fc32File:
        """The batch file corresponding to the `.fc32` extension."""
        return typing.cast(_Fc32File, self.get_file(IQStreamBatchExtension.FC32))

    @property
    def fc64_file(self) -> _Fc64File:
        """The batch file corresponding to the `.fc64` extension."""
        return typing.cast(_Fc64File, self.get_file(IQStreamBatchExtension.FC64))

    @property
    def sc8_file(self) -> _Sc8File:
        """The batch file corresponding to the `.sc8` extension."""
        return typing.cast(_Sc8File, self.get_file(IQStreamBatchExtension.SC8))

    @property
    def sc16_file(self) -> _Sc16File:
        """The batch file corresponding to the `.sc16` extension."""
        return typing.cast(_Sc16File, self.get_file(IQStreamBatchExtension.SC16))

    @property
    def hdr_file(self) -> _HdrFile:
        """The batch file corresponding to the `.hdr` extension."""
        return typing.cast(_HdrFile, self.get_file(IQStreamBatchExtension.HDR))

    @property
    def spectrogram_file(self) -> _FitsFile:
        return self.fits_file

    def read_iq(self, extension: str) -> npt.NDArray[np.complex64]:
        """Read I/Q samples from the batch."""
        if extension == IQStreamBatchExtension.FC32:
            return self.fc32_file.read()
        elif extension == IQStreamBatchExtension.FC64:
            return self.fc64_file.read()
        elif extension == IQStreamBatchExtension.SC8:
            return self.sc8_file.read()
        elif extension == IQStreamBatchExtension.SC16:
            return self.sc16_file.read()
        else:
            raise ValueError(f"Unsupported output type: {extension}")

    def cached_read_iq(self, extension: str) -> npt.NDArray[np.complex64]:
        """Read I/Q samples from the batch."""
        if extension == IQStreamBatchExtension.FC32:
            return self.fc32_file.cached_read()
        elif extension == IQStreamBatchExtension.FC64:
            return self.fc64_file.cached_read()
        elif extension == IQStreamBatchExtension.SC8:
            return self.sc8_file.cached_read()
        elif extension == IQStreamBatchExtension.SC16:
            return self.sc16_file.cached_read()
        else:
            raise ValueError(f"Unsupported output type: {extension}")

    def delete_iq(self, extension: str) -> None:
        """Delete I/Q samples from the batch."""
        if extension == IQStreamBatchExtension.FC32:
            self.fc32_file.delete()
        elif extension == IQStreamBatchExtension.FC64:
            self.fc64_file.delete()
        elif extension == IQStreamBatchExtension.SC8:
            self.sc8_file.delete()
        elif extension == IQStreamBatchExtension.SC16:
            self.sc16_file.delete()
        else:
            raise ValueError(f"Unsupported output type: {extension}")

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

        # Create the primary HDU (the basic keywords are set by Astropy).
        primary_hdu = astropy.io.fits.PrimaryHDU(spectrogram.dynamic_spectra)

        # All data in the batch should have the same start time.
        if self.start_datetime != spectrogram.start_datetime.astype(datetime.datetime):
            raise ValueError(
                "Start time of the spectrogram must coincide with the start time of the batch. "
                f"Expected: {self.start_datetime}. Got: {spectrogram.start_datetime}."
            )
        start_datetime = datetime.datetime.strftime(
            self.start_datetime, spectre_server.core.config.TimeFormat.FITS
        )

        # Set keywords representing time.
        primary_hdu.header.set("DATE", start_datetime)
        primary_hdu.header.set("DATE-OBS", start_datetime)
        primary_hdu.header.set("TIMESYS", "UTC")
        primary_hdu.header.set("TREFPOS", "TOPOCENTER")
        primary_hdu.header.set("OBSGEO-B", obsgeo_b)
        primary_hdu.header.set("OBSGEO-L", obsgeo_l)
        primary_hdu.header.set("OBSGEO-H", obsgeo_h)
        primary_hdu.header.set("DATEREF", start_datetime)

        date_beg = datetime.datetime.strftime(
            spectrogram.datetimes[0].astype(datetime.datetime),
            spectre_server.core.config.TimeFormat.FITS,
        )
        date_end = datetime.datetime.strftime(
            spectrogram.datetimes[-1].astype(datetime.datetime),
            spectre_server.core.config.TimeFormat.FITS,
        )
        primary_hdu.header.set("DATE-BEG", date_beg)
        primary_hdu.header.set("DATE-END", date_end)

        # Set general descriptive keywords.
        primary_hdu.header.set("ORIGIN", origin)
        # TODO: Set to True when we include a binary table extension.
        primary_hdu.header.set("EXTEND", False)

        # Set keywords describing observations.
        primary_hdu.header.set("TELESCOP", telescop)
        primary_hdu.header.set("INSTRUME", instrume)
        primary_hdu.header.set("OBSERVER", observer)
        primary_hdu.header.set("OBJECT", object_)

        # Set keywords describing the primary data array.
        # No linear scaling.
        primary_hdu.header.set("BSCALE", 1.0)
        primary_hdu.header.set("BZERO", 0.0)
        primary_hdu.header.set("DATAMAX", np.nanmax(spectrogram.dynamic_spectra))
        primary_hdu.header.set("DATAMIN", np.nanmin(spectrogram.dynamic_spectra))

        # Set keywords describing the mapping between image coordinates and world coordinates.
        primary_hdu.header["WCSAXES"] = 2
        primary_hdu.header["CTYPE1"] = "UTC"
        primary_hdu.header["CUNIT1"] = "s"
        # As per the standard, the first pixel in the image has pixel coordinates (1.0, 1.0)
        primary_hdu.header["CRPIX1"] = 1.0
        primary_hdu.header["CRVAL1"] = spectrogram.times[0]
        primary_hdu.header["CDELT1"] = spectrogram.time_resolution
        primary_hdu.header["CTYPE2"] = "FREQ"
        primary_hdu.header["CUNIT2"] = "Hz"
        # As per the standard, the first pixel in the image has pixel coordinates (1.0, 1.0)
        primary_hdu.header["CRPIX2"] = 1.0
        primary_hdu.header["CRVAL2"] = spectrogram.frequencies[0]
        primary_hdu.header["CDELT2"] = spectrogram.frequency_resolution
        # Identity linear transformation matrix.
        primary_hdu.header["PC1_1"] = 1.0
        primary_hdu.header["PC2_2"] = 1.0
        primary_hdu.header["PC1_2"] = 0.0
        primary_hdu.header["PC2_1"] = 0.0

        # Add a checksum.
        primary_hdu.add_checksum()

        os.makedirs(self.fits_file.parent_dir_path, exist_ok=True)
        astropy.io.fits.HDUList([primary_hdu]).writeto(
            self.fits_file.file_path,
            overwrite=True,
        )
