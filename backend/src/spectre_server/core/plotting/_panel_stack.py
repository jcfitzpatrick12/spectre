# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import typing
import datetime
import gc

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.axes
from matplotlib import use

import spectre_server.core.spectrograms
import spectre_server.core.config

from ._base import BasePanel, XAxisType
from ._format import PanelFormat


class PanelStack:
    """Visualise spectrogram data in a stack of panels."""

    def __init__(
        self,
        panel_format: PanelFormat = PanelFormat(),
        time_type: spectre_server.core.spectrograms.TimeType = spectre_server.core.spectrograms.TimeType.RELATIVE,
        figsize: tuple[int, int] = (15, 8),
        non_interactive: bool = False,
    ) -> None:
        """Initialize an instance of `PanelStack`.

        :param panel_format: Formatting applied across all panels in the stack. Defaults to `PanelFormat()`.
        :param time_type: The type of time assigned to spectrograms, defaults to `spectre_server.core.spectrograms.TimeType.RELATIVE`.
        :param figsize: The size of the `matplotlib` figure as (width, height). Defaults to (15, 8).
        """
        self._panel_format = panel_format
        self._time_type = time_type
        self._figsize = figsize

        if non_interactive:
            # Use a non-interactive matplotlib backend, which can only write files.
            use("agg")

        self._panels: list[BasePanel] = []
        self._superimposed_panels: list[BasePanel] = []

        self._fig: typing.Optional[matplotlib.figure.Figure] = None
        self._axs: typing.Optional[np.ndarray] = None

    def _sort_by_xaxis_type(self, panels: list[BasePanel]) -> list[BasePanel]:
        return list(sorted(panels, key=lambda panel: panel.xaxis_type.value))

    @property
    def panels(self) -> list[BasePanel]:
        """Get the panels in the stack, sorted by their `XAxisType`."""
        return self._sort_by_xaxis_type(self._panels)

    @property
    def superimposed_panels(self) -> list[BasePanel]:
        """Get the superimposed panels in the stack, sorted by their `XAxisType"""
        return self._sort_by_xaxis_type(self._superimposed_panels)

    @property
    def num_panels(self) -> int:
        """Get the number of panels in the stack."""
        return len(self._panels)

    @property
    def num_superimposed_panels(self) -> int:
        """Get the number of superimposed panels in the stack."""
        return len(self._superimposed_panels)

    @property
    def time_type(self) -> spectre_server.core.spectrograms.TimeType:
        """The imposed time type on all time series panels in the stack.

        :raises ValueError: If the `time_type` has not been set.
        """
        return self._time_type

    @time_type.setter
    def time_type(self, value: spectre_server.core.spectrograms.TimeType) -> None:
        """Set the `spectre_server.core.spectrograms.TimeType` for all time series panels in the stack.

        This controls how time is represented and annotated on the panel.

        :param value: The `spectre_server.core.spectrograms.TimeType` to impose on all time series panels in the stack.
        """
        self._time_type = value

    def _get_fig(self) -> matplotlib.figure.Figure:
        """Get the shared `matplotlib` figure for the panel stack.

        :raises ValueError: If the axes have not been initialized.
        """
        if self._fig is None:
            raise ValueError(
                f"An unexpected error has occured, `fig` must be set for the panel stack."
            )
        return self._fig

    def _get_axes(self) -> np.ndarray:
        """Get the `matplotlib` axes in the stack.

        :return: An array of `matplotlib.axes.Axes`, one for each panel in the stack.
        :raises ValueError: If the axes have not been initialized.
        """
        if self._axs is None:
            raise ValueError(
                f"An unexpected error has occured, `axs` must be set for the panel stack."
            )
        return np.atleast_1d(self._axs)

    def _validate_time_type(self, panel: BasePanel) -> None:
        """Check that the time type of the input panel, is consistent with the time type of the stack."""
        if panel.get_time_type() != self._time_type:
            raise ValueError(
                f"Cannot add a panel with inconsistent time type. "
                f"Expected {self._time_type.value}, but got {panel.get_time_type().value}"
            )

    def add_panel(
        self,
        panel: BasePanel,
        identifier: typing.Optional[str] = None,
        panel_format: typing.Optional[PanelFormat] = None,
    ) -> None:
        """Add a panel to the stack.

        Overrides the time type of the panel, to the time type of the stack.

        :param panel: An instance of a `BasePanel` subclass to be added to the stack.
        :param identifier: An typing.Optional string to link the panel with others for superimposing.
        """
        panel.set_panel_format(panel_format or self._panel_format)
        panel.set_time_type(self._time_type)
        if identifier:
            panel.set_identifier(identifier)

        self._panels.append(panel)

    def superimpose_panel(
        self,
        panel: BasePanel,
        identifier: typing.Optional[str] = None,
        panel_format: typing.Optional[PanelFormat] = None,
    ) -> None:
        """Superimpose a panel onto an existing panel in the stack.

        Overrides the time type of the panel, to the time type of the stack.

        :param panel: The panel to superimpose.
        :param identifier: An typing.Optional identifier to link panels during superimposing, defaults to None
        """
        if identifier:
            panel.set_identifier(identifier)
        panel.set_panel_format(panel_format or self._panel_format)
        panel.set_time_type(self._time_type)

        self._superimposed_panels.append(panel)

    def _init_plot_style(self) -> None:
        """Initialize the global plot style for the stack.

        This method sets `matplotlib` styles and font sizes based on the `panel_format`.
        """
        plt.style.use(self._panel_format.style)

        plt.rc("font", size=self._panel_format.small_size)

        plt.rc(
            "axes",
            titlesize=self._panel_format.medium_size,
            labelsize=self._panel_format.medium_size,
        )

        plt.rc("xtick", labelsize=self._panel_format.small_size)
        plt.rc("ytick", labelsize=self._panel_format.small_size)

        plt.rc("legend", fontsize=self._panel_format.small_size)
        plt.rc("figure", titlesize=self._panel_format.large_size)

    def _create_figure_and_axes(self) -> None:
        """Create the `matplotlib` figure and axes for the panel stack.

        This initializes a figure with a specified number of vertically stacked axes.
        """
        self._fig, self._axs = plt.subplots(
            self.num_panels, 1, figsize=self._figsize, layout="constrained"
        )

    def _assign_axes(self) -> None:
        """Assign each axes in the figure to some panel in the stack.

        Axes are shared between panels with common `XAxisType`.
        """
        shared_axes: dict[XAxisType, matplotlib.axes.Axes] = {}
        for i, panel in enumerate(self.panels):
            ax = self._get_axes()[i]
            panel.set_ax(ax)
            panel.set_fig(self._fig)
            if panel.xaxis_type in shared_axes:
                panel.sharex(shared_axes[panel.xaxis_type])
            else:
                shared_axes[panel.xaxis_type] = ax

    def _overlay_superimposed_panels(self) -> None:
        """Superimpose panels onto matching panels in the stack.

        For each superimposed panel, find a matching panel in the stack with the same name
        and identifier. Share the axes and figure, then draw the superimposed panel. If the
        panel contains cuts, overlay those cuts onto the corresponding spectrogram panels.
        """
        for super_panel in self._superimposed_panels:
            for panel in self._panels:
                if panel.name == super_panel.name and (
                    panel.get_identifier() == super_panel.get_identifier()
                ):
                    super_panel.share_axes(panel)
                    super_panel.draw()

    def _make_figure(self) -> None:
        """Make the panel stack figure."""
        if self.num_panels < 1:
            raise ValueError(f"There must be at least one panel in the stack.")

        self._init_plot_style()
        self._create_figure_and_axes()
        self._assign_axes()

        last_panel_per_axis = {panel.xaxis_type: panel for panel in self.panels}

        for panel in self.panels:
            panel.draw()
            panel.annotate_yaxis()

            if panel == last_panel_per_axis[panel.xaxis_type]:
                panel.annotate_xaxis()
            else:
                panel.hide_xaxis_labels()

        self._overlay_superimposed_panels()

    def _close(self) -> None:
        """Prevent memory leaks once a figure has been created, and successfully visualised."""
        self._get_fig().clear()
        plt.close(self._fig)
        # Garbage collection seems to be required to prevent the memory leak.
        # See https://github.com/jcfitzpatrick12/spectre/issues/128
        gc.collect()

    def show(self) -> None:
        """Display the panel stack figure."""
        self._make_figure()
        self._get_fig().show()
        self._close()

    def save(self, tag: str, batches_dir_path: typing.Optional[str] = None) -> str:
        """Save the panel stack figure as a batch file under the input tag.

        :return: The file path of the newly created batch file containing the figure.
        """
        self._make_figure()
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
        # If the parent directory does not exist, create it.
        os.makedirs(os.path.dirname(batch_file_path), exist_ok=True)
        self._get_fig().savefig(batch_file_path)
        self._close()
        return batch_file_path
