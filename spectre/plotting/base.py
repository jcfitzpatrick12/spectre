# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.dates as mdates
import numpy as np

from spectre.spectrograms.spectrogram import Spectrogram

class BasePanel:
    def __init__(self, spectrogram: Spectrogram, time_type: str = "seconds"):
        self.spectrogram = spectrogram
        self.time_type = time_type
        self.set_times()
        
        self.x_axis_type: Optional[str] = None
        self.set_x_axis_type()

        self.index = None
    

    @abstractmethod
    def draw(fig, ax):
        pass


    @abstractmethod
    def annotate_x_axis(self, ax):
        pass


    @abstractmethod
    def annotate_y_axis(self, ax):
        pass


    @abstractmethod
    def set_x_axis_type(self):
        """ Required to allow for axes sharing in the stack"""
        pass


    def _validate_time_types(self):
        valid_time_types = ["seconds", "datetimes"]
        if self.time_type not in valid_time_types:
            raise ValueError(f"Invalid time type. "
                             f"Expected one of {valid_time_types} "
                             f"but received {self.time_type}")


    def set_times(self):
        self._validate_time_types()
        self.times = self.spectrogram.times if self.time_type == "seconds" else self.spectrogram.datetimes
        return
    

    def bind_to_colors(self, values: np.ndarray, cmap = cm.winter): 
        return zip(values, cmap(np.linspace(0.25, 0.75, len(values))))
    

    def hide_x_axis_numbers(self, ax):
        ax.tick_params(axis='x', labelbottom=False)


    def hide_y_axis_numbers(self, ax):
        ax.tick_params(axis='y', labelbottom=False)
    

class BaseTimeSeriesPanel(BasePanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def annotate_x_axis(self, ax):
        if self.time_type == "seconds":
            ax.set_xlabel('Time [s]')
        else:
            ax.set_xlabel('Time [UTC]')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
    def set_x_axis_type(self):
        self.x_axis_type = "time"


class BaseSpectrumPanel(BasePanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def annotate_x_axis(self, ax):
        ax.set_xlabel('Frequency [MHz]')

    def set_x_axis_type(self):
        self.x_axis_type = "frequency"
