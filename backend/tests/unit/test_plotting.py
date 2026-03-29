# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import os
import datetime

import numpy as np
import matplotlib.axes
import matplotlib.figure

import spectre_server.core.plotting
import spectre_server.core.config
import spectre_server.core.spectrograms


@pytest.fixture(autouse=True)
def setup_random_seed():
    """Set fixed random seed for all tests in this module."""
    # Arbitrarily chosen random seed.
    np.random.seed(42)


@pytest.fixture
def figure() -> matplotlib.figure.Figure:
    return matplotlib.figure.Figure()


@pytest.fixture
def axes(figure: matplotlib.figure.Figure) -> matplotlib.axes.Axes:
    return matplotlib.axes.Axes(figure, [0.1, 0.1, 0.8, 0.8])


# An arbitrary datetime to assign to the first spectrum in the spectrogram fixture.
ARBITRARY_DATETIME = datetime.datetime(2025, 2, 13, 6, 0, 0)
TAG = "tag"


@pytest.fixture
def spectrogram() -> spectre_server.core.spectrograms.Spectrogram:
    """Create a spectrogram, using random values for the spectral components."""
    num_spectrums = 20
    num_spectral_components = 64

    # Populate the dynamic spectra with some random values.
    dynamic_spectra = np.random.uniform(
        -1, 1, (num_spectral_components, num_spectrums)
    ).astype(np.float32)
    # Arbitrarily, consider `num_spectrums` spectrums over an interval of 10 [s]
    times = np.linspace(0, 10, num_spectrums).astype(np.float32)
    # Arbitrarily, consider `num_spectral_components` spectral components, over the FM band
    frequencies = np.linspace(90e6, 110e6, num_spectral_components).astype(np.float32)
    # Arbitrarily, assign some date to be the datetime corresponding to the first spectrum.
    start_datetime = ARBITRARY_DATETIME
    spectrum_unit = spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE
    return spectre_server.core.spectrograms.Spectrogram(
        dynamic_spectra, times, frequencies, spectrum_unit, start_datetime
    )


