# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import datetime

import matplotlib.colors
import matplotlib.cm
import numpy as np
import numpy.typing as npt

import spectre_server.core.spectrograms
from ._base import BasePanel, BaseTimeSeriesPanel, XAxisType
from ._panel_names import PanelName

T = typing.TypeVar("T")


def _bind_to_colors(
    values: list[T], cmap: str = "winter"
) -> typing.Iterator[tuple[T, npt.NDArray[np.float32]]]:
    """
    Assign RGBA colors to a list of values using a colormap.

    Each value is mapped linearly to a subset of the unit interval and then converted
    to an RGBA color using the specified colormap.

    :param values: List of values to map to colors.
    :param cmap: Name of the Matplotlib colormap to use. Defaults to "winter".
    :return: An iterator of tuples, each containing a value and its corresponding RGBA color.
    """
    colormap = matplotlib.cm.get_cmap(cmap)
    rgbas = colormap(np.linspace(0.1, 0.9, len(values)))
    return zip(values, rgbas)


class FrequencyCutsPanel(BasePanel):
    """
    Panel for visualising spectrogram data as frequency cuts.

    This panel plots spectrums corresponding to specific time instances
    in the spectrogram. Each cut is drawn as a line plot, optionally normalized
    or converted to decibels above the background.
    """

    def __init__(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        *times: float | str,
        dBb: bool = False,
        peak_normalise: bool = False,
    ) -> None:
        """Initialise an instance of `FrequencyCutsPanel`.

        :param spectrogram: The spectrogram to be visualised.
        :param *times: Times at which to take frequency cuts. Can be floats (relative time) or
        strings (formatted datetimes).
        :param dBb: If True, plots the spectrums in decibels above the background. Defaults to False.
        :param peak_normalise: If True, normalizes each spectrum such that its peak value is 1.
        Ignored if `dBb` is True. Defaults to False.
        """
        super().__init__(PanelName.FREQUENCY_CUTS, spectrogram)

        if len(times) == 0:
            raise ValueError(
                f"You must specify the time of at least one cut in `*times`"
            )
        self._times = times

        self._dBb = dBb
        self._peak_normalise = peak_normalise
        self._frequency_cuts: dict[
            float | datetime.datetime, spectre_server.core.spectrograms.FrequencyCut
        ] = {}

    @property
    def xaxis_type(self) -> typing.Literal[XAxisType.FREQUENCY]:
        return XAxisType.FREQUENCY

    @property
    def frequencies(self) -> npt.NDArray[np.float32]:
        """The physical frequencies assigned to each spectral component."""
        return self._spectrogram.frequencies

    def annotate_xaxis(self) -> None:
        """Annotate the x-axis assuming frequency in units of Hz."""
        self._get_ax().set_xlabel("Frequency [Hz]")

    def get_frequency_cuts(
        self,
    ) -> dict[float | datetime.datetime, spectre_server.core.spectrograms.FrequencyCut]:
        """
        Get the frequency cuts for the specified times.

        Computes and caches the spectrum for each requested time. The results are
        stored as a mapping from time to the corresponding `FrequencyCut`.

        :return: A dictionary mapping each time to its corresponding frequency cut.
        """
        if not self._frequency_cuts:
            for time in self._times:
                frequency_cut = self._spectrogram.get_frequency_cut(
                    time, dBb=self._dBb, peak_normalise=self._peak_normalise
                )
                self._frequency_cuts[frequency_cut.time] = frequency_cut
        return self._frequency_cuts

    def get_cut_times(self) -> list[float | datetime.datetime]:
        """
        Get the exact times of the frequency cuts.

        Returns the closest matches to the times specified in the constructor.

        :return: A list of times corresponding to the stored frequency cuts.
        """
        frequency_cuts = self.get_frequency_cuts()
        return list(frequency_cuts.keys())

    def draw(self) -> None:
        """Draw the frequency cuts onto the panel."""
        frequency_cuts = self.get_frequency_cuts()
        for time, color in self.bind_to_colors():
            frequency_cut = frequency_cuts[time]
            self._get_ax().step(
                self.frequencies,  # convert to MHz
                frequency_cut.cut,
                where="mid",
                color=color,
            )

    def annotate_yaxis(self) -> None:
        """Annotate the y-axis of the panel based on the current state.

        The y-axis label reflects whether the data is in decibels above the background (`dBb`),
        normalized to peak values, or in the original units of the spectrogram.
        """
        ax = self._get_ax()
        if self._dBb:
            ax.set_ylabel("dBb")
        elif self._peak_normalise:
            # no y-axis label if we are peak normalising
            return
        else:
            ax.set_ylabel(f"{self._spectrogram.spectrum_unit.value.capitalize()}")

    def bind_to_colors(
        self,
    ) -> typing.Iterator[tuple[float | datetime.datetime, npt.NDArray[np.float32]]]:
        """
        Bind each frequency cut time to an RGBA color.

        Colors are assigned using the colormap specified in the panel format.

        :return: An iterator of tuples, each containing a cut time and its corresponding RGBA color.
        """
        return _bind_to_colors(
            self.get_cut_times(), cmap=self.get_panel_format().line_cmap
        )


