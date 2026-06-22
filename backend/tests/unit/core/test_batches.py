# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import datetime

import pytest
import numpy as np
import astropy.io.fits
import astropy.wcs

import spectre_server.core.batches
import spectre_server.core.config
import spectre_server.core.spectrograms

TAG = "tag"
ORIGIN = "Spectregrams"
TELESCOP = "LPDA"
INSTRUME = "SDR"
OBJECT = "Sun"
OBSERVER = "jimmy@spectregrams.org"
OBSGEO_B = -4.3342366
OBSGEO_L = 55.7726726
OBSGEO_H = 138
TEST_START = datetime.datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)


@pytest.fixture
def spectrograms() -> list[spectre_server.core.spectrograms.Spectrogram]:
    """Create a sequence of simple spectrograms with identical dynamic spectra and frequency bins
    which are nonoverlapping in time.

      1MHz  | 0    1    2    3 || 0    1    2    3 || 0    1    2    3 |
      2MHz  | 4    5    6    7 || 4    5    6    7 || 4    5    6    7 |
      3MHz  | 8    9    10   11|| 8    9    10   11|| 8    9    10   11|
      4MHz  | 12   13   14   15|| 12   13   14   15|| 12   13   14   15|
             0.00 0.25 0.50 0.75 1.00 1.25 1.50 1.75 2.00 2.25 2.50 2.75 [s]
    """
    times = np.array([0.00, 0.25, 0.50, 0.75])
    frequencies = np.array([1e6, 2e6, 3e6, 4e6])
    dynamic_spectra = np.array(
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]]
    )

    datetimes = [
        TEST_START + datetime.timedelta(seconds=seconds) for seconds in range(3)
    ]
    return [
        spectre_server.core.spectrograms.Spectrogram(
            dynamic_spectra,
            times,
            frequencies,
            spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
            dt,
        )
        for dt in datetimes
    ]


@pytest.fixture
def batches(
    spectre_config_paths: spectre_server.core.config.Paths,
    spectrograms: list[spectre_server.core.spectrograms.Spectrogram],
) -> typing.Generator[
    spectre_server.core.batches.Batches[spectre_server.core.batches.IQStreamBatch],
    None,
    None,
]:
    """Set up some batches in a temporary filesystem."""
    for spectrogram in spectrograms:
        batch = spectre_server.core.batches.from_spectrogram(
            spectre_server.core.batches.IQStreamBatch,
            TAG,
            spectrogram,
            batches_dir_path=spectre_config_paths.get_batches_dir_path(),
        )
        batch.write_spectrogram(
            spectrogram,
            ORIGIN,
            INSTRUME,
            OBSERVER,
            OBJECT,
            TELESCOP,
            OBSGEO_B,
            OBSGEO_L,
            OBSGEO_H,
        )

    yield spectre_server.core.batches.Batches(
        TAG,
        spectre_server.core.batches.IQStreamBatch,
        batches_dir_path=spectre_config_paths.get_batches_dir_path(),
    )


@pytest.fixture
def spectrogram() -> spectre_server.core.spectrograms.Spectrogram:
    """Create the following spectrogram:

    1MHz  | 0    1    2    3   4   5   |
    2MHz  | 6    7    8    9   10  11  |
    3MHz  | 12   13   14   15  16  17  |
    4MHz  | 18   19   20   21  22  23  |
            0.0  0.2  0.4  0.6 0.8 1.0 [s]

    The spectrogram has a datetime associated with the first spectrum.
    """
    dynamic_spectra = np.array(
        [
            [0, 1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10, 11],
            [12, 13, 14, 15, 16, 17],
            [18, 19, 20, 21, 22, 23],
        ],
        dtype=np.float32,
    )
    times = np.array([0.00, 0.20, 0.40, 0.60, 0.80, 1.0])
    frequencies = np.array([1e6, 2e6, 3e6, 4e6])
    return spectre_server.core.spectrograms.Spectrogram(
        dynamic_spectra,
        times,
        frequencies,
        spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
        TEST_START,
    )


