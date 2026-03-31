# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import numpy as np

import spectre_server.core.spectrograms


@pytest.fixture
def spectrogram() -> spectre_server.core.spectrograms.Spectrogram:
    """Create the following spectrogram:

    1MHz  | 0    1    2    3   4   5   |
    2MHz  | 6    7    8    9   10  11  |
    3MHz  | 12   13   14   15  16  17  |
    4MHz  | 18   19   20   21  22  23  |
            0.0  0.2  0.4  0.6 0.8 1.0 [s]
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


class TestTimeAverage:
    def test_resolution_too_small(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check an error is raised when the desired time resolution is less than the current."""
        with pytest.raises(ValueError):
            spectre_server.core.spectrograms.time_average(spectrogram, 0.1)

    def test_resolution_too_big(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check an error is raised when the desired time resolution is more than the time spanned by the spectrogram."""
        with pytest.raises(ValueError):
            spectre_server.core.spectrograms.time_average(spectrogram, 1.0)

    def test_no_change_at_current_resolution(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check that we get back the spectrogram unchanged when the time resolution is equal to the current."""
        averaged_s = spectre_server.core.spectrograms.time_average(spectrogram, 0.2)
        assert spectrogram.time_resolution == averaged_s.time_resolution
        assert np.array_equal(averaged_s.times, spectrogram.times)
        assert np.array_equal(averaged_s.frequencies, spectrogram.frequencies)
        assert np.array_equal(averaged_s.dynamic_spectra, spectrogram.dynamic_spectra)

    @pytest.mark.parametrize(
        "resolution, expected_resolution, expected_dynamic_spectra, expected_times",
        [
            # Impossible resolution, moving average divides 6 spectra into 3 full windows.
            pytest.param(
                0.45,
                0.4,
                [
                    [0.5, 2.5, 4.5],
                    [6.5, 8.5, 10.5],
                    [12.5, 14.5, 16.5],
                    [18.5, 20.5, 22.5],
                ],
                [0, 0.4, 0.8],
            ),
            # Impossible resolution, moving average divides 6 spectra into 1 full window, 1 partial.
            pytest.param(
                0.85,
                0.8,
                [[1.5, 4.5], [7.5, 10.5], [13.5, 16.5], [19.5, 22.5]],
                [0, 0.8],
            ),
            # Exact resolution, moving average divides 6 spectra into 1 full window, 1 partial.
            pytest.param(
                0.8,
                0.8,
                [[1.5, 4.5], [7.5, 10.5], [13.5, 16.5], [19.5, 22.5]],
                [0, 0.8],
            ),
        ],
    )
    def test_averaging(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        resolution: float,
        expected_resolution: float,
        expected_dynamic_spectra: list[list[float]],
        expected_times: list[float],
    ) -> None:
        """Check that time averaging yields the correct resolution, dynamic spectra, times, and frequencies."""
        averaged_s = spectre_server.core.spectrograms.time_average(
            spectrogram, resolution
        )
        assert averaged_s.time_resolution == expected_resolution
        assert np.allclose(
            averaged_s.dynamic_spectra,
            np.array(expected_dynamic_spectra, dtype=np.float32),
        )
        assert np.allclose(averaged_s.times, np.array(expected_times, dtype=np.float32))
        assert np.allclose(averaged_s.frequencies, spectrogram.frequencies)


class TestFrequencyAverage:
    def test_resolution_too_small(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check an error is raised when the desired frequency resolution is less than the current."""
        with pytest.raises(ValueError):
            spectre_server.core.spectrograms.frequency_average(spectrogram, 0.5e6)

    def test_resolution_too_big(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check an error is raised when the desired frequency resolution is more than the frequency spanned by the spectrogram."""
        with pytest.raises(ValueError):
            spectre_server.core.spectrograms.frequency_average(spectrogram, 3e6)

    def test_no_change_at_current_resolution(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check that we get back the spectrogram unchanged when the frequency resolution is equal to the current."""
        averaged_s = spectre_server.core.spectrograms.frequency_average(
            spectrogram, 1e6
        )
        assert spectrogram.frequency_resolution == averaged_s.frequency_resolution
        assert np.array_equal(averaged_s.frequencies, spectrogram.frequencies)
        assert np.array_equal(averaged_s.times, spectrogram.times)
        assert np.array_equal(averaged_s.dynamic_spectra, spectrogram.dynamic_spectra)

    @pytest.mark.parametrize(
        "resolution, expected_resolution, expected_dynamic_spectra, expected_frequencies",
        [
            # Impossible resolution, moving average divides 4 frequency bins into 2 full windows.
            pytest.param(
                2.5e6,
                2e6,
                [
                    [3, 4, 5, 6, 7, 8],
                    [15, 16, 17, 18, 19, 20],
                ],
                [1.5e6, 3.5e6],
            ),
            # Exact resolution, moving average divides 4 frequency bins into 2 full windows.
            pytest.param(
                2e6,
                2e6,
                [
                    [3, 4, 5, 6, 7, 8],
                    [15, 16, 17, 18, 19, 20],
                ],
                [1.5e6, 3.5e6],
            ),
        ],
    )
    def test_averaging(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        resolution: float,
        expected_resolution: float,
        expected_dynamic_spectra: list[list[float]],
        expected_frequencies: list[float],
    ) -> None:
        """Check that frequency averaging yields the correct resolution, dynamic spectra, frequencies, and times."""
        averaged_s = spectre_server.core.spectrograms.frequency_average(
            spectrogram, resolution
        )
        assert averaged_s.frequency_resolution == expected_resolution
        assert np.allclose(
            averaged_s.dynamic_spectra,
            np.array(expected_dynamic_spectra, dtype=np.float32),
        )
        assert np.allclose(
            averaged_s.frequencies,
            np.array(expected_frequencies, dtype=np.float32),
        )
        assert np.allclose(averaged_s.times, spectrogram.times)
