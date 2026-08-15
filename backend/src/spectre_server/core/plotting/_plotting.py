# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import datetime
import gc
import os
import typing

import matplotlib.colors
import matplotlib.dates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import use

import spectre_server.core.config
import spectre_server.core.spectrograms


@dataclasses.dataclass(frozen=True)
class PanelFormat:
    """Visual style applied to all panels in a stack."""

    small_size: int = 14
    medium_size: int = 16
    large_size: int = 18
    style: str = "dark_background"
    spectrogram_cmap: str = "gray"


@dataclasses.dataclass
class SpectrogramPanel:
    """Configuration for a single spectrogram in a panel stack."""

    spectrogram: spectre_server.core.spectrograms.Spectrogram
    log_norm: bool = False
    dBb: bool = False
    vmin: typing.Optional[float] = None
    vmax: typing.Optional[float] = None


class PanelStack:
    """Plot one or more spectrograms in a vertically stacked figure."""

    def __init__(
        self,
        panel_format: PanelFormat = PanelFormat(),
        elapsed_time: bool = False,
        mhz: bool = False,
        figsize: tuple[int, int] = (15, 8),
        non_interactive: bool = False,
    ) -> None:
        self._panel_format = panel_format
        self._elapsed_time = elapsed_time
        self._mhz = mhz
        self._figsize = figsize
        self._panels: list[SpectrogramPanel] = []

        if non_interactive:
            use("agg")

    @property
    def num_panels(self) -> int:
        return len(self._panels)

    def add_panel(self, panel: SpectrogramPanel) -> None:
        self._panels.append(panel)

    def _start_date_str(self, panel: SpectrogramPanel) -> str:
        dt = panel.spectrogram.start_datetime.astype(datetime.datetime)
        return datetime.datetime.strftime(
            dt, spectre_server.core.config.TimeFormat.DATE
        )

    def _get_times(self, panel: SpectrogramPanel):
        if self._elapsed_time:
            return panel.spectrogram.times
        return panel.spectrogram.datetimes

    def _get_frequencies(self, panel: SpectrogramPanel):
        freqs = panel.spectrogram.frequencies
        if self._mhz:
            return freqs / 1e6
        return freqs

    def _draw_panel(self, ax, panel: SpectrogramPanel) -> None:
        times = self._get_times(panel)
        frequencies = self._get_frequencies(panel)
        fmt = self._panel_format

        if panel.dBb:
            dynamic_spectra = panel.spectrogram.compute_dynamic_spectra_dBb()
            vmin = panel.vmin if panel.vmin is not None else -1
            vmax = panel.vmax if panel.vmax is not None else 2
            pcm = ax.pcolormesh(
                times,
                frequencies,
                dynamic_spectra,
                vmin=vmin,
                vmax=vmax,
                cmap=fmt.spectrogram_cmap,
            )
            cbar_ticks = np.linspace(vmin, vmax, 6)
            cbar = ax.figure.colorbar(pcm, ax=ax, ticks=cbar_ticks)
            cbar.set_label("dB")
        else:
            dynamic_spectra = panel.spectrogram.dynamic_spectra
            norm = None
            if panel.log_norm:
                positive = dynamic_spectra[dynamic_spectra > 0]
                if positive.size > 0:
                    norm = matplotlib.colors.LogNorm(
                        vmin=np.nanmin(positive), vmax=np.nanmax(dynamic_spectra)
                    )
            ax.pcolormesh(
                times,
                frequencies,
                dynamic_spectra,
                cmap=fmt.spectrogram_cmap,
                norm=norm,
            )

    def _annotate_yaxis(self, ax) -> None:
        label = "Frequency [MHz]" if self._mhz else "Frequency [Hz]"
        ax.set_ylabel(label)

    def _annotate_xaxis(self, ax, panel: SpectrogramPanel) -> None:
        start_date = self._start_date_str(panel)
        if self._elapsed_time:
            ax.set_xlabel(f"Time [s] (Start Date: {start_date})")
        else:
            ax.set_xlabel(f"Time [UTC] (Start Date: {start_date})")
            ax.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter(
                    spectre_server.core.config.TimeFormat.TIME
                )
            )

    def _make_figure(self):
        if self.num_panels < 1:
            raise ValueError("There must be at least one panel in the stack.")

        fmt = self._panel_format
        plt.style.use(fmt.style)
        plt.rc("font", size=fmt.small_size)
        plt.rc("axes", titlesize=fmt.medium_size, labelsize=fmt.medium_size)
        plt.rc("xtick", labelsize=fmt.small_size)
        plt.rc("ytick", labelsize=fmt.small_size)
        plt.rc("figure", titlesize=fmt.large_size)

        fig, axs = plt.subplots(
            self.num_panels, 1, figsize=self._figsize, layout="constrained"
        )
        axs = np.atleast_1d(axs)

        for i, panel in enumerate(self._panels):
            ax = axs[i]
            self._draw_panel(ax, panel)
            self._annotate_yaxis(ax)
            if i == self.num_panels - 1:
                self._annotate_xaxis(ax, panel)
            else:
                ax.tick_params(axis="x", labelbottom=False)

        return fig

    def _close(self, fig) -> None:
        fig.clear()
        plt.close(fig)
        gc.collect()

    def save(self, tag: str, batches_dir_path: typing.Optional[str] = None) -> str:
        """Save the panel stack as a PNG batch file.

        :return: The file path of the created PNG.
        """
        fig = self._make_figure()
        first_panel = self._panels[0]

        start_dt = typing.cast(
            datetime.datetime,
            first_panel.spectrogram.start_datetime.astype(datetime.datetime),
        )
        batch_name = (
            f"{start_dt.strftime(spectre_server.core.config.TimeFormat.DATETIME)}_{tag}"
        )
        batch_file_path = os.path.join(
            batches_dir_path
            or spectre_server.core.config.paths.get_batches_dir_path(
                start_dt.year, start_dt.month, start_dt.day
            ),
            f"{batch_name}.png",
        )
        os.makedirs(os.path.dirname(batch_file_path), exist_ok=True)
        fig.savefig(batch_file_path)
        self._close(fig)
        return batch_file_path
