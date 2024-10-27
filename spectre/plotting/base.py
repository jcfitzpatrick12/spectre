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

TIME_X_AXIS = "time"
FREQUENCY_X_AXIS = "frequency"

class BasePanel(ABC):
    def __init__(self, 
                 name: str,
                 spectrogram: Spectrogram, 
                 time_type: str = "seconds"):
        self._name = name
        self._spectrogram = spectrogram

        self._validate_time_type(time_type)
        self._time_type = time_type

        self._x_axis_type: Optional[str] = None
        self._set_x_axis_type()

        self._ax: Optional[Axes] = None # defined while stacking
        self._fig: Optional[Figure] = None # defined while stacking


    @abstractmethod
    def draw(self):
        pass


    @abstractmethod
    def annotate_x_axis(self):
        pass


    @abstractmethod
    def annotate_y_axis(self):
        pass


    @abstractmethod
    def _set_x_axis_type(self):
        """ Required to allow for axes sharing in the stack"""
        pass

    
    @abstractmethod
    def _set_name(self):
        pass


    @property
    def spectrogram(self) -> Spectrogram:
        return self._spectrogram
    

    @property
    def tag(self) -> str:
        return self._spectrogram.tag
    

    @property
    def time_type(self) -> str:
        return self._time_type
    

    @property
    def name(self) -> str:
        if self._name is None:
            raise AttributeError(f"Name for this panel has not yet been set")
        return self._name
    

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
    
    
    @property
    def ax(self) -> Axes:
        if self._ax is None:
            raise AttributeError(f"Axes have not yet been set for this panel")
        return self._ax
    

    @ax.setter
    def ax(self, value: Axes) -> None:
        self._ax = value


    @property
    def fig(self) -> Figure:
        if self._fig is None:
            raise AttributeError(f"Figure has not yet been set for this panel")
        return self._fig
    

    @fig.setter
    def fig(self, value: Figure) -> None:
        self._fig = value
    


    @property
    def x_axis_type(self) -> str:
        if self._x_axis_type is None:
            raise AttributeError(f"x-axis type has not been defined for this panel")
        return self._x_axis_type


    def _validate_time_type(self, 
                            time_type: str):
        valid_time_types = ["seconds", "datetimes"]
        if time_type not in valid_time_types:
            raise ValueError(f"Invalid time type. "
                             f"Expected one of {valid_time_types} "
                             f"but received {time_type}")
    

    def bind_to_colors(self, 
                       values: np.ndarray, 
                       cmap: str = "winter"): 
        cmap = cm.get_cmap(cmap)
        rgbas = cmap(np.linspace(0.1, 0.9, len(values)))
        return zip(values, rgbas) # assign each RGBA array to each value
    

    def hide_x_axis_labels(self) -> None:
        self.ax.tick_params(axis='x', labelbottom=False)


    def hide_y_axis_labels(self) -> None:
        self.ax.tick_params(axis='y', labelbottom=False)
    

class BaseTimeSeriesPanel(BasePanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

    @property
    def times(self):
        return self.spectrogram.times if self.time_type == "seconds" else self.spectrogram.datetimes
    

    def annotate_x_axis(self):
        if self.time_type == "seconds":
            self.ax.set_xlabel('Time [s]')
        else:
            self.ax.set_xlabel('Time [UTC]')
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        
    def _set_x_axis_type(self):
        self._x_axis_type = TIME_X_AXIS



class BaseSpectrumPanel(BasePanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @property
    def frequencies(self):
        return self._spectrogram.frequencies


    def annotate_x_axis(self):
        self.ax.set_xlabel('Frequency [MHz]')


    def _set_x_axis_type(self):
        self._x_axis_type = FREQUENCY_X_AXIS
