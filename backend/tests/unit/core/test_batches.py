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
TEST_START = datetime.datetime(year=2000, month=1, day=25, hour=1, minute=0, second=0)


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
    times = np.array([0.00, 0.20, 0.40, 0.60, 0.80, 1.0], dtype=np.float32)
    frequencies = np.array([1e6, 2e6, 3e6, 4e6], dtype=np.float32)
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


@pytest.fixture
def callisto_batch(
    spectre_config_paths: spectre_server.core.config.Paths,
) -> spectre_server.core.batches.CallistoBatch:
    batches_dir_path = spectre_config_paths.get_batches_dir_path(
        TEST_START.year,
        TEST_START.month,
        TEST_START.day,
    )
    return spectre_server.core.batches.CallistoBatch(
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
            "2025-06-01T01:00:00.000000Z_tag.ext",
            ("2025-06-01T01:00:00.000000Z", "tag", "ext"),
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
        "2025-06-01T01:00:00.000000Z.ext",  # No tag
        "2025-06-01T01:00:00.000000Z_bad_tag.ext",  # Multiple underscores.
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
                    "2000-01-25T01:00:00.000000Z_tag",
                    "2000-01-25T01:00:01.000000Z_tag",
                    "2000-01-25T01:00:02.000000Z_tag",
                ],
            ),
            (
                0,
                3,
                [
                    "2000-01-25T01:00:00.000000Z_tag",
                    "2000-01-25T01:00:01.000000Z_tag",
                    "2000-01-25T01:00:02.000000Z_tag",
                ],
            ),
            # Range includes only the first batch.
            (0, 0.0001, ["2000-01-25T01:00:00.000000Z_tag"]),
            (0, 0.9999, ["2000-01-25T01:00:00.000000Z_tag"]),
            # Range includes only the middle batch.
            (1, 1.0001, ["2000-01-25T01:00:01.000000Z_tag"]),
            (1, 1.9999, ["2000-01-25T01:00:01.000000Z_tag"]),
            # Range includes only the last batch.
            (2, 2.0001, ["2000-01-25T01:00:02.000000Z_tag"]),
            (2, 2.9999, ["2000-01-25T01:00:02.000000Z_tag"]),
            # Range includes first two batches.
            (
                0,
                1.5,
                ["2000-01-25T01:00:00.000000Z_tag", "2000-01-25T01:00:01.000000Z_tag"],
            ),
            # Range includes last two batches.
            (
                1,
                3,
                ["2000-01-25T01:00:01.000000Z_tag", "2000-01-25T01:00:02.000000Z_tag"],
            ),
            # Range before all batches
            (-10, -1, []),
            # Range after all batches (final batch has an indeterminate end)
            (10, 20, ["2000-01-25T01:00:02.000000Z_tag"]),
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

        # Check the spectrogram we wrote to disk is consistent with what we read back.
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
            assert primary_hdu.header.get("DATE") == "2000-01-25T01:00:00.000000"
            assert primary_hdu.header.get("DATE-OBS") == "2000-01-25T01:00:00.000000"
            assert primary_hdu.header.get("TIMESYS") == "UTC"
            assert primary_hdu.header.get("TREFPOS") == "TOPOCENTER"
            assert primary_hdu.header.get("OBSGEO-B") == OBSGEO_B
            assert primary_hdu.header.get("OBSGEO-L") == OBSGEO_L
            assert primary_hdu.header.get("OBSGEO-H") == OBSGEO_H
            assert primary_hdu.header.get("DATEREF") == "2000-01-25T01:00:00.000000"
            assert primary_hdu.header.get("DATE-BEG") == "2000-01-25T01:00:00.000000"
            assert primary_hdu.header.get("DATE-END") == "2000-01-25T01:00:01.000000"

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
            assert np.isclose(primary_hdu.header.get("CDELT1"), 0.2)

            assert primary_hdu.header.get("CTYPE2") == "FREQ"
            assert primary_hdu.header.get("CUNIT2") == "Hz"
            assert primary_hdu.header.get("CRPIX2") == 1.0
            assert primary_hdu.header.get("CRVAL2") == 1e6
            assert np.isclose(primary_hdu.header.get("CDELT2"), 1e6)

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
            assert np.allclose(wcs.wcs_pix2world([[1, 1]], 1), [[0.0, 1e6]])
            assert np.allclose(wcs.wcs_pix2world([[1, 4]], 1), [[0.0, 4e6]])
            assert np.allclose(wcs.wcs_pix2world([[6, 1]], 1), [[1.0, 1e6]])
            assert np.allclose(wcs.wcs_pix2world([[6, 4]], 1), [[1.0, 4e6]])


