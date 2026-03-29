# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import abc
import typing
import enum
import datetime

import numpy.typing as npt
import numpy as np
import matplotlib.axes
import matplotlib.dates
import matplotlib.figure

import spectre_server.core.spectrograms
import spectre_server.core.config
from ._format import PanelFormat
from ._panel_names import PanelName


class XAxisType(enum.Enum):
    """The xaxis type for a panel.

    Axes are shared in a stack between panels with common `XAxisType`.

    :ivar TIME: The xaxis has units of time.
    :ivar FREQUENCY: The xaxis has units of frequency.
    """

    TIME = "time"
    FREQUENCY = "frequency"


class BasePanel(abc.ABC):
    """Abstract base class for a panel used to visualise spectrogram data.

    `BasePanel` instances are designed to be part of a `PanelStack`, where multiple
    panels contribute to a composite plot. Subclasses must implement methods to define
    how the panel is drawn and annotated, and specify its xaxis type.
    """

    def __init__(
        self,
        name: PanelName,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        time_type: spectre_server.core.spectrograms.TimeType = spectre_server.core.spectrograms.TimeType.RELATIVE,
    ) -> None:
        """Initialize an instance of `BasePanel`.

        :param name: The name of the panel.
        :param spectrogram: The spectrogram being visualised.
        :param time_type: Indicates whether the times of each spectrum are relative to the first
        spectrum in the spectrogram, or datetimes.
        """
        self._name = name
        self._spectrogram = spectrogram
        self._time_type = time_type

        # These attributes should be set by instances of `PanelStack`.
        self._ax: typing.Optional[matplotlib.axes.Axes] = None
        self._fig: typing.Optional[matplotlib.figure.Figure] = None
        self._panel_format: typing.Optional[PanelFormat] = None
        self._identifier: typing.Optional[str] = None

    @abc.abstractmethod
    def draw(self) -> None:
        """Modify the `ax` attribute to draw the panel contents."""

    @abc.abstractmethod
    def annotate_xaxis(self) -> None:
        """Modify the `ax` attribute to annotate the xaxis of the panel."""

    @abc.abstractmethod
    def annotate_yaxis(self) -> None:
        """Modify the `ax` attribute to annotate the yaxis of the panel."""

    @property
    @abc.abstractmethod
    def xaxis_type(self) -> XAxisType:
        """Specify the xaxis type for the panel."""

    @property
    def spectrogram(self) -> spectre_server.core.spectrograms.Spectrogram:
        """The spectrogram being visualised on this panel."""
        return self._spectrogram

    @property
    def name(self) -> PanelName:
        """The name of the panel."""
        return self._name

    def get_time_type(self) -> spectre_server.core.spectrograms.TimeType:
        """The time type of the spectrogram.

        :raises ValueError: If the `time_type` has not been set.
        """
        return self._time_type

    def set_time_type(self, value: spectre_server.core.spectrograms.TimeType) -> None:
        """Set the `TimeType` for the spectrogram.

        This controls how time is represented and annotated on the panel.

        :param value: The `TimeType` to assign to the spectrogram.
        """
        self._time_type = value

    def get_panel_format(self) -> PanelFormat:
        """Retrieve the panel format, which controls the style of the panel.

        :raises ValueError: If the `panel_format` has not been set.
        """
        if self._panel_format is None:
            raise ValueError(f"`panel_format` must be set for the panel `{self.name}`")
        return self._panel_format

    def set_panel_format(self, value: PanelFormat) -> None:
        """Set the panel format to control the style of the panel.

        :param value: The `PanelFormat` to assign to the panel.
        """
        self._panel_format = value

    def _get_ax(self) -> matplotlib.axes.Axes:
        """Return the `Axes` object bound to this panel.

        This method is protected to restrict direct access to `matplotlib` functionality,
        promoting encapsulation, promoting encapsulation.

        :raises ValueError: If the `Axes` object has not been set.
        """
        if self._ax is None:
            raise ValueError(f"`ax` must be set for the panel `{self.name}`")
        return self._ax

    def set_ax(self, value: matplotlib.axes.Axes) -> None:
        """Assign a Matplotlib `Axes` object to this panel.

        This `Axes` will be used for drawing and annotations.

        :param value: The Matplotlib `Axes` to assign to the panel.
        """
        self._ax = value

    def _get_fig(self) -> matplotlib.figure.Figure:
        """Return the `Figure` object bound to this panel.

        This method is protected to restrict direct access to `matplotlib` functionality,
        promoting encapsulation, promoting encapsulation.

        :raises ValueError: If the `Figure` object has not been set.
        """
        if self._fig is None:
            raise ValueError(f"`fig` must be set for the panel `{self.name}`")
        return self._fig

    def set_fig(self, value: matplotlib.figure.Figure) -> None:
        """
        Assign a Matplotlib `Figure` object to this panel.

        This `Figure` is shared across all panels in the `PanelStack`.

        :param value: The Matplotlib `Figure` to assign to the panel.
        """
        self._fig = value

    def get_identifier(self) -> typing.Optional[str]:
        """Optional identifier for the panel.

        This identifier can be used to distinguish panels or aid in superimposing
        panels in a stack.
        """
        return self._identifier

    def set_identifier(self, value: str) -> None:
        """Set the optional identifier for the panel.

        This can be used to distinguish panels or aid in superimposing panels.
        """
        self._identifier = value

    def hide_xaxis_labels(self) -> None:
        """Hide the labels for xaxis ticks in the panel."""
        self._get_ax().tick_params(axis="x", labelbottom=False)

    def hide_yaxis_labels(self) -> None:
        """Hide the labels for yaxis ticks in the panel."""
        self._get_ax().tick_params(axis="y", labelleft=False)

    def sharex(self, axes: matplotlib.axes.Axes):
        """Share the xaxis with another axes."""
        self._get_ax().sharex(axes)

    def get_xaxis_labels(self) -> list[str]:
        """Get the text string of all xaxis tick labels."""
        tick_labels = self._get_ax().get_xaxis().get_ticklabels(which="both")
        return [tick_label.get_text() for tick_label in tick_labels]

    def get_yaxis_labels(self) -> list[str]:
        """Get the text string of all yaxis tick labels."""
        tick_labels = self._get_ax().get_yaxis().get_ticklabels(which="both")
        return [tick_label.get_text() for tick_label in tick_labels]

    def get_xlabel(self) -> str:
        """Get the xlabel text string."""
        return self._get_ax().get_xlabel()

    def get_ylabel(self) -> str:
        """Get the ylabel text string."""
        return self._get_ax().get_ylabel()

    def share_axes(self, panel: "BasePanel") -> None:
        # TODO: More elegantly share axes, rather than access protected method from
        # another instance. Probably, this should just be entirely managed by the `PanelStack`
        self.set_ax(panel._get_ax())
        self.set_fig(panel._get_fig())