@pytest.fixture
def base_panel(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.BasePanel:
    """Arbitrarily create an instance of any `BasePanel` subclass, to test functionality of `BasePanel`."""
    return spectre_server.core.plotting.SpectrogramPanel(spectrogram)


@pytest.fixture
def base_time_series_panel(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.BaseTimeSeriesPanel:
    """Arbitrarily create an instance of any `BaseTimeSeriesPanel` subclass, to test functionality of `BaseTimeSeriesPanel`."""
    return spectre_server.core.plotting.SpectrogramPanel(spectrogram)


@pytest.fixture
def frequency_cuts_panel_relative_cuts(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.FrequencyCutsPanel:
    """A frequency cuts panel, with cuts indicated by relative times, using default keyword arguments."""
    return spectre_server.core.plotting.FrequencyCutsPanel(spectrogram, 0.0, 1.0)


@pytest.fixture
def frequency_cuts_panel_datetime_cuts(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.FrequencyCutsPanel:
    """A frequency cuts panel, with cuts indicated by datetimes, using default keyword arguments."""
    cuts = [
        datetime.datetime.strftime(
            ARBITRARY_DATETIME, spectre_server.core.config.TimeFormat.DATETIME
        ),
        datetime.datetime.strftime(
            ARBITRARY_DATETIME + datetime.timedelta(1),
            spectre_server.core.config.TimeFormat.DATETIME,
        ),
    ]
    return spectre_server.core.plotting.FrequencyCutsPanel(spectrogram, *cuts)


@pytest.fixture
def frequency_cuts_panel_dBb(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.FrequencyCutsPanel:
    """A frequency cuts panel, whose spectrums are in units of decibels above the background."""
    return spectre_server.core.plotting.FrequencyCutsPanel(
        spectrogram, 0.0, 1.0, dBb=True
    )


@pytest.fixture
def frequency_cuts_panel_peak_normalised(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.FrequencyCutsPanel:
    """A frequency cuts panel, whose spectrums are in units normalised to the peak values, respectively."""
    return spectre_server.core.plotting.FrequencyCutsPanel(
        spectrogram, 0.0, 1.0, peak_normalise=True
    )


@pytest.fixture
def time_cuts_panel(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.TimeCutsPanel:
    """A time cuts panel, using the default keyword arguments."""
    return spectre_server.core.plotting.TimeCutsPanel(spectrogram, 90e6, 90.3e6)


@pytest.fixture
def time_cuts_panel_dBb(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.TimeCutsPanel:
    """A time cuts panel, whose spectrums are in units of decibels above the background."""
    return spectre_server.core.plotting.TimeCutsPanel(
        spectrogram, 90e6, 90.3e6, dBb=True
    )


@pytest.fixture
def time_cuts_panel_peak_normalised(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.TimeCutsPanel:
    """A time cuts panel, whose spectrums are in units normalised to the peak values, respectively."""
    return spectre_server.core.plotting.TimeCutsPanel(
        spectrogram, 90e6, 90.3e6, peak_normalise=True
    )


@pytest.fixture
def integral_over_frequency_panel(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.IntegralOverFrequencyPanel:
    """A panel plotting the integral of the spectrogram over frequency, using default system arguments."""
    return spectre_server.core.plotting.IntegralOverFrequencyPanel(spectrogram)


@pytest.fixture
def spectrogram_panel(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.SpectrogramPanel:
    """A spectrogram panel using default keyword arguments."""
    return spectre_server.core.plotting.SpectrogramPanel(spectrogram)


@pytest.fixture
def spectrogram_panel_dBb(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.SpectrogramPanel:
    """A spectrogram panel with dBb visualization."""
    return spectre_server.core.plotting.SpectrogramPanel(spectrogram, dBb=True)


@pytest.fixture
def spectrogram_panel_log_norm(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.SpectrogramPanel:
    """A spectrogram panel with logarithmic normalization."""
    return spectre_server.core.plotting.SpectrogramPanel(spectrogram, log_norm=True)


@pytest.fixture
def panel_stack() -> spectre_server.core.plotting.PanelStack:
    """Create a non-interactive panel stack for testing."""
    return spectre_server.core.plotting.PanelStack(non_interactive=True)


class TestBasePanel:
    """Test shared functionality between all `BasePanel` subclasses."""

    def test_initialisation(
        self,
        base_panel: spectre_server.core.plotting.BasePanel,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check that a `BasePanel` subclass is initialised correctly."""
        # Test the public instance attributes are set correctly
        assert base_panel.name == spectre_server.core.plotting.PanelName.SPECTROGRAM
        assert base_panel.spectrogram == spectrogram
        assert base_panel.get_identifier() is None

        with pytest.raises(ValueError):
            _ = base_panel.get_panel_format()

    def test_xaxis_hidden(
        self,
        base_panel: spectre_server.core.plotting.BasePanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that calling for the xaxis labels to be hidden, actually hides them."""
        base_panel.set_ax(axes)
        base_panel.hide_xaxis_labels()
        assert not base_panel.get_xaxis_labels()

    def test_yaxis_hidden(
        self,
        base_panel: spectre_server.core.plotting.BasePanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that calling for the yaxis labels to be hidden, actually hides them."""
        base_panel.set_ax(axes)
        base_panel.hide_yaxis_labels()
        assert not base_panel.get_yaxis_labels()


class TestBaseTimeSeriesPanel:
    def test_xaxis_is_time(
        self, base_time_series_panel: spectre_server.core.plotting.BaseTimeSeriesPanel
    ) -> None:
        """Check that the xaxis type for a time series panel is always time."""
        assert (
            base_time_series_panel.xaxis_type
            == spectre_server.core.plotting.XAxisType.TIME
        )

    def test_times(
        self,
        base_time_series_panel: spectre_server.core.plotting.BaseTimeSeriesPanel,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check that setting the time type for the panel, updates the times of each spectrum appropriately.

        The `spectrogram` fixture is used to construct the panel, so we use that to compare equality.
        """

        # Check both cases of time type.
        base_time_series_panel.set_time_type(
            spectre_server.core.spectrograms.TimeType.RELATIVE
        )
        assert np.array_equal(base_time_series_panel.times, spectrogram.times)

        base_time_series_panel.set_time_type(
            spectre_server.core.spectrograms.TimeType.DATETIMES
        )
        assert np.array_equal(base_time_series_panel.times, spectrogram.datetimes)

    @pytest.mark.parametrize(
        ("time_type", "expected_label"),
        [
            (spectre_server.core.spectrograms.TimeType.RELATIVE, "Time [s]"),
            (
                spectre_server.core.spectrograms.TimeType.DATETIMES,
                "Time [UTC] (Start Date: 2025-02-13)",
            ),
        ],
    )
    def test_xaxis_labelling(
        self,
        base_time_series_panel: spectre_server.core.plotting.BaseTimeSeriesPanel,
        axes: matplotlib.axes.Axes,
        time_type: spectre_server.core.spectrograms.TimeType,
        expected_label: str,
    ) -> None:
        """Check axis labeling for different time types."""
        base_time_series_panel.set_ax(axes)
        base_time_series_panel.set_time_type(time_type)
        base_time_series_panel.annotate_xaxis()
        assert base_time_series_panel.get_xlabel() == expected_label


# ...existing code...


class TestFrequencyCutsPanel:
    def test_xaxis_is_frequency(
        self,
        frequency_cuts_panel_relative_cuts: spectre_server.core.plotting.FrequencyCutsPanel,
    ) -> None:
        """Check that the xaxis type for a time series panel is always frequency.

        Arbitrarily choose the relative cuts panel, as it doesn't matter for this test.
        """
        assert (
            frequency_cuts_panel_relative_cuts.xaxis_type
            == spectre_server.core.plotting.XAxisType.FREQUENCY
        )

    def test_frequencies(
        self,
        frequency_cuts_panel_relative_cuts: spectre_server.core.plotting.FrequencyCutsPanel,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check that the frequencies assigned to each spectral component as managed by the panel, are equal to the frequencies
        assigned to each spectral component in the spectrogram used to construct the panel.

        Arbitrarily choose the relative cuts panel, as it doesn't matter for this test.
        """
        assert np.array_equal(
            frequency_cuts_panel_relative_cuts.frequencies, spectrogram.frequencies
        )

    def test_xaxis_annotation(
        self,
        frequency_cuts_panel_relative_cuts: spectre_server.core.plotting.FrequencyCutsPanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that the xaxis gets annotated appropriately."""
        frequency_cuts_panel_relative_cuts.set_ax(axes)
        frequency_cuts_panel_relative_cuts.annotate_xaxis()
        assert frequency_cuts_panel_relative_cuts.get_xlabel() == "Frequency [Hz]"

    def test_no_times_specified(
        self, spectrogram: spectre_server.core.spectrograms.Spectrogram
    ) -> None:
        """Check that an error is raised when the class is instantiated with no times specified."""
        times: list[float] = []
        with pytest.raises(ValueError):
            spectre_server.core.plotting.FrequencyCutsPanel(spectrogram, *times)

    def test_yaxis_annotation_dBb(
        self,
        frequency_cuts_panel_dBb: spectre_server.core.plotting.FrequencyCutsPanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that the ylabel is annotated appropriately, in the case where the spectrum units are `dBb`."""
        frequency_cuts_panel_dBb.set_ax(axes)
        frequency_cuts_panel_dBb.annotate_yaxis()
        assert frequency_cuts_panel_dBb.get_ylabel() == "dBb"

    def test_yaxis_annotation_peak_normalised(
        self,
        frequency_cuts_panel_peak_normalised: spectre_server.core.plotting.FrequencyCutsPanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that the ylabel is annotated appropriately, in the case where the spectrum units are normalised to their peak values, respectively."""
        frequency_cuts_panel_peak_normalised.set_ax(axes)
        frequency_cuts_panel_peak_normalised.annotate_yaxis()
        # We don't expect any label in this case
        assert not frequency_cuts_panel_peak_normalised.get_ylabel()

    def test_yaxis_annotation(
        self,
        frequency_cuts_panel_relative_cuts: spectre_server.core.plotting.FrequencyCutsPanel,
        axes: matplotlib.axes.Axes,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check that the ylabel is annotated appropriately, when the spectrum units are those defined by the spectrogram used to construct
        the panel.
        """
        frequency_cuts_panel_relative_cuts.set_ax(axes)
        frequency_cuts_panel_relative_cuts.annotate_yaxis()
        assert (
            frequency_cuts_panel_relative_cuts.get_ylabel()
            == f"{spectrogram.spectrum_unit.value}".capitalize()
        )


class TestTimeCutsPanel:
    def test_no_frequencies_specified(
        self, spectrogram: spectre_server.core.spectrograms.Spectrogram
    ) -> None:
        """Check that an error is raised when the class is instantiated with no frequencies specified."""
        frequencies: list[float] = []
        with pytest.raises(ValueError):
            spectre_server.core.plotting.TimeCutsPanel(spectrogram, *frequencies)

    def test_yaxis_annotation_dBb(
        self,
        time_cuts_panel_dBb: spectre_server.core.plotting.TimeCutsPanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that the ylabel is annotated appropriately, in the case where the spectrum units are `dBb`."""
        # Arbitrarily set the time type (it has to be set)
        time_cuts_panel_dBb.set_time_type(
            spectre_server.core.spectrograms.TimeType.RELATIVE
        )
        time_cuts_panel_dBb.set_ax(axes)
        time_cuts_panel_dBb.annotate_yaxis()
        assert time_cuts_panel_dBb.get_ylabel() == "dBb"

    def test_yaxis_annotation_peak_normalised(
        self,
        time_cuts_panel_peak_normalised: spectre_server.core.plotting.TimeCutsPanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that the ylabel is annotated appropriately, in the case where the spectrum units are normalised to their peak values, respectively."""
        time_cuts_panel_peak_normalised.set_ax(axes)
        time_cuts_panel_peak_normalised.annotate_yaxis()
        # We don't expect any label in this case
        assert not time_cuts_panel_peak_normalised.get_ylabel()

    def test_yaxis_annotation(
        self,
        time_cuts_panel: spectre_server.core.plotting.TimeCutsPanel,
        axes: matplotlib.axes.Axes,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        """Check that the ylabel is annotated appropriately, when the spectrum units are those defined by the spectrogram used to construct
        the panel.
        """
        time_cuts_panel.set_ax(axes)
        time_cuts_panel.annotate_yaxis()
        assert (
            time_cuts_panel.get_ylabel()
            == f"{spectrogram.spectrum_unit.value}".capitalize()
        )


class TestIntegralOverFrequencyPanel:
    def test_yaxis_annotation(
        self,
        integral_over_frequency_panel: spectre_server.core.plotting.IntegralOverFrequencyPanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that the yaxis is not annotated."""
        integral_over_frequency_panel.set_ax(axes)
        integral_over_frequency_panel.annotate_yaxis()
        # We don't expect any label in this case
        assert not integral_over_frequency_panel.get_ylabel()


class TestSpectrogramPanel:
    """Test functionality specific to SpectrogramPanel."""

    def test_yaxis_annotation(
        self,
        spectrogram_panel: spectre_server.core.plotting.SpectrogramPanel,
        axes: matplotlib.axes.Axes,
    ) -> None:
        """Check that the yaxis is annotated appropriately."""
        spectrogram_panel.set_ax(axes)
        spectrogram_panel.annotate_yaxis()
        assert spectrogram_panel.get_ylabel() == "Frequency [Hz]"


class TestPanelStack:
    def test_time_type_getter_setters(
        self, panel_stack: spectre_server.core.plotting.PanelStack
    ) -> None:
        """Check that the time type getters and setters work as expected."""
        panel_stack.time_type = spectre_server.core.spectrograms.TimeType.RELATIVE
        assert (
            panel_stack.time_type == spectre_server.core.spectrograms.TimeType.RELATIVE
        )

        panel_stack.time_type = spectre_server.core.spectrograms.TimeType.DATETIMES
        assert (
            panel_stack.time_type == spectre_server.core.spectrograms.TimeType.DATETIMES
        )

    def test_adding_panel_increments_panel_count(
        self,
        panel_stack: spectre_server.core.plotting.PanelStack,
        spectrogram_panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        """Check that adding a panel increments the number of panels in the stack."""
        # Take a record of the initial number of panels
        initial_num_panels = panel_stack.num_panels

        # Check that it is zero.
        assert initial_num_panels == 0

        # Add a panel, and check that the number of panels is as expected.
        panel_stack.add_panel(spectrogram_panel)
        assert panel_stack.num_panels == initial_num_panels + 1

        # Add a panel, and check that the number of panels is as expected.
        panel_stack.add_panel(spectrogram_panel)
        assert panel_stack.num_panels == initial_num_panels + 2

    def test_adding_superimposed_panel_increments_panel_count(
        self,
        panel_stack: spectre_server.core.plotting.PanelStack,
        spectrogram_panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        """Check that adding a superimposed panel increments the number of panels in the stack."""
        # Take a record of the initial number of superimposed panels
        initial_num_superimposed_panels = panel_stack.num_superimposed_panels

        # Check that it is zero.
        assert initial_num_superimposed_panels == 0

        # Add a panel, and check that the number of panels is as expected.
        panel_stack.superimpose_panel(spectrogram_panel)
        assert (
            panel_stack.num_superimposed_panels == initial_num_superimposed_panels + 1
        )

        # Add a panel, and check that the number of panels is as expected.
        panel_stack.superimpose_panel(spectrogram_panel)
        assert (
            panel_stack.num_superimposed_panels == initial_num_superimposed_panels + 2
        )

    def test_check_panel_ordering(
        self,
        panel_stack: spectre_server.core.plotting.PanelStack,
        spectrogram_panel: spectre_server.core.plotting.SpectrogramPanel,
        time_cuts_panel: spectre_server.core.plotting.TimeCutsPanel,
        frequency_cuts_panel_relative_cuts: spectre_server.core.plotting.FrequencyCutsPanel,
    ) -> None:
        """Check that panels are ordered by their `XAxisType`.

        Frequency cut panels should always be first, at the top of the plot.
        Regardless of the order in which they were added to the stack. Time series
        panels, on the other hand, should respect the order they were added to the stack.
        """
        panel_stack.add_panel(spectrogram_panel)
        panel_stack.add_panel(frequency_cuts_panel_relative_cuts)
        panel_stack.add_panel(time_cuts_panel)
        # Frequency cut panels should be first, at the top of the plot.
        assert panel_stack.panels == [
            frequency_cuts_panel_relative_cuts,
            spectrogram_panel,
            time_cuts_panel,
        ]

    def test_incompatible_time_types(
        self,
        panel_stack: spectre_server.core.plotting.PanelStack,
        spectrogram_panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        """Check that the panel stack overrides the time type of the panel, if they are incompatible."""
        panel_stack.time_type = spectre_server.core.spectrograms.TimeType.RELATIVE
        spectrogram_panel.set_time_type(
            spectre_server.core.spectrograms.TimeType.DATETIMES
        )
        panel_stack.add_panel(spectrogram_panel)
        assert (
            spectrogram_panel.get_time_type()
            == spectre_server.core.spectrograms.TimeType.RELATIVE
        )

    def test_save_creates_file(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        panel_stack: spectre_server.core.plotting.PanelStack,
        spectrogram_panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        """Test that saving a panel stack, creates a file in the filesystem with the appropriate path."""
        # Add a panel to the stack, so there's something in the figure.
        panel_stack.add_panel(spectrogram_panel)

        batches_dir_path = spectre_config_paths.get_batches_dir_path(2025, 2, 13)

        file_path = panel_stack.save(TAG, batches_dir_path)

        assert file_path == os.path.join(
            batches_dir_path,
            f"2025-02-13T06:00:00.000000Z_{TAG}.png",
        )

        # Check that the file was actually created.
        assert os.path.exists(file_path)

    def test_save_no_panels(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        panel_stack: spectre_server.core.plotting.PanelStack,
    ) -> None:
        """Check that trying to save a plot with no panels raises an error."""
        batches_dir_path = spectre_config_paths.get_batches_dir_path(2025, 2, 13)
        with pytest.raises(ValueError):
            _ = panel_stack.save(TAG, batches_dir_path)

    def test_show_no_panels(
        self, panel_stack: spectre_server.core.plotting.PanelStack
    ) -> None:
        """Check that trying to show a plot with no panels raises an error."""
        with pytest.raises(ValueError):
            panel_stack.show()