class TimeCutsPanel(BaseTimeSeriesPanel):
    """
    Panel for visualising spectrogram data as time series of spectral components.

    This panel plots the time evolution of spectral components at specific
    frequencies in the spectrogram. Each time series is drawn as a line plot,
    optionally normalized, background-subtracted, or converted to decibels above the background.
    """

    def __init__(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        *frequencies: float,
        dBb: bool = False,
        peak_normalise: bool = False,
        background_subtract: bool = False,
    ) -> None:
        """Initialise an instance of `TimeCutsPanel`.

        :param spectrogram: The spectrogram to be visualised.
        :param *frequencies: Frequencies at which to extract time series.
        :param dBb: If True, returns the cuts in decibels above the background. Defaults to False.
        :param peak_normalise: If True, normalizes each time series so its peak value is 1.
        Ignored if `dBb` is True. Defaults to False.
        :param background_subtract: If True, subtracts the background from each time series.
        Ignored if `dBb` is True. Defaults to False.
        """
        super().__init__(PanelName.TIME_CUTS, spectrogram)

        if len(frequencies) == 0:
            raise ValueError(
                f"You must specify the frequency of at least one cut in `*frequencies`."
            )
        self._frequencies = frequencies

        self._dBb = dBb
        self._peak_normalise = peak_normalise
        self._background_subtract = background_subtract
        self._time_cuts: dict[float, spectre_server.core.spectrograms.TimeCut] = {}

    def get_time_cuts(self) -> dict[float, spectre_server.core.spectrograms.TimeCut]:
        """
        Get the time cuts for the specified frequencies.

        Computes and caches the time series for each requested frequency. The results
        are stored as a mapping from frequency to `TimeCut`.

        :return: A dictionary mapping each frequency to its corresponding time cut.
        """
        if not self._time_cuts:
            for frequency in self._frequencies:
                time_cut = self._spectrogram.get_time_cut(
                    frequency,
                    dBb=self._dBb,
                    peak_normalise=self._peak_normalise,
                    correct_background=self._background_subtract,
                    return_time_type=self.get_time_type(),
                )
                self._time_cuts[time_cut.frequency] = time_cut
        return self._time_cuts

    def get_frequencies(self) -> list[float]:
        """
        Get the exact frequencies for the spectral components being plotted.

        :return: A list of frequencies corresponding to the stored time cuts.
        """
        time_cuts = self.get_time_cuts()
        return list(time_cuts.keys())

    def draw(self) -> None:
        """Draw the time series for each spectral component onto the panel."""
        time_cuts = self.get_time_cuts()
        for frequency, color in self.bind_to_colors():
            time_cut = time_cuts[frequency]
            self._get_ax().step(self.times, time_cut.cut, where="mid", color=color)

    def annotate_yaxis(self) -> None:
        """
        Annotate the y-axis of the panel based on the current state.

        The y-axis label reflects whether the data is in decibels above the background (`dBb`),
        normalized to peak values, or in the original units of the spectrogram.
        """
        ax = self._get_ax()
        if self._dBb:
            ax.set_ylabel("dBb")
        elif self._peak_normalise:
            return  # no y-axis label if we are peak normalising.
        else:
            ax.set_ylabel(f"{self._spectrogram.spectrum_unit.value.capitalize()}")

    def bind_to_colors(self) -> typing.Iterator[tuple[float, npt.NDArray[np.float32]]]:
        """
        Bind each spectral component's frequency to an RGBA color.

        Colors are assigned using the colormap specified in the panel format.

        :return: An iterator of tuples, each containing a frequency and its corresponding RGBA color.
        """
        return _bind_to_colors(
            self.get_frequencies(), cmap=self.get_panel_format().line_cmap
        )


class IntegralOverFrequencyPanel(BaseTimeSeriesPanel):
    """Panel for visualising the spectrogram integrated over frequency.

    This panel plots the spectrogram numerically integrated over frequency as a time
    series. The result can be normalized to its peak value or adjusted by subtracting
    the background.
    """

    def __init__(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        peak_normalise: bool = False,
        background_subtract: bool = False,
    ):
        """Initialise an instance of `IntegralOverFrequencyPanel`.

        :param spectrogram: The spectrogram to be visualised.
        :param peak_normalise: If True, normalizes the integral so its peak value is 1. Defaults to False.
        :param background_subtract: If True, subtracts the background after computing the integral. Defaults to False.
        """
        super().__init__(PanelName.INTEGRAL_OVER_FREQUENCY, spectrogram)
        self._peak_normalise = peak_normalise
        self._background_subtract = background_subtract

    def draw(self):
        """Integrate the spectrogram over frequency and plot the result."""
        I = self._spectrogram.integrate_over_frequency(
            correct_background=self._background_subtract,
            peak_normalise=self._peak_normalise,
        )
        self._get_ax().step(
            self.times, I, where="mid", color=self.get_panel_format().line_color
        )

    def annotate_yaxis(self):
        """This panel does not annotate the y-axis."""


