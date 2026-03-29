# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import datetime

import pytest
import numpy as np

import spectre_server.core.batches
import spectre_server.core.config
import spectre_server.core.spectrograms

TAG = "tag"
ORIGIN = "NOTSET"
TELESCOPE = "NOTSET"
INSTRUMENT = "NOTSET"
OBJECT = "NOTSET"
OBS_ALT = 0.0
OBS_LON = 0.0
OBS_LAT = 0.0
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
        spectrogram.save(
            TAG,
            ORIGIN,
            INSTRUMENT,
            TELESCOPE,
            OBJECT,
            OBS_ALT,
            OBS_LAT,
            OBS_LON,
            batches_dir_path=spectre_config_paths.get_batches_dir_path(),
        )

    yield spectre_server.core.batches.Batches(
        TAG,
        spectre_server.core.batches.IQStreamBatch,
        batches_dir_path=spectre_config_paths.get_batches_dir_path(),
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