@pytest.fixture
def spectrogram_no_start_datetime() -> spectre_server.core.spectrograms.Spectrogram:
    """Create the following spectrogram:

    1MHz  | 0    1    2    3   4   5   |
    2MHz  | 6    7    8    9   10  11  |
    3MHz  | 12   13   14   15  16  17  |
    4MHz  | 18   19   20   21  22  23  |
            0.0  0.2  0.4  0.6 0.8 1.0 [s]

    The spectrogram does _not_ have a datetime associated with the first spectrum.
    """
    dynamic_spectra = np.array(
        [
            [0, 1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10, 11],
            [12, 13, 14, 15, 16, 17],
            [18, 19, 20, 21, 22, 23],
        ],
        dtype=np.float32,
    )
    times = np.array([0.00, 0.20, 0.40, 0.60, 0.80, 1.0])
    frequencies = np.array([1e6, 2e6, 3e6, 4e6])
    return spectre_server.core.spectrograms.Spectrogram(
        dynamic_spectra,
        times,
        frequencies,
        spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
    )


@pytest.fixture
def iqstream_batch(
    spectre_config_paths: spectre_server.core.config.Paths,
) -> spectre_server.core.batches.IQStreamBatch:
    batches_dir_path = spectre_config_paths.get_batches_dir_path(
        TEST_START.year,
        TEST_START.month,
        TEST_START.day,
    )
    return spectre_server.core.batches.IQStreamBatch(
        batches_dir_path,
        datetime.datetime.strftime(
            TEST_START, spectre_server.core.config.TimeFormat.DATETIME
        ),
        TAG,
    )


@pytest.mark.parametrize(
    "file_name, parsed_file_name",
    [
        (
            "2025-06-01T00:00:00.000000Z_tag.ext",
            ("2025-06-01T00:00:00.000000Z", "tag", "ext"),
        ),  # Happy path.
    ],
)
def test_parse_batch_file_name(
    file_name: str, parsed_file_name: tuple[str, str, str]
) -> None:
    """Check that we can properly extract the components of batch file names."""
    result = spectre_server.core.batches.parse_batch_file_name(file_name)
    assert result == parsed_file_name


@pytest.mark.parametrize(
    "file_name",
    [
        "2025-06-01T00:00:00.000000Z.ext",  # No tag
        "2025-06-01T00:00:00.000000Z_bad_tag.ext",  # Multiple underscores.
    ],
)
def test_parse_batch_file_name_invalid_underscores(file_name: str) -> None:
    """Check that batch file names must always contain exactly one underscore."""
    with pytest.raises(ValueError):
        spectre_server.core.batches.parse_batch_file_name(file_name)