class SpectrogramPanel(BaseTimeSeriesPanel):
    """
    Panel for visualising the full spectrogram.

    This panel plots the spectrogram as a colormap, with optional log normalization or
    in units of decibels above the background.
    """

    def __init__(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        log_norm: bool = False,
        dBb: bool = False,
        vmin: typing.Optional[float] = None,
        vmax: typing.Optional[float] = None,
    ) -> None:
        """Initialise an instance of `SpectrogramPanel`.

        :param spectrogram: The spectrogram to be visualised.
        :param log_norm: If True, normalizes the values to the 0-1 range on a logarithmic scale. Defaults to False.
        :param dBb: If True, plots the spectrogram in decibels above the background. Defaults to False.
        :param vmin: Minimum value for the colormap. Only applies if `dBb` is True. Defaults to None.
        :param vmax: Maximum value for the colormap. Only applies if `dBb` is True. Defaults to None.
        """
        super().__init__(PanelName.SPECTROGRAM, spectrogram)
        self._log_norm = log_norm
        self._dBb = dBb
        self._vmin = vmin
        self._vmax = vmax

    def _draw_dBb(self) -> None:
        """Plot the spectrogram in decibels above the background (dBb).

        This method handles plotting the spectrogram with dBb scaling, applying
        colormap bounds (`vmin` and `vmax`) and adding a colorbar to the panel.
        """
        dynamic_spectra = self._spectrogram.compute_dynamic_spectra_dBb()

        # use defaults if neither vmin or vmax is specified
        vmin = self._vmin or -1
        vmax = self._vmax or 2

        ax = self._get_ax()
        # Plot the spectrogram
        pcm = ax.pcolormesh(
            self.times,
            self._spectrogram.frequencies,
            dynamic_spectra,
            vmin=vmin,
            vmax=vmax,
            cmap=self.get_panel_format().spectrogram_cmap,
        )

        # Add colorbar
        cbar_ticks = np.linspace(vmin, vmax, 6)
        cbar = self._get_fig().colorbar(pcm, ax=ax, ticks=cbar_ticks)
        cbar.set_label("dBb")

    def _draw_normal(self) -> None:
        """Plot the spectrogram with optional logarithmic normalization.

        This method handles plotting the spectrogram without dBb scaling, using
        linear or log normalization based on the `log_norm` attribute.
        """
        dynamic_spectra = self._spectrogram.dynamic_spectra

        if self._log_norm:
            norm = matplotlib.colors.LogNorm(
                vmin=np.nanmin(dynamic_spectra[dynamic_spectra > 0]),
                vmax=np.nanmax(dynamic_spectra),
            )
        else:
            norm = None

        # Plot the spectrogram
        self._get_ax().pcolormesh(
            self.times,
            self._spectrogram.frequencies,
            dynamic_spectra,
            cmap=self.get_panel_format().spectrogram_cmap,
            norm=norm,
        )

    def draw(self) -> None:
        """Draw the spectrogram onto the panel."""
        if self._dBb:
            self._draw_dBb()
        else:
            self._draw_normal()

    def annotate_yaxis(self) -> None:
        """Annotate the yaxis, assuming units of Hz."""
        self._get_ax().set_ylabel("Frequency [Hz]")
        return

    def overlay_time_cuts(self, cuts_panel: TimeCutsPanel) -> None:
        """
        Overlay horizontal lines on the spectrogram to indicate time cuts.

        The lines correspond to the frequencies of the cuts on a `TimeCutsPanel`.
        Colors are matched to the lines on the `TimeCutsPanel`.

        :param cuts_panel: The `TimeCutsPanel` containing the cut frequencies to overlay.
        """
        for frequency, color in cuts_panel.bind_to_colors():
            self._get_ax().axhline(
                frequency, color=color, linewidth=self.get_panel_format().line_width
            )

    def overlay_frequency_cuts(self, cuts_panel: FrequencyCutsPanel) -> None:
        """
        Overlay vertical lines on the spectrogram to indicate frequency cuts.

        The lines correspond to the times of the cuts on a `FrequencyCutsPanel`.
        Colors are matched to the lines on the `FrequencyCutsPanel`.

        :param cuts_panel: The `FrequencyCutsPanel` containing the cut times to overlay.
        """
        for time, color in cuts_panel.bind_to_colors():
            self._get_ax().axvline(
                time, color=color, linewidth=self.get_panel_format().line_width
            )