class BaseTimeSeriesPanel(BasePanel):
    """
    Abstract subclass of `BasePanel` designed for visualising time series data.

    Subclasses must implement any remaining abstract methods from `BasePanel`.
    """

    @property
    def xaxis_type(self) -> typing.Literal[XAxisType.TIME]:
        return XAxisType.TIME

    @property
    def times(self) -> npt.NDArray[np.float32 | np.datetime64]:
        """The times assigned to each spectrum according to the `TimeType`."""
        return (
            self.spectrogram.times
            if self.get_time_type()
            == spectre_server.core.spectrograms.TimeType.RELATIVE
            else self.spectrogram.datetimes
        )

    def annotate_xaxis(self) -> None:
        """Annotate the xaxis according to the specified `TimeType`."""
        ax = self._get_ax()
        if self.get_time_type() == spectre_server.core.spectrograms.TimeType.RELATIVE:
            ax.set_xlabel("Time [s]")
        else:
            # TODO: Adapt for time ranges greater than one day
            start_date = datetime.datetime.strftime(
                self.spectrogram.start_datetime.astype(datetime.datetime),
                spectre_server.core.config.TimeFormat.DATE,
            )
            ax.set_xlabel(f"Time [UTC] (Start Date: {start_date})")
            ax.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter(
                    spectre_server.core.config.TimeFormat.TIME
                )
            )