class TestBatches:
    @pytest.mark.parametrize(
        ("start_offset", "end_offset", "expected_batch_names"),
        [
            # Range includes all batches.
            (
                -1,
                4,
                [
                    "2000-01-01T00:00:00.000000Z_tag",
                    "2000-01-01T00:00:01.000000Z_tag",
                    "2000-01-01T00:00:02.000000Z_tag",
                ],
            ),
            (
                0,
                3,
                [
                    "2000-01-01T00:00:00.000000Z_tag",
                    "2000-01-01T00:00:01.000000Z_tag",
                    "2000-01-01T00:00:02.000000Z_tag",
                ],
            ),
            # Range includes only the first batch.
            (0, 0.0001, ["2000-01-01T00:00:00.000000Z_tag"]),
            (0, 0.9999, ["2000-01-01T00:00:00.000000Z_tag"]),
            # Range includes only the middle batch.
            (1, 1.0001, ["2000-01-01T00:00:01.000000Z_tag"]),
            (1, 1.9999, ["2000-01-01T00:00:01.000000Z_tag"]),
            # Range includes only the last batch.
            (2, 2.0001, ["2000-01-01T00:00:02.000000Z_tag"]),
            (2, 2.9999, ["2000-01-01T00:00:02.000000Z_tag"]),
            # Range includes first two batches.
            (
                0,
                1.5,
                ["2000-01-01T00:00:00.000000Z_tag", "2000-01-01T00:00:01.000000Z_tag"],
            ),
            # Range includes last two batches.
            (
                1,
                3,
                ["2000-01-01T00:00:01.000000Z_tag", "2000-01-01T00:00:02.000000Z_tag"],
            ),
            # Range before all batches
            (-10, -1, []),
            # Range after all batches (final batch has an indeterminate end)
            (10, 20, ["2000-01-01T00:00:02.000000Z_tag"]),
        ],
    )
    def test_get_batches_in_range(
        self,
        batches: spectre_server.core.batches.Batches[
            spectre_server.core.batches.IQStreamBatch
        ],
        start_offset: float,
        end_offset: float,
        expected_batch_names: list[str],
    ) -> None:
        """Check filtering for batches in various time ranges."""
        start_time = TEST_START + datetime.timedelta(seconds=start_offset)
        end_time = TEST_START + datetime.timedelta(seconds=end_offset)

        batches_in_range = batches.get_batches_in_range(start_time, end_time)
        batch_names = [batch.name for batch in batches_in_range]
        assert batch_names == expected_batch_names

    @pytest.mark.parametrize(
        ("start_offset", "end_offset"),
        [
            # Start time is equal to the end time.
            (0, 0),
            # Start time is more than the end time.
            (1, 0),
        ],
    )
    def test_get_batches_in_invalid_ranges(
        self,
        batches: spectre_server.core.batches.Batches[
            spectre_server.core.batches.IQStreamBatch
        ],
        start_offset: float,
        end_offset: float,
    ) -> None:
        """Check that an error is raised when we try and pass an invalid time range"""
        start_time = TEST_START + datetime.timedelta(seconds=start_offset)
        end_time = TEST_START + datetime.timedelta(seconds=end_offset)

        with pytest.raises(ValueError):
            _ = batches.get_batches_in_range(start_time, end_time)

    def test_get_spectrogram(
        self,
        batches: spectre_server.core.batches.Batches[
            spectre_server.core.batches.IQStreamBatch
        ],
    ) -> None:
        """A basic check that we can retrieve the spectrogram written to the filesystem"""
        spectrogram = batches.get_spectrogram(
            TEST_START, TEST_START + datetime.timedelta(seconds=3)
        )
        assert spectrogram.start_datetime == TEST_START
        assert np.allclose(spectrogram.frequencies, np.array([1e6, 2e6, 3e6, 4e6]))
        assert np.allclose(
            spectrogram.times,
            np.array(
                [0.00, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75]
            ),
        )
        assert np.allclose(
            spectrogram.dynamic_spectra,
            [
                [
                    0,
                    1,
                    2,
                    3,
                    0,
                    1,
                    2,
                    3,
                    0,
                    1,
                    2,
                    3,
                ],
                [
                    4,
                    5,
                    6,
                    7,
                    4,
                    5,
                    6,
                    7,
                    4,
                    5,
                    6,
                    7,
                ],
                [
                    8,
                    9,
                    10,
                    11,
                    8,
                    9,
                    10,
                    11,
                    8,
                    9,
                    10,
                    11,
                ],
                [
                    12,
                    13,
                    14,
                    15,
                    12,
                    13,
                    14,
                    15,
                    12,
                    13,
                    14,
                    15,
                ],
            ],
        )


