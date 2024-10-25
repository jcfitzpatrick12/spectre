# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

from matplotlib import cm
import matplotlib.dates as mdates
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from spectre.spectrograms.spectrogram import Spectrogram

class BasePanel(ABC):
    def __init__(self, 
                 spectrogram: Spectrogram, 
                 time_type: str = "seconds"):
        self._spectrogram = spectrogram

        self._validate_time_type(time_type)
        self._time_type = time_type
        self._index: Optional[int] = None
        
        self._x_axis_type: Optional[str] = None
        self._set_x_axis_type()

    

    @abstractmethod
    def draw(fig: Figure, ax: Axes):
        pass


    @abstractmethod
    def annotate_x_axis(self, ax: Axes):
        pass


    @abstractmethod
    def annotate_y_axis(self, ax: Axes):
        pass


    @abstractmethod
    def _set_x_axis_type(self):
        """ Required to allow for axes sharing in the stack"""
        pass


    @property
    def spectrogram(self) -> Spectrogram:
        return self._spectrogram
    

    @property
    def time_type(self) -> str:
        return self._time_type
    

    @property
    def index(self) -> int:
        if self._index is None:
            raise ValueError(f"Index has not yet been set!")
        return self._index 
    

    @index.setter
    def index(self, value: int) -> None:
        self._index = value


    @property
    def x_axis_type(self) -> str:
        return self._x_axis_type


    @property
    def times(self):
        return self.spectrogram.times if self.time_type == "seconds" else self.spectrogram.datetimes


    def _validate_time_type(self, 
                            time_type: str):
        valid_time_types = ["seconds", "datetimes"]
        if time_type not in valid_time_types:
            raise ValueError(f"Invalid time type. "
                             f"Expected one of {valid_time_types} "
                             f"but received {time_type}")
    

    def bind_to_colors(self, 
                       values: np.ndarray, 
                       cmap = cm.winter): 
        return zip(values, cmap(np.linspace(0.25, 0.75, len(values))))
    

    def hide_x_axis_numbers(self, 
                            ax: Axes):
        ax.tick_params(axis='x', labelbottom=False)


    def hide_y_axis_numbers(self, 
                            ax: Axes):
        ax.tick_params(axis='y', labelbottom=False)
    

class BaseTimeSeriesPanel(BasePanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

    def annotate_x_axis(self, 
                        ax: Axes):
        if self.time_type == "seconds":
            ax.set_xlabel('Time [s]')
        else:
            ax.set_xlabel('Time [UTC]')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        
    def _set_x_axis_type(self):
        self._x_axis_type = "time"


class BaseSpectrumPanel(BasePanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def annotate_x_axis(self, 
                        ax: Axes):
        ax.set_xlabel('Frequency [MHz]')


    def _set_x_axis_type(self):
        self._x_axis_type = "frequency"