class TestCallistoBatch:
    def test_callisto_digits_from_linear_no_underflow(
        self,
    ) -> None:
        """Check that small values don't underflow when they're transformed to CALLISTO digits."""
        dynamic_spectra = np.array([-1, 0, 0.5, 1, 2, 3], dtype=np.float32)
        expected = np.array([0, 0, 0, 0, 8, 12], dtype=np.uint8)
        assert np.array_equal(
            spectre_server.core.batches.callisto_digits_from_linear(dynamic_spectra),
            expected,
        )

    def test_callisto_digits_from_linear_no_overflow(
        self,
    ) -> None:
        """Check that large values don't overflow when they're transformed to CALLISTO digits."""
        # The big value and delta were found empircally.
        big_value, delta = 6958566400, 5e8
        just_under, just_over = big_value - delta, big_value + delta
        very_over = big_value * 2
        dynamic_spectra = np.array(
            [just_under, big_value, just_over, very_over],
            dtype=np.float32,
        )
        expected = np.array([254, 255, 255, 255], dtype=np.uint8)
        assert np.array_equal(
            spectre_server.core.batches.callisto_digits_from_linear(dynamic_spectra),
            expected,
        )

    def test_callisto_digits_from_linear_typical(self) -> None:
        """Check a typical value correctly transforms to a CALLISTO digit."""
        # The expected value is computed by hand.
        dynamic_spectra = np.array([3.470352815], dtype=np.float32)
        expected = np.array([14], dtype=np.uint8)
        assert np.array_equal(
            spectre_server.core.batches.callisto_digits_from_linear(dynamic_spectra),
            expected,
        )

    def test_callisto_digits_to_linear_min(
        self,
    ) -> None:
        """Check that the minimum possible CALLISTO digit is correctly transformed to unity when linearised."""
        digits = np.array([0], dtype=np.uint8)
        expected = np.float32(1)
        assert (
            spectre_server.core.batches.callisto_digits_to_linear(digits)[0] == expected
        )

    def test_callisto_digits_to_linear_max(
        self,
    ) -> None:
        """Check that the maximum possible CALLISTO digit is correctly transformed to the maximum value when linearised."""
        digits = np.array([255], dtype=np.uint8)
        expected = np.float32(6958566400)
        assert np.isclose(
            spectre_server.core.batches.callisto_digits_to_linear(digits)[0],
            expected,
        )

    def test_callisto_digits_to_linear_typical(
        self,
    ) -> None:
        """Check that a typical digit is correctly transformed when linearised."""
        # The expected value is computed by hand.
        digits = np.array([14], dtype=np.uint8)
        expected = np.float32(3.470352815)
        assert np.isclose(
            spectre_server.core.batches.callisto_digits_to_linear(digits)[0], expected
        )

    def test_round_trip_from_callisto_digits(
        self,
    ) -> None:
        """Check that CALLISTO digits are preserved transforming to and from the linear scale."""
        digits = np.arange(255, dtype=np.uint8)
        assert np.array_equal(
            digits,
            spectre_server.core.batches.callisto_digits_from_linear(
                spectre_server.core.batches.callisto_digits_to_linear(digits)
            ),
        )

    def test_round_trip_from_linear(
        self,
    ) -> None:
        """Explicitly recognise a round trip is _not_ possible starting from linear values,
        due to floating point precision loss and quantisation errors."""
        # The range of values was chosen arbitrarily, we just have to stick to positive values.
        linear = np.arange(100, dtype=np.float32)
        assert not np.allclose(
            linear,
            spectre_server.core.batches.callisto_digits_to_linear(
                spectre_server.core.batches.callisto_digits_from_linear(linear)
            ),
        )

    def test_write_and_read_spectrogram(
        self,
        callisto_batch: spectre_server.core.batches.CallistoBatch,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Spectrograms written to disk must conform to e-Callisto FITS conventions,
        and be consistent with the spectrogram read back.
        """

        # Write the spectrogram to disk.
        callisto_batch.write_spectrogram(
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

        # Check the spectrogram we wrote to disk is consistent with what we read back.
        # A full round trip is _not_ possible starting from linear values due to floating point precision loss
        # and quantisation errors during the transformation. So, check a few of the values are close, up to a tolerance.
        s = callisto_batch.read_spectrogram()
        assert np.allclose(s.dynamic_spectra, spectrogram.dynamic_spectra, atol=1)

        # Should be bitwise equal, since this is read from the binary table extension.
        assert np.array_equal(s.times, spectrogram.times)
        assert np.array_equal(s.frequencies, spectrogram.frequencies)

        # Check the FITS file conforms to e-Callisto conventions.
        with astropy.io.fits.open(callisto_batch.fit_file.file_path) as hdulist:

            # First, check the keywords in the primary HDU.
            primary_hdu: astropy.io.fits.PrimaryHDU = hdulist[0]

            # ----------------------------------------------- #
            # Conformal keywords that assume conformal values.
            # ----------------------------------------------- #
            assert primary_hdu.header.get("SIMPLE") == True
            assert primary_hdu.header.get("BITPIX") == 8
            assert primary_hdu.header.get("NAXIS") == 2
            assert primary_hdu.header.get("NAXIS1") == 6
            assert primary_hdu.header.get("NAXIS2") == 4
            assert primary_hdu.header.get("EXTEND") == True
            assert primary_hdu.header.get("DATE") == "2000-01-25"
            assert primary_hdu.header.get("ORIGIN") == ORIGIN
            assert primary_hdu.header.get("TELESCOP") == TELESCOP
            assert primary_hdu.header.get("INSTRUME") == INSTRUME
            assert primary_hdu.header.get("OBJECT") == OBJECT
            assert primary_hdu.header.get("BZERO") == 0
            assert primary_hdu.header.get("BSCALE") == 1
            assert primary_hdu.header.get("DATAMIN") == 0
            assert primary_hdu.header.get("DATAMAX") == 35
            # Not reccommended (the value should conform with the recommendations in the IAU Style Manual), but this is conformal.
            assert primary_hdu.header.get("BUNIT") == "digits"

            # ----------------------------------------------------------------------- #
            # Conformal keywords that do not assume conformal values.
            #
            # Keyword records are retained for consistency with e-Callisto FITS files.
            # ----------------------------------------------------------------------- #
            # Non-conformal due to invalid date format.
            assert primary_hdu.header.get("DATE-OBS") == "2000/01/25"
            assert primary_hdu.header.get("DATE-END") == "2000/01/25"

            # ----------------------------------------------------------------------- #
            # Non-conformal keywords.
            #
            # Keyword records are retained for consistency with e-Callisto FITS files.
            # ----------------------------------------------------------------------- #
            # Values are retained for consistency with e-Callisto FITS files.
            assert (
                primary_hdu.header.get("CONTENT")
                == f"{primary_hdu.header.get('DATE-OBS')}  Radio flux density, e-CALLISTO ({primary_hdu.header.get('INSTRUME')})"
            )
            # Exactly three digits to the fractional component is intentional.
            assert primary_hdu.header.get("TIME-OBS") == "01:00:00.000"
            # No fractional component is intentional.
            assert primary_hdu.header.get("TIME-END") == "01:00:01"
            assert primary_hdu.header.get("OBS_LAT") == OBSGEO_B
            assert primary_hdu.header.get("OBS_LAC") == "N"
            assert primary_hdu.header.get("OBS_LON") == OBSGEO_L
            assert primary_hdu.header.get("OBS_LOC") == "E"
            assert primary_hdu.header.get("OBS_ALT") == OBSGEO_H
            # Empty values are intentional - these keyword records don't carry over in any meaningful way.
            assert primary_hdu.header.get("FRQFILE") == ""
            assert primary_hdu.header.get("PWM_VAL") == ""

            # ----------------------------------------------------------------------- #
            # In the e-Callisto FITS files, the values assumed by the world coordinate
            # system keywords don't appear to be consistent with the data in the binary
            # table extension or the spectrogram. We prioritise making them consistent
            # with e-Callisto, rather than the FITS standard. Values may be hardcoded and
            # inconsistent with the data.
            # ----------------------------------------------------------------------- #
            # This appears to be the elapsed time from midnight on DATE-OBS.
            assert primary_hdu.header.get("CRVAL1") == 3600
            assert primary_hdu.header.get("CRPIX1") == 0
            assert primary_hdu.header.get("CTYPE1") == "Time [UT]"
            # All e-Calliso files inspected appear to hold here the time resolution (as opposed to CDELT2, which does not
            # hold the frequency resolution).
            assert np.isclose(primary_hdu.header.get("CDELT1"), 0.2)

            # All e-Calliso files inspected held a fixed value of 200.
            assert primary_hdu.header.get("CRVAL2") == 200
            assert primary_hdu.header.get("CRPIX2") == 0
            assert primary_hdu.header.get("CRTYPE2") == "Frequency [MHz]"
            assert primary_hdu.header.get("CDELT2") == -1

            # Secondly, check the keywords in the binary table extension.
            bintable_hdu: astropy.io.fits.BinTableHDU = hdulist[1]

            # ----------------------------------------------- #
            # Conformal keywords that assume conformal values.
            # ----------------------------------------------- #
            assert bintable_hdu.header.get("XTENSION") == "BINTABLE"
            assert bintable_hdu.header.get("BITPIX") == 8
            assert bintable_hdu.header.get("NAXIS") == 2
            assert bintable_hdu.header.get("PCOUNT") == 0
            assert bintable_hdu.header.get("GCOUNT") == 1
            assert bintable_hdu.header.get("TFIELDS") == 2
            assert bintable_hdu.header.get("TTYPE1") == "TIME"
            assert bintable_hdu.header.get("TTYPE2") == "FREQUENCY"
            assert bintable_hdu.header.get("TSCAL1") == 1
            assert bintable_hdu.header.get("TSCAL2") == 1
            assert bintable_hdu.header.get("TZERO1") == 0
            assert bintable_hdu.header.get("TZERO2") == 0
            assert bintable_hdu.header.get("NAXIS1") == 4 * 8 + 6 * 8
            assert bintable_hdu.header.get("NAXIS2") == 1
            # The .3 are e-Callisto conventions.
            assert bintable_hdu.header.get("TFORM1") == "6D8.3"
            assert bintable_hdu.header.get("TFORM2") == "4D8.3"