class TestBase:
    @pytest.mark.parametrize(("batch_cls"), [spectre_server.core.batches.IQStreamBatch])
    def test_from_spectrogram(
        self,
        batch_cls: typing.Type[spectre_server.core.batches.Base],
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Test a batch made from a spectogram has the same start time."""
        batch = spectre_server.core.batches.from_spectrogram(
            batch_cls, TAG, spectrogram
        )
        assert batch.start_datetime == spectrogram.start_datetime.astype(
            datetime.datetime
        )

    @pytest.mark.parametrize(("batch_cls"), [spectre_server.core.batches.IQStreamBatch])
    def test_from_spectrogram_no_start_datetime(
        self,
        batch_cls: typing.Type[spectre_server.core.batches.Base],
        spectrogram_no_start_datetime: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Ensure we can't make a batch from a spectrogram with no start datetime."""
        with pytest.raises(ValueError):
            spectre_server.core.batches.from_spectrogram(
                batch_cls, TAG, spectrogram_no_start_datetime
            )


class TestIQStreamBatch:
    def test_write_and_read_spectrogram(
        self,
        iqstream_batch: spectre_server.core.batches.IQStreamBatch,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Spectrograms written to disk must conform to the FITS standard,
        and be consistent with the spectrogram read back.
        """

        # Write the spectrogram to disk.
        iqstream_batch.write_spectrogram(
            spectrogram,
            origin=ORIGIN,
            instrume=INSTRUME,
            observer=OBSERVER,
            object_=OBJECT,
            telescop=TELESCOP,
            obsgeo_b=OBSGEO_B,
            obsgeo_l=OBSGEO_L,
            obsgeo_h=OBSGEO_H,
        )

        # Check the spectrogram we wrote to disk, is consistent with what we read back.
        s = iqstream_batch.read_spectrogram()
        assert np.array_equal(s.dynamic_spectra, spectrogram.dynamic_spectra)

        # Not bit-wise equal, since this is computed based on world coordinates.
        assert np.allclose(s.times, spectrogram.times)
        assert np.allclose(s.frequencies, spectrogram.frequencies)

        # Check the FITS file conforms to the FITS standard, and has all the expected
        # keywords.
        with astropy.io.fits.open(iqstream_batch.fits_file.file_path) as hdulist:

            # Basic mandatory key words in the primary HDU.
            primary_hdu: astropy.io.fits.PrimaryHDU = hdulist[0]
            assert primary_hdu.header.get("SIMPLE") == True
            assert primary_hdu.header.get("BITPIX") == -32
            assert primary_hdu.header.get("NAXIS") == 2
            assert primary_hdu.header.get("NAXIS1") == 6
            assert primary_hdu.header.get("NAXIS2") == 4
            # Although this is a required keyword, Astropy does not expose it publically.
            # assert "END" in primary_hdu.header.keys()

            # Keywords representing time.
            assert primary_hdu.header.get("DATE") == "2000-01-01T00:00:00.000000"
            assert primary_hdu.header.get("DATE-OBS") == "2000-01-01T00:00:00.000000"
            assert primary_hdu.header.get("TIMESYS") == "UTC"
            assert primary_hdu.header.get("TREFPOS") == "TOPOCENTER"
            assert primary_hdu.header.get("OBSGEO-B") == OBSGEO_B
            assert primary_hdu.header.get("OBSGEO-L") == OBSGEO_L
            assert primary_hdu.header.get("OBSGEO-H") == OBSGEO_H
            assert primary_hdu.header.get("DATEREF") == "2000-01-01T00:00:00.000000"
            assert primary_hdu.header.get("DATE-BEG") == "2000-01-01T00:00:00.000000"
            assert primary_hdu.header.get("DATE-END") == "2000-01-01T00:00:01.000000"

            # General descriptive keywords.
            assert primary_hdu.header.get("ORIGIN") == ORIGIN
            assert primary_hdu.header.get("EXTEND") == False

            # Keywords describing observations.
            assert primary_hdu.header.get("TELESCOP") == TELESCOP
            assert primary_hdu.header.get("INSTRUME") == INSTRUME
            assert primary_hdu.header.get("OBSERVER") == OBSERVER
            assert primary_hdu.header.get("OBJECT") == OBJECT

            # Keywords describing the primary data array.
            assert primary_hdu.header.get("BSCALE") == 1.0
            assert primary_hdu.header.get("BZERO") == 0.0
            # Not required - in general the DFT of samples from SDRs don't directly correspond to a physical quantity.
            assert "BUNIT" not in primary_hdu.header.keys()
            assert primary_hdu.header.get("DATAMIN") == 0.0
            assert primary_hdu.header.get("DATAMAX") == 23

            # Keywords describing the mapping between image coordinates and world (physical) coordinates.
            assert primary_hdu.header.get("WCSAXES") == 2
            assert primary_hdu.header.get("CTYPE1") == "UTC"
            assert primary_hdu.header.get("CUNIT1") == "s"
            assert primary_hdu.header.get("CRPIX1") == 1.0
            assert primary_hdu.header.get("CRVAL1") == 0.0
            assert primary_hdu.header.get("CDELT1") == 0.2

            assert primary_hdu.header.get("CTYPE2") == "FREQ"
            assert primary_hdu.header.get("CUNIT2") == "Hz"
            assert primary_hdu.header.get("CRPIX2") == 1.0
            assert primary_hdu.header.get("CRVAL2") == 1e6
            assert primary_hdu.header.get("CDELT2") == 1e6

            assert primary_hdu.header.get("PC1_1") == 1.0
            assert primary_hdu.header.get("PC2_2") == 1.0
            assert primary_hdu.header.get("PC1_2") == 0.0
            assert primary_hdu.header.get("PC2_1") == 0.0

            # Check the spectrogram we wrote is consistent with the primary data array.
            assert np.array_equal(spectrogram.dynamic_spectra, primary_hdu.data)

            # Check that the world coordinates determined by the keywords are consistent
            # with the spectrogram we wrote to disk.
            wcs = astropy.wcs.WCS(primary_hdu.header, fix=False)

            # Check the four world coordinates at extremal indices (1-indexed, by convention in the standard)
            assert np.array_equal(wcs.wcs_pix2world([[1, 1]], 1), [[0.0, 1e6]])
            assert np.array_equal(wcs.wcs_pix2world([[1, 4]], 1), [[0.0, 4e6]])
            assert np.array_equal(wcs.wcs_pix2world([[6, 1]], 1), [[1.0, 1e6]])
            assert np.array_equal(wcs.wcs_pix2world([[6, 4]], 1), [[1.0, 4e6]])
